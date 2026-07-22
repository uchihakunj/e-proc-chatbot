# =============================================================================
#  voice_server.py  —  Fully OFFLINE voice backend for the eProcurement chatbot
# =============================================================================
#  Speech-to-Text  : faster-whisper ("small", auto-detects Hindi & English)
#  Text-to-Speech  : pyttsx3 (Windows SAPI voices — no extra download)
#  Nothing leaves this machine. Runs on http://localhost:5050
#
#  -------------------------------------------------------------------------
#  WINDOWS SETUP
#  -------------------------------------------------------------------------
#  1. Install Python dependencies (in a terminal / PowerShell):
#
#         pip install flask flask-cors faster-whisper pyttsx3
#
#  2. Install ffmpeg for Windows (needed to convert browser audio -> WAV):
#       - Download a Windows build from:  https://ffmpeg.org/download.html
#         (e.g. the "Windows builds from gyan.dev" release-full zip)
#       - Unzip it, e.g. to  C:\ffmpeg
#       - Add the "bin" folder to your PATH, e.g.  C:\ffmpeg\bin
#         (Settings -> System -> About -> Advanced system settings ->
#          Environment Variables -> Path -> Edit -> New -> C:\ffmpeg\bin)
#       - Open a NEW terminal and verify:   ffmpeg -version
#
#  3. Run this server:
#
#         python voice_server.py
#
#  NOTE: the first run downloads the faster-whisper "small" model (~460 MB)
#        into your local cache. After that it works fully offline.
# =============================================================================

import os
import subprocess
import tempfile
import time

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

try:
    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio
except ImportError as e:
    raise SystemExit(
        "faster-whisper is not installed. Run:\n"
        "    pip install flask flask-cors faster-whisper pyttsx3"
    ) from e

import pyttsx3
import re
import asyncio
import threading

# Edge-TTS: free Microsoft neural voices with REAL Hindi + Indian-English voices
# (pyttsx3/SAPI on this box has English voices only, so it can't speak Hindi).
# Optional — if it's unavailable (offline / not installed) we fall back to
# pyttsx3 so English speech still works with no internet.
try:
    import edge_tts
    _EDGE_OK = True
except Exception:            # pragma: no cover - optional dependency
    _EDGE_OK = False

# Neural voice per (language, gender). Female by default (the old SAPI default
# was male "David"). All env-overridable.
TTS_VOICES = {
    ("hi", "female"): os.getenv("TTS_VOICE_HI_F", "hi-IN-SwaraNeural"),
    ("hi", "male"):   os.getenv("TTS_VOICE_HI_M", "hi-IN-MadhurNeural"),
    ("en", "female"): os.getenv("TTS_VOICE_EN_F", "en-IN-NeerjaNeural"),
    ("en", "male"):   os.getenv("TTS_VOICE_EN_M", "en-IN-PrabhatNeural"),
}
TTS_DEFAULT_GENDER = os.getenv("TTS_GENDER", "female").lower()
# Speak a little faster than the neutral default (env-overridable, e.g. "+25%").
TTS_RATE = os.getenv("TTS_RATE", "+15%")
_DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def _pick_voice(text, gender):
    """Route to a Hindi voice if the text has Devanagari, else English."""
    lang = "hi" if _DEVANAGARI.search(text or "") else "en"
    g = gender if gender in ("male", "female") else TTS_DEFAULT_GENDER
    return TTS_VOICES.get((lang, g), TTS_VOICES[(lang, "female")]), lang


def _edge_stream_sync(text, voice):
    """Yield MP3 chunks from edge-tts as they are synthesised, so the browser can
    start playing on the FIRST chunk instead of waiting for the whole clip.
    Bridges edge-tts' async stream into a sync generator via a per-call loop."""
    loop = asyncio.new_event_loop()
    agen = edge_tts.Communicate(text, voice, rate=TTS_RATE).stream()
    try:
        while True:
            try:
                chunk = loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                break
            if chunk.get("type") == "audio" and chunk.get("data"):
                yield chunk["data"]
    finally:
        try:
            loop.run_until_complete(agen.aclose())
        except Exception:            # pragma: no cover - best-effort cleanup
            pass
        loop.close()


def _prewarm_tts():
    """Fetch the edge-tts security token once at startup so the FIRST real click
    doesn't pay the ~5s cold-connect (edge-tts caches the token process-wide)."""
    if not _EDGE_OK:
        return
    try:
        voice, _ = _pick_voice("नमस्ते", "female")
        for _ in _edge_stream_sync("नमस्ते", voice):
            pass
        print("[TTS] edge-tts pre-warmed (token cached)")
    except Exception as exc:         # pragma: no cover
        print(f"[TTS] edge-tts pre-warm skipped: {exc}")


def _pyttsx3_fallback(text, gender, wav_path):
    """Offline SAPI synthesis; prefer a female (Zira) voice when available."""
    engine = pyttsx3.init()
    try:
        want_male = (gender == "male")
        for v in engine.getProperty("voices"):
            nm = (getattr(v, "name", "") or "").lower()
            if (want_male and "david" in nm) or (not want_male and "zira" in nm):
                engine.setProperty("voice", v.id)
                break
    except Exception:            # pragma: no cover - voice enumeration is best-effort
        pass
    engine.save_to_file(text, wav_path)
    engine.runAndWait()
    engine.stop()

# -----------------------------------------------------------------------------
# Flask app + CORS (so the HTML page in the browser can call this server)
# -----------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)  # allow cross-origin requests from the chatbot HTML page

# -----------------------------------------------------------------------------
# Load the speech-to-text model ONCE at startup.
#   - "small"  : good balance of accuracy/speed, multilingual (hi + en)
#   - device   : "cpu" works everywhere; compute_type "int8" keeps it fast/light
# -----------------------------------------------------------------------------
# Model is env-configurable: set WHISPER_MODEL=medium for noticeably better
# Hindi / accented-English accuracy (~1.5 GB, slower on CPU). "small" is the
# fast default. "large-v3" is best but heavy.
# Default "base": ~2x faster than "small" on CPU for short voice queries, which
# matters because whisper competes with the resident Ollama LLM for cores.
# Set WHISPER_MODEL=small (better Hindi) or =medium (best, slow) to override.
_WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
# cpu_threads: faster-whisper defaults to ~4; this box has more cores. A small
# bump helps a little (the real cost is auto-detect + contention with Ollama).
_WHISPER_THREADS = int(os.getenv("WHISPER_THREADS", "8"))
_STT_FORCE_LANG = os.getenv("STT_FORCE_LANG", "auto").strip().lower()
if _STT_FORCE_LANG not in {"auto", "en", "hi"}:
    _STT_FORCE_LANG = "auto"
_STT_VAD_MIN_SILENCE_MS = int(os.getenv("STT_VAD_MIN_SILENCE_MS", "300"))
_STT_LOG_TIMINGS = os.getenv("STT_LOG_TIMINGS", "1").strip().lower() in ("1", "true", "yes", "on")
print(f"Loading faster-whisper '{_WHISPER_MODEL}' model (downloads on first run) ...")
stt_model = WhisperModel(
    _WHISPER_MODEL, device="cpu", compute_type="int8", cpu_threads=_WHISPER_THREADS,
)
print("Speech-to-text model ready.")

# Domain bias for the decoder: without it, whisper mis-hears procurement terms
# (e.g. "challan" -> "Holland"). initial_prompt nudges it toward this vocabulary.
#
# IMPORTANT: the prompt must MATCH the spoken language. A single bilingual prompt
# (English + Devanagari) corrupts transcription: on noisy/accented ENGLISH speech
# the model mis-detects Hindi and then *leaks the Devanagari prompt vocabulary*
# into the output as garbage (e.g. "नामत पीड्यि फर्रावक ... पुगतान"). So we detect
# the language first and feed a single-language prompt, locking the output script.
STT_PROMPT_EN = (
    "Indian government e-procurement. Terms: tender, bid, EMD, earnest money deposit, "
    "challan, corrigendum, vendor, supplier, contractor, bank guarantee, GFR, DSC, "
    "performance security, auction, registration, bid security, refund."
)
STT_PROMPT_HI = (
    "भारत सरकार ई-प्रोक्योरमेंट। शब्द: निविदा, बोली, धरोहर राशि, चालान, शुद्धिपत्र, विक्रेता, "
    "ठेकेदार, बैंक गारंटी, पंजीकरण, नीलामी, भुगतान, अनुबंध, वापसी, स्थिति, वैधता, "
    "निविदा जमा करने की तिथि। "
    # Hindi procurement speech is code-mixed — these terms are spoken in English
    # even inside Hindi sentences, so the Hindi prompt must bias toward them too
    # (else "EMD"->इएम्टी, "corrigendum"->कोरिंडम, "status"->इस्तिठी).
    "Common English terms used as-is: EMD, tender, bid, corrigendum, refund, status, "
    "validity, vendor, registration, challan, bank guarantee, GFR, DSC, NIT, "
    "bid security, e-Procurement portal."
)


def _safe_remove(path):
    """Delete a temp file if it exists (Windows-safe — handles must be closed)."""
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def _prompt_for_lang(lang):
    return STT_PROMPT_HI if lang == "hi" else STT_PROMPT_EN


def _detect_supported_lang(pcm):
    det_lang, det_prob, all_probs = stt_model.detect_language(pcm)
    if det_lang == "en":
        return "en", STT_PROMPT_EN, det_prob
    if det_lang == "hi":
        return "hi", STT_PROMPT_HI, det_prob
    probs = dict(all_probs or [])
    if probs.get("hi", 0.0) >= probs.get("en", 0.0):
        return "hi", STT_PROMPT_HI, probs.get("hi", 0.0)
    return "en", STT_PROMPT_EN, probs.get("en", 0.0)


# -----------------------------------------------------------------------------
# /stt  —  Speech to Text
#   Accepts:  multipart/form-data with field "audio" (webm or wav)
#   Returns:  {"text": "<transcript>"}
# -----------------------------------------------------------------------------
@app.route("/stt", methods=["POST"])
def stt():
    raw_path = wav_path = None
    started = time.perf_counter()
    marks = {}
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No 'audio' file in request."}), 500

        audio = request.files["audio"]

        # 1. Save the raw browser audio to a temp file.
        #    NamedTemporaryFile(delete=False) so we can close it and let
        #    ffmpeg / Whisper open it (Windows can't delete an open file).
        raw_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".webm")
        raw_path = raw_tmp.name
        raw_tmp.close()           # close our handle BEFORE writing/using it
        audio.save(raw_path)
        marks["saved"] = time.perf_counter()

        # 2. Convert to 16 kHz mono WAV using ffmpeg.exe (must be on PATH).
        wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wav_path = wav_tmp.name
        wav_tmp.close()

        result = subprocess.run(
            ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
             "-i", raw_path, "-vn", "-sn", "-dn", "-ac", "1", "-ar", "16000",
             wav_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return jsonify({
                "error": "ffmpeg conversion failed. Is ffmpeg on PATH? "
                         + (result.stderr or "")[-400:]
            }), 500
        marks["ffmpeg"] = time.perf_counter()

        # 3a. Decode the WAV once into the float32 array Whisper wants, so we can
        #     run language detection AND transcription on it without re-reading.
        pcm = decode_audio(wav_path, sampling_rate=16000)
        marks["decode"] = time.perf_counter()

        # 3b. Detect the spoken language FIRST, then lock the decoder to it with a
        #     single-language prompt. The split EN/HI prompts (not an English
        #     default) are what stop English from leaking into Devanagari, so we
        #     now TRUST the detector for both languages instead of biasing to
        #     English — biasing English was breaking genuine Hindi speech.
        if _STT_FORCE_LANG in {"en", "hi"}:
            lang = _STT_FORCE_LANG
            prompt = _prompt_for_lang(lang)
            det_prob = 1.0
        else:
            lang, prompt, det_prob = _detect_supported_lang(pcm)
        marks["lang"] = time.perf_counter()

        # 3c. Transcribe with the language LOCKED and a single-language prompt.
        #     beam_size=1 (greedy) is far faster than the default 5; vad_filter
        #     strips silence (faster, and stops prompt-echo on silent clips);
        #     condition_on_previous_text=False keeps short clips from drifting.
        segments, info = stt_model.transcribe(
            pcm,
            language=lang,
            initial_prompt=prompt,
            beam_size=int(os.getenv("WHISPER_BEAM", "1")),
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": _STT_VAD_MIN_SILENCE_MS},
            condition_on_previous_text=False,
        )
        text = "".join(seg.text for seg in segments).strip()
        marks["transcribe"] = time.perf_counter()

        if _STT_LOG_TIMINGS:
            print(
                "[STT] "
                f"lang={lang} model={_WHISPER_MODEL} "
                f"save={marks['saved']-started:.3f}s "
                f"ffmpeg={marks['ffmpeg']-marks['saved']:.3f}s "
                f"decode={marks['decode']-marks['ffmpeg']:.3f}s "
                f"lang_detect={marks['lang']-marks['decode']:.3f}s "
                f"transcribe={marks['transcribe']-marks['lang']:.3f}s "
                f"total={marks['transcribe']-started:.3f}s "
                f"chars={len(text)}"
            )

        return jsonify({"text": text, "lang": lang, "lang_prob": round(float(det_prob), 3)})

    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500

    finally:
        # Windows: files were closed above, so deletion now succeeds.
        _safe_remove(raw_path)
        _safe_remove(wav_path)


# -----------------------------------------------------------------------------
# /tts  —  Text to Speech
#   Accepts:  JSON  {"text": "...", "voice": "female"|"male" (optional)}
#   Returns:  audio/mpeg (edge-tts neural, Hindi+English) or audio/wav (pyttsx3
#             offline fallback). Language is auto-detected from the text script.
# -----------------------------------------------------------------------------
@app.route("/tts", methods=["GET", "POST"])
def tts():
    data = request.get_json(force=True, silent=True) if request.method == "POST" else None
    data = data or {}
    # GET query params let an <audio src=...> element stream + play progressively.
    text = (request.values.get("text") or data.get("text") or "").strip()
    # Optional gender hint from the UI ("female" | "male"); default female.
    gender = (request.values.get("voice") or data.get("voice") or data.get("gender") or "").lower()
    if not text:
        return jsonify({"error": "No 'text' provided."}), 400
    text = text[:1200]

    # 1) Preferred: STREAM edge-tts neural audio (Hindi/English by script) so the
    #    browser starts playing on the first chunk. Pull the first chunk here so
    #    an early failure (offline) falls back to pyttsx3 cleanly.
    if _EDGE_OK:
        try:
            voice, lang = _pick_voice(text, gender)
            gen = _edge_stream_sync(text, voice)
            first = next(gen, b"")
            if first:
                def _body(_first=first, _gen=gen):
                    yield _first
                    yield from _gen
                return Response(stream_with_context(_body()), mimetype="audio/mpeg",
                                headers={"X-TTS-Voice": voice, "X-TTS-Lang": lang,
                                         "Cache-Control": "no-store"})
            print("[TTS] edge-tts produced no audio; falling back to pyttsx3")
        except Exception as exc:  # noqa: BLE001 - network/voice error -> fallback
            print(f"[TTS] edge-tts failed ({exc}); falling back to pyttsx3")

    # 2) Offline fallback: pyttsx3/SAPI (English voices only on this box).
    wav_path = None
    try:
        wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wav_path = wav_tmp.name
        wav_tmp.close()
        _pyttsx3_fallback(text, gender, wav_path)
        with open(wav_path, "rb") as fh:
            wav_bytes = fh.read()
        return Response(wav_bytes, mimetype="audio/wav")
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500
    finally:
        _safe_remove(wav_path)


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "offline voice server",
        "endpoints": {"POST /stt": "audio -> text", "POST /tts": "text -> audio/wav"},
    })


# -----------------------------------------------------------------------------
# Start
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 62)
    print("  Offline Voice Server is running")
    print("  URL        :  http://localhost:5050")
    print("  Endpoints  :  POST /stt   (speech -> text)")
    print("               POST /tts   (text   -> speech)")
    print("  Privacy    :  STT local; TTS uses edge-tts (online) + offline fallback.")
    print("=" * 62)
    # Warm the edge-tts token in the background so the first Listen click is fast.
    threading.Thread(target=_prewarm_tts, daemon=True).start()
    # threaded=True so a slow transcription doesn't block a TTS request.
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)
