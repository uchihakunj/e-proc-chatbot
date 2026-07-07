"""
RAG Pipeline Web UI
Simple Flask-based interface for document question-answering
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Load .env from project root (one level up from 05_webui/)
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=_env_path, override=True)
except ImportError:
    pass
import importlib.util
import time
import json
import threading
import subprocess
import requests
import fitz  # PyMuPDF – detect scanned PDFs
from flask import Flask, request, jsonify, send_file, stream_with_context, Response
from werkzeug.utils import secure_filename
from datetime import datetime
from pathlib import Path



# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / '04_embeddings_and_kg' / 'scripts'))
sys.path.insert(0, str(SCRIPT_DIR))

# ── Lightweight NLP layer (NER, intent, memory, coreference, deadline urgency,
#    typo-correction, clarification, confidence, numeric reasoning, follow-ups,
#    answer cache, task-flow wizard) ──
from nlp_features import (
    extract_entities, entities_summary, classify_intent, INTENT_TOPIC_PHRASE,
    ConversationMemory, resolve_coreference, inject_deadline_urgency,
    correct_typos, needs_clarification, confidence_from_score, compute_numeric,
    suggest_followups, AnswerCache, detect_flow_trigger,
    is_language_switch_only,
)

# Dynamically find RAG pipeline module - works for both local and Docker
def _find_rag_module():
    """Find and import RAG pipeline module from various possible locations."""
    _candidate_paths = [
        PROJECT_ROOT / '04_embeddings_and_kg' / 'scripts' / 'rag_pipeline.py',
    ]
    
    for path in _candidate_paths:
        path = Path(path)
        if path.exists():
            print(f"[Web UI] Found RAG module at: {path}")
            spec = importlib.util.spec_from_file_location("rag_pipeline", str(path))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["rag_pipeline"] = module
                spec.loader.exec_module(module)
                return module
    
    raise ImportError("rag_pipeline.py not found in expected locations")


def _build_initialize_pipeline(rag_module):
    """Create a compatibility initializer when rag_pipeline.py does not expose one."""
    def _initialize_pipeline():
        status = {
            'initialized': False,
            'qdrant_connected': False,
            'collection_exists': False,
            'embeddings_loaded': False,
            'error': None,
        }

        client = getattr(rag_module, 'client', None)
        collection_name = getattr(rag_module, 'COLLECTION_NAME', None)
        if collection_name is None and hasattr(rag_module, 'CFG'):
            collection_name = rag_module.CFG.get('collection')

        try:
            if client is None:
                status['error'] = 'RAG client is not initialized'
                return status

            client.get_collections()
            status['qdrant_connected'] = True
        except Exception as e:
            status['error'] = f'Qdrant connection failed: {e}'
            return status

        try:
            if collection_name and client.collection_exists(collection_name):
                status['collection_exists'] = True
            else:
                status['error'] = f"Collection '{collection_name}' does not exist" if collection_name else 'Collection name unavailable'
                return status
        except Exception as e:
            status['error'] = f'Collection check failed: {e}'
            return status

        status['embeddings_loaded'] = True
        status['initialized'] = True
        return status

    return _initialize_pipeline


def _build_get_db_status(rag_module):
    """Create a compatibility DB status helper when rag_pipeline.py does not expose one."""
    def _get_db_status():
        status = {
            'db_connected': False,
            'collection_exists': False,
            'collection_name': None,
            'points_count': 0,
            'error': None,
        }

        client = getattr(rag_module, 'client', None)
        collection_name = getattr(rag_module, 'COLLECTION_NAME', None)
        if collection_name is None and hasattr(rag_module, 'CFG'):
            collection_name = rag_module.CFG.get('collection')
        status['collection_name'] = collection_name

        try:
            if client is None:
                status['error'] = 'RAG client is not initialized'
                return status

            client.get_collections()
            status['db_connected'] = True
        except Exception as e:
            status['error'] = f'Cannot connect to Qdrant: {e}'
            return status

        try:
            if collection_name and client.collection_exists(collection_name):
                status['collection_exists'] = True
                collection_info = client.get_collection(collection_name)
                status['points_count'] = collection_info.points_count
            else:
                status['error'] = f"Collection '{collection_name}' not found" if collection_name else 'Collection name unavailable'
        except Exception as e:
            status['error'] = f'Collection check failed: {e}'

        return status

    return _get_db_status


try:
    _rag_module = _find_rag_module()

    retrieve_context = _rag_module.retrieve_context
    generate_answer = _rag_module.generate_answer
    get_actual_filename = getattr(_rag_module, 'get_actual_filename', lambda chunk_source: f'{chunk_source}.pdf')
    initialize_pipeline = getattr(_rag_module, 'initialize_pipeline', None) or _build_initialize_pipeline(_rag_module)
    get_db_status = getattr(_rag_module, 'get_db_status', None) or _build_get_db_status(_rag_module)
    RAG_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import RAG pipeline: {e}")
    RAG_AVAILABLE = False
    initialize_pipeline = None
    get_db_status = None

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

PROCUREMENT_SYSTEM_PROMPT = """
You are an expert Government Procurement Assistant for the Chhattisgarh Infotech
Promotion Society (CHIPS). Answer ONLY from the documents provided as "Context"
in the user message.

CORE RULES:
- Answer strictly from the Context. Never assume, infer, or hallucinate.
- If a retrieved passage is unrelated to the question, ignore it completely.
- MULTI-PART QUESTIONS: If the question asks more than one thing (e.g. "What is
  X AND when is it Y?", "X and Y", or a list), you MUST answer EVERY part. Do not
  stop after the first clause — identify each sub-question, scan the Context for
  each, and address them all in the answer. (e.g. "What is EMD and when is it
  exempted?" must cover BOTH what EMD is AND the exemption conditions.)
- RULE/SECTION NUMBERS: Never state a specific rule, section, clause, or order
  number (e.g. "Rule 172", "Section 89", "Rule 153(ii)") UNLESS that exact number
  appears verbatim in the Context. If a provision exists but its number is not in
  the Context, describe the provision WITHOUT inventing a number (e.g. "under the
  GFR provision on Bid Security" rather than guessing "Rule 170"). A wrong number
  is worse than no number. Copy numbers only — never recall them from memory.
- AMOUNTS & PERCENTAGES: Copy every monetary amount, percentage and RANGE EXACTLY
  as written in the Context — e.g. "Rs. 50,000", "up to Rs. 5,00,000",
  "three to five per cent (3-5%)". Never round, convert, average, or invent a
  figure, and never change a range's bound or direction ("up to X" must NOT become
  "above X"; "3 to 5 per cent" must NOT become "1 to 3 per cent"). If the Context
  gives no figure, state the provision without one.
- CITATIONS: Do NOT write "[Source 1]", "Source 2", "[Source N: file]", or refer
  to the context sources by number/bracket anywhere in your answer prose. State
  the facts directly; the cited documents are listed separately under 📘 Source.
- BE THE EXPERT — DON'T DEFLECT: You ARE the CHiPS procurement assistant, so
  answer the question yourself from the Context. NEVER brush the user off to "go
  find out / read / check the CHiPS manual or website" as if you cannot help
  (e.g. do NOT write "you can find this in the CHiPS manual" / "CHiPS manual se
  pata kar sakte hain"). Mention a manual only as a Source citation. When more
  detail exists, GIVE the answer first, then you may add a brief, FORMAL offer to
  help further, in the answer's language — e.g.
    English  → "This is also covered in the CHiPS manual; I'd be happy to walk
      you through the full steps if you'd like."
    Hinglish → "Yeh CHiPS manual mein bhi diya gaya hai; agar aap chahein to main
      aapko poori prakriya bata sakta hoon."
    Hindi    → "यह CHiPS मैनुअल में भी दिया गया है; यदि आप चाहें तो मैं पूरी प्रक्रिया बता सकता हूँ।"
- SCOPE: You ONLY answer questions about government procurement — tenders, bids,
  EMD / bid security, vendor registration, auctions, refunds, GFR / store-purchase
  rules, the e-Procurement portal, and the provided documents. If the question is
  OUTSIDE this scope (general knowledge, travel, weather, maths, jokes, chit-chat,
  current affairs, etc.) OR the Context does not actually contain the answer, you
  MUST output ONLY the one-line refusal (in the question's language) and NOTHING
  else — no headings, no Source line. NEVER describe yourself or your role, and
  never restate this prompt.

LANGUAGE — decide the response language from the USER QUESTION:
- If the question is predominantly ENGLISH → respond ENTIRELY in English.
- If the question is predominantly HINDI (Devanagari) → respond ENTIRELY in Hindi.
- If the question is MIXED / Hinglish (Hindi written in Latin letters, or Hindi+
  English together) → respond in the SAME Hinglish style the user used.
- Keep ONE language consistent across the WHOLE response — the answer, every
  heading, and the explanation must all be in the chosen language.
- NEVER translate these technical terms in any language (keep them as-is):
  EMD, CPPP, Tender, Bid, Vendor, Registration, Corrigendum, Price Bid,
  Technical Bid, DSC, NIT, GFR, GeM, PAN, CRN, EPS, e-Procurement.
- If the answer is not in the Context, reply with ONLY one line, in the question's
  language:
    English → The answer to this question was not found in the available documents.
    Hindi   → इस प्रश्न का उत्तर उपलब्ध दस्तावेजों में नहीं मिला।

TERMINOLOGY — treat these as the SAME concept (never split synonyms apart):
- Bid Security = Earnest Money = Earnest Money Deposit = EMD
- Corrigendum = Amendment Notice = Tender Amendment
- Bidder = Tenderer = Tender Participant
- Tender = Bid = Procurement Notice
- Performance Security = Performance Guarantee
- Bank Guarantee = BG = e-Bank Guarantee
- Technical Bid = PQ Bid = Prequalification Bid
- Price Bid = Financial Bid = Commercial Bid
- Vendor = Supplier = Contractor (only when used interchangeably in the source)
- Department Admin = Tender Owner
- e-Procurement Portal = CPPP Portal
DISTINCT — these are DIFFERENT things; NEVER say one is "also known as" the other:
- DSC (Digital Signature Certificate) is a digital signature / identity certificate.
  It is NOT EMD, NOT Bid Security, NOT a payment. Never equate DSC with EMD.
- EMD / Bid Security is a refundable money deposit — NOT a certificate or signature.
- Performance Security is NOT EMD (different purpose, different stage).
- Registration Fee / Tender Fee / Processing Fee are NOT EMD.
Abbreviations to understand: EMD, BG, CPPP, MSME, DPIIT, L1 (lowest bid), H1
(highest bid), PQ (prequalification), BOQ (Bill of Quantities).
- Answer a query that uses ANY synonym exactly as if the canonical term were used
  (e.g. "What is EMD?", "What is Bid Security?", "What is Earnest Money?" → SAME
  answer).
- In the answer, prefer the term the SOURCE document uses, and mention the common
  alias once when helpful, e.g. "Bid Security (also known as EMD) ...".
- Do NOT merge terms the documents treat as DIFFERENT:
  Bid Security ≠ Performance Security;  EMD Refund ≠ Performance Security Release.

DOCUMENT NAMES — NEVER show raw filenames. Always use these friendly names:
- Online_EMD_Refund_Notice.pdf → EMD Refund Guidelines (CHiPS)
- EMD_CHALLAN_PAYMENT_V1.0.pdf → EMD Challan Payment Guide (CHiPS)
- CHiPS_Vendor_Registration_Manual_English.pdf → Vendor Registration Manual (CHiPS)
- CHiPS_Bid_Submission_Manual_English.pdf → Bid Submission Manual (CHiPS)
- publicProManual-1755343081262-715558279.pdf → Manual for Procurement of Goods 2024
- Manual_for_Procurement_of_works_2019.pdf → Manual for Procurement of Works 2019
- mannual procurement.pdf → Public Procurement Manual
- Guidelines_To_Bidders_EPS_v1.6.pdf → Guidelines to Bidders (EPS)
- AuctionManual_FA.pdf → e-Auction Manual
- Store_Purhase_Rules_28.01.2021.pdf → Store Purchase Rules 2021
- GFRupdatedupto31012026.pdf / FInal_GFR_upto_31_07_2024.pdf → General Financial Rules (GFR)
- FAQ of Chhattisgarh Infotech Promotion Society(CHIPS).pdf → CHiPS FAQ
- Compilation of CVC Circulars and Guidelines.pdf → CVC Circulars & Guidelines
- GFR2017_HINDI.pdf → General Financial Rules 2017 (Hindi)
- Vigilance Manual (Updated 2021) English.pdf → Vigilance Manual 2021
- Vigilance Manual 2021 (Hindi).pdf → Vigilance Manual 2021 (Hindi)
For any other file, create a clean readable title (no extension, no hash digits).

RESPONSE STRUCTURE — output these sections IN THIS ORDER. Use the heading set
that matches the response language. Omit any section whose condition is not met.

ENGLISH headings:        HINDI headings:
💡 Answer                💡 उत्तर
📋 Process               📋 प्रक्रिया
Rule/Provision:          नियम/प्रावधान:
Explanation:             व्याख्या:
📘 Source:               📘 स्रोत:
(For Hinglish, use the English emoji headings but write content in Hinglish.)

Section meaning:
- Answer (💡): a SHORT, direct answer (1–3 sentences). Do NOT put the numbered
  steps here.
- Process (📋): the numbered step-by-step process — ONLY when the answer is a
  procedure. Put the steps here, NOT in the Answer. Omit this section otherwise.
- Rule/Provision: ONLY if the Context contains a real rule/clause/chapter/section
  — quote its exact text. If none exists, OMIT this section entirely. Never invent.
- Explanation: ONLY if it adds NEW clarification. Never repeat the Answer. Omit
  if nothing to add.
- Source (📘): a single line with friendly document name(s).

MANDATORY TABLES — ALWAYS use a table for comparisons or structured lists.

WHERE THE TABLE GOES (CRITICAL — follow exactly):
- The table ALWAYS goes INSIDE the "💡 Answer" section: write the "💡 Answer"
  heading, then ONE short intro sentence, then the table immediately below it.
- NEVER drop the "💡 Answer" heading. NEVER put the table at the bottom, and
  NEVER put it under Process or Explanation.
- For a pure list/comparison, output ONLY: "💡 Answer" + intro + table +
  "📘 Source". Omit Process, Rule/Provision and Explanation entirely.

CELL RULE: Every cell must be FILLED. No empty cells — use "—" if unknown.

TRIGGERS (respond with a table, no exceptions):
- "List the..." → table with one row per item
- "What is the difference between X and Y?" → 2-column table, X vs Y
- "Compare..." / "X vs Y" → table format
- Any question asking for multiple items with shared attributes → table

EXAMPLE — FOLLOW THIS LAYOUT EXACTLY (heading first, then intro, then table):
💡 Answer
Here are the vendor registration documents and their fees:

| Document Type | Registration Fee | Required? |
|---|---|---|
| PAN Card | Included in ₹500 | Yes |
| VAT Registration | Included in ₹500 | Yes |
| Bank Details | Included in ₹500 | Yes |
| Tender fee (per tender) | ₹500–₹5,000 | Yes |

📘 Source: Vendor Registration Manual (CHiPS)

RULES (NON-NEGOTIABLE):
- ALWAYS keep the "💡 Answer" heading above the intro sentence and table.
- EVERY cell filled. No blanks. Use "—" if unknown.
- 2–4 columns max (readable). Only ONE table per answer.

HARD OUTPUT RULES:
- Do NOT repeat the same content across Answer, Process and Explanation.
- Do NOT show any Confidence score, and never write the words "Source Verification".
- Do NOT show Chapter / Clause / Page numbers unless the user EXPLICITLY asks for
  detailed source metadata.
- Always end with the single-line source ("📘 Source:" for English/Hinglish,
  "📘 स्रोत:" for Hindi) using friendly names only — never a raw filename, file
  path, or "[Source N: ...]" marker.

EXAMPLE — English question ("What is the EMD refund process?"):
💡 Answer
For unsuccessful bidders, the Department Admin initiates the EMD refund process. After approval, the e-Procurement system instructs the bank and the amount is credited within 1–2 days.

📋 Process
1. Department Admin initiates the refund.
2. Department Approver verifies and approves.
3. The system sends instructions to the bank.
4. The amount is credited to the bidder's account.
5. Refund status can be checked on the portal.

📘 Source: EMD Refund Guidelines (CHiPS)

EXAMPLE — Hindi question ("वेंडर पंजीकरण कैसे करें?"):
💡 उत्तर
CHiPS पोर्टल पर Vendor Registration एक बार की जाने वाली ऑनलाइन प्रक्रिया है, जिसके लिए वैध DSC आवश्यक होता है।

📋 प्रक्रिया
1. पोर्टल पर "New Supplier Registration" विकल्प चुनें।
2. PAN दर्ज करें।
3. Vendor Class A–D होने पर CRN Certificate की scanned copy अपलोड करें।
4. Preferred Login code बनाएँ।
5. सभी business coordinates भरकर फॉर्म सबमिट करें।

📘 स्रोत: Vendor Registration Manual (CHiPS)

PERSONALIZATION — if the user mentions a specific person by name (e.g. "name ramesh",
"my name is priya", "for suresh", "main ramesh hoon"), use that name naturally
throughout the answer. For example, if Ramesh is registering as a vendor, say
"Ramesh needs to..." or "Ramesh ko pehle..." rather than "the user" or "the vendor".
Keep the name exactly as the user wrote it (do not change capitalisation).

REFUSAL EXAMPLES — out-of-scope or not-in-documents → output ONLY the one-line
refusal in the question's language, nothing else (no headings, no Source):
Q (Hindi):   "चंद्रमा पर जाने का किराया कितना है?"
A: इस प्रश्न का उत्तर उपलब्ध दस्तावेजों में नहीं मिला।
Q (English): "What is today's weather in Raipur?"
A: The answer to this question was not found in the available documents.
"""

# Backwards-compatible alias used by the non-streaming /api/query path
SYSTEM_PROMPT = PROCUREMENT_SYSTEM_PROMPT


def _sanitize_rule_numbers(text, context_text):
    """Strip GFR/IT-Act rule/section NUMBERS the model cited that are NOT present
    in the retrieved context (the model's known weak spot — correct substance,
    wrong number). Server-side twin of the client's stripUngroundedRuleNumbers so
    cached, logged and decomposed answers are clean too, not just the browser view.
    - A parenthetical whose every cited number is ungrounded is dropped whole.
    - An inline ungrounded "Rule 173" becomes "the relevant GFR rule".
    - Grounded numbers (present in the context) are always preserved.
    """
    import re
    if not text or not context_text:
        return text
    def _grounded(num):
        # Number must appear as an actual rule/section CITATION in context, not
        # just any coincidental substring (page numbers, dates, other figures).
        return bool(re.search(rf'(?:Rule|Section|Order|Clause|Regulation|Para)\s*0*{num}\b',
                              context_text, re.I)
                    or re.search(rf'\b0*{num}\s*\(', context_text))
    def _paren(m):
        inner = m.group(1)
        nums = re.findall(r'(?:Rule|Section|Clause|Order)\s+(\d+)', inner, re.I)
        return '' if (nums and all(not _grounded(n) for n in nums)) else m.group(0)
    text = re.sub(r'\(((?:[^()]|\([^()]*\))*?\b(?:Rule|Section|Clause|Order)\s+\d+(?:[^()]|\([^()]*\))*)\)',
                  _paren, text, flags=re.I)
    def _inline(m):
        if _grounded(m.group(2)):
            return m.group(0)
        return 'the relevant GFR rule' if m.group(1).lower() == 'rule' else 'the relevant section'
    text = re.sub(r'\b(Rule|Section)\s+(\d+)(?:[A-Za-z]+|\([ivxlcdmIVXLCDM\d]+\))?',
                  _inline, text, flags=re.I)
    text = re.sub(r'\(\s*\)', '', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\s+([,.;:)])', r'\1', text)
    return text


def _decompose_question(q):
    """Split a compound question into standalone sub-questions for the LLM.

    gemma3:4b answers only the first clause of a multi-part question and silently
    drops the rest (verified on "What is EMD and when is it exempted?" — the
    exemption answer is retrieved but never written). Reformulating the question
    into an explicit numbered list of sub-questions makes each part a concrete
    task the model addresses point-by-point.

    Returns [q] when it isn't multi-part. Splits on '?' boundaries and on ' and '
    ONLY when the following clause starts with an interrogative — so noun phrases
    like "goods and services" are NOT split.
    """
    import re
    if not q:
        return [q]
    interrog = (r"when|how|why|what|where|which|who|whom|whose|is\s+it|are\s+they|"
                r"are\s+there|can\b|could\b|should\b|does\b|do\b|did\b|will\b|would\b")
    parts = []
    for seg in re.split(r'\?+', q):
        seg = seg.strip()
        if not seg:
            continue
        for s in re.split(rf'\s+and\s+(?=(?:{interrog}))', seg, flags=re.I):
            s = s.strip()
            if s:
                parts.append(s if s.endswith('?') else s + '?')
    return parts if parts else [q]

# Per-session conversation memory (multi-turn slots + coreference topic).
# In-memory; sessions expire after 1h of inactivity. Keyed by session_id sent
# from the frontend (one id per browser conversation).
CONV_MEMORY = ConversationMemory(max_turns=6, ttl_seconds=3600)

# Near-duplicate answer cache — instant replies for repeated/rephrased questions.
ANSWER_CACHE = AnswerCache(ttl_seconds=86400, max_entries=2000)

# Analytics + feedback logs (JSONL, one event per line).
ANALYTICS_LOG = str(SCRIPT_DIR / 'analytics.log')
FEEDBACK_LOG = str(SCRIPT_DIR / 'feedback.log')


def _log_event(path, event):
    """Append a JSON event line to a log file (best-effort, never raises)."""
    try:
        event.setdefault('ts', datetime.now().isoformat())
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
    except Exception:
        pass


def detect_query_language(text):
    """Detect response language from the user's question: 'hi', 'hinglish', or 'en'.
    Code-side detection is far more reliable than asking an 8B model to self-detect.

    An EXPLICIT request inside the query overrides auto-detection, so a user can
    type in English but ask for another language — e.g. "what is EMD, answer in
    hinglish", "explain in hindi", "hindi me batao", "हिंदी में बताओ"."""
    import re
    raw = text or ''
    t = raw.lower()

    # 1) EXPLICIT language request wins over everything else.
    #    Devanagari script-name forms (हिंग्लिश checked before हिंदी).
    if 'हिंग्लिश' in raw:
        return 'hinglish'
    if 'हिंदी' in raw or 'हिन्दी' in raw:
        return 'hi'
    if 'अंग्रेज़ी' in raw or 'अंग्रेजी' in raw:
        return 'en'
    #    Latin "(in) <lang>" or "<lang> me/mein" forms. Alternation tries
    #    'hinglish' before 'hindi' so it is never mis-caught as Hindi.
    _req = re.search(
        r'(?:\b(?:in|into|reply in|answer in|respond in|response in|explain in|'
        r'tell me in|write in|give (?:it )?in|batao in|bolo in)\s+'
        r'(hinglish|hindi|english)\b)'
        r'|(?:\b(hinglish|hindi|english)\s+(?:me|mein|m)\b)', t)
    if _req:
        _lang_word = _req.group(1) or _req.group(2)
        if _lang_word == 'hinglish':
            return 'hinglish'
        if _lang_word == 'hindi':
            return 'hi'
        if _lang_word == 'english':
            return 'en'

    # 2) Otherwise infer from the script / words the question is written in.
    if re.search(r'[ऀ-ॿ]', raw):
        return 'hi'  # any Devanagari → Hindi
    hinglish = (' kya', 'kya ', ' hai', 'hai?', 'kaise', 'kaisi', 'kitna', 'kitni',
                'prakriya', ' ka ', ' ki ', ' ke ', 'batao', 'bataye', 'chahiye',
                'karna', 'karne', 'kaun', 'kyun', 'nahi', 'wala',
                # Common Hinglish words that were missing — e.g. "refund kab tak
                # aayega?", "block ho gaya", "milti hai". Space-bounded so they
                # never false-match inside an English word.
                ' kab ', ' tak ', ' hone ', ' hoga', ' hogi', ' aayega', ' aayegi',
                ' padega', ' padegi', ' padenge', ' mutabik ', ' sath ', ' jaruri',
                ' hoti', ' milta', ' milti', ' gaya', ' gayi', ' raha', ' rahi')
    if any(m in t for m in hinglish):
        return 'hinglish'
    return 'en'


def language_directive(lang):
    """A strong, unambiguous instruction injected so the model cannot default to English."""
    if lang == 'hi':
        return ("\n\n=== LANGUAGE LOCK ===\n"
                "The user's question is in HINDI. You MUST write the ENTIRE response in "
                "Hindi (Devanagari) — even though the source Context is in English, translate "
                "it. Use ONLY the Hindi headings: 💡 उत्तर, 📋 प्रक्रिया, नियम/प्रावधान:, "
                "व्याख्या:, 📘 स्रोत:. Keep technical terms (EMD, CPPP, Tender, Bid, Vendor, "
                "DSC, NIT, GFR, GeM, PAN, CRN, e-Procurement) unchanged.")
    if lang == 'hinglish':
        return ("\n\n=== LANGUAGE LOCK ===\n"
                "The user's question is in HINGLISH (a mix of English and transliterated local languages written using the standard English A-Z alphabet). "
                "You MUST write the ENTIRE response in HINGLISH too — even though the source Context "
                "is in English, translate it to Hinglish. That means sentences written in Roman "
                "script, NOT plain English and ABSOLUTELY NO Devanagari script. "
                "CRITICAL: You MUST use ONLY the English alphabet (A-Z, a-z). Do not use any native scripts (no Devanagari, no Bengali). "
                "Example style: 'E-procurement ka matlab hai internet ke zariye goods, works "
                "aur services kharidna.' "
                "Keep technical terms (EMD, CPPP, Tender, Bid, Vendor, DSC, NIT, GFR, GeM, PAN, "
                "CRN, e-Procurement) in English. Use ONLY the English emoji headings: "
                "💡 Answer, 📋 Process, 📘 Source:. DO NOT write the answer in plain English.")
    return ("\n\n=== LANGUAGE LOCK ===\n"
            "The user's question is in ENGLISH. You MUST write the ENTIRE response in English. "
            "Use ONLY the English headings: 💡 Answer, 📋 Process, Rule/Provision:, "
            "Explanation:, 📘 Source:.")


# ── Procurement terminology dictionary (synonyms / abbreviations) ──────────
# Synonym groups — terms in the same list mean the SAME concept. Kept separate
# where the documents distinguish them (e.g. Bid Security vs Performance Security).
TERM_SYNONYMS = [
    ["bid security", "earnest money deposit", "earnest money", "emd"],
    ["corrigendum", "amendment", "amendment notice", "tender amendment",
     "shuddhipatra", "shuddhi patra", "शुद्धिपत्र", "शुद्धि पत्र", "सुद्धिपत्र"],
    ["bidder", "tenderer", "tender participant"],
    ["tender", "procurement notice"],
    ["performance security", "performance guarantee"],
    ["bank guarantee", "e-bank guarantee", "bg"],
    ["technical bid", "pq bid", "prequalification bid", "prequalification"],
    ["price bid", "financial bid", "commercial bid"],
    ["vendor", "supplier", "contractor"],
    ["department admin", "tender owner"],
    ["e-procurement portal", "cppp portal", "cppp"],
    # Hinglish (romanized Hindi) → English + Devanagari, so romanized queries
    # retrieve the same documents. bge-m3 cannot embed romanized Hindi directly,
    # so we inject the canonical English/Devanagari equivalents for recall.
    ["nivida", "niwida", "tender", "निविदा"],
    ["boli", "bid", "बोली"],
    ["bhugtan", "payment", "भुगतान"],
    ["tithi", "tareekh", "tarikh", "date", "last date", "तिथि", "अंतिम तिथि"],
    ["jama", "submission", "submit", "जमा करना"],
    ["thekedar", "contractor", "ठेकेदार"],
    ["vikreta", "supplier", "vendor", "विक्रेता"],
    ["panjikaran", "panjiyan", "registration", "पंजीकरण"],
    ["dharohar", "bayana", "earnest money", "emd", "bid security", "धरोहर", "धरोहर राशि", "बयाना", "जमानत"],
    ["nilami", "auction", "नीलामी"],
    ["dastavej", "dastavez", "document", "दस्तावेज"],
    ["kharid", "khareed", "kray", "purchase", "procurement", "खरीद", "क्रय"],
    ["samagri", "goods", "material", "सामग्री"],
    ["anubandh", "contract", "अनुबंध"],
    ["shulk", "fee", "शुल्क"],
    ["nibandhan", "niyam", "terms", "rules", "नियम"],
]
ABBREVIATION_EXPANSIONS = {
    "emd":   "earnest money deposit bid security",
    "bg":    "bank guarantee",
    "cppp":  "central public procurement portal",
    "msme":  "micro small and medium enterprises",
    "dpiit": "department for promotion of industry and internal trade",
    "l1":    "lowest evaluated bidder lowest quoted price",
    "h1":    "highest bidder highest quoted price",
    "pq":    "prequalification technical bid",
    "boq":   "bill of quantities",
}


REFUSAL_LINES = {
    'hi':       'इस प्रश्न का उत्तर उपलब्ध दस्तावेजों में नहीं मिला।',
    'hinglish': 'Is question ka answer uplabdh documents mein nahi mila.',
    'en':       'The answer to this question was not found in the available documents.',
}

# Procurement domain vocabulary (English + Hindi + Hinglish) for a fast scope gate.
DOMAIN_TERMS = [
    'tender', 'bid', 'emd', 'earnest', 'bid security', 'vendor', 'supplier', 'contractor',
    'registration', 'register', 'auction', 'corrigendum', 'amendment', 'procure', 'procurement',
    'gfr', 'store purchase', 'performance security', 'bank guarantee', ' bg ', 'cppp', 'gem',
    'msme', 'dpiit', 'boq', 'price bid', 'technical bid', 'financial bid', 'commercial bid',
    'refund', 'challan', 'payment', 'dsc', 'nit', ' pq ', 'portal', 'bidder', 'tenderer',
    'eligibility', 'guarantee', 'security deposit', 'prequalification', 'quotation', 'rfp', 'rfq',
    'penalty', 'blacklist', 'empanel', 'contract', 'supply', 'goods', 'works', 'consultancy',
    'browser', 'login', 'chips', 'e-procurement', 'eprocurement', 'e proc', 'eproc',
    'chatbot', 'assistant', 'help', 'capabilities', 'features',
    'your purpose', 'what are you', 'who are you', 'tumhara purpose', 'tumhara kaam',
    # Meta-questions (Hindi)
    'बता', 'बताओ', 'बताएँ', 'क्या', 'क्या-क्या', 'उद्देश्य', 'तुम्हारा',
    # Meta-questions (Hinglish/romanized)
    'bta', 'batao', 'bataye', 'kya', 'kya kya', 'tum', 'aap', 'uddeshya',
    'store', 'purchase', 'purhase', 'rule', 'rules', 'manual', 'guideline',
    'guidelines', 'disposal', 'inventory', 'document', 'procedure', 'limit',
    'committee', 'कमेटी', 'समिति', 'परचेज', 'क्रय', 'खरीद',   # purchase-committee etc.
    'cvc', 'circular', 'circulars', 'vigilance', 'reverse auction', 'mobilization',
    ' ppm', ' pef', 'approval', 'inquiry', 'faq',
    # IT Act 2000 / cyber-law (so questions about the IT Act are not refused by the gate)
    'it act', 'information technology', 'cyber', 'cybersecurity', 'cyber security',
    'computer', 'electronic', 'digital signature', 'electronic signature', 'signature',
    'certificate', 'certifying authority', 'electronic record', 'data', 'hacking',
    'offence', 'offense', 'adjudicating', 'intermediary', 'controller', 'damage',
    'terrorism', 'identity theft', 'tampering', 'network', 'internet', 'website',
    # Hinglish (romanized Hindi) procurement terms — so romanized queries are not
    # refused by the gate (bge-m3 can't embed them; TERM_SYNONYMS handles recall).
    'nivida', 'niwida', 'boli', 'bhugtan', 'tithi', 'tareekh', 'tarikh', 'thekedar',
    'vikreta', 'panjikaran', 'panjiyan', 'dharohar', 'bayana', 'nilami', 'dastavej',
    'dastavez', 'kharid', 'khareed', 'samagri', 'anubandh', 'shulk', 'nibandhan',
    # Hindi
    'निविदा', 'बोली', 'नीलामी', 'विक्रेता', 'आपूर्ति', 'ठेकेदार', 'पंजीकरण', 'पंजीयन',
    'भुगतान', 'वापसी', 'रिफंड', 'धरोहर', 'बयाना', 'जमानत', 'ठेका', 'खरीद', 'क्रय',
    'दस्तावेज', 'चालान', 'पोर्टल', 'टेंडर', 'बिड', 'अनुबंध', 'प्रतिभूति', 'गारंटी',
    'शुद्धिपत्र', 'सुद्धिपत्र', 'शुद्धि पत्र',
    'भण्डार', 'भंडार', 'नियम', 'शासन', 'सामग्री', 'मैनुअल', 'प्रक्रिया', 'खरीदी',
    'प्रोक्योरमेंट', 'ई-प्रोक्योरमेंट', 'परियोजना', 'नोडल', 'चिप्स',
    # IT Act 2000 / cyber-law (Hindi)
    'साइबर', 'कंप्यूटर', 'कम्प्यूटर', 'सूचना प्रौद्योगिकी', 'अधिनियम', 'इलेक्ट्रॉनिक',
    'इलैक्ट्रानिक', 'अंकीय', 'हस्ताक्षर', 'चिह्नक', 'अपराध', 'दंड', 'दण्ड', 'संसाधन',
    'प्रमाणपत्र', 'आतंकवाद', 'मध्यवर्ती',
]

# ── Greeting patterns (for friendly UX on social openers) ────────────────────
GREETING_PATTERNS_EN = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon',
                        'good evening', 'thanks', 'thank you', 'welcome']
GREETING_PATTERNS_HI = ['नमस्ते', 'सलाम', 'हेलो', 'स्वागत', 'धन्यवाद', 'शुक्रिया']
GREETING_PATTERNS_HIN = ['namaste', 'salam', 'hello', 'hi', 'swagat', 'thanks', 'shukriya',
                         'dhanyavaad', 'haan', 'ok', 'theek']

def detect_greeting(query):
    """Return 'hi', 'hinglish', 'en', or None if query is a greeting.
    Uses word-boundary matching to avoid false positives (e.g., 'ok' in 'chatbot')."""
    if not query or len(query.strip()) > 50:
        return None
    q = query.lower().strip()
    import re
    # Only greetings: single word or 2-3 word phrases, must start/end with greeting words
    q_words = q.split()
    if not q_words:
        return None
    first_word = q_words[0]
    last_word = q_words[-1].rstrip('?!.,')

    if re.search(r'[ऀ-ॿ]', query):
        if any(first_word == p or last_word == p for p in GREETING_PATTERNS_HI):
            return 'hi'
    elif any(first_word == p or last_word == p for p in GREETING_PATTERNS_HIN):
        return 'hinglish'
    elif any(first_word == p or last_word == p for p in GREETING_PATTERNS_EN):
        return 'en'
    return None

def greeting_response(lang):
    """Friendly greeting response in the detected language."""
    responses = {
        'hi': ("💬 नमस्ते! मैं CHiPS ई-प्रोक्योरमेंट सहायक हूँ। 👋\n\n"
               "मैं आपको निम्नलिखित के बारे में मदद कर सकता हूँ:\n"
               "• निविदाएँ और NIT (Tender details)\n"
               "• बिड जमा करने की प्रक्रिया\n"
               "• वेंडर पंजीकरण\n"
               "• EMD, बैंक गारंटी, GFR नियम\n"
               "• नीलामी (Auction) प्रक्रिया\n"
               "• पोर्टल फ़ीचर्स और DSC\n\n"
               "आप क्या जानना चाहते हैं?"),
        'hinglish': ("💬 Namaste! Main CHiPS e-Procurement assistant hoon. 👋\n\n"
                    "Main aapko help kar sakta hoon:\n"
                    "• Tenders aur NIT ke baare mein\n"
                    "• Bid submission process\n"
                    "• Vendor registration\n"
                    "• EMD, Bank Guarantee, GFR rules\n"
                    "• Auction process\n"
                    "• Portal features aur DSC\n\n"
                    "Aap kya jaan­na chahte hain?"),
        'en': ("💬 Hello! I'm the CHiPS e-Procurement Assistant. 👋\n\n"
               "I can help you with:\n"
               "• Tenders and procurement notices (NITs)\n"
               "• Bid submission process\n"
               "• Vendor registration\n"
               "• EMD, Bank Guarantees, and GFR rules\n"
               "• Auction procedures\n"
               "• Portal features and Digital Signatures (DSC)\n\n"
               "What would you like to know?"),
    }
    return responses.get(lang, responses['en'])


def is_meta_question(query):
    """Detect if query is about the chatbot itself (meta-question).
    Meta-questions should retrieve only from Chatbot_Capabilities, not e-procurement docs."""
    if not query:
        return False
    q = query.lower()
    # A meta-question asks about the ASSISTANT itself ("what can you do",
    # "your purpose"). Every signal must therefore reference the bot (you/tum/
    # aap/chatbot) or be a capability-listing phrase. Do NOT list bare topic
    # words like "purpose/objective/उद्देश्य/feature/बता(tell)" — those appear in
    # legitimate domain questions ("core objective of the e-Procurement project",
    # "features of GeM", "mujhe ... bataye") and were misrouting them to the
    # Capabilities doc instead of the manuals.
    meta_keywords = [
        # English — must reference the assistant
        'chatbot', 'this bot', 'what can you', 'what do you do',
        'what do you know', 'what topics', 'what subjects', 'help me with',
        'your capabilit', 'your feature', 'your purpose', 'what is your',
        'what are you', 'who are you', 'are you a bot', 'are you an ai',
        # Hinglish (Roman Hindi) — bot capability / identity, anchored
        'tumhara purpose', 'aapka purpose', 'tumhara kaam', 'aapka kaam',
        'tumhara uddeshya', 'aapka uddeshya', 'tum kya kar', 'aap kya kar',
        'tum kya kya', 'aap kya kya', 'kya kya bta', 'kya kya bata',
        'kya kar skte', 'kya kar sako', 'tum kaun', 'aap kaun',
        'tumhe kya aata', 'aapko kya aata',
        # Hindi (Devanagari) — bot capability / identity, anchored
        'तुम क्या कर', 'आप क्या कर', 'तुम क्या क्या', 'आप क्या क्या',
        'क्या क्या बता', 'क्या बता सकते',
        'तुम्हारा उद्देश्य', 'आपका उद्देश्य', 'तुम्हारा काम', 'आपका काम',
        'तुम कौन', 'आप कौन',
    ]
    return any(kw in q for kw in meta_keywords)


def is_in_scope(query):
    """Fast deterministic scope check. A query is treated as OUT of scope only when
    it contains NONE of the procurement domain terms — so we refuse clearly
    unrelated questions (moon fare, weather, jokes) without invoking the LLM, which
    cannot be trusted to self-refuse. Errs toward letting queries through."""
    if not query:
        return False
    low = ' ' + query.lower() + ' '
    return any(term in low for term in DOMAIN_TERMS)


# Retrieval-relevance scope gate (replaces relying on the keyword list alone).
# Measured separation with bge-reranker-v2-m3 (normalized): genuine in-scope
# questions score >= 0.20 — including Hindi with typos (निवीदा → 0.29) and new
# document domains (IT Act → 0.99) — while clearly out-of-scope junk (weather,
# jokes, trivia) scores <= 0.008. A 0.05 threshold sits well between the two.
SCOPE_MIN_RELEVANCE = float(os.getenv('CHIPPY_SCOPE_MIN_RELEVANCE', '0.05'))


def _scope_relevance(query, context_results, top_n=3):
    """Max normalized reranker relevance over the top retrieved chunks, or None
    if unavailable. retrieve_context now reranks (cross-encoder) and stores the
    normalized score on each result, so reuse it directly instead of running a
    second rerank — out-of-scope questions retrieve nothing relevant and score
    near zero, real questions score high."""
    try:
        if not context_results:
            return None
        scores = [float(r.get('score', 0.0)) for r in context_results[:top_n]]
        return max(scores) if scores else None
    except Exception:
        return None


def query_in_scope(query, context_results):
    """Decide if a query is in scope. A keyword hit is a fast-accept; otherwise
    fall back to retrieval relevance, so typos, Hinglish-in-Devanagari, and
    newly-added document domains are not falsely refused by a fixed keyword list.
    Clearly out-of-scope questions retrieve nothing relevant and are refused."""
    if is_in_scope(query):
        return True
    rel = _scope_relevance(query, context_results)
    if rel is None:
        return False
    return rel >= SCOPE_MIN_RELEVANCE


# Profanity / abuse filter — such input is refused without retrieval, LLM, or
# echoing the term. Patterns use word boundaries to avoid false positives
# (e.g. "assistant", "class", "passes").
_PROFANITY_PATTERNS = [
    r'n[i1!]+gg(?:a|er|uh)', r'\bf+u+c+k', r'\bf[\W_]*u[\W_]*c[\W_]*k', r'motherf',
    r'\bb[i1]tch', r'\bbastard', r'\basshole', r'\bcunt', r'\bfaggot', r'\bslut\b',
    r'\bwhore\b', r'\bdick(?:head)?\b', r'\bpussy\b', r'\bretard', r'\bnazi\b',
    # common Hindi/Hinglish abuses
    r'bhosdi', r'b?madarchod', r'be?hen?chod', r'chut(?:iya|iye)', r'gaand?u',
    r'\blund\b', r'\brandi\b', r'\bchod\b', r'\bgandu\b', r'\bharami',
]
_PROFANITY_REPLIES = {
    'hi':       'कृपया e-Procurement से संबंधित उचित प्रश्न पूछें।',
    'hinglish': 'Please ask a relevant question about e-Procurement.',
    'en':       'Please ask a question related to e-Procurement.',
}


def contains_profanity(query):
    """True if the query contains profanity/slurs — refuse such input outright."""
    import re
    low = (query or '').lower()
    return any(re.search(p, low) for p in _PROFANITY_PATTERNS)


def strip_chunk_header(text):
    """Remove the metadata preamble the chunkers prepend to every chunk file
    (lines like "Headings: [...]", "Source: structured", "---"). Left in the
    LLM context, the model parrots it back into answers (e.g. citing
    'निर्धारित प्रारूप (Structured)'). Strips only the LEADING block."""
    lines = (text or '').split('\n')
    i = 0
    while i < len(lines) and (
            lines[i].startswith('Headings:') or lines[i].startswith('Source:')
            or lines[i].strip() == '---' or not lines[i].strip()):
        i += 1
    return '\n'.join(lines[i:]) if i < len(lines) else (text or '')


def expand_query_for_retrieval(query):
    """Append known procurement synonyms / abbreviation expansions to the query so
    semantically equivalent terms (EMD ↔ Bid Security ↔ Earnest Money) match the
    same documents. Used ONLY for retrieval — the original query is what the LLM
    sees and answers."""
    import re
    if not query:
        return query
    low = query.lower()

    def _present(term):
        # ASCII terms use word boundaries so short abbreviations (e.g. "emd")
        # don't match inside a larger word. Devanagari / non-ASCII terms use
        # substring matching: Python's \b is unreliable around Devanagari matras
        # (vowel signs are non-word chars), so r'\bधरोहर राशि\b' NEVER matches
        # because "राशि" ends in ि — silently breaking expansion for the many
        # Hindi terms ending in a matra (राशि, तिथि, बोली, निविदा …).
        if term.isascii():
            return re.search(r'\b' + re.escape(term) + r'\b', low) is not None
        return term in low

    extra = []
    for group in TERM_SYNONYMS:
        present = [t for t in group if _present(t)]
        if present:
            extra.extend(t for t in group if t not in present)
    for abbr, expansion in ABBREVIATION_EXPANSIONS.items():
        if _present(abbr):
            extra.append(expansion)
    if not extra:
        return query
    seen, uniq = set(), []
    for e in extra:
        if e not in seen:
            seen.add(e)
            uniq.append(e)
    return f"{query} {' '.join(uniq)}"


# ── Lexical lookup for specific Rule / Section numbers ─────────────────────
# Dense embeddings (bge-m3) are weak at exact identifiers: a query like "GFR
# Rule 156" scores near the relevance floor and never retrieves the right
# chunk, so the LLM answers "not found" even when the rule plainly exists in
# the documents (e.g. as a one-line "Rule 156 Deleted." heading whose only
# mention of "156" is in chunk metadata that gets stripped before the model
# sees it). For any query that names a Rule/Section number we do a direct text
# lookup over the source documents and inject the exact passage at the FRONT of
# the context, so deleted or rarely-phrased rules are answered correctly —
# including telling the user the rule has been deleted.
_STRUCTURED_CACHE = {}   # str(path) -> list[str] lines (read once per process)
_SUPERSCRIPTS = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
                 '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}


def _normalize_superscripts(s):
    return ''.join(_SUPERSCRIPTS.get(ch, ch) for ch in (s or ''))


def _structured_docs():
    """Yield (source_name, lines) for each ingested source document, cached.
    Primary source is 01_preprocessing/stage2_output/<doc>/structured.md. Docs that
    were ingested ONLY via chunking (IT Act, GFR-Hindi, Précis, CVC, Vigilance, the
    short-tender notices) have no structured.md, so fall back to concatenating their
    03_chunking/output/<doc>/*_chunk_*.txt files (headers stripped). Without this,
    lexical Rule/Section/fact lookups can't reach those docs at all. GFR documents
    are yielded first so a generic 'Rule N' query prefers them."""
    base = PROJECT_ROOT / '01_preprocessing' / 'stage2_output'
    seen_names = set()
    paths = sorted(base.glob('*/structured.md'),
                   key=lambda p: (0 if 'gfr' in p.parent.name.lower() else 1, p.parent.name))
    for md in paths:
        key = str(md)
        if key not in _STRUCTURED_CACHE:
            try:
                _STRUCTURED_CACHE[key] = md.read_text(encoding='utf-8', errors='replace').split('\n')
            except Exception:
                _STRUCTURED_CACHE[key] = []
        seen_names.add(md.parent.name)
        yield md.parent.name, _STRUCTURED_CACHE[key]
    # Fallback: docs present only in 03_chunking/output (no structured.md).
    cbase = PROJECT_ROOT / '03_chunking' / 'output'
    if cbase.is_dir():
        cdirs = sorted([d for d in cbase.iterdir() if d.is_dir() and d.name not in seen_names],
                       key=lambda d: (0 if 'gfr' in d.name.lower() else 1, d.name))
        for d in cdirs:
            key = 'CHUNKS::' + str(d)
            if key not in _STRUCTURED_CACHE:
                lines = []
                for cf in sorted(d.glob('*_chunk_*.txt')):
                    try:
                        lines.extend(strip_chunk_header(cf.read_text(encoding='utf-8', errors='replace')).split('\n'))
                    except Exception:
                        continue
                _STRUCTURED_CACHE[key] = lines
            yield d.name, _STRUCTURED_CACHE[key]


class _LexPoint:
    """Minimal stand-in for a Qdrant point so synthesized lexical hits flow
    through the same downstream code (which reads point.payload['source'/'text'])."""
    __slots__ = ('payload',)

    def __init__(self, source, text):
        self.payload = {'source': source, 'text': text}


def lexical_rule_lookup(query, max_hits=3, window=14, cap=700):
    """If the query names specific Rule/Section numbers, return synthesized
    context results pulled by EXACT text match from the source documents — the
    rule's heading/definition line plus, for a deleted rule, the resolved
    'Deleted vide ...' footnote. Returns [] when no rule number is named or none
    is found, so normal retrieval is unaffected for every other query."""
    import re
    if not query:
        return []
    raw = re.findall(r'\b(?:rule|section|regulation|article)\s*(\d+\s*[A-Za-z]?)\b', query, flags=re.I)
    # Hindi RULE keywords (नियम / विनियम) — so "GFR नियम 144" triggers the exact-
    # passage lookup. We deliberately EXCLUDE धारा / अनुच्छेद ("Section"/"Article"):
    # the Act PDFs number sections as "43." (not "Section 43"), so a section lookup
    # never matches their headings and would only inject an unrelated GFR "Rule 43".
    # Devanagari \b is unreliable around matras, so match without word boundaries.
    raw += re.findall(r'(?:नियम|विनियम)\s*(\d+\s*[A-Za-z]?)', query)
    nums = []
    for n in raw:
        n = re.sub(r'\s+', '', n).upper()
        if n not in nums:
            nums.append(n)
    if not nums:
        return []

    hits, seen = [], set()
    for num in nums:
        # Match a heading/definition line for this rule at line start (after any
        # markdown #/* markers) — NOT a mid-line cross-reference such as
        # "...in cases covered under Rule 154 and 155".
        # Allow an optional leading list marker ("8. ", "7) ") because some rules are
        # ingested as numbered list items ("8. Rule 166 Single Tender Enquiry") rather
        # than markdown headings ("## Rule 166") — without this, single-tender (166)
        # and late-bids (165) never inject and the LLM cites a wrong number.
        _lead = r'(?:\d{1,3}[.)]\s*)?'
        # A rule heading is EITHER "…Rule/Section/Regulation N…" (optionally after a list
        # marker / ## / **) OR a markdown/bold heading that starts with the BARE number +
        # a title word. The bare-number branch is needed because the two-column PDF
        # extraction sometimes DROPPED the word "Rule" (e.g. Rule 155 came out as
        # "**155 Purchase of goods by Purchase Committee**"), which defeated the exact-rule
        # lookup. The bare branch REQUIRES a ## or ** marker + a following title word, so it
        # never matches plain "155." cross-references or numbered list items like "37. …".
        _bare = r'^\s*(?:#{1,4}\s*|\*{2}\s*)' + re.escape(num) + r'\b(?=\s+[*A-Za-zऀ-ॿ])'
        _bare_any = r'^\s*(?:#{1,4}\s*|\*{2}\s*)\d+\b(?=\s+[*A-Za-zऀ-ॿ])'
        head_pat = re.compile(r'^\s*' + _lead + r'#{0,4}\s*\*{0,2}(?:Rule|Section|Regulation)\s*'
                              + re.escape(num) + r'\b' + '|' + _bare, re.I)
        stop_pat = re.compile(r'^\s*' + _lead + r'#{0,4}\s*\*{0,2}(?:Rule|Section|Regulation)\s*\d'
                              + '|' + _bare_any, re.I)
        strip_head = head_pat
        for source, lines in _structured_docs():
            if (source, num) in seen:
                continue
            for i, line in enumerate(lines):
                if not head_pat.match(line):
                    continue
                seen.add((source, num))
                end = i + 1
                while end < len(lines) and end < i + window and not stop_pat.match(lines[end]):
                    end += 1
                snippet = '\n'.join(l for l in lines[i:end] if l.strip())
                # For a deleted rule, resolve its footnote ("²⁵" -> 25 -> the
                # "25 Deleted vide DoE OM ..." line) so the answer can cite it.
                if 'delet' in line.lower():
                    rest = strip_head.sub('', _normalize_superscripts(line))
                    mk = re.search(r'(\d{1,3})\s*$', rest)
                    if mk:
                        marker = mk.group(1)
                        foot_pat = re.compile(r'^\s*' + marker + r'\b.*deleted vide', re.I)
                        for fl in lines:
                            if foot_pat.match(_normalize_superscripts(fl)):
                                snippet += '\n' + fl.strip()
                                break
                snippet = snippet[:cap]
                hits.append({'rank': 0, 'score': 0.95, 'parent_id': '',
                             'point': _LexPoint(source, snippet),
                             'source': source, 'text': snippet})
                break
            if len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break
    return hits


# Map GFR *concept* phrases → rule number. Verified against the ingested GFR text
# (01_preprocessing/stage2_output/FInal_GFR_upto_31_07_2024/structured.md headings):
#   154 Purchase without quotation · 155 Purchase Committee · 161 Advertised Tender ·
#   162 Limited Tender · 163 Two-bid · 166 Single Tender · 171 Performance Security.
# Phrases are intentionally GFR-officer-specific (EN + Devanagari + romanized Hinglish)
# so they do NOT hijack vendor/portal EMD/DSC queries. Broad terms (bare "emd",
# "tender") are deliberately excluded.
CONCEPT_RULE_MAP = [
    ("154", ["without quotation", "bina quotation", "bina kotation", "बिना कोटेशन",
             "बिना उद्धरण", "no quotation", "directly purchase", "सीधे खरीद", "sidhe kharid"]),
    ("155", ["purchase committee", "local purchase committee", "क्रय समिति",
             "स्थानीय क्रय समिति", "kharid samiti", "purchase committee banane",
             # English "purchase committee" transliterated into Devanagari (BGE-M3
             # embeds these poorly, so match them literally) + Hindi variants.
             "परचेज कमेटी", "परचेज़ कमेटी", "परचेज कमिटी", "खरीद समिति", "क्रय-समिति",
             "purchase samiti", "kharid committee"]),
    ("161", ["advertised tender", "open tender", "विज्ञापन निविदा", "खुली निविदा",
             "vigyapan nivida", "advertised tender enquiry"]),
    ("162", ["limited tender", "सीमित निविदा", "seemit nivida", "limited tender enquiry"]),
    ("163", ["two bid system", "two-bid", "two bid", "दो-बोली", "दो बोली",
             "two envelope", "do lifafe"]),
    ("166", ["single tender", "एकल निविदा", "single source", "ekal nivida",
             "single tender enquiry"]),
    ("171", ["performance security", "प्रदर्शन प्रतिभूति", "प्रदर्शन सुरक्षा",
             "performance guarantee", "pradarshan pratibhuti"]),
]


def lexical_concept_lookup(query):
    """Map a GFR *concept* phrase (EN/Hindi/romanized) to its rule number and inject
    that rule's exact passage — so 'purchase without quotation' / 'bina quotation'
    reaches Rule 154 even though the query never names a number. Complements
    lexical_rule_lookup (which only fires when a Rule NUMBER is present). This is the
    fix for the Q91 class: a romanized concept query that BGE-M3 embeds poorly now
    still lands the correct rule chunk at the FRONT of the context."""
    if not query:
        return []
    low = query.lower()
    nums = []
    for num, phrases in CONCEPT_RULE_MAP:
        if num not in nums and any(p in low for p in phrases):
            nums.append(num)
    if not nums:
        return []
    # Reuse the exact-passage extractor by handing it a synthetic "Rule N …" query.
    return lexical_rule_lookup(' '.join(f'Rule {n}' for n in nums), max_hits=len(nums))


def concept_or_rule_nums(query):
    """Rule numbers the query names ("Rule 171") or implies via CONCEPT_RULE_MAP."""
    import re
    if not query:
        return []
    low = query.lower()
    nums = [n for n, ph in CONCEPT_RULE_MAP if any(p in low for p in ph)]
    nums += re.findall(r'(?:rule|section|regulation|नियम|विनियम)\s*(\d+)', query, re.I)
    out = []
    for n in nums:
        if n not in out:
            out.append(n)
    return out


def rule_grounding_note(query, cap=260, max_lines=3):
    """Verbatim quote-grounding: return the exact source line(s) carrying amounts /
    percentages / day-counts from the resolved rule's FULL section (heading → next
    rule heading), skipping footnote & page-break noise. Returns '' when the query
    names/implies no rule. Appended under the answer so the shown figures are ground
    truth even when the 4B model paraphrases them imprecisely (e.g. Rule 171 '3-5%').
    We scan the whole section — not a fixed window — because extraction splits a rule
    across page breaks with footnotes between the heading and the figure."""
    import re
    nums = concept_or_rule_nums(query)
    if not nums:
        return ''
    NUM = re.compile(
        r'(?:₹|Rs\.?)\s*[\d,]+(?:/-)?'
        r'|\d+(?:\.\d+)?\s*%'
        r'|\d+\s*(?:to\s*\d+\s*)?per\s*cent'
        r'|(?:one|two|three|four|five|six|seven|eight|nine|ten|twenty[- ]?five|fifty)'
        r'[^.\n]{0,40}?per\s*cent'
        r'|\b[\d,]+\s*(?:lakh|crore|thousand)'
        r'|\d+\s*(?:days?|दिन|प्रतिशत)', re.I)
    NOISE = re.compile(
        r'^\s*(?:\[\^|-{3,}|\d{1,3}\s*$|(?:\^?\d+\s+)?(?:Inserted|Deleted|Substituted)\s+vide'
        r'|[²³⁰¹⁴⁵⁶⁷⁸⁹]+\s|Replace with)', re.I)
    _lead = r'(?:\d{1,3}[.)]\s*)?'
    _bare_any = r'^\s*(?:#{1,4}\s*|\*{2}\s*)\d+\b(?=\s+[*A-Za-zऀ-ॿ])'
    for num in nums:
        _bare = r'^\s*(?:#{1,4}\s*|\*{2}\s*)' + re.escape(num) + r'\b(?=\s+[*A-Za-zऀ-ॿ])'
        head = re.compile(r'^\s*' + _lead + r'#{0,4}\s*\*{0,2}(?:Rule|Section|Regulation)\s*'
                          + re.escape(num) + r'\b' + '|' + _bare, re.I)
        stop = re.compile(r'^\s*' + _lead + r'#{0,4}\s*\*{0,2}(?:Rule|Section|Regulation)\s*\d'
                          + '|' + _bare_any, re.I)
        for source, lines in _structured_docs():
            for i, l in enumerate(lines):
                if not head.match(l):
                    continue
                picked, j = [], i + 1
                while j < len(lines) and j < i + 90 and not stop.match(lines[j]):
                    s = lines[j].strip()
                    if s and not NOISE.match(s) and NUM.search(s):
                        picked.append(s)
                        if len(picked) >= max_lines or sum(len(x) for x in picked) > cap:
                            break
                    j += 1
                if picked:
                    body = re.sub(r'\s+', ' ', ' '.join(picked))
                    if len(body) > cap:
                        body = body[:cap].rsplit(' ', 1)[0]        # don't cut mid-word
                    body = re.sub(r'[\[(]\s*$', '', body).rstrip(' ,;([')  # drop dangling bracket
                    return f"Rule {num}: " + body
    return ''


# Some substantive text isn't under a clean nearby rule heading — it sits far below
# the heading and is SPLIT across a page break (e.g. the bid-submission TIME: the
# "three weeks" clause and the "four weeks for foreign" clause are ~90 lines under
# Rule 161 with footnotes + a page number between them, so the 4B grabs only one
# half). For these we anchor on a distinctive phrase, join across the noise, and
# inject the COMPLETE provision. Fires only when the query carries BOTH a time word
# AND an action word, so it never hijacks e.g. "EMD kitne din valid".
_PHRASE_ANCHORS = [
    (("time", "समय", "din", "hafte", "saptah", "week", "day", "दिन", "सप्ताह"),
     ("submit", "submission", "prepare", "allow", "जमा", "प्रस्तुत", "publish", "bid", "बोली", "निविदा"),
     "minimum time to be allowed for submission of bids", 750),
]


def lexical_phrase_lookup(query, cap=600):
    """Phrase-anchored injection for provisions that are split across a page break /
    sit far from their heading (so rule/concept-heading lookups miss them). Returns a
    synthesized front-of-context hit with the noise stripped and both clauses rejoined."""
    import re
    if not query:
        return []
    low = query.lower()
    for tw, aw, anchor, span in _PHRASE_ANCHORS:
        if not (any(t in low for t in tw) and any(a in low for a in aw)):
            continue
        al = anchor.lower()
        for source, lines in _structured_docs():
            joined = re.sub(r'\s+', ' ', ' '.join(lines))
            pos = joined.lower().find(al)
            if pos == -1:
                continue
            txt = joined[pos:pos + span]
            # Strip the interleaved footnotes / page numbers that split the clauses.
            txt = re.sub(r'\d{1,3}\s+(?:Deleted|Inserted|Amended|Substituted)\s+vide.*?\d{2}\.\d{2}\.\d{4}',
                         ' ', txt, flags=re.I)
            txt = re.sub(r'\s+\d{1,3}\s+(?:---|—)\s+', ' ', txt)
            txt = re.sub(r'\bF\.\S+\s*', ' ', txt)          # stray "OM No. F.1/3/2024-PPD" refs
            txt = re.sub(r'\s+([.,])', r'\1', re.sub(r'\s+', ' ', txt)).strip()[:cap]
            return [{'rank': 0, 'score': 0.95, 'parent_id': '',
                     'point': _LexPoint(source, txt), 'source': source, 'text': txt}]
    return []


def lexical_section_lookup(query, window=45, cap=1400):
    """IT-Act / legal-Act SECTION lookup. The Act PDFs number sections as 'N.'
    (e.g. '43. Penalty and compensation …'), NOT 'Section N', so lexical_rule_lookup
    can't find them — and dense retrieval pulls the §66 punishment chunk for a §43
    query. For a query naming a section (English 'section 43' or Hindi 'धारा 43'),
    find the SUBSTANTIVE provision line in the it_act docs (preferring the operative
    text over the table-of-contents stub) and inject it. Scoped to it_act only, so
    it never injects an unrelated GFR 'Rule 43'."""
    import re
    if not query:
        return []
    nums = re.findall(r'\b(?:section|sec\.?)\s*(\d+\s*[A-Za-z]?)\b', query, flags=re.I)
    nums += re.findall(r'(?:धारा|अनुच्छेद)\s*(\d+\s*[A-Za-z]?)', query)
    norm = []
    for n in nums:
        n = re.sub(r'\s+', '', n).upper()
        if n and n not in norm:
            norm.append(n)
    if not norm:
        return []
    def _sec_num(s):
        m = re.match(r'^\s*(\d+)[A-Za-z]?\.\s', s)
        return int(m.group(1)) if m else None

    hits = []
    for num in norm:
        head = re.compile(r'^\s*' + re.escape(num) + r'\.\s', re.I)       # "43. ..."
        cur = int(re.match(r'(\d+)', num).group(1))
        best = None
        for source, lines in _structured_docs():
            if 'it_act' not in source.lower():
                continue
            for i, line in enumerate(lines):
                if not head.match(line):
                    continue
                # Extend to the NEXT real section heading (number >= current). A bare
                # "1."/"2." is a footnote, not section 1 — don't stop the window there.
                end = i + 1
                while end < len(lines) and end < i + window:
                    nx = _sec_num(lines[end])
                    if nx is not None and nx >= cur:
                        break
                    end += 1
                snippet = '\n'.join(l for l in lines[i:end] if l.strip())
                # Prefer the operative provision (longest, mentions liability/penalty)
                # over the bare arrangement-of-sections stub.
                bonus = 250 if re.search(r'if any person|compensation|damages|liable|punish', snippet, re.I) else 0
                sc = len(snippet) + bonus
                if best is None or sc > best[0]:
                    best = (sc, source, snippet[:cap])
        if best:
            _, source, snippet = best
            hits.append({'rank': 0, 'score': 0.95, 'parent_id': '',
                         'point': _LexPoint(source, snippet),
                         'source': source, 'text': snippet})
    return hits


# ── Lexical lookup for portal contact details and fees ────────────────────
# Dense retrieval often returns a FAQ / Manual chunk that does NOT contain the
# specific helpline number or fee figure, so the model truthfully answers "not
# in the documents" (observed: the toll-free helpline, and the renewal fee —
# which it once even hallucinated as ₹250). For contact- or fee-intent queries
# we pull the exact fact lines from the FAQ / Vendor Registration / Guidelines
# documents and inject them at the FRONT of the context.
_CONTACT_INTENT = (
    "helpline", "help line", "helpdesk", "help desk", "toll free", "toll-free",
    "contact", "phone", "mobile", "call", "email", "e-mail", "number",
    "हेल्पलाइन", "हेल्प लाइन", "हेल्पडेस्क", "टोल", "संपर्क", "सम्पर्क",
    "फोन", "फ़ोन", "नंबर", "नम्बर", "ईमेल", "मेल",
)
_FEE_INTENT = (
    "fee", "fees", "charge", "charges",
    "शुल्क", "फीस", "फ़ीस", "राशि",
)
_FEE_CONTEXT = (
    "registration", "register", "renewal", "renew", "vendor", "supplier", "portal",
    "पंजीकरण", "पंजीयन", "नवीनीकरण", "रजिस्ट्रेशन", "वेंडर", "विक्रेता", "नवीन",
)
_AUCTION_INTENT = (
    "auction", "e-auction", "eauction", "rfx", " h1", "h-1", "h 1",
    "नीलामी", "नीलाम", "ऑक्शन", "एच1",
)
_SIZE_INTENT = (
    "document size", "file size", "size limit", "maximum size", "max size",
    "bandwidth", "mbps", "kbps", "साइज़", "साइज", "आकार", "बैंडविड्थ", "एमबी",
)
_COST_INTENT = (
    "project cost", "total cost", "cost of the project", "crore", "budget",
    "लागत", "कुल लागत", "परियोजना लागत", "करोड़", "बजट",
)
# Portal-usage facts in the Bid Submission manual that dense retrieval keeps losing
# to the big GoI Works/Goods manuals + EMD-Challan/Auction (QA report: Q3/5/6/12/13).
_TYPE_INTENT = (
    "tender type", "types of tender", "tender types", "kind of tender", "kinds of tender",
    "निविदा के प्रकार", "निविदा प्रकार", "टेंडर के प्रकार", "प्रकार के टेंडर", "कितने प्रकार",
)
_CAT_INTENT = (
    "vendor category", "vendor categories", "category vendor", "category of vendor",
    "वेंडर श्रेणी", "वेंडर कैटेगरी", "श्रेणी", "कैटेगरी",
)
_2PART_INTENT = (
    "2-part", "2 part", "two part", "two-part", "part tender", "2 भाग", "दो भाग", "दो पार्ट",
)
_REGRET_INTENT = ("regret", "रीग्रेट", "रिग्रेट")
_GATEWAY_INTENT = (
    "payment gateway", "gateway", "payment mode", "पेमेंट गेटवे", "गेटवे",
    "भुगतान गेटवे", "पेमेंट मोड", "भुगतान मोड",
)
_LOGIN_INTENT = ("login", "log in", "sign in", "लॉगिन", "लॉग इन", "साइन इन")
_FAILURE_INTENT = (
    "internet failure", "power failure", "system failure", "server down", "deadline",
    "extend", "extension", "बिजली", "इंटरनेट फेल", "विफलता", "समय सीमा", "बढ़ा",
)
_JAVA_INTENT = ("java", "jre", "runtime environment", "जावा", "रनटाइम", "रनटाईम")
_REGNUM_SIGNAL = (
    "registration number", "vendor registration number", "पंजीकरण क्रमांक", "पंजीकरण संख्या",
    "पंजीकरण नंबर", "क्या मिलता", "क्या प्राप्त", "क्या मिलेगा", "मिलता है", "प्राप्त होता",
    "what does the vendor receive", "what is generated", "generated after",
)
_REG_CTX = ("registration", "register", "vendor", "supplier",
            "पंजीकरण", "पंजीयन", "वेंडर", "रजिस्ट्रेशन")
_DSCREG_KEY = ("dsc", "डीएससी", "digital signature", "digital certificate",
               "डिजिटल हस्ताक्षर", "डिजिटल सर्टिफिकेट", "डिजिटल प्रमाणपत्र")
_DSCREG_ACT = ("register", "registering", "रजिस्टर", "पंजीक", "map", "मैप",
               "select", "selecting", "चयन", "चुन")
_FAQ_DOC     = "FAQ of Chhattisgarh Infotech Promotion Society(CHIPS)"
_VENDOR_DOC  = "CHiPS_Vendor_Registration_Manual_English"
_GUIDE_DOC   = "Guidelines_To_Bidders_EPS_v1.6"
_AUCTION_DOC = "AuctionManual_FA"
_PRECIS_DOC  = "Précis  e-Procurement Project"   # two spaces — matches the folder name
_BID_DOC     = "CHiPS_Bid_Submission_Manual_English"


def lexical_portal_fact_lookup(query, cap=900):
    """Inject exact contact / fee lines for contact- or fee-intent queries so the
    answer never misses a phone number or fee figure that IS in the corpus.
    Returns [] for every other query, so normal retrieval is unaffected."""
    import re
    if not query:
        return []
    q = query.lower()
    want_contact = any(t in q for t in _CONTACT_INTENT)
    want_fee = any(t in q for t in _FEE_INTENT) and any(t in q for t in _FEE_CONTEXT)
    want_auction = any(t in q for t in _AUCTION_INTENT)
    want_size = any(t in q for t in _SIZE_INTENT)
    want_cost = any(t in q for t in _COST_INTENT)
    want_type = any(t in q for t in _TYPE_INTENT)
    want_cat = any(t in q for t in _CAT_INTENT)
    want_2part = any(t in q for t in _2PART_INTENT)
    want_regret = any(t in q for t in _REGRET_INTENT)
    want_gateway = any(t in q for t in _GATEWAY_INTENT)
    want_login = any(t in q for t in _LOGIN_INTENT)
    want_failure = any(t in q for t in _FAILURE_INTENT)
    want_java = any(t in q for t in _JAVA_INTENT)
    want_regnum = any(t in q for t in _REGNUM_SIGNAL) and any(t in q for t in _REG_CTX)
    want_dscreg = any(k in q for k in _DSCREG_KEY) and any(a in q for a in _DSCREG_ACT)
    if not (want_contact or want_fee or want_auction or want_size or want_cost or want_type
            or want_cat or want_2part or want_regret or want_gateway or want_login or want_failure
            or want_java or want_regnum or want_dscreg):
        return []
    phone_re = re.compile(r'(toll[\s-]*free|help\s*line|help\s*desk|1800|@cgswan|helpdesk\.eproc)', re.I)
    fee_re = re.compile(r'(registration|renewal|portal).{0,40}(rs\.?|₹|inr)\s*\.?\s*\d'
                        r'|(rs\.?|₹|inr)\s*\.?\s*\d{2,}.{0,30}(registration|renewal|year)', re.I)
    # e-Auction PORTAL mechanics — keep only the high-value facts (H1 visibility,
    # auto-refresh interval, opening price, DSC login password) so they stay salient.
    auction_re = re.compile(r'(H1|H-1|ranking|auto refresh|1 min|refresh|opening price|Password@123)', re.I)
    # Bid-document upload SIZE limit + minimum bandwidth (Guidelines to Bidders).
    size_re = re.compile(r'(less than .{0,8}MB|five MB|fifty MB|size of bid|'
                         r'minimum .{0,8}MBPS|MBPS|bandwidth)', re.I)
    # Project cost — inject the PHASE-LABELLED cost lines so "2.0" maps to ₹36.90 Cr
    # (admin-approved) and "3.0" to ₹42.3 Cr (DPR projected), not the wrong phase.
    cost_re = re.compile(r'(Integrated e-Procurement Project\s*[0-9]\.[0-9]|'
                         r'Total Project(?:ed)?\s*Cost)', re.I)
    # Bid-Submission portal facts (definitions, not the GoI policy manuals' versions).
    type_re = re.compile(r'In this type of tender', re.I)                       # Open/Limited/Restricted/Short defs
    cat_re = re.compile(r'Category vendor.{0,40}(participate|crore|Rs)', re.I)   # A/B/C/D value limits
    twopart_re = re.compile(r'(first part consists|second part consists|pre-qualification and techno)', re.I)
    regret_re = re.compile(r'(regret some items|rate contract tenders only)', re.I)
    gateway_re = re.compile(r'(INDUSIND|NSDL|PAYMENT GATEWAY|Debit/Credit|Net banking|payment gateway available)', re.I)
    login_re = re.compile(r'(Type your user ID|select Organisation|Correct Digital Certificate|Click - Submit|Click - Allow)', re.I)
    failure_re = re.compile(r'(24/48/72|System Administrator|Administrative Corrigendum|extend.{0,25}bid submission|bid submission date)', re.I)
    targets = []
    if want_contact:
        targets += [(_FAQ_DOC, phone_re), (_VENDOR_DOC, phone_re)]
    if want_fee:
        targets += [(_GUIDE_DOC, fee_re), (_VENDOR_DOC, fee_re)]
    if want_auction:
        targets += [(_AUCTION_DOC, auction_re)]
    if want_size:
        targets += [(_GUIDE_DOC, size_re)]
    if want_cost:
        targets += [(_PRECIS_DOC, cost_re)]
    if want_type:
        targets += [(_BID_DOC, type_re)]
    if want_cat:
        targets += [(_BID_DOC, cat_re)]
    if want_2part:
        targets += [(_BID_DOC, twopart_re)]
    if want_regret:
        targets += [(_BID_DOC, regret_re)]
    if want_gateway:
        targets += [(_BID_DOC, gateway_re)]
    if want_login:
        targets += [(_BID_DOC, login_re)]
    if want_failure:
        targets += [(_BID_DOC, failure_re)]
    docs = {s: l for s, l in _structured_docs()}
    hits, seen = [], set()
    for src, pat in targets:
        if src in seen:
            continue
        picked = []
        for ln in (docs.get(src) or []):
            s = ln.strip()
            if s and s not in picked and pat.search(s):
                picked.append(s)
            if len(picked) >= 6:
                break
        if picked:
            seen.add(src)
            snippet = '\n'.join(picked)[:cap]
            hits.append({'rank': 0, 'score': 0.95, 'parent_id': '',
                         'point': _LexPoint(src, snippet),
                         'source': src, 'text': snippet})
    # Regret: the raw manual line ("…rate contract tenders only") sits in context but
    # the model keeps mis-reading "which type of tender" as the tender-TYPES list.
    # Lead with a crisp, answer-shaped restatement of the §3.5.7 fact.
    if want_regret:
        msg = ("On the CHiPS e-Procurement portal, the 'regret' option — a YES/NO "
               "dropdown that lets a bidder regret (skip) individual line items while "
               "bidding — is available ONLY in RATE CONTRACT tenders (Bid Submission "
               "Manual, section 3.5.7). It is NOT a 'reject all bids' / lack-of-"
               "competition action.")
        hits.insert(0, {'rank': 0, 'score': 0.97, 'parent_id': '',
                        'point': _LexPoint(_BID_DOC, msg), 'source': _BID_DOC, 'text': msg})
    if want_java:
        msg = ("To install Java for the CHiPS e-Procurement portal: open Internet "
               "Explorer, go to eproc.cgstate.gov.in, then Click Download -> Java -> "
               "Java Runtime Environment -> Download. The portal requires JRE version "
               "8.77 (1.8.0_77); keep only one Java version installed on the system.")
        hits.insert(0, {'rank': 0, 'score': 0.96, 'parent_id': '',
                        'point': _LexPoint(_BID_DOC, msg), 'source': _BID_DOC, 'text': msg})
    if want_failure:
        msg = ("If the e-Procurement system fails (internet failure, power failure, "
               "server/system failure or natural calamity), the System Administrator — "
               "in consultation with the Tender Inviting Authority — may extend the bid "
               "submission deadline by 24/48/72 hours by issuing an Administrative "
               "Corrigendum; affected bidders receive automatic email alerts.")
        hits.insert(0, {'rank': 0, 'score': 0.96, 'parent_id': '',
                        'point': _LexPoint(_BID_DOC, msg), 'source': _BID_DOC, 'text': msg})
    if want_regnum:
        msg = ("On successful vendor registration, after reading and accepting the "
               "Terms & Conditions (ticking the checkboxes and clicking Accept), the "
               "portal generates a Vendor Registration Number; the application / "
               "registration number is then displayed in red.")
        hits.insert(0, {'rank': 0, 'score': 0.96, 'parent_id': '',
                        'point': _LexPoint(_VENDOR_DOC, msg), 'source': _VENDOR_DOC, 'text': msg})
    if want_dscreg:
        msg = ("Registering your DSC during vendor registration on the CHiPS portal: "
               "(1) first procure a DSC — Class II or Class III, with BOTH Signing & "
               "Encryption certificates — from a licensed CA; (2) fill the registration "
               "details and click Save & Next; (3) at the 'Selecting DSC' step, select "
               "the appropriate Digital Signature Certificate to register it with your "
               "Vendor/Bidder account (the certificate must be registered before you can "
               "proceed); (4) after successful selection of the DSC, click Confirmation "
               "to accept the Terms & Conditions for registration.")
        hits.insert(0, {'rank': 0, 'score': 0.96, 'parent_id': '',
                        'point': _LexPoint(_VENDOR_DOC, msg), 'source': _VENDOR_DOC, 'text': msg})
    return hits


_OFFLINE_TENDER_INTENT = (
    "offline tender", "manual tender", "offline/manual", "manual/offline",
    "ऑफलाइन टेंडर", "ऑफ़लाइन", "मैनुअल टेंडर", "मैन्युअल टेंडर",
)
_OFFLINE_HOWTO = (
    "how", "create", "upload", "add", "fill", "submit", "step",
    "कैसे", "अपलोड", "बनाएं", "बनाना", "बनाये", "जारी", "भरें", "दर्ज", "चरण", "प्रक्रिया",
)


def lexical_offline_tender_lookup(query, cap=750):
    """Assemble the OFFLINE/MANUAL tender creation workflow for the CHiPS portal.
    The Offline-Tenders manual is a UI walkthrough whose steps are scattered across
    11 chunks + image captions, so dense retrieval grabs the 'ADVANCE SEARCH' banner
    instead. For a how-to query about offline/manual tenders we extract the header
    fields + the in-order action phrases ('Login as…', 'Click on…', 'Enter…') from
    the structured doc and inject them as one coherent step list."""
    import re
    if not query:
        return []
    q = query.lower()
    if not (any(t in q for t in _OFFLINE_TENDER_INTENT) and any(t in q for t in _OFFLINE_HOWTO)):
        return []
    text = '\n'.join(dict(_structured_docs()).get('Manual_Offline_Tenders_v.1.0') or [])
    if not text:
        return []
    fields, seen = [], set()
    for f in re.findall(r'(TENDER NO\.|NIT REFERENCE NO|TENDER CALL NO|DETAILED DESCRIPTION|'
                        r'PROBABLE AMOUNT OF CONTRACT|Bid Submission Start date|Bid Open Date|'
                        r'TENDER & PROCESSING FEES|EMD / BID SECURITY FEES)', text):
        if f not in seen:
            seen.add(f); fields.append(f)
    _NOISE = {'click on ok', 'click on search', 'click on ok to add', 'click on register new bidder'}
    acts, aseen = [], set()
    for m in re.finditer(r"(Login as [A-Z][\w ]+|Click on [A-Z][\w/ ]+?(?=[.'’\"]| inside| and click| if| with|$)|"
                         r"Add Bidders by[^.'’\"]*|REGISTER NEW BIDDER|Fill-in all PO[^.'’\"]*|"
                         r"Enter (?:Payment|Quoted)[^.'’\"]*)", text):
        a = re.sub(r'\s+', ' ', m.group(1)).strip()
        if a and a.lower() not in _NOISE and a.lower() not in aseen:
            aseen.add(a.lower()); acts.append(a)
    snippet = ("Offline/Manual Tender on the CHiPS e-Procurement portal — "
               "login as Tender Creator and open the 'Offline Tender' menu, then fill the "
               "MANUAL TENDER HEADER DETAIL (" + ", ".join(fields[:8]) + ") and SAVE. "
               "Workflow steps: " + " → ".join(acts[:10]) + ".")
    return [{'rank': 0, 'score': 0.95, 'parent_id': '',
             'point': _LexPoint('Manual_Offline_Tenders_v.1.0', snippet[:cap]),
             'source': 'Manual_Offline_Tenders_v.1.0', 'text': snippet[:cap]}]


# GoI policy-manual sources whose "regret = reject all bids" concept hijacks the
# portal "regret items" answer. For a regret query we DROP these from context (the
# correct portal line is injected by lexical_portal_fact_lookup) — score-demotion
# alone only lowers their rank, it doesn't remove them from the prompt.
_POLICY_SRC_KEYS = (
    "manual_for_procurement", "mannual procurement", "publicpromanual", "ppm 00002",
    "gfr", "store_purhase", "store purchase",
)


def _suppress_policy_for_regret(query, context_results):
    """Remove GoI policy-manual chunks for a portal 'regret items' query so their
    'reject all bids' framing can't override the injected portal definition."""
    if not query or not context_results:
        return context_results
    q = query.lower()
    if not any(t in q for t in _REGRET_INTENT):
        return context_results
    kept = []
    for r in context_results:
        pt = r.get('point', {})
        src = (pt.payload.get('source', '') if hasattr(pt, 'payload') else '').lower()
        if any(k in src for k in _POLICY_SRC_KEYS):
            continue
        kept.append(r)
    return kept or context_results   # never return empty


# ── Curated critical facts ──────────────────────────────────────────────────
# Hand-verified authoritative facts injected at the FRONT of the context (high
# score) so a stray/demo value in some retrieved chunk cannot override them.
# Each entry: (intent-words, context-words, source-label, fact-text). Fires only
# when the query has BOTH an intent word AND a context word. Add more as needed.
_URL_INTENT = ("web pata", "वेब पता", "url", "website", "web site", "web address",
               "portal ka pata", "portal address", "पोर्टल का पता", "पोर्टल का वेब",
               "पोर्टल कहाँ", "पोर्टल कहां", "kaunsi website", "kaun si website",
               "link", "domain", "kis website")
_PORTAL_WORD = ("portal", "पोर्टल", "e-procurement", "eprocurement", "e proc", "eproc",
                "e-proc", "cgstate", "chips", "e-प्रोक्योरमेंट", "ई-प्रोक्योरमेंट")
CURATED_FACTS = [
    (_URL_INTENT, _PORTAL_WORD, "CHiPS e-Procurement Portal (official)",
     "Official Chhattisgarh CHiPS e-Procurement portal URL: https://eproc.cgstate.gov.in "
     "(this is the live production portal address)."),
]


def lexical_curated_facts(query):
    """Inject hand-verified authoritative facts (e.g. the live portal URL) at the
    front of the context so a demo/stray value in a retrieved chunk can't win.
    Fires only on a matching intent; [] otherwise (normal retrieval unaffected)."""
    if not query:
        return []
    low = query.lower()
    hits = []
    for intent, ctx, source, fact in CURATED_FACTS:
        if any(t in low for t in intent) and any(c in low for c in ctx):
            hits.append({'rank': 0, 'score': 0.98, 'parent_id': '',
                         'point': _LexPoint(source, fact),
                         'source': source, 'text': fact})
    return hits


def prepend_lexical_rule_hits(query, context_results):
    """Put exact Rule/Section matches AND exact portal facts (contact, fee, size,
    cost, auction, offline-tender workflow) at the FRONT of the retrieved context so
    the LLM sees them first and the scope gate passes. Also suppresses the GoI
    policy manuals for regret queries. No-op when no intent matches."""
    lex = (lexical_curated_facts(query) + lexical_rule_lookup(query) + lexical_concept_lookup(query)
           + lexical_phrase_lookup(query) + lexical_section_lookup(query)
           + lexical_portal_fact_lookup(query) + lexical_offline_tender_lookup(query))
    # De-dup identical injected passages (rule-number and concept lookups overlap when
    # a query names both, e.g. "Rule 154 purchase without quotation").
    _seen, _dedup = set(), []
    for _h in lex:
        _k = (_h.get('source', ''), (_h.get('text', '') or '')[:80])
        if _k not in _seen:
            _seen.add(_k)
            _dedup.append(_h)
    merged = _dedup + list(context_results or [])
    return _suppress_policy_for_regret(query, merged)


# Store settings
pipeline_initialized = False
qdrant_retry_attempted = False
kg_enabled = True
num_results = 5


def _is_qdrant_connection_failure(error_text):
    """Return True when the error likely indicates Qdrant connectivity failure."""
    if not error_text:
        return False

    msg = str(error_text).lower()
    keywords = [
        "qdrant connection failed",
        "cannot connect to qdrant",
        "connection refused",
        "failed to connect",
    ]
    return any(k in msg for k in keywords)


def _retry_initialize_once_on_qdrant_failure(error_text):
    """Attempt a single re-initialization after a Qdrant connection failure."""
    global qdrant_retry_attempted, pipeline_initialized

    if qdrant_retry_attempted:
        return None
    if not _is_qdrant_connection_failure(error_text):
        return None
    if not RAG_AVAILABLE or initialize_pipeline is None:
        return None

    qdrant_retry_attempted = True
    print("[Web UI] Qdrant connection failed. Retrying pipeline initialization once...")

    retry_result = initialize_pipeline()
    if retry_result.get('initialized'):
        pipeline_initialized = True
        print("[Web UI] One-time retry succeeded.")
    else:
        print(f"[Web UI] One-time retry failed: {retry_result.get('error')}")

    return retry_result

@app.route('/api/health', methods=['GET'])
def health():
    """Check system health"""
    return jsonify({
        'status': 'ok',
        'rag_pipeline': 'available' if RAG_AVAILABLE else 'unavailable',
        'pipeline_initialized': pipeline_initialized,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/init', methods=['POST'])
def init():
    """Initialize RAG pipeline and verify database connection"""
    global pipeline_initialized
    
    if not RAG_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'RAG pipeline not available. Check imports and configuration.',
            'details': {}
        }), 503
    
    try:
        print("\n[Web UI] Initializing RAG pipeline...")
        init_result = initialize_pipeline()
        
        if init_result.get('initialized'):
            pipeline_initialized = True
            print("[Web UI] RAG pipeline initialization successful")
            return jsonify({
                'success': True,
                'message': 'RAG pipeline initialized successfully',
                'details': init_result,
            }), 200

        retry_result = _retry_initialize_once_on_qdrant_failure(init_result.get('error'))
        if retry_result and retry_result.get('initialized'):
            return jsonify({
                'success': True,
                'message': 'RAG pipeline initialized successfully after one retry',
                'details': retry_result,
                'retried_once': True,
            }), 200

        else:
            print(f"[Web UI] RAG pipeline initialization failed: {init_result.get('error')}")
            return jsonify({
                'success': False,
                'error': init_result.get('error', 'Initialization failed'),
                'details': init_result,
                'retried_once': retry_result is not None,
                'retry_details': retry_result,
            }), 400
            
    except Exception as e:
        print(f"[Web UI] Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Initialization error: {str(e)}',
            'details': {}
        }), 500

@app.route('/api/db-status', methods=['GET'])
def db_status():
    """Check database connection and collection status"""
    
    if not RAG_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'RAG pipeline not available',
            'db_connected': False,
            'collection_exists': False
        }), 503
    
    try:
        status = get_db_status()

        if not status.get('db_connected', False):
            retry_result = _retry_initialize_once_on_qdrant_failure(status.get('error'))
            if retry_result and retry_result.get('initialized'):
                status = get_db_status()

        return jsonify({
            'success': True,
            'db_connected': status.get('db_connected', False),
            'collection_exists': status.get('collection_exists', False),
            'collection_name': status.get('collection_name'),
            'points_count': status.get('points_count', 0),
            'error': status.get('error'),
            'retried_once': qdrant_retry_attempted,
        }), 200
        
    except Exception as e:
        print(f"[Web UI] Error checking DB status: {e}")
        return jsonify({
            'success': False,
            'error': f'DB status check failed: {str(e)}',
            'db_connected': False,
            'collection_exists': False
        }), 500

@app.route('/api/query', methods=['POST'])
def query():
    """Process a query"""
    query_start_time = time.time()
    
    if not RAG_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'RAG pipeline not available. Check imports and configuration.',
            'query': ''
        }), 503
    
    data = request.get_json()
    query_text = data.get('query', '').strip()
    num_context = data.get('num_results', num_results)
    
    if not query_text:
        return jsonify({
            'success': False,
            'error': 'Query cannot be empty',
            'query': ''
        }), 400

    # Profanity / abuse filter — refuse outright, no retrieval or sources.
    if contains_profanity(query_text):
        reply = _PROFANITY_REPLIES.get(detect_query_language(query_text), _PROFANITY_REPLIES['en'])
        return jsonify({
            'success': True, 'query': query_text, 'answer': reply,
            'results': [], 'result_count': 0,
        }), 200

    # Scope gating now happens AFTER retrieval (relevance-based) — see below.
    try:
        print(f"\n⏱️ [FLASK] Total request start")
        print(f"[Web UI] Processing query: {query_text}")
        
        # Step 1: Retrieve context (parent chunks; expand synonyms for recall)
        print(f"[Web UI] Retrieving context...")
        retrieval_start = time.time()
        context_results = retrieve_context(expand_query_for_retrieval(query_text), num_context=num_context, rerank_query=query_text)
        # Exact Rule/Section lookups beat dense retrieval's blind spot for numbers.
        context_results = prepend_lexical_rule_hits(query_text, context_results)
        retrieval_time = time.time() - retrieval_start
        print(f"⏱️ [FLASK] Retrieval completed in {retrieval_time:.2f}s")
        
        # Scope gate (retrieval-relevance based): refuse if nothing was retrieved
        # or the best match is not relevant enough. A keyword hit is a fast-accept.
        if context_results is None or len(context_results) == 0 or not query_in_scope(query_text, context_results):
            refusal = REFUSAL_LINES.get(detect_query_language(query_text), REFUSAL_LINES['en'])
            return jsonify({
                'success': True, 'query': query_text, 'answer': refusal,
                'results': [], 'result_count': 0,
            }), 200
        
        # Step 2: Generate answer
        print(f"[Web UI] Generating answer...")
        answer_start = time.time()
        answer = generate_answer(query_text, context_results)
        answer_time = time.time() - answer_start
        print(f"⏱️ [FLASK] Answer generation completed in {answer_time:.2f}s")
        
        # Format results for frontend with actual PDF names and highlighted excerpts
        formatted_results = []
        query_words = [w for w in query_text.lower().split() if len(w) > 3]
        
        for result in context_results:
            point = result.get('point', {})
            source = point.payload.get('source', '') if hasattr(point, 'payload') else ''
            text = point.payload.get('text', '') if hasattr(point, 'payload') else ''
            
            # Get actual PDF name
            actual_pdf = _rag_module.get_actual_filename(source) if '_rag_module' in globals() else source
            
            # Extract highlighted excerpt
            from_rag = getattr(_rag_module, 'extract_highlighted_excerpt', None)
            if from_rag:
                excerpt = from_rag(text, query_words, max_length=250)
            else:
                excerpt = text[:250] + "..." if len(text) > 250 else text
            
            result_item = {
                'rank': result.get('rank', 0),
                'source': source,
                'actual_pdf': actual_pdf,  # New: Show actual PDF name
                'score': result.get('score', 0),
                'text': text,
                'excerpt': excerpt,  # New: Show highlighted excerpt
                'parent_id': result.get('parent_id', '')
            }
            
            formatted_results.append(result_item)
        
        total_time = time.time() - query_start_time
        print(f"[Web UI] Query processed successfully")
        print(f"⏱️ [FLASK] TOTAL PIPELINE TIME: {total_time:.2f}s\n")
        
        return jsonify({
            'success': True,
            'query': query_text,
            'answer': answer,
            'results': formatted_results,
            'result_count': len(formatted_results),
            'execution_time': f"{total_time:.2f}s"
        }), 200
    
    except Exception as e:
        print(f"[Web UI] Error processing query: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Error processing query: {str(e)}',
            'query': query_text,
            'results': []
        }), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    global kg_enabled, num_results
    
    if request.method == 'GET':
        return jsonify({
            'kg_enabled': kg_enabled,
            'num_results': num_results
        }), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if 'kg_enabled' in data:
            kg_enabled = data['kg_enabled']
        if 'num_results' in data:
            num_results = max(1, min(10, data['num_results']))  # Clamp between 1-10
        
        return jsonify({
            'success': True,
            'kg_enabled': kg_enabled,
            'num_results': num_results
        }), 200

@app.route('/api/examples', methods=['GET'])
def examples():
    """Return example queries"""
    examples_list = [
        "What approval was given in the recent meeting?",
        "Who leads the committee?",
        "What are the key financial decisions?",
        "Summarize the meeting agenda",
        "What are the next action items?",
        "What entities are mentioned in the documents?",
        "What was discussed about budget allocation?",
        "Tell me about the committee members",
    ]
    
    return jsonify({
        'examples': examples_list
    }), 200

@app.route('/01_preprocessing/used_files/<filename>', methods=['GET'])
def serve_pdf(filename):
    """Serve a cited source PDF for the in-UI viewer.

    The chatbot cites documents from the full ingest corpus (``input_pdfs/``),
    but a handful of deduplicated copies live only in ``used_files/``. Search
    both so every cited source resolves regardless of which folder holds it —
    ``input_pdfs`` first (it is the authoritative corpus), then ``used_files``.
    """
    import os

    # Security: only PDFs, and no directory traversal. (Spaces, parentheses and
    # accented characters in the real filenames are fine — they arrive URL-
    # decoded and are matched as a plain basename below.)
    if not filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 403
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 403

    search_dirs = [
        PROJECT_ROOT / '01_preprocessing' / 'input_pdfs',
        PROJECT_ROOT / '01_preprocessing' / 'used_files',
    ]
    pdf_path = next((d / filename for d in search_dirs
                     if (d / filename).exists()), None)

    if pdf_path is None:
        print(f"[Web UI] PDF not found in {[str(d) for d in search_dirs]}: {filename}")
        return jsonify({'error': f'PDF not found: {filename}'}), 404

    try:
        return send_file(str(pdf_path), mimetype='application/pdf')
    except Exception as e:
        print(f"[Web UI] Error serving PDF {filename}: {e}")
        return jsonify({'error': f'Error serving PDF: {str(e)}'}), 500

def _highlight_phrases(text, max_phrases=60):
    """Split a retrieved chunk into searchable phrases for PDF highlighting.

    Strips the chunker header, then splits on newlines and sentence boundaries
    (handles the Devanagari danda ``।`` too). Fragments shorter than ~18 chars
    produce noisy/ambiguous matches; ones longer than the PDF's own line wrap
    rarely match verbatim, so over-long units are clipped to a leading window.
    """
    import re
    body = strip_chunk_header(text or '')
    units = re.split(r'[\n\r]+|(?<=[।.?!])\s+', body)
    phrases, seen = [], set()
    for u in units:
        u = ' '.join(u.split()).strip(' \t-•*|>#')
        if len(u) > 180:                       # too long to match verbatim
            u = u[:160].rsplit(' ', 1)[0]
        if len(u) < 18 or u in seen:
            continue
        seen.add(u)
        phrases.append(u)
        if len(phrases) >= max_phrases:
            break
    return phrases


# Small in-memory cache of already-highlighted PDFs so reopening the same
# source (the common case — users click around the cited chunks) is instant
# instead of re-scanning + re-serializing a multi-MB PDF every time. Keyed by
# (filename, file-mtime, snippet-hash); bounded so memory can't grow unbounded.
from collections import OrderedDict as _OrderedDict
import hashlib as _hashlib
_HL_CACHE = _OrderedDict()           # key -> (bytes, page_1based_or_None, hits)
_HL_CACHE_MAX = 32

# Once we've found the passage, it's almost always confined to a couple of
# consecutive pages. Keep scanning a little past the last hit to catch a chunk
# that straddles a page break, then stop — no need to search a 300-page manual
# end-to-end for a single retrieved chunk.
_HL_TAIL_PAGES = 2


@app.route('/api/highlighted_pdf', methods=['POST'])
def highlighted_pdf():
    """Serve a cited source PDF with the retrieved context highlighted.

    The in-UI viewer fetches this instead of the raw PDF so the user can SEE the
    exact passage the answer was grounded in. We locate the chunk text with
    PyMuPDF and add native highlight annotations (rendered by the browser's PDF
    viewer). On any miss — OCR/whitespace drift, no match, or a fitz error — we
    fall back to the original PDF so the viewer always works.

    Results are cached and the page scan early-exits once the passage region is
    found, so first load is fast and reopening the same source is instant.
    """
    data     = request.get_json(silent=True) or {}
    filename = (data.get('filename') or '').strip()
    snippet  = data.get('snippet') or data.get('text') or ''

    # Same guards as serve_pdf: PDFs only, no directory traversal.
    if not filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 403
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 403

    search_dirs = [
        PROJECT_ROOT / '01_preprocessing' / 'input_pdfs',
        PROJECT_ROOT / '01_preprocessing' / 'used_files',
    ]
    pdf_path = next((d / filename for d in search_dirs
                     if (d / filename).exists()), None)
    if pdf_path is None:
        return jsonify({'error': f'PDF not found: {filename}'}), 404

    def _serve_plain():
        return send_file(str(pdf_path), mimetype='application/pdf')

    def _make_resp(out_bytes, page_1based, hits):
        resp = Response(bytes(out_bytes), mimetype='application/pdf')
        if page_1based is not None:
            resp.headers['X-Highlight-Page'] = str(page_1based)
        resp.headers['X-Highlight-Hits'] = str(hits)
        resp.headers['Access-Control-Expose-Headers'] = 'X-Highlight-Page, X-Highlight-Hits'
        return resp

    phrases = _highlight_phrases(snippet)
    if not phrases:
        return _serve_plain()

    # Cache lookup (mtime in the key invalidates if the source PDF is replaced).
    try:
        mtime = pdf_path.stat().st_mtime_ns
    except OSError:
        mtime = 0
    cache_key = (filename, mtime,
                 _hashlib.md5(snippet.encode('utf-8', 'replace')).hexdigest())
    cached = _HL_CACHE.get(cache_key)
    if cached is not None:
        _HL_CACHE.move_to_end(cache_key)          # LRU touch
        out, page_1based, hits = cached
        return _make_resp(out, page_1based, hits)

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"[highlight] open failed for {filename}: {e}")
        return _serve_plain()

    first_hit_page, last_hit_page, total_hits = None, None, 0
    try:
        for page in doc:
            page_hit = False
            for phrase in phrases:
                try:
                    quads = page.search_for(phrase, quads=True)
                except Exception:
                    quads = []
                if quads:
                    annot = page.add_highlight_annot(quads)
                    annot.set_colors(stroke=(1, 0.84, 0.2))   # amber
                    annot.update()
                    total_hits += len(quads)
                    page_hit = True
            if page_hit:
                if first_hit_page is None:
                    first_hit_page = page.number
                last_hit_page = page.number
            # Stop once we're past the passage: found hits and the scan has
            # moved a couple of pages beyond the last match.
            elif last_hit_page is not None and page.number - last_hit_page > _HL_TAIL_PAGES:
                break
        if total_hits == 0:
            return _serve_plain()
        out = doc.tobytes(garbage=3, deflate=True)
    except Exception as e:
        print(f"[highlight] annotate failed for {filename}: {e}")
        return _serve_plain()
    finally:
        try:
            doc.close()
        except Exception:
            pass

    page_1based = (first_hit_page + 1) if first_hit_page is not None else None
    _HL_CACHE[cache_key] = (out, page_1based, total_hits)
    _HL_CACHE.move_to_end(cache_key)
    while len(_HL_CACHE) > _HL_CACHE_MAX:
        _HL_CACHE.popitem(last=False)             # evict oldest
    return _make_resp(out, page_1based, total_hits)


@app.route('/api/stream', methods=['POST'])
def stream_query():
    """Stream query response using SSE."""
    if not RAG_AVAILABLE:
        def err_gen():
            yield f"data: {json.dumps({'type':'error','message':'RAG pipeline not available'})}\n\n"
        return Response(stream_with_context(err_gen()), mimetype='text/event-stream')

    data = request.get_json()
    query_text = data.get('query', '').strip()
    num_context = data.get('num_results', num_results)
    # Conversation id for multi-turn memory (NER slots + coreference topic).
    # Falls back to a single shared bucket if the frontend doesn't send one.
    session_id = (data.get('session_id') or 'anon').strip() or 'anon'

    if not query_text:
        def err_gen():
            yield f"data: {json.dumps({'type':'error','message':'Query cannot be empty'})}\n\n"
        return Response(stream_with_context(err_gen()), mimetype='text/event-stream')

    def generate():
        import time
        t0 = time.time()
        try:
            # Profanity / abuse filter — refuse outright, do not engage or cite sources.
            if contains_profanity(query_text):
                reply = _PROFANITY_REPLIES.get(detect_query_language(query_text), _PROFANITY_REPLIES['en'])
                yield f"data: {json.dumps({'type':'token','content':reply})}\n\n"
                yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':[]})}\n\n"
                return

            # Greeting handler — friendly responses for social openers (hi, hello, thanks, etc.)
            greeting_lang = detect_greeting(query_text)
            if greeting_lang:
                reply = greeting_response(greeting_lang)
                yield f"data: {json.dumps({'type':'token','content':reply})}\n\n"
                yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':[]})}\n\n"
                return

            # ── Guided task-flow (wizard) ────────────────────────────────────
            # If a flow is already running for this session, treat the message as
            # the answer to the current step (unless the user cancels).
            if CONV_MEMORY.flow_active(session_id):
                if query_text.strip().lower() in (
                        'cancel', 'stop', 'exit', 'quit', 'cancel karo', 'rehne do'):
                    CONV_MEMORY.cancel_flow(session_id)
                    msg = "No problem — I've cancelled the guided registration. Ask me anything else."
                    yield f"data: {json.dumps({'type':'token','content':msg})}\n\n"
                    yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':[]})}\n\n"
                    return
                step = CONV_MEMORY.advance_flow(session_id, query_text)
                out = step['summary'] if step['done'] else step['prompt']
                yield f"data: {json.dumps({'type':'token','content':out})}\n\n"
                yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':[]})}\n\n"
                return

            # Start a guided flow if the user asks for one ("register me", etc.).
            _flow = detect_flow_trigger(query_text)
            if _flow:
                first_prompt = CONV_MEMORY.start_flow(session_id, _flow)
                if first_prompt:
                    yield f"data: {json.dumps({'type':'token','content':first_prompt})}\n\n"
                    yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':[]})}\n\n"
                    return

            # ── NLP layer: NER + typo-fix + intent + coreference ─────────────
            # 1) Extract entities from the RAW query (names/PAN must not be "fixed").
            entities = extract_entities(query_text)
            slots = CONV_MEMORY.update_slots(session_id, entities)
            # 2) Typo-correct the query for retrieval/intent (conservative).
            corrected_query, corrections = correct_typos(query_text)
            if corrections:
                print(f"[NLP] typo-fix: {query_text!r} -> {corrected_query!r} {corrections}")
                yield f"data: {json.dumps({'type':'status','message':f'Showing results for: {corrected_query}'})}\n\n"
            # 3) Resolve coreference ("tell me more about it" -> "...about EMD refund").
            sess = CONV_MEMORY.get_session(session_id)
            effective_query, coref_applied = resolve_coreference(corrected_query, sess.last_topic)
            # 3b) Language-switch follow-up ("hindi me batao"): no new subject —
            #     re-answer the PREVIOUS question in the requested language instead
            #     of retrieving on the bare language word (which fetches junk).
            if not coref_applied and is_language_switch_only(query_text):
                _prev_q = next((t.query for t in reversed(sess.turns)
                                if t.query and not is_language_switch_only(t.query)), "")
                if _prev_q:
                    effective_query, coref_applied = _prev_q, True
                elif sess.last_topic:
                    effective_query, coref_applied = f"explain {sess.last_topic}", True
                if coref_applied:
                    print(f"[NLP] language-switch follow-up: {query_text!r} "
                          f"-> re-answering {effective_query!r}")
            # 4) Classify intent on the resolved query (formal taxonomy).
            intent, intent_conf = classify_intent(effective_query)
            topic = INTENT_TOPIC_PHRASE.get(intent, sess.last_topic)
            _ent_summary = entities_summary(entities)
            print(f"[NLP] session={session_id} intent={intent}({intent_conf}) "
                  f"coref={'yes' if coref_applied else 'no'} "
                  f"entities=[{_ent_summary}]")
            if coref_applied:
                print(f"[NLP] coreference: {query_text!r} -> {effective_query!r}")

            # 5) Clarification: ask back when a required slot is missing.
            _clarify = needs_clarification(effective_query, intent, entities)
            if _clarify and not coref_applied:
                yield f"data: {json.dumps({'type':'token','content':_clarify})}\n\n"
                CONV_MEMORY.record_turn(session_id, query_text, intent, topic, _clarify[:200])
                yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':[]})}\n\n"
                return

            # 6) Answer cache: serve near-duplicate questions instantly. Skip when
            #    the query is personalised (has a name) or is a context-dependent
            #    follow-up, since those need a fresh, tailored answer.
            if not coref_applied and not entities.get('persons'):
                _cached = ANSWER_CACHE.get(effective_query)
                if _cached:
                    yield f"data: {json.dumps({'type':'status','message':'Instant answer (cached)'})}\n\n"
                    yield f"data: {json.dumps({'type':'token','content':_cached['answer']})}\n\n"
                    _fu = suggest_followups(intent)
                    if _fu:
                        yield f"data: {json.dumps({'type':'followups','items':_fu})}\n\n"
                    CONV_MEMORY.record_turn(session_id, query_text, intent, topic, _cached['answer'][:300])
                    _log_event(ANALYTICS_LOG, {'q': query_text, 'intent': intent,
                                               'cache_hit': True, 'elapsed': round(time.time()-t0, 2)})
                    yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':_cached['sources']})}\n\n"
                    return

            # Step 1: Retrieve context (expand synonyms/abbreviations for recall).
            # Use the coreference-resolved query so follow-ups find the right docs.
            yield f"data: {json.dumps({'type':'status','message':'🔍 Searching the procurement manuals…'})}\n\n"
            context_results = retrieve_context(expand_query_for_retrieval(effective_query), num_context=num_context, rerank_query=effective_query)
            # Exact Rule/Section lookups beat dense retrieval's blind spot for numbers.
            context_results = prepend_lexical_rule_hits(effective_query, context_results)

            # Meta-question filter: if asking about the chatbot itself, only use Chatbot_Capabilities.
            # Always re-retrieve with a canonical English query so both the embedder and the
            # cross-encoder can match the Capabilities doc regardless of the user's language
            # (Hinglish "tum mujhe kya kya bta skte ho?" is a poor embedding match for Hindi
            # text; the canonical query is not).
            if is_meta_question(query_text):
                _META_CANONICAL = (
                    "what can this chatbot do capabilities features topics help "
                    "chatbot kya kya bata sakta hai"
                )
                meta_ctx = retrieve_context(
                    _META_CANONICAL, num_context=6, rerank_query=_META_CANONICAL
                )
                meta_results = []
                if meta_ctx:
                    for r in (meta_ctx or []):
                        point = r.get('point', {})
                        if hasattr(point, 'payload') and \
                                'Chatbot_Capabilities' in point.payload.get('source', ''):
                            meta_results.append(r)
                if meta_results:
                    context_results = meta_results
                else:
                    # Capabilities doc missing from Qdrant — fall back to normal results
                    # but at least filter out non-procurement noise (leave context_results as-is)
                    pass

            # Scope gate (retrieval-relevance based): refuse out-of-scope questions
            # AFTER retrieval, so typos / Hinglish-in-Devanagari / new document
            # domains are not falsely rejected by a fixed keyword list. A keyword
            # hit is a fast-accept; clearly unrelated questions retrieve nothing
            # relevant and are refused.
            if not context_results or not query_in_scope(effective_query, context_results):
                refusal = REFUSAL_LINES.get(detect_query_language(query_text), REFUSAL_LINES['en'])
                yield f"data: {json.dumps({'type':'token','content':refusal})}\n\n"
                yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':[]})}\n\n"
                return

            # Send context cards immediately
            formatted = []
            query_words = [w for w in effective_query.lower().split() if len(w) > 3]
            for r in context_results:
                point = r.get('point', {})
                source = point.payload.get('source', '') if hasattr(point, 'payload') else ''
                text   = point.payload.get('text', '')   if hasattr(point, 'payload') else ''
                actual_pdf = _rag_module.get_actual_filename(source) if '_rag_module' in globals() else source
                from_rag = getattr(_rag_module, 'extract_highlighted_excerpt', None)
                excerpt = from_rag(text, query_words, max_length=250) if from_rag else text[:250]
                formatted.append({'rank': r.get('rank',0), 'source': source,
                                   'actual_pdf': actual_pdf, 'score': r.get('score',0),
                                   'text': text, 'excerpt': excerpt})
            yield f"data: {json.dumps({'type':'context','results':formatted})}\n\n"

            # Confidence from the top reranker score (low → caveat note in answer).
            _top_score = context_results[0].get('score', 0) if context_results else 0
            _conf_label, _conf_note = confidence_from_score(_top_score)

            # Build context — cap total size so the prompt fits the model's
            # context window (num_ctx 4096). Full chunks (some are 8KB) across 5
            # sources overflow the window; some models then emit nothing/garbage
            # (gemma4 produced only "💡"). Reranking already orders the most
            # relevant chunks first, so trimming the tail costs little. The UI
            # still shows all sources (sent as cards above).
            # Trimmed to keep the iGPU off its memory ceiling: gemma4:12b (8.3GB)
            # + a large KV cache leaves little headroom on the Arc iGPU, and a
            # big retrieved context tips the runner into an OOM crash (Flask then
            # reports "Ollama error 500"). 7000/1600 keeps the full prompt well
            # under num_ctx with room for checkpoints + output; reranking already
            # front-loads the best chunks so the tail costs little.
            # NOTE: do NOT lower this for speed — on the Arc iGPU the bottleneck
            # is output decoding, not prompt size, so a smaller budget gives no
            # speedup but can drop relevant context and cause false "not found"
            # refusals.
            CTX_CHAR_BUDGET = 7000
            PER_CHUNK_CAP   = 1600
            context_parts = []
            source_refs   = []
            used = 0
            for i, r in enumerate(context_results, 1):
                point = r.get('point', {})
                src  = point.payload.get('source','') if hasattr(point,'payload') else ''
                txt  = point.payload.get('text','')   if hasattr(point,'payload') else ''
                apdf = _rag_module.get_actual_filename(src) if '_rag_module' in globals() else src
                body = strip_chunk_header(txt)[:PER_CHUNK_CAP]
                if context_parts and used + len(body) > CTX_CHAR_BUDGET:
                    break
                if apdf not in source_refs:
                    source_refs.append(apdf)
                context_parts.append(f"[Source {i}: {apdf}]\n{body}")
                used += len(body)

            context_text = "\n\n".join(context_parts)
            sources_str  = ", ".join(source_refs)
            system_msg   = SYSTEM_PROMPT.strip() + f"\n\nAvailable source documents: {sources_str}"
            user_msg     = f"Context from documents:\n{context_text}\n\nQuestion: {query_text}\n\nAnswer:"

            # ── Step 2: Ollama (llama3.2 on Intel Arc GPU) ───────────────────
            OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')
            OLLAMA_URL   = os.getenv('OLLAMA_URL', 'http://localhost:11434')
            _src_count = len(source_refs)
            yield f"data: {json.dumps({'type':'status','message':f'📖 Reading {_src_count} relevant document(s)…'})}\n\n"
            yield f"data: {json.dumps({'type':'status','message':'✍️ Composing your answer…'})}\n\n"

            # Expert Government Procurement Assistant — language-locked structured output.
            # The language instruction is placed LAST (after the English context) so the
            # model weights it most by recency — otherwise llama3:8b drifts to English.
            _lang = detect_query_language(query_text)
            # Tell the client the target language so it can enforce Roman-script
            # Hinglish if gemma3:4b drifts into Devanagari (client romanises).
            yield f"data: {json.dumps({'type':'lang','lang':_lang})}\n\n"
            ollama_system = PROCUREMENT_SYSTEM_PROMPT.strip() + language_directive(_lang)
            if _lang == 'hi':
                _final = ("\n\n>>> महत्वपूर्ण: ऊपर दी गई सामग्री अंग्रेज़ी में है, फिर भी पूरा उत्तर "
                          "केवल हिंदी (Devanagari लिपि) में, निर्धारित प्रारूप (💡 उत्तर / 📋 प्रक्रिया / "
                          "📘 स्रोत) में लिखें। कोई वाक्य अंग्रेज़ी में न लिखें; तकनीकी शब्द (EMD, Tender, "
                          "Bid, GFR, DSC आदि) ज्यों के त्यों रखें।")
            elif _lang == 'hinglish':
                _final = ("\n\n>>> IMPORTANT: Even though the Context is in English, you MUST "
                          "translate it and reply ENTIRELY in HINGLISH (sentences in Roman script, "
                          "e.g. 'E-procurement ka matlab hai...'). DO NOT write your answer in plain English. "
                          "CRITICAL: You MUST use ONLY the English alphabet (A-Z, a-z). ABSOLUTELY NO Devanagari or Bengali scripts allowed. "
                          "Keep technical terms (EMD, Tender, Bid, DSC, NIT, GFR, e-Procurement) in English. "
                          "Use the English emoji headings (💡 Answer / 📋 Process / 📘 Source).")
            else:
                _final = ("\n\n>>> IMPORTANT: Reply ENTIRELY in English, using the English "
                          "headings (💡 Answer / 📋 Process / 📘 Source).")
            # Memory block: known user details (name/company) + previous turn so
            # the LLM can personalise and resolve follow-ups. Empty on turn 1.
            _mem_block = CONV_MEMORY.memory_block(session_id)
            _mem_prefix = f"[Conversation memory]\n{_mem_block}\n\n" if _mem_block else ""
            # Entity hints: pass the user's amount so the LLM uses the exact figure.
            # (Deadline urgency is injected deterministically in code after the
            # answer heading — see _deadline_line below — not left to the LLM.)
            _entity_hints = ""
            if entities.get("amounts"):
                _entity_hints = (f"[Time-sensitive context]\n"
                                 f"Amount(s): {', '.join(entities['amounts'])}\n\n")
            # When a follow-up was coreference-resolved, give the LLM the resolved
            # (self-contained) question so it answers the right subject.
            _llm_question = effective_query if coref_applied else query_text
            
            _ans_prefix = "\n\nAnswer:"
            if _lang == 'hinglish':
                _ans_prefix = "\n\nAnswer (in Roman script Hinglish):"
            elif _lang == 'hi':
                _ans_prefix = "\n\nAnswer (in Devanagari Hindi):"

            ollama_user = f"Context:\n{context_text}\n\n{_mem_prefix}{_entity_hints}Question: {_llm_question}{_final}{_ans_prefix}"

            # ── Multi-part questions: TRUE decomposition ─────────────────────
            # gemma3:4b answers only the FIRST clause of a compound question and
            # silently drops the rest, even when the answer is in Context — but it
            # answers each sub-question correctly IN ISOLATION (verified: a trailing
            # nudge AND an enumerated single-prompt both failed; a lone sub-question
            # works). So generate each sub-answer in its own call and merge. The
            # whole branch is wrapped so any failure falls through to the normal
            # single-pass generation below (the single-question path is untouched).
            _parts = _decompose_question(_llm_question)
            if len(_parts) >= 2 and not is_meta_question(query_text) and not coref_applied:
                import re as _re
                # Carry the subject into later parts so a bare pronoun ("when is
                # IT exempted?") isn't retrieved/answered in isolation (which
                # pulls the WRONG topic — e.g. e-publishing exemption instead of
                # EMD). Subject = the first part minus its leading wh-word.
                _subj = _re.sub(r"^(what(?:'s| is| are)?|who is|which|name|the)\s+",
                                '', _parts[0].rstrip('? ').strip(), flags=_re.I).strip()

                def _disambig(p):
                    if not _subj:
                        return p
                    if _re.search(r'\b(it|its|they|them|their)\b', p, _re.I):
                        return _re.sub(r'\b(it|its|they|them|their)\b', _subj, p, count=1, flags=_re.I)
                    if _subj.lower() not in p.lower():
                        return f"{p.rstrip('?')} (regarding {_subj})?"
                    return p

                _subqs = [_parts[0]] + [_disambig(p) for p in _parts[1:]]
                # Sub-answers must NOT carry their own 💡/📋/📘 structure (multiple
                # "📘 Source" lines would break the client's answer renderer); we
                # wrap them under one heading and one source-chip set.
                if _lang == 'hi':
                    _sub_dir = ("\n\n>>> उत्तर पूरा हिंदी में दें। केवल सीधा उत्तर लिखें — "
                                "कोई 💡/📋/📘 शीर्षक या स्रोत पंक्ति नहीं।")
                elif _lang == 'hinglish':
                    _sub_dir = ("\n\n>>> IMPORTANT: Translate the Context and reply in HINGLISH "
                                "(sentences in Roman script). Give ONLY the direct answer — no 💡/📋/📘 "
                                "headings, no Source line. DO NOT answer in plain English. "
                                "CRITICAL: Use ONLY the English alphabet (A-Z, a-z). No Devanagari or Bengali script allowed.")
                else:
                    _sub_dir = ("\n\n>>> Answer in English. Give ONLY the direct answer text — "
                                "no 💡/📋/📘 headings, no Source line.")

                def _strip_struct(t):
                    out = []
                    for ln in (t or '').splitlines():
                        s = ln.strip()
                        if s and (s[0] in '💡📋📘🔖'
                                  or _re.match(r'^(source|स्रोत|स्त्रोत)\s*[:：]', s, _re.I)):
                            continue
                        out.append(ln)
                    return '\n'.join(out).strip()

                def _answer_sub(sub_q):
                    sres = retrieve_context(expand_query_for_retrieval(sub_q),
                                            num_context=num_context, rerank_query=sub_q)
                    sres = prepend_lexical_rule_hits(sub_q, sres)
                    sparts, ssrcs, sused = [], [], 0
                    for j, r in enumerate(sres or [], 1):
                        pt = r.get('point', {})
                        src = pt.payload.get('source', '') if hasattr(pt, 'payload') else ''
                        txt = pt.payload.get('text', '') if hasattr(pt, 'payload') else ''
                        apdf = _rag_module.get_actual_filename(src) if '_rag_module' in globals() else src
                        body = strip_chunk_header(txt)[:PER_CHUNK_CAP]
                        if sparts and sused + len(body) > CTX_CHAR_BUDGET:
                            break
                        if apdf not in ssrcs:
                            ssrcs.append(apdf)
                        sparts.append(f"[Source {j}: {apdf}]\n{body}")
                        sused += len(body)
                    su = (f"Context:\n{chr(10).join(sparts)}\n\nQuestion: {sub_q}{_sub_dir}{_ans_prefix}")
                    rj = requests.post(f"{OLLAMA_URL}/api/chat", json={
                        'model': OLLAMA_MODEL,
                        'messages': [{'role': 'system', 'content': ollama_system},
                                     {'role': 'user', 'content': su}],
                        'stream': False, 'think': False,
                        'keep_alive': os.getenv('OLLAMA_KEEP_ALIVE', '30m'),
                        'options': {'temperature': 0, 'seed': 42, 'num_predict': int(os.getenv('OLLAMA_NUM_PREDICT', '1536')),
                                    'num_ctx': int(os.getenv('OLLAMA_NUM_CTX', '6144'))},
                    }, timeout=300)
                    ans = ''
                    if rj.status_code == 200:
                        ans = ((rj.json().get('message') or {}).get('content') or '').strip()
                    # Clean structure AND ungrounded rule numbers before merging
                    # (this path streams the pre-built text, so it must be clean).
                    ans = _sanitize_rule_numbers(_strip_struct(ans), chr(10).join(sparts))
                    return ans, ssrcs

                try:
                    yield f"data: {json.dumps({'type':'status','message':f'🧩 Answering {len(_parts)} parts…'})}\n\n"
                    _hdr = '💡 उत्तर' if _lang == 'hi' else '💡 Answer'
                    _union, _subtexts, _ok = [], [], False
                    for _i, _sub in enumerate(_subqs, 1):
                        _a, _ss = _answer_sub(_sub)
                        if _a:
                            _ok = True
                        for _s in _ss:
                            if _s not in _union:
                                _union.append(_s)
                        _subtexts.append(f"**{_i}. {_sub.rstrip('?')}**\n{_a or '—'}")
                    if _ok:
                        _merged = f"{_hdr}\n" + "\n\n".join(_subtexts)
                        for _k in range(0, len(_merged), 60):
                            yield f"data: {json.dumps({'type':'token','content':_merged[_k:_k+60]})}\n\n"
                        _fu = suggest_followups(intent)
                        if _fu:
                            yield f"data: {json.dumps({'type':'followups','items':_fu})}\n\n"
                        try:
                            CONV_MEMORY.record_turn(session_id, query_text, intent, topic, _merged[:300])
                            if not entities.get('persons') and _conf_label != 'low':
                                ANSWER_CACHE.put(effective_query, _merged, _union)
                        except Exception:
                            pass
                        _log_event(ANALYTICS_LOG, {'q': query_text, 'intent': intent,
                                                   'decomposed': len(_parts),
                                                   'elapsed': round(time.time() - t0, 2)})
                        yield f"data: {json.dumps({'type':'done','elapsed':f'{time.time()-t0:.2f}s','sources':_union})}\n\n"
                        return
                except Exception as _e:
                    print(f"[decompose] failed, falling back to single-pass: {_e}")

            # ── Generation with automatic fallback ───────────────────────────
            # Primary is gemma4:12b (best Hindi) but it sits near the Arc iGPU
            # memory ceiling and can OOM-crash the runner on a large-context
            # query (HTTP 500 / dropped connection). Instead of surfacing that,
            # transparently retry on the lighter llama3:8b, which has plenty of
            # iGPU headroom. Fallback fires only if the primary failed BEFORE any
            # answer token was streamed — a mid-stream crash after partial output
            # can't be cleanly restarted.
            FALLBACK_MODEL = os.getenv('OLLAMA_FALLBACK_MODEL', 'llama3:8b')

            # Language-based model routing: English queries use a faster model
            # (Mistral 7B). Hindi and Hinglish stay on the primary model because
            # Gemma3 12B has proven multilingual quality; Mistral is weak on both.
            if _lang == 'en' and os.getenv('OLLAMA_MODEL_EN'):
                OLLAMA_MODEL = os.getenv('OLLAMA_MODEL_EN')

            # ── Deterministic lines injected after the answer heading (the LLM
            #    is too unreliable to format these): deadline urgency, numeric
            #    calculation, and a low-confidence caveat. ──
            _inject_parts = []
            if entities.get("dates"):
                try:
                    from nlp_features import _parse_date_str, _days_until
                    for _d in entities["dates"]:
                        _parsed = _parse_date_str(_d)
                        if _parsed:
                            _days = _days_until(*_parsed)
                            if _days < 0:
                                _inject_parts.append(f"⏰ OVERDUE (was {abs(_days)} day{'s' if abs(_days) != 1 else ''} ago)")
                            elif _days == 0:
                                _inject_parts.append("⏰ DEADLINE IS TODAY")
                            elif _days == 1:
                                _inject_parts.append("⏰ Deadline is TOMORROW")
                            else:
                                _inject_parts.append(f"⏰ Deadline is in {_days} days ({_d})")
                            break
                except Exception:
                    pass
            _numeric = compute_numeric(entities)
            if _numeric:
                _inject_parts.append(_numeric)
            # NOTE: the low-confidence caveat (_conf_note) is intentionally NOT
            # prepended to the answer — it read as the bot doubting itself. A
            # standing "AI can make mistakes…" disclaimer already sits under every
            # response. _conf_label is still used for the cache guards below.
            _deadline_line = "\n".join(_inject_parts)   # name kept for stream logic below

            def _stream_model(model, state):
                """Run one Ollama streaming attempt. Yields SSE strings; records
                on `state` whether any content was produced ('content_streamed')
                and whether it failed before producing output
                ('failed_before_output') so the caller can fall back."""
                try:
                    resp = requests.post(
                        f"{OLLAMA_URL}/api/chat",
                        json={'model': model,
                              'messages': [{'role':'system','content':ollama_system},
                                           {'role':'user','content':ollama_user}],
                              'stream': True,
                              # Keep the model resident between queries so the next
                              # user doesn't pay the ~66s cold-load. Default 30m;
                              # set OLLAMA_KEEP_ALIVE=-1 to pin it indefinitely.
                              'keep_alive': os.getenv('OLLAMA_KEEP_ALIVE', '30m'),
                              # Disable reasoning models' thinking phase (gemma4):
                              # otherwise a long thinking block consumes the token
                              # budget and no answer content streams. llama3 ignores.
                              'think': False,
                              'options': {
                                  # Deterministic generation: same query + context
                                  # must yield the same answer (factual gov Q&A bot).
                                  'temperature': 0,
                                  'seed':        42,
                                  'num_predict': int(os.getenv('OLLAMA_NUM_PREDICT', '1536')),
                                  # Trimmed context keeps the full prompt ~3.7k tok;
                                  # 5120 fits it with ~1.4k output headroom and shrinks
                                  # the KV cache ~17% vs 6144 — the headroom that stops
                                  # the Arc iGPU runner OOM-crashing (500). 8192 OOMs.
                                  'num_ctx':     int(os.getenv('OLLAMA_NUM_CTX', '6144')),
                              }},
                        stream=True, timeout=300
                    )
                    if resp.status_code != 200:
                        # Crash during prompt processing → 500 before any stream.
                        state['failed_before_output'] = True
                        return

                    thinking_notified   = False
                    thinking_ping_count = 0
                    for line in resp.iter_lines():
                        if not line: continue
                        try:
                            chunk    = json.loads(line)
                            # Ollama may stream an error line (status was 200) if
                            # the runner dies mid-generation.
                            if chunk.get('error') and not state.get('content_streamed'):
                                state['failed_before_output'] = True
                                break
                            msg      = chunk.get('message', {})
                            content  = msg.get('content', '')
                            thinking = msg.get('thinking', '')

                            if thinking:
                                if not thinking_notified:
                                    yield f"data: {json.dumps({'type':'status','message':'Thinking...'})}\n\n"
                                    thinking_notified = True
                                else:
                                    # SSE keepalive every 20 thinking tokens so the
                                    # proxy/browser doesn't close the connection.
                                    thinking_ping_count += 1
                                    if thinking_ping_count % 20 == 0:
                                        yield ": ping\n\n"

                            if content:
                                if content.strip():
                                    state['content_streamed'] = True
                                # Deterministic deadline injection: hold back the
                                # opening heading until its line completes, then
                                # insert the ⏰ line right after it. Guarantees the
                                # "💡 Answer" heading stays first and the deadline
                                # is always present (the LLM can't be trusted to).
                                if _deadline_line and not state.get('hdr_done'):
                                    buf = state.get('hdr_buf', '') + content
                                    nl = buf.find('\n')
                                    if nl != -1 and buf[:nl].strip():
                                        out = buf[:nl] + '\n' + _deadline_line + '\n' + buf[nl+1:]
                                        state['hdr_done'] = True
                                        state['hdr_buf'] = ''
                                        state.setdefault('answer_buf', []).append(out)
                                        yield f"data: {json.dumps({'type':'token','content':out})}\n\n"
                                    elif len(buf) > 200:
                                        # No heading newline found — give up, flush as-is.
                                        state['hdr_done'] = True
                                        state['hdr_buf'] = ''
                                        state.setdefault('answer_buf', []).append(buf)
                                        yield f"data: {json.dumps({'type':'token','content':buf})}\n\n"
                                    else:
                                        state['hdr_buf'] = buf  # keep buffering silently
                                else:
                                    state.setdefault('answer_buf', []).append(content)
                                    yield f"data: {json.dumps({'type':'token','content':content})}\n\n"

                            if chunk.get('done'):
                                # Flush any buffered heading content (short/single-line answer).
                                if _deadline_line and not state.get('hdr_done') and state.get('hdr_buf'):
                                    buf = state['hdr_buf']
                                    nl = buf.find('\n')
                                    if nl != -1 and buf[:nl].strip():
                                        out = buf[:nl] + '\n' + _deadline_line + '\n' + buf[nl+1:]
                                    else:
                                        out = buf + '\n' + _deadline_line
                                    state['hdr_done'] = True
                                    state['hdr_buf'] = ''
                                    state.setdefault('answer_buf', []).append(out)
                                    yield f"data: {json.dumps({'type':'token','content':out})}\n\n"
                                break
                        except Exception:
                            pass
                    # Natural end of stream without an explicit 'done': flush buffer.
                    if _deadline_line and not state.get('hdr_done') and state.get('hdr_buf'):
                        buf = state['hdr_buf']
                        nl = buf.find('\n')
                        if nl != -1 and buf[:nl].strip():
                            out = buf[:nl] + '\n' + _deadline_line + '\n' + buf[nl+1:]
                        else:
                            out = buf + '\n' + _deadline_line
                        state['hdr_done'] = True
                        state['hdr_buf'] = ''
                        state.setdefault('answer_buf', []).append(out)
                        yield f"data: {json.dumps({'type':'token','content':out})}\n\n"
                except Exception as e:
                    # Connection forcibly closed = runner crash. Safe to fall back
                    # only if nothing was streamed yet; otherwise surface the error.
                    if not state.get('content_streamed'):
                        state['failed_before_output'] = True
                        state['error'] = str(e)
                    else:
                        yield f"data: {json.dumps({'type':'error','message':f'Ollama error: {e}'})}\n\n"

            state = {'content_streamed': False, 'failed_before_output': False}
            for sse in _stream_model(OLLAMA_MODEL, state):
                yield sse

            # Transparent fallback to the lighter model when the primary either
            # crashed before output (iGPU OOM → 500) OR streamed zero content
            # (gemma4 occasionally emits nothing on mixed Hindi+Hinglish queries
            # where the language directive conflicts). Either way the user would
            # otherwise see nothing useful, so retry on llama3:8b before giving up.
            if ((state['failed_before_output'] or not state['content_streamed'])
                    and FALLBACK_MODEL and FALLBACK_MODEL != OLLAMA_MODEL):
                yield f"data: {json.dumps({'type':'status','message':'Switching to a lighter model...'})}\n\n"
                # Free the iGPU BEFORE falling back. gemma4:12b (~8GB) and the
                # fallback model both resident on the Arc iGPU exhaust its VRAM,
                # so the fallback OOMs too and the user gets an empty answer.
                # Ask Ollama to evict the primary (keep_alive=0, no prompt → an
                # immediate unload) so llama3:8b has headroom to actually answer.
                # Best-effort: if Ollama already dropped the crashed runner this
                # is a no-op. The next query reloads gemma cold (acceptable on
                # this rare path).
                try:
                    requests.post(f"{OLLAMA_URL}/api/generate",
                                  json={'model': OLLAMA_MODEL, 'keep_alive': 0},
                                  timeout=30)
                except Exception:
                    pass
                state = {'content_streamed': False, 'failed_before_output': False}
                for sse in _stream_model(FALLBACK_MODEL, state):
                    yield sse

            content_streamed = state['content_streamed']

            # Empty-answer guard: the model occasionally streams zero content
            # tokens (observed with llama3:8b on Hinglish queries), leaving a
            # blank bubble in the UI. Emit a graceful fallback instead.
            if not content_streamed:
                _fallbacks = {
                    'hi':       'क्षमा करें, उत्तर तैयार नहीं हो सका। कृपया प्रश्न को थोड़ा बदलकर दोबारा पूछें।',
                    'hinglish': 'Sorry, answer generate nahi ho paya. Please question thoda badal kar dobara poochhein.',
                    'en':       'Sorry, an answer could not be generated. Please try rephrasing your question.',
                }
                yield f"data: {json.dumps({'type':'token','content':_fallbacks.get(_lang, _fallbacks['en'])})}\n\n"

            # Record this turn in conversation memory so the NEXT question can use
            # coreference ("tell me more about it") and remembered details.
            _answer_text = ''.join(state.get('answer_buf', []))
            # Clean ungrounded rule numbers before this text is cached/recorded so
            # non-browser consumers (cache replays, logs, exports) match the
            # client-sanitised UI view. The live stream is cleaned client-side.
            _answer_text = _sanitize_rule_numbers(_answer_text, context_text)
            # Verbatim quote-grounding: when a GFR rule is named/implied, append the
            # exact source line(s) carrying the amounts/percentages, so the shown
            # figures are ground-truth even if the 4B model paraphrased them (e.g.
            # Rule 171 "3-5%"). No-op for non-rule queries.
            try:
                if content_streamed:
                    _gn = rule_grounding_note(effective_query)
                    if _gn and _gn[:40] not in _answer_text:
                        _gblock = f"\n\n📎 As written in the rulebook — {_gn}"
                        yield f"data: {json.dumps({'type':'token','content':_gblock})}\n\n"
                        _answer_text += _gblock
            except Exception:
                pass
            try:
                _summary = _answer_text.strip()[:300]
                CONV_MEMORY.record_turn(session_id, query_text, intent, topic, _summary)
            except Exception:
                pass

            # Cache the answer for near-duplicate future questions (skip personalised /
            # follow-up / refusal answers — those aren't reusable).
            try:
                _is_refusal = any(rl[:25] in _answer_text for rl in REFUSAL_LINES.values())
                # Do NOT cache LOW-confidence answers: the reranker's top score was
                # weak, so the answer is likely grounded in the wrong passage (this is
                # exactly how the Q91 "Rule 192 / Rs 1-10 lakh" wrong answer got frozen
                # and replayed). Only cache medium/high-confidence, non-refusal answers.
                if (content_streamed and not coref_applied
                        and not entities.get('persons') and not _is_refusal
                        and _conf_label != 'low'):
                    ANSWER_CACHE.put(effective_query, _answer_text, source_refs)
            except Exception:
                pass

            # Suggested follow-up questions (clickable chips in the UI).
            try:
                _fu = suggest_followups(intent)
                if _fu and content_streamed:
                    yield f"data: {json.dumps({'type':'followups','items':_fu})}\n\n"
            except Exception:
                pass

            # Analytics event.
            _log_event(ANALYTICS_LOG, {
                'q': query_text, 'intent': intent, 'lang': _lang,
                'confidence': _conf_label, 'cache_hit': False,
                'corrected': bool(corrections),
                'elapsed': round(time.time()-t0, 2),
            })

            elapsed = f"{time.time()-t0:.2f}s"
            # Expose the server-sanitised full answer on the done event so EVERY
            # consumer (API clients, eval harness, exports) gets the same
            # ungrounded-rule-number cleaning the browser applies client-side —
            # not just the raw live token stream.
            yield f"data: {json.dumps({'type':'done','elapsed':elapsed,'sources':source_refs,'answer':_answer_text})}\n\n"

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type':'error','message':str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no',
                 'Access-Control-Allow-Origin': '*'}
    )


@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Record a thumbs up/down on an answer (Tier 2 #8)."""
    data = request.get_json(silent=True) or {}
    rating = str(data.get('rating', '')).lower()
    if rating not in ('up', 'down'):
        return jsonify({'success': False, 'error': 'rating must be up or down'}), 400
    _sources = data.get('sources') or []
    if isinstance(_sources, list):
        _sources = [str(s)[:200] for s in _sources][:8]
    else:
        _sources = []
    _log_event(FEEDBACK_LOG, {
        'rating': rating,
        'query': (data.get('query') or '')[:500],
        'answer': (data.get('answer') or '')[:1000],
        'sources': _sources,          # cited docs, so bad answers can be traced
        'session_id': data.get('session_id', ''),
    })
    return jsonify({'success': True}), 200


@app.route('/api/analytics', methods=['GET'])
def analytics():
    """Aggregate analytics: query counts, intents, languages, cache-hit rate,
    avg latency, and feedback tallies (Tier 3 #12)."""
    stats = {
        'total_queries': 0, 'cache_hits': 0, 'typo_corrected': 0,
        'intents': {}, 'languages': {}, 'confidence': {},
        'avg_elapsed': 0.0, 'feedback': {'up': 0, 'down': 0},
        'top_queries': {},
    }
    elapsed_sum = 0.0
    try:
        with open(ANALYTICS_LOG, encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                stats['total_queries'] += 1
                if e.get('cache_hit'):
                    stats['cache_hits'] += 1
                if e.get('corrected'):
                    stats['typo_corrected'] += 1
                it = e.get('intent', 'UNKNOWN')
                stats['intents'][it] = stats['intents'].get(it, 0) + 1
                lg = e.get('lang', 'unknown')
                stats['languages'][lg] = stats['languages'].get(lg, 0) + 1
                cf = e.get('confidence', 'unknown')
                stats['confidence'][cf] = stats['confidence'].get(cf, 0) + 1
                q = (e.get('q') or '').strip().lower()
                if q:
                    stats['top_queries'][q] = stats['top_queries'].get(q, 0) + 1
                elapsed_sum += float(e.get('elapsed', 0) or 0)
    except FileNotFoundError:
        pass
    if stats['total_queries']:
        stats['avg_elapsed'] = round(elapsed_sum / stats['total_queries'], 2)
    try:
        with open(FEEDBACK_LOG, encoding='utf-8') as f:
            for line in f:
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                r = e.get('rating')
                if r in stats['feedback']:
                    stats['feedback'][r] += 1
    except FileNotFoundError:
        pass
    # Keep only the top 10 queries.
    stats['top_queries'] = dict(sorted(stats['top_queries'].items(),
                                       key=lambda kv: kv[1], reverse=True)[:10])
    return jsonify(stats), 200


def _is_scanned_pdf(pdf_path: Path) -> bool:
    """Return True when a PDF has little or no extractable text (i.e. it's scanned)."""
    try:
        doc = fitz.open(str(pdf_path))
        total_chars = sum(len(page.get_text().strip()) for page in doc)
        doc.close()
        return total_chars < 200  # fewer than 200 chars = scanned
    except Exception:
        return False


def _run_ocr_pipeline(pdf_path: Path, yield_fn) -> Path:
    """Run Stage 1 + Stage 2 OCR on a scanned PDF.

    Returns the path to the structured.md produced by Stage 2, or None on failure.
    Stage 1 takes the PDF as a positional arg and writes to stage1_output/<stem>/.
    Stage 2 takes that directory as a positional arg and writes to stage2_output/<stem>/.
    """
    preproc_dir  = PROJECT_ROOT / '01_preprocessing'
    run1         = preproc_dir / 'run_stage1.py'
    run2         = preproc_dir / 'run_stage2.py'
    stage1_out   = preproc_dir / 'stage1_output' / pdf_path.stem
    stage2_out   = preproc_dir / 'stage2_output' / pdf_path.stem
    structured   = stage2_out / 'structured.md'

    # ── Stage 1: PDF → cleaned images ────────────────────────────────────
    if not run1.exists():
        yield_fn({'type': 'progress', 'message': 'Stage 1 script not found – skipping OCR', 'pct': 20})
        return None

    yield_fn({'type': 'progress', 'message': 'Stage 1: converting PDF to images…', 'pct': 20})
    try:
        r1 = subprocess.run(
            [sys.executable, str(run1), str(pdf_path)],   # positional arg
            capture_output=True, text=True, timeout=600,
            cwd=str(preproc_dir)
        )
        if r1.returncode != 0:
            yield_fn({'type': 'progress',
                      'message': f'Stage 1 warning (exit {r1.returncode}): {r1.stderr[:200]}', 'pct': 25})
    except subprocess.TimeoutExpired:
        yield_fn({'type': 'progress', 'message': 'Stage 1 timed out', 'pct': 25})
        return None
    except Exception as e:
        yield_fn({'type': 'progress', 'message': f'Stage 1 error: {e}', 'pct': 25})
        return None

    if not stage1_out.exists():
        yield_fn({'type': 'progress', 'message': 'Stage 1 output not found – aborting OCR', 'pct': 25})
        return None

    # ── Stage 2: images → OCR text ───────────────────────────────────────
    if not run2.exists():
        yield_fn({'type': 'progress', 'message': 'Stage 2 script not found – skipping OCR', 'pct': 30})
        return None

    yield_fn({'type': 'progress', 'message': 'Stage 2: running Hindi-English OCR…', 'pct': 30})
    try:
        r2 = subprocess.run(
            [sys.executable, str(run2), str(stage1_out)],  # positional arg = stage1 output dir
            capture_output=True, text=True, timeout=1200,
            cwd=str(preproc_dir)
        )
        if r2.returncode != 0:
            yield_fn({'type': 'progress',
                      'message': f'Stage 2 warning (exit {r2.returncode}): {r2.stderr[:200]}', 'pct': 45})
    except subprocess.TimeoutExpired:
        yield_fn({'type': 'progress', 'message': 'Stage 2 timed out', 'pct': 45})
        return None
    except Exception as e:
        yield_fn({'type': 'progress', 'message': f'Stage 2 error: {e}', 'pct': 45})
        return None

    if structured.exists():
        yield_fn({'type': 'progress', 'message': 'OCR complete – structured text extracted', 'pct': 50})
        return structured

    yield_fn({'type': 'progress', 'message': 'Stage 2 finished but structured.md not found', 'pct': 45})
    return None


def _chunk_document(input_path: Path, yield_fn):
    """Run the docling chunker on a PDF/DOCX/MD file, return number of chunks created."""
    chunker_script = PROJECT_ROOT / '03_chunking' / 'docling_chunker.py'
    output_dir     = PROJECT_ROOT / '03_chunking' / 'output'

    yield_fn({'type': 'progress', 'message': 'Chunking document…', 'pct': 55})

    if not chunker_script.exists():
        yield_fn({'type': 'progress', 'message': 'Using fallback chunker…', 'pct': 60})
        return _fallback_chunk(input_path, output_dir, yield_fn)

    try:
        # docling_chunker.py uses --input / --output flags (checked in docling_chunker.py argparse)
        subprocess.run(
            [sys.executable, str(chunker_script),
             '--input', str(input_path),
             '--output', str(output_dir)],
            capture_output=True, text=True, timeout=600
        )
        doc_stem  = input_path.stem
        chunk_dir = output_dir / doc_stem
        if chunk_dir.exists():
            return len(list(chunk_dir.rglob('*_chunk_*.txt')))
        return len(list(output_dir.glob(f'{doc_stem}_chunk_*.txt')))
    except Exception as e:
        yield_fn({'type': 'progress', 'message': f'Chunker error: {e}', 'pct': 65})
        return 0


def _fallback_chunk(input_path: Path, output_dir: Path, yield_fn) -> int:
    """Simple PyMuPDF-based text chunker when docling is unavailable."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        doc_stem = input_path.stem

        if input_path.suffix.lower() == '.pdf':
            doc   = fitz.open(str(input_path))
            pages = [page.get_text() for page in doc]
            doc.close()
            full_text = '\n'.join(pages)
        else:
            full_text = input_path.read_text(encoding='utf-8', errors='replace')

        # Split into ~800-char chunks
        words     = full_text.split()
        chunk_size = 300  # words
        chunks    = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

        doc_out = output_dir / doc_stem
        doc_out.mkdir(exist_ok=True)
        for idx, chunk in enumerate(chunks, 1):
            (doc_out / f'{doc_stem}_chunk_{idx:03d}.txt').write_text(
                f'Source: {input_path.name}\n---\n{chunk}\n', encoding='utf-8'
            )
        return len(chunks)
    except Exception as e:
        yield_fn({'type': 'progress', 'message': f'Fallback chunker error: {e}', 'pct': 70})
        return 0


def _embed_new_chunks(yield_fn):
    """Run the incremental embeddings indexer."""
    embed_script = PROJECT_ROOT / '04_embeddings_and_kg' / 'scripts' / 'embeddings_production.py'
    yield_fn({'type': 'progress', 'message': 'Indexing embeddings…', 'pct': 75})

    if not embed_script.exists():
        yield_fn({'type': 'progress', 'message': 'Embeddings script not found – skipping', 'pct': 90})
        return

    try:
        subprocess.run(
            [sys.executable, str(embed_script)],
            capture_output=True, text=True, timeout=1800,
            cwd=str(embed_script.parent)
        )
    except subprocess.TimeoutExpired:
        yield_fn({'type': 'progress', 'message': 'Embedding timed out – may still be running', 'pct': 90})
    except Exception as e:
        yield_fn({'type': 'progress', 'message': f'Embedding error: {e}', 'pct': 90})


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Accept a PDF/DOCX upload, run OCR if scanned, chunk, embed, stream progress via SSE."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400

    uploaded = request.files['file']
    if not uploaded.filename:
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    filename = secure_filename(uploaded.filename)
    ext      = Path(filename).suffix.lower()
    if ext not in {'.pdf', '.docx'}:
        return jsonify({'success': False, 'error': 'Only PDF and DOCX files are supported'}), 400

    upload_dir = PROJECT_ROOT / '01_preprocessing' / 'input_pdfs'
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / filename
    uploaded.save(str(save_path))

    def generate():
        events = []
        lock   = threading.Lock()

        def emit(evt):
            with lock:
                events.append(json.dumps(evt))

        try:
            emit({'type': 'progress', 'message': f'Received {filename}', 'pct': 5})

            # Detect scanned PDF
            chunk_input = save_path   # default: chunk the uploaded file directly
            if ext == '.pdf':
                emit({'type': 'progress', 'message': 'Analysing PDF…', 'pct': 10})
                is_scanned = _is_scanned_pdf(save_path)
                pdf_type   = 'scanned (Hindi-English OCR required)' if is_scanned else 'digital (text-based)'
                emit({'type': 'progress', 'message': f'Detected: {pdf_type}', 'pct': 15})

                if is_scanned:
                    # Run full Stage 1 + Stage 2 OCR pipeline; returns path to structured.md
                    ocr_output = _run_ocr_pipeline(save_path, emit)
                    if ocr_output and ocr_output.exists():
                        chunk_input = ocr_output   # chunk the OCR markdown, not the raw PDF
                    else:
                        emit({'type': 'progress',
                              'message': 'OCR pipeline did not produce output – chunking raw PDF with built-in OCR',
                              'pct': 50})

            # Chunk the document (PDF/DOCX/MD)
            chunks = _chunk_document(chunk_input, emit)
            emit({'type': 'progress', 'message': f'Created {chunks} chunk(s)', 'pct': 65})

            if chunks > 0:
                # Index new chunks into Qdrant
                _embed_new_chunks(emit)
                emit({'type': 'done', 'message': 'Processing complete', 'chunks': chunks, 'pct': 100})
            else:
                emit({'type': 'error', 'message': 'No chunks were created – check if docling is installed'})

        except Exception as e:
            import traceback
            traceback.print_exc()
            emit({'type': 'error', 'message': str(e)})

        for evt in events:
            yield f'data: {evt}\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no',
                 'Access-Control-Allow-Origin': '*'}
    )


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 CHiPS-RAG Pipeline (Internal Backend)")
    print("="*70)
    print(f"\nRAG Pipeline Status: {'✅ Available' if RAG_AVAILABLE else '❌ Unavailable'}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print("\nℹ️  This Flask server is INTERNAL ONLY.")
    print("   Authentication is handled by Express.js at :3000")
    
    flask_host = '0.0.0.0'
    flask_port = 5000
    flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Production: serve via waitress (a real WSGI server) instead of Flask's
    # single-purpose dev server. Opt-in so the default keeps the dev server,
    # whose SSE streaming we know is smooth; flip USE_WAITRESS=true (or set
    # ENVIRONMENT=production) for deployment. Falls back to the dev server if
    # waitress is missing.
    use_waitress = (os.getenv('USE_WAITRESS', '').lower() == 'true'
                    or os.getenv('ENVIRONMENT', '').lower() == 'production')

    if use_waitress and not flask_debug:
        try:
            from waitress import serve
            threads = int(os.getenv('WAITRESS_THREADS', '8'))
            print(f"\nStarting Waitress (production WSGI) on http://{flask_host}:{flask_port} "
                  f"({threads} threads)")
            print("Press Ctrl+C to stop the server\n")
            # channel_timeout generous so long LLM streams aren't cut off.
            serve(app, host=flask_host, port=flask_port, threads=threads,
                  channel_timeout=int(os.getenv('WAITRESS_CHANNEL_TIMEOUT', '600')))
        except ImportError:
            print("\n⚠️  waitress not installed — falling back to Flask dev server.")
            print("Press Ctrl+C to stop the server\n")
            app.run(debug=False, host=flask_host, port=flask_port, use_reloader=False)
    else:
        print(f"\nStarting Flask dev server on http://{flask_host}:{flask_port} (debug: {flask_debug})")
        print("Press Ctrl+C to stop the server\n")
        app.run(debug=flask_debug, host=flask_host, port=flask_port, use_reloader=False)
