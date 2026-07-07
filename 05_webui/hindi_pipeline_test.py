# -*- coding: utf-8 -*-
"""End-to-end test of the proposed Hindi architecture:
   Hindi query -> translate hi->en -> qwen2.5:7b + Arc RAG (English) -> translate en->hi.
Measures each stage and prints the final Hindi answer. NLLB-600M stands in for
IndicTrans2 (gated/uncompilable here); translation LATENCY is representative,
domain-term QUALITY would be better with IndicTrans2.
"""
import sys, json, time, requests, torch
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

HINDI_Q = "चालान भुगतान की प्रक्रिया क्या है? कृपया चरण-दर-चरण बताइए।"

print("Loading NLLB translator (one-time)...", flush=True)
_t = time.time()
M = "facebook/nllb-200-distilled-600M"
tok = AutoTokenizer.from_pretrained(M)
mt = AutoModelForSeq2SeqLM.from_pretrained(M).eval()
print(f"  translator loaded in {time.time()-_t:.0f}s (one-time at startup, not per-query)\n", flush=True)

def translate(texts, src, tgt, max_new=256):
    """Batch-translate a list of strings src->tgt."""
    tok.src_lang = src
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        out = mt.generate(**enc, forced_bos_token_id=tok.convert_tokens_to_ids(tgt),
                          max_new_tokens=max_new, num_beams=1)
    return tok.batch_decode(out, skip_special_tokens=True)

def ask_english(q):
    """Stream the English answer from the running qwen+Arc chatbot."""
    ttc = ttft = None; toks = []; t0 = time.time()
    with requests.post("http://localhost:5000/api/stream",
                       json={"query": q, "session_id": "hi_pipe"}, stream=True, timeout=400) as r:
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "): continue
            try: e = json.loads(line[6:])
            except: continue
            ty = e.get("type")
            if ty == "context" and ttc is None: ttc = time.time()-t0
            elif ty == "token":
                if ttft is None: ttft = time.time()-t0
                toks.append(e.get("content", ""))
    return "".join(toks), ttc, ttft, time.time()-t0

print("="*60)
print("PROPOSED PIPELINE: qwen2.5:7b + Arc + NLLB translate-roundtrip")
print("="*60)
print(f"\nHindi query: {HINDI_Q}\n", flush=True)
T0 = time.time()

# 1) hi -> en
t = time.time(); en_q = translate([HINDI_Q], "hin_Deva", "eng_Latn", max_new=80)[0]; t_q = time.time()-t
print(f"[1] hi->en query   {t_q:4.1f}s  -> {en_q}", flush=True)

# 2) English RAG answer (qwen + Arc)
en_ans, ttc, ttft, t_ans = ask_english(en_q)
print(f"[2] English answer {t_ans:4.1f}s  (context {ttc:.1f}s, first-token {ttft:.1f}s, {len(en_ans)} chars)", flush=True)

# 3) en -> hi  (line-by-line to preserve structure; batch for speed)
lines = en_ans.split("\n")
idx = [i for i, ln in enumerate(lines) if ln.strip() and set(ln.strip()) - set("|-: ")]
t = time.time()
translated = translate([lines[i] for i in idx], "eng_Latn", "hin_Deva", max_new=256) if idx else []
for j, i in enumerate(idx): lines[i] = translated[j]
hi_ans = "\n".join(lines); t_back = time.time()-t
print(f"[3] en->hi answer  {t_back:4.1f}s  ({len(idx)} lines)\n", flush=True)

TOTAL = time.time()-T0
print("="*60)
print(f"TOTAL Hindi response: {TOTAL:.1f}s")
print(f"  = hi->en {t_q:.1f}s  +  English answer {t_ans:.1f}s  +  en->hi {t_back:.1f}s")
print("="*60)
print("\n--- FINAL HINDI ANSWER ---\n")
print(hi_ans[:1400])
