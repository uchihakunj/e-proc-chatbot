"""
nlp_features.py — Lightweight NLP layer for the CHiPS e-Procurement chatbot.

Adds the four NLP capabilities the pipeline previously lacked, all
dependency-free (pure regex + stdlib) so they run offline on the VM with no
model downloads:

  1. Named Entity Recognition (NER)  — extract person / company / date /
     amount / percent / PAN / GSTIN / email / phone from a query.
  2. Intent classification           — a formal procurement intent taxonomy
     (VENDOR_REGISTRATION, EMD_PAYMENT, EMD_REFUND, DSC, TENDER_SEARCH, ...).
  3. Conversation memory + slots     — per-session multi-turn state so the bot
     remembers names/companies and the last topic across questions.
  4. Coreference resolution          — rewrite follow-ups like "tell me more
     about it" / "iske baare mein aur batao" into a self-contained query using
     the previous topic.

Design notes
------------
* Everything is regex / keyword based to match the rest of the pipeline and to
  avoid heavy dependencies (spaCy/transformers) that complicate the offline VM.
* The functions are pure where possible; ConversationMemory holds the only
  mutable state and is thread-safe (Flask may serve requests on threads).
"""

from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ════════════════════════════════════════════════════════════════════════════
# 1. NAMED ENTITY RECOGNITION (NER)
# ════════════════════════════════════════════════════════════════════════════

# Words that should never be captured as a person's name (they follow the same
# trigger patterns but are not names).
_NAME_STOPWORDS = {
    'a', 'an', 'the', 'is', 'am', 'are', 'was', 'looking', 'trying', 'here',
    'new', 'vendor', 'bidder', 'supplier', 'contractor', 'from', 'going',
    'interested', 'not', 'sure', 'asking', 'wondering', 'unable', 'facing',
    'registered', 'registering', 'ready', 'planning', 'hoon', 'hu', 'hun',
}

# PERSON name triggers. Capture group 1 = candidate name (1-3 tokens).
_NAME_WORD = r"[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2}"
_DEVA_WORD = r"[ऀ-ॿ]+(?:\s+[ऀ-ॿ]+){0,2}"
_PERSON_PATTERNS = [
    re.compile(r"\bmy\s+name\s+is\s+(" + _NAME_WORD + r")", re.I),
    re.compile(r"\bi\s+am\s+(" + _NAME_WORD + r")\b"),
    re.compile(r"\bi'?m\s+(" + _NAME_WORD + r")\b"),
    re.compile(r"\bthis\s+is\s+(" + _NAME_WORD + r")\b"),
    re.compile(r"\bname\s+(?:is\s+)?(" + _NAME_WORD + r")\b"),
    # Hinglish: "main ramesh hoon", "mera naam ramesh hai", "naam ramesh"
    re.compile(r"\bmera\s+naam\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})\s+(?:hai|h)\b", re.I),
    re.compile(r"\bmain\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})\s+(?:hoon|hu|hun)\b", re.I),
    re.compile(r"\bnaam\s+([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})\b", re.I),
    # Hindi (Devanagari): "मेरा नाम रमेश है", "मैं रमेश हूँ"
    re.compile(r"मेरा\s+नाम\s+(" + _DEVA_WORD + r")"),
    re.compile(r"मैं\s+(" + _DEVA_WORD + r")\s+(?:हूँ|हूं|हु)"),
]

# COMPANY: a name immediately followed by a corporate suffix, or after a trigger.
_CORP_SUFFIX = (r"(?:Pvt\.?\s*Ltd\.?|Private\s+Limited|Limited|Ltd\.?|LLP|"
                r"Inc\.?|Corp\.?|Corporation|Enterprises?|Industries|"
                r"Technologies|Solutions|Infotech|Constructions?|Traders?|"
                r"&\s*Co\.?)")
_COMPANY_PATTERNS = [
    # "TechBuild Pvt Ltd", "Acme Solutions Pvt. Ltd."
    re.compile(r"\b([A-Z][\w&.\-]*(?:\s+[A-Z][\w&.\-]*){0,4}\s+" + _CORP_SUFFIX + r")"),
    # "company is X", "company name is X", "firm X", "my company X"
    re.compile(r"\b(?:company|firm|organisation|organization)\s+(?:name\s+)?"
               r"(?:is\s+)?([A-Z][\w&.\-]*(?:\s+[A-Z][\w&.\-]*){0,4})"),
]

# DATE: a wide range of common Indian date formats + relative dates.
_MONTHS = (r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
           r"[a-z]*")
_DATE_PATTERNS = [
    re.compile(r"\b\d{1,2}(?:st|nd|rd|th)?\s+" + _MONTHS + r"\.?(?:\s+\d{2,4})?", re.I),
    re.compile(r"\b" + _MONTHS + r"\.?\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{2,4})?", re.I),
    re.compile(r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
]
_RELATIVE_DATES = re.compile(r"\b(today|tomorrow|yesterday|aaj|kal|parso)\b", re.I)

# AMOUNT: rupee values, including lakh/crore shorthand.
_AMOUNT_PATTERNS = [
    re.compile(r"(?:₹|rs\.?|inr|rupees?)\s*[\d,]+(?:\.\d+)?\s*"
               r"(?:lakh?s?|lac?s?|crore?s?|cr|k|thousand)?", re.I),
    re.compile(r"\b[\d,]+(?:\.\d+)?\s*(?:lakh?s?|lac?s?|crore?s?|cr)\b", re.I),
    re.compile(r"\b[\d,]+(?:\.\d+)?\s*(?:rupees?|rs\.?|inr)\b", re.I),
]
# Note: '%' is a non-word char, so a trailing \b never matches after it — match
# the '%' form separately from the word forms (percent/pct/...).
_PERCENT_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*%|\b\d+(?:\.\d+)?\s*(?:percent|pct|fisdi|fisadi)\b", re.I)

# Structured IDs.
_PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
_GSTIN_PATTERN = re.compile(r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]\b")
_EMAIL_PATTERN = re.compile(r"\b[\w.\-]+@[\w.\-]+\.\w+\b")
_PHONE_PATTERN = re.compile(r"\b(?:\+?91[\-\s]?)?[6-9]\d{9}\b")


def _norm_amount(raw: str) -> Optional[float]:
    """Best-effort numeric value of an amount string (handles lakh/crore/k)."""
    s = raw.lower()
    num_match = re.search(r"[\d,]+(?:\.\d+)?", s)
    if not num_match:
        return None
    try:
        val = float(num_match.group(0).replace(",", ""))
    except ValueError:
        return None
    if re.search(r"crore|cr\b", s):
        val *= 10_000_000
    elif re.search(r"lakh|lac", s):
        val *= 100_000
    elif re.search(r"\bk\b|thousand", s):
        val *= 1_000
    return val


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen, out = set(), []
    for it in items:
        key = it.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(it.strip())
    return out


def extract_entities(query: str) -> Dict[str, object]:
    """Extract named entities from a query.

    Returns a dict with keys: persons, companies, dates, amounts, percents,
    pan, gstin, emails, phones. Each value is a list (amounts also carries a
    parallel `amounts_value` list of normalised floats). Empty lists when none
    found, so callers can safely iterate.
    """
    q = query or ""
    persons: List[str] = []
    for pat in _PERSON_PATTERNS:
        for m in pat.finditer(q):
            cand = m.group(1).strip()
            # Drop candidates that are only stopwords (e.g. "I am looking").
            toks = [t for t in cand.split() if t.lower() not in _NAME_STOPWORDS]
            if toks:
                persons.append(" ".join(toks))

    companies: List[str] = []
    for pat in _COMPANY_PATTERNS:
        for m in pat.finditer(q):
            companies.append(m.group(1).strip())

    dates: List[str] = []
    for pat in _DATE_PATTERNS:
        dates.extend(m.group(0).strip() for m in pat.finditer(q))
    dates.extend(m.group(0).strip() for m in _RELATIVE_DATES.finditer(q))
    dates = _dedupe_keep_order(dates)
    # Drop partial matches: "June 20" extracted from "15 June 2026" by the
    # month-first pattern is a substring of the full date — keep only the longest.
    dates = [d for d in dates
             if not any(d != other and d.lower() in other.lower() for other in dates)]

    amounts: List[str] = []
    for pat in _AMOUNT_PATTERNS:
        amounts.extend(m.group(0).strip() for m in pat.finditer(q))
    amounts = _dedupe_keep_order(amounts)

    result = {
        "persons":   _dedupe_keep_order(persons),
        "companies": _dedupe_keep_order(companies),
        "dates":     _dedupe_keep_order(dates),
        "amounts":   amounts,
        "amounts_value": [v for v in (_norm_amount(a) for a in amounts) if v is not None],
        "percents":  _dedupe_keep_order(m.group(0).strip() for m in _PERCENT_PATTERN.finditer(q)),
        "pan":       _dedupe_keep_order(_PAN_PATTERN.findall(q)),
        "gstin":     _dedupe_keep_order(_GSTIN_PATTERN.findall(q)),
        "emails":    _dedupe_keep_order(_EMAIL_PATTERN.findall(q)),
        "phones":    _dedupe_keep_order(_PHONE_PATTERN.findall(q)),
    }
    return result


def entities_summary(entities: Dict[str, object]) -> str:
    """Human-readable one-line summary of extracted entities (for logs/prompt)."""
    parts = []
    label = {
        "persons": "Person", "companies": "Company", "dates": "Date",
        "amounts": "Amount", "percents": "Percent", "pan": "PAN",
        "gstin": "GSTIN", "emails": "Email", "phones": "Phone",
    }
    for key, name in label.items():
        vals = entities.get(key) or []
        if vals:
            parts.append(f"{name}: {', '.join(map(str, vals))}")
    return " | ".join(parts)


# ════════════════════════════════════════════════════════════════════════════
# 2. INTENT CLASSIFICATION
# ════════════════════════════════════════════════════════════════════════════

# Ordered intent taxonomy. Each intent maps to keyword/phrase signals (English +
# Hinglish + Hindi). More specific intents are listed first so they win ties.
INTENT_TAXONOMY: List[Tuple[str, List[str]]] = [
    ("EMD_REFUND", [
        "emd refund", "emd wapas", "emd return", "refund emd", "refund of emd",
        "emd vapas", "earnest money refund", "धरोहर वापस", "emd kab milega",
        "emd kab wapas", "refund", "wapas", "वापसी", "रिफंड",
    ]),
    ("EMD_PAYMENT", [
        "emd pay", "pay emd", "emd payment", "emd challan", "challan", "emd bharna",
        "emd bhren", "emd jama", "deposit emd", "emd kaise bhar", "emd deposit",
        "धरोहर जमा", "emd ka payment",
    ]),
    ("VENDOR_REGISTRATION", [
        "vendor registration", "register as vendor", "supplier registration",
        "new user registration", "vendor register", "registration kaise",
        "register karna", "panjikaran", "panjiyan", "kaise register",
        "how to register", "sign up", "signup", "enroll", "पंजीकरण", "पंजीयन",
    ]),
    ("DSC", [
        "dsc", "digital signature", "signature certificate", "dsc token",
        "dsc expire", "class 3 dsc", "class 2 dsc", "डिजिटल हस्ताक्षर", "token",
        "डीएससी",  # Devanagari "DSC" — Hindi queries often omit the Latin acronym
    ]),
    ("BID_SUBMISSION", [
        "submit bid", "bid submission", "upload bid", "submit my bid",
        "bid kaise", "boli jama", "technical bid", "price bid", "financial bid",
        "commercial bid", "modify bid", "resubmit", "बोली जमा", "bid submit",
        "participate in", "participate", "participation", "how to bid",
        "place a bid", "apply for tender", "bid for",
    ]),
    ("TENDER_SEARCH", [
        "search tender", "find tender", "active tender", "available tender",
        "tender dhundo", "tender search", "nit number", "search nit",
        "list of tender", "live tender", "निविदा खोज",
        # NOTE: "open tender" removed — it names a procurement METHOD
        # (advertised/open tender enquiry) far more often than a search action,
        # so it mis-routed GFR threshold questions into TENDER_SEARCH.
    ]),
    ("AUCTION", [
        "auction", "reverse auction", "nilami", "e-auction", "bidding auction",
        "नीलामी",
    ]),
    ("DOCUMENT_REQUIREMENTS", [
        "documents needed", "documents required", "required documents",
        "kaunse documents", "kya documents", "list of documents", "dastavej",
        "dastavez", "papers needed", "दस्तावेज", "what documents",
    ]),
    ("PORTAL_USAGE", [
        "login", "log in", "password", "reset password", "session expired",
        "browser", "edge browser", "portal not", "cannot login", "can't login",
        "activate", "otp", "captcha", "लॉगिन", "पासवर्ड",
    ]),
    ("RULES_GFR", [
        "gfr", "general financial rule", "store purchase rule", "procurement rule",
        "purchase committee", "single source", "limited tender enquiry",
        "store purchase", "niyam", "नियम", "rule", "rules", "it act",
        "information technology act",
    ]),
    ("EMD_GENERAL", [
        "emd", "earnest money", "bid security", "dharohar", "bayana", "धरोहर",
        "बयाना", "जमानत",
    ]),
]


def classify_intent(query: str) -> Tuple[str, float]:
    """Classify a query into the intent taxonomy.

    Returns (intent_label, confidence 0-1). Confidence is a simple normalised
    keyword-hit score. Returns ("UNKNOWN", 0.0) when nothing matches — callers
    can still fall through to normal retrieval, so an UNKNOWN intent is not a
    refusal, just "no specific intent detected".
    """
    if not query:
        return ("UNKNOWN", 0.0)
    q = " " + query.lower() + " "
    best_intent, best_score = "UNKNOWN", 0
    for intent, signals in INTENT_TAXONOMY:
        hits = sum(1 for s in signals if s in q)
        if hits > best_score:
            best_intent, best_score = intent, hits
    if best_score == 0:
        return ("UNKNOWN", 0.0)
    # Confidence: saturate quickly — 1 hit = 0.6, 2 = 0.8, 3+ ≈ 1.0.
    confidence = min(1.0, 0.4 + 0.2 * best_score)
    return (best_intent, round(confidence, 2))


# Map an intent to a short human topic phrase, used for coreference rewriting
# and as the "current topic" stored in memory.
INTENT_TOPIC_PHRASE = {
    "EMD_REFUND":            "EMD refund",
    "EMD_PAYMENT":           "EMD payment",
    "EMD_GENERAL":           "EMD",
    "VENDOR_REGISTRATION":   "vendor registration",
    "DSC":                   "Digital Signature Certificate (DSC)",
    "BID_SUBMISSION":        "bid submission",
    "TENDER_SEARCH":         "tender search",
    "AUCTION":               "auction process",
    "DOCUMENT_REQUIREMENTS": "required documents",
    "PORTAL_USAGE":          "portal usage",
    "RULES_GFR":             "procurement rules (GFR)",
}


# ════════════════════════════════════════════════════════════════════════════
# 3. CONVERSATION MEMORY + SLOT FILLING
# ════════════════════════════════════════════════════════════════════════════

# Slots that persist across turns (sticky) until the user overrides them.
_STICKY_SLOTS = ("person", "company", "pan", "gstin", "email", "phone")


@dataclass
class _Turn:
    query: str
    intent: str
    topic: str
    answer_summary: str
    ts: float = field(default_factory=time.time)


@dataclass
class _Session:
    turns: List[_Turn] = field(default_factory=list)
    slots: Dict[str, str] = field(default_factory=dict)
    last_topic: str = ""
    last_intent: str = ""
    updated: float = field(default_factory=time.time)
    # Guided task-flow (wizard) state: name of active flow, current step index,
    # and the data collected so far. flow_name == "" means no flow is active.
    flow_name: str = ""
    flow_step: int = 0
    flow_data: Dict[str, str] = field(default_factory=dict)


class ConversationMemory:
    """Thread-safe, in-memory, per-session conversation store.

    Holds the last `max_turns` turns and a sticky slot dict (name, company,
    PAN, ...) per session id. Sessions expire after `ttl_seconds` of inactivity
    so memory does not grow unbounded on a long-running server.
    """

    def __init__(self, max_turns: int = 6, ttl_seconds: int = 3600):
        self.max_turns = max_turns
        self.ttl = ttl_seconds
        self._store: Dict[str, _Session] = {}
        self._lock = threading.Lock()

    def _evict_expired(self, now: float) -> None:
        stale = [sid for sid, s in self._store.items() if now - s.updated > self.ttl]
        for sid in stale:
            self._store.pop(sid, None)

    def get_session(self, session_id: str) -> _Session:
        now = time.time()
        with self._lock:
            self._evict_expired(now)
            sess = self._store.get(session_id)
            if sess is None:
                sess = _Session()
                self._store[session_id] = sess
            return sess

    def update_slots(self, session_id: str, entities: Dict[str, object]) -> Dict[str, str]:
        """Merge freshly extracted entities into the session's sticky slots."""
        mapping = {
            "person": "persons", "company": "companies", "pan": "pan",
            "gstin": "gstin", "email": "emails", "phone": "phones",
        }
        with self._lock:
            sess = self._store.setdefault(session_id, _Session())
            for slot, ent_key in mapping.items():
                vals = entities.get(ent_key) or []
                if vals:
                    sess.slots[slot] = str(vals[0])
            sess.updated = time.time()
            return dict(sess.slots)

    def record_turn(self, session_id: str, query: str, intent: str,
                    topic: str, answer_summary: str) -> None:
        with self._lock:
            sess = self._store.setdefault(session_id, _Session())
            sess.turns.append(_Turn(query=query, intent=intent, topic=topic,
                                    answer_summary=answer_summary))
            if len(sess.turns) > self.max_turns:
                sess.turns = sess.turns[-self.max_turns:]
            if topic:
                sess.last_topic = topic
            if intent and intent != "UNKNOWN":
                sess.last_intent = intent
            sess.updated = time.time()

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)

    # ── Guided task-flow (wizard) ───────────────────────────────────────────
    def flow_active(self, session_id: str) -> str:
        """Return the active flow name for the session, or '' if none."""
        return self.get_session(session_id).flow_name

    def start_flow(self, session_id: str, flow_name: str) -> str:
        """Begin a guided flow; return the first step's prompt."""
        flow = FLOWS.get(flow_name)
        if not flow:
            return ""
        with self._lock:
            sess = self._store.setdefault(session_id, _Session())
            sess.flow_name = flow_name
            sess.flow_step = 0
            sess.flow_data = {}
            sess.updated = time.time()
        return flow["steps"][0][1]

    def cancel_flow(self, session_id: str) -> None:
        with self._lock:
            sess = self._store.get(session_id)
            if sess:
                sess.flow_name = ""
                sess.flow_step = 0
                sess.flow_data = {}

    def advance_flow(self, session_id: str, user_answer: str):
        """Record the user's answer to the current step and move to the next.

        Returns a dict: {prompt, done, summary, data}. When done is True the flow
        is complete and `summary` holds a confirmation message."""
        sess = self.get_session(session_id)
        flow = FLOWS.get(sess.flow_name)
        if not flow:
            return {"prompt": "", "done": True, "summary": "", "data": {}}
        steps = flow["steps"]
        with self._lock:
            # Store the answer for the current step's slot.
            if 0 <= sess.flow_step < len(steps):
                slot = steps[sess.flow_step][0]
                sess.flow_data[slot] = user_answer.strip()
            sess.flow_step += 1
            sess.updated = time.time()
            if sess.flow_step < len(steps):
                prompt = steps[sess.flow_step][1]
                return {"prompt": prompt, "done": False, "summary": "",
                        "data": dict(sess.flow_data)}
            # Flow complete — build summary and clear flow state.
            data = dict(sess.flow_data)
            title = flow["title"]
            sess.flow_name = ""
            sess.flow_step = 0
            sess.flow_data = {}
        lines = [f"✅ {title} details collected:"]
        label = {"person": "Name", "company": "Company", "pan": "PAN",
                 "email": "Email"}
        for slot, val in data.items():
            lines.append(f"- {label.get(slot, slot.title())}: {val}")
        lines.append("\nNext, submit these on the e-Procurement portal under "
                     "\"New Supplier Registration\" and upload your DSC. "
                     "Ask me \"what documents are required for vendor registration\" "
                     "for the full checklist.")
        return {"prompt": "", "done": True, "summary": "\n".join(lines),
                "data": data}

    def running_summary(self, session_id: str) -> str:
        """One-line summary of older turns (for long-chat context retention)."""
        return summarize_turns(self.get_session(session_id).turns)

    def memory_block(self, session_id: str, max_chars: int = 600) -> str:
        """A compact context block (previous turn + known details) to prepend to
        the LLM prompt so follow-ups and personalisation work. Empty string when
        there is nothing useful yet. Includes sticky slots AND dates/amounts from
        the last query (time-sensitive info)."""
        sess = self.get_session(session_id)
        lines: List[str] = []
        if sess.slots:
            known = []
            label = {"person": "Name", "company": "Company", "pan": "PAN",
                     "gstin": "GSTIN", "email": "Email", "phone": "Phone"}
            for slot, name in label.items():
                if sess.slots.get(slot):
                    known.append(f"{name}: {sess.slots[slot]}")
            if known:
                lines.append("Known user details - " + "; ".join(known))
        if sess.turns:
            last = sess.turns[-1]
            summ = (last.answer_summary or "").strip().replace("\n", " ")
            if summ:
                lines.append(f"Previous topic: {last.topic}")
                lines.append(f"Previous question: {last.query}")
                lines.append(f"Previous answer (summary): {summ[:300]}")
        block = "\n".join(lines)
        return block[:max_chars]


# ════════════════════════════════════════════════════════════════════════════
# 4. COREFERENCE RESOLUTION
# ════════════════════════════════════════════════════════════════════════════

# Pronouns / references that signal the query depends on the previous topic.
_COREF_PRONOUNS = (
    r"\bit\b", r"\bits\b", r"\bthat\b", r"\bthis\b", r"\bthose\b", r"\bthem\b",
    r"\bthe same\b", r"\babove\b",
    # Hinglish / Hindi
    r"\buska\b", r"\buske\b", r"\busko\b", r"\biska\b", r"\biske\b", r"\bisko\b",
    r"\bwo\b", r"\bwoh\b", r"\bye\b", r"\byeh\b", r"\bwahi\b", r"\byahi\b",
    r"उसका", r"उसके", r"उसको", r"इसका", r"इसके", r"इसको", r"वही", r"यही",
)
_COREF_RE = re.compile("|".join(_COREF_PRONOUNS), re.I)

# Follow-up markers: short queries that elaborate on the previous topic even
# without an explicit pronoun ("tell me more", "aur batao", "explain", "why").
_FOLLOWUP_MARKERS = (
    "more", "explain", "elaborate", "details", "detail", "continue", "go on",
    "why", "how", "what about", "and", "also", "aur batao", "aur bataye",
    "vistar", "detail me", "kyun", "kyu", "kaise", "iske baare", "uske baare",
    "और बताओ", "विस्तार", "क्यों", "कैसे",
)

# A query is only treated as a follow-up if it is short (few words) — long
# queries are self-contained and must not be rewritten.
_COREF_MAX_WORDS = 7


def needs_coreference(query: str) -> bool:
    """True if the query looks like a context-dependent follow-up."""
    if not query:
        return False
    q = query.lower().strip()
    word_count = len(q.split())
    if word_count > _COREF_MAX_WORDS:
        return False
    if _COREF_RE.search(query):
        return True
    return any(m in q for m in _FOLLOWUP_MARKERS)


def resolve_coreference(query: str, last_topic: str) -> Tuple[str, bool]:
    """Rewrite a follow-up query into a self-contained one using `last_topic`.

    Returns (resolved_query, was_resolved). If the query is not a follow-up, or
    there is no remembered topic, the original query is returned unchanged.
    """
    if not query or not last_topic:
        return (query, False)
    if not needs_coreference(query):
        return (query, False)

    # Replace a standalone pronoun with the topic, else append the topic as
    # context so retrieval has the missing subject.
    if _COREF_RE.search(query):
        resolved = _COREF_RE.sub(last_topic, query, count=1)
    else:
        resolved = f"{query.rstrip(' ?.!')} (regarding {last_topic})"
    return (resolved, True)


# A pure language-switch follow-up ("hindi me batao", "in english", "iska hindi
# me bolo") carries NO new subject — it just asks to restate the PREVIOUS answer
# in another language. Such a query must reuse the previous question's content,
# otherwise retrieval matches on the language word alone and fetches junk.
_LANG_NAMES = (
    "hindi", "english", "hinglish", "angrezi", "angreji",
    "हिंदी", "हिन्दी", "अंग्रेजी", "अंग्रेज़ी", "हिंग्लिश", "इंग्लिश",
)
# Filler that may accompany a language directive without adding a real subject.
_LANG_FILLER = frozenset((
    "in", "into", "to", "me", "mein", "m", "reply", "answer", "respond", "response",
    "explain", "tell", "write", "give", "say", "it", "this", "that", "same", "the",
    "please", "plz", "kindly", "translate", "convert", "batao", "bataye", "bata",
    "bataiye", "bataen", "bolo", "bol", "boliye", "samjhao", "samjha", "samjhaiye",
    "kar", "karo", "kardo", "krke", "krdo", "de", "do", "dijiye", "mujhe", "zara",
    "thoda", "ise", "isko", "iska", "iske", "ise", "kripya", "again", "dobara",
    "phir", "wapas", "ka", "ki", "ke", "and", "ans", "answer",
    "को", "में", "बताओ", "बताइए", "बता", "समझाओ", "समझाइए", "अनुवाद", "करो",
    "इसे", "इसका", "इसको", "फिर", "दोबारा", "कृपया", "बोलो", "मुझे", "जरा",
))


def is_language_switch_only(query: str) -> bool:
    """True if the query only asks to restate the prior answer in another
    language (no new subject), e.g. "hindi me batao", "in english", "iska
    hinglish me bolo". Such follow-ups must reuse the previous question."""
    if not query:
        return False
    q = query.lower().strip()
    if not any(name in q for name in _LANG_NAMES):
        return False
    toks = re.findall(r"[a-zऀ-ॿ]+", q)
    if not toks:
        return False
    residual = [t for t in toks
                if t not in _LANG_FILLER and t not in _LANG_NAMES]
    return len(residual) == 0


# ════════════════════════════════════════════════════════════════════════════
# 5. POST-PROCESSING: DEADLINE URGENCY INJECTION
# ════════════════════════════════════════════════════════════════════════════

# Parse dates in the answer and inject urgency markers if missing.
_DATE_PARSE_PATTERNS = [
    re.compile(r"(\d{1,2})\s+(" + _MONTHS + r")(?:\s+(\d{4}))?", re.I),
]

def _parse_date_str(date_str: str) -> Optional[Tuple[int, int, int]]:
    """Parse a date string and return (year, month, day) or None if unparseable.
    Falls back to current year if year is missing. Very permissive."""
    try:
        date_str = date_str.strip()
        for pat in _DATE_PARSE_PATTERNS:
            m = pat.search(date_str)
            if m:
                day = int(m.group(1))
                month_str = m.group(2).lower()
                year_str = m.group(3) or "2026"
                months = {
                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                    'july': 7, 'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9,
                    'oct': 10, 'nov': 11, 'dec': 12,
                }
                for mname, mnum in months.items():
                    if mname in month_str:
                        month = mnum
                        year = int(year_str)
                        return (year, month, day)
    except Exception:
        pass
    return None


def _days_until(year: int, month: int, day: int) -> int:
    """Days from today (2026-06-20) until the given date. Negative = past."""
    from datetime import date
    today = date(2026, 6, 20)
    try:
        target = date(year, month, day)
        delta = (target - today).days
        return delta
    except ValueError:
        return 0


def inject_deadline_urgency(answer: str, extracted_dates: List[str]) -> str:
    """Post-process the LLM answer to inject deadline urgency markers if dates
    are mentioned but the LLM didn't highlight them.

    Checks if the answer already has a ⏰ marker; if not and dates were extracted,
    adds one near the start of the answer."""
    if not extracted_dates or "⏰" in answer:
        return answer

    # Try to parse extracted dates and find the most urgent one.
    deadlines = []
    for date_str in extracted_dates:
        parsed = _parse_date_str(date_str)
        if parsed:
            days = _days_until(*parsed)
            deadlines.append((days, date_str))

    if not deadlines:
        return answer

    # Pick the most urgent deadline (soonest, whether future or past).
    deadlines.sort(key=lambda x: abs(x[0]))
    days_left, date_str = deadlines[0]

    # Build the urgency marker.
    if days_left < 0:
        urgency = f"⏰ OVERDUE (was {abs(days_left)} day{'s' if abs(days_left) != 1 else ''} ago)"
    elif days_left == 0:
        urgency = "⏰ DEADLINE IS TODAY"
    elif days_left == 1:
        urgency = "⏰ Deadline is TOMORROW"
    else:
        urgency = f"⏰ Deadline is in {days_left} days ({date_str})"

    # Inject before the first section (💡 Answer, etc.).
    answer_upper = answer.upper()
    for heading in ("💡", "📋", "📘", "ANSWER", "PROCESS", "SOURCE"):
        idx = answer_upper.find(heading)
        if idx != -1:
            return urgency + "\n\n" + answer

    # No section found; prepend to the start.
    return urgency + "\n\n" + answer


# ════════════════════════════════════════════════════════════════════════════
# 6. TYPO CORRECTION / QUERY NORMALIZATION  (Tier 1 #1)
# ════════════════════════════════════════════════════════════════════════════
import difflib

# Explicit high-frequency misspellings -> canonical form. These are the ones a
# fuzzy matcher is least reliable on (Hinglish phonetic spellings especially).
_TYPO_MAP = {
    "tendor": "tender", "tenderr": "tender", "tander": "tender",
    "paticipate": "participate", "particippate": "participate",
    "kerna": "karna", "krna": "karna", "krne": "karne",
    "bhren": "bharein", "bhrna": "bharna",
    "regsiter": "register", "registor": "register", "registeration": "registration",
    "regstration": "registration", "vender": "vendor", "vendoor": "vendor",
    "biding": "bidding", "submision": "submission", "submisson": "submission",
    "paymnet": "payment", "payement": "payment", "documnet": "document",
    "documment": "document", "certificat": "certificate", "certifcate": "certificate",
    "ernest": "earnest", "earnst": "earnest", "gurantee": "guarantee",
    "guaranty": "guarantee", "auciton": "auction", "auctoin": "auction",
    "proccess": "process", "proces": "process", "prosess": "process",
    "eligiblity": "eligibility", "elgibility": "eligibility",
}

# Canonical procurement vocabulary for fuzzy correction (close-match fallback).
_VOCAB = sorted({
    "tender", "bid", "bidding", "bidder", "emd", "earnest", "money", "deposit",
    "vendor", "supplier", "contractor", "registration", "register", "auction",
    "corrigendum", "amendment", "procurement", "gfr", "store", "purchase",
    "performance", "security", "bank", "guarantee", "portal", "payment",
    "challan", "refund", "document", "documents", "certificate", "signature",
    "digital", "submission", "submit", "technical", "financial", "commercial",
    "price", "eligibility", "quotation", "participate", "participation",
    "process", "deadline", "manual", "guidelines", "blacklist", "penalty",
})

# Common words that look short but must never be "corrected".
_SAFE_WORDS = {
    "the", "and", "for", "you", "are", "how", "what", "when", "where", "can",
    "will", "with", "this", "that", "from", "have", "need", "want", "does",
    "kya", "hai", "kaise", "main", "mujhe", "aap", "tum", "karna", "karne",
    "name", "pay", "paid", "date", "days", "year", "much", "many", "form",
}


def correct_typos(query: str):
    """Return (corrected_query, corrections) where corrections is a list of
    (original, fixed) pairs. Conservative: only fixes known typos and very-close
    fuzzy matches so a valid query is never mangled."""
    if not query:
        return (query, [])
    corrections = []
    out_tokens = []
    for raw in query.split():
        m = re.match(r"^(\W*)(.*?)(\W*)$", raw, re.S)
        pre, core, post = (m.group(1), m.group(2), m.group(3)) if m else ("", raw, "")
        low = core.lower()
        fixed = None
        if low in _TYPO_MAP:
            fixed = _TYPO_MAP[low]
        elif (core.isascii() and core.isalpha() and len(core) >= 5
              and low not in _SAFE_WORDS and low not in _VOCAB):
            match = difflib.get_close_matches(low, _VOCAB, n=1, cutoff=0.84)
            if match:
                fixed = match[0]
        if fixed and fixed != low:
            if core[:1].isupper():
                fixed = fixed.capitalize()
            corrections.append((core, fixed))
            out_tokens.append(pre + fixed + post)
        else:
            out_tokens.append(raw)
    return (" ".join(out_tokens), corrections)


# ════════════════════════════════════════════════════════════════════════════
# 7. CLARIFICATION / SLOT-GAP DETECTION  (Tier 1 #2)
# ════════════════════════════════════════════════════════════════════════════

def needs_clarification(query: str, intent: str, entities: dict):
    """If a query is missing a slot required to answer well, return a clarifying
    question (str), else None. Deliberately narrow so the bot only asks back when
    it genuinely cannot answer precisely."""
    if not query:
        return None
    q = query.lower()
    asks_quantity = any(w in q for w in
                        ("how much", "kitna", "kitni", "what amount", "how many"))

    if intent in ("EMD_GENERAL", "EMD_PAYMENT") and asks_quantity \
            and not entities.get("amounts") and not entities.get("percents"):
        return ("EMD is usually a percentage of the tender value. "
                "What is the estimated value of your tender so I can work it out?")

    if intent == "DOCUMENT_REQUIREMENTS" and len(q.split()) <= 5 \
            and not any(w in q for w in ("registration", "register", "vendor",
                                          "bid", "tender", "emd", "auction")):
        return ("Which process do you mean - vendor registration, bid "
                "submission, or EMD payment? Tell me and I'll list the exact "
                "documents.")
    return None


# ════════════════════════════════════════════════════════════════════════════
# 8. CONFIDENCE LABEL  (Tier 1 #3)
# ════════════════════════════════════════════════════════════════════════════

def confidence_from_score(top_score):
    """Map the top reranker relevance score to (label, note). `note` is a short
    caveat to prepend to low-confidence answers (empty for medium/high)."""
    try:
        s = float(top_score)
    except (TypeError, ValueError):
        return ("unknown", "")
    if s >= 0.55:
        return ("high", "")
    if s >= 0.18:
        return ("medium", "")
    return ("low",
            "I'm not fully certain this matches your question - please verify "
            "with the cited document.")


# ════════════════════════════════════════════════════════════════════════════
# 9. NUMERIC / CONSTRAINT REASONING  (Tier 2 #5)
# ════════════════════════════════════════════════════════════════════════════

def _fmt_inr(value: float) -> str:
    """Format a number in the Indian grouping system with a Rs sign."""
    neg = value < 0
    value = abs(value)
    s = f"{value:.2f}".rstrip("0").rstrip(".")
    if "." in s:
        intpart, dec = s.split(".")
        dec = "." + dec
    else:
        intpart, dec = s, ""
    if len(intpart) > 3:
        last3 = intpart[-3:]
        rest = intpart[:-3]
        rest = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", rest)
        grouped = rest + "," + last3
    else:
        grouped = intpart
    return ("-" if neg else "") + "₹" + grouped + dec


def compute_numeric(entities: dict):
    """If the query carries an amount AND a percentage, compute the percentage of
    the amount (e.g. EMD = 2% of Rs 50,00,000). Returns a short string or None."""
    amounts = entities.get("amounts_value") or []
    percents = entities.get("percents") or []
    if not amounts or not percents:
        return None
    try:
        pct = float(re.search(r"\d+(?:\.\d+)?", percents[0]).group(0))
    except (AttributeError, ValueError):
        return None
    base = max(amounts)  # the largest figure is almost always the tender value
    result = base * pct / 100.0
    return f"\U0001f9ee {percents[0]} of {_fmt_inr(base)} = {_fmt_inr(result)}"


# ════════════════════════════════════════════════════════════════════════════
# 10. FOLLOW-UP SUGGESTIONS  (Tier 1 #4)
# ════════════════════════════════════════════════════════════════════════════

INTENT_FOLLOWUPS = {
    "EMD_PAYMENT": [
        "When will my EMD be refunded?",
        "Who is eligible for EMD exemption?",
        "What is the difference between EMD and performance security?",
    ],
    "EMD_REFUND": [
        "How do I pay EMD online?",
        "How long does the EMD refund take?",
        "What if my bank account details changed?",
    ],
    "EMD_GENERAL": [
        "How do I pay EMD online?",
        "When will my EMD be refunded?",
        "What percentage of tender value is the EMD?",
    ],
    "VENDOR_REGISTRATION": [
        "What documents are required for vendor registration?",
        "How long does registration approval take?",
        "Do I need a DSC to register?",
    ],
    "DSC": [
        "My DSC token is not recognised - what do I do?",
        "Which class of DSC is required?",
        "Can one DSC be used for multiple logins?",
    ],
    "BID_SUBMISSION": [
        "What is the difference between technical and price bid?",
        "Can I modify my bid after submission?",
        "What happens if a corrigendum is issued?",
    ],
    "TENDER_SEARCH": [
        "How do I download a tender document?",
        "How do I find a tender by NIT number?",
        "Is registration needed to view tenders?",
    ],
    "AUCTION": [
        "How does reverse auction work?",
        "How is EMD handled in auctions?",
        "When is the auction EMD refunded?",
    ],
    "DOCUMENT_REQUIREMENTS": [
        "How do I upload these documents?",
        "What format should the documents be in?",
        "Is a DSC mandatory?",
    ],
    "PORTAL_USAGE": [
        "How do I reset my password?",
        "Which browser is recommended for the portal?",
        "How do I set up my DSC token?",
    ],
    "RULES_GFR": [
        "When is a limited tender enquiry allowed?",
        "What does GFR say about single-source procurement?",
        "When is a purchase committee required?",
    ],
}


def suggest_followups(intent: str, max_n: int = 3):
    """Return up to max_n related questions for the detected intent (or [])."""
    return list(INTENT_FOLLOWUPS.get(intent, []))[:max_n]


# ════════════════════════════════════════════════════════════════════════════
# 11. SEMANTIC (NEAR-DUPLICATE) ANSWER CACHE  (Tier 2 #7)
# ════════════════════════════════════════════════════════════════════════════

def _norm_cache_key(text: str) -> str:
    t = (text or "").lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# Generic question/filler words that carry no topic. Two queries that differ
# only by these (or word order / typos) are genuine paraphrases; queries that
# differ by anything else — most importantly the *document name* (dsc vs gem,
# manual vs tutorial, ppm, gfr …) — are different questions and must NOT share
# a cache entry. NOTE: never add topic-bearing nouns (gem, dsc, manual, tender,
# emd, …) here; the safe failure mode is to treat a word as content, not filler.
_CACHE_STOPWORDS = frozenset("""
a an the of to for in on at by about regarding concerning under as is are was
were be been being do does did can could would should will what which who whom
whose when where why how me my mine i we our you your please tell explain
describe give provide list show find want need know main mentioned this that
these those and or any some it its their there here step process steps
kya hai ka ki ke ko mujhe bataye batao bata sakte ho hain
""".split())


def _content_tokens(key: str) -> frozenset:
    """Topic-bearing tokens of a normalised cache key (drops generic filler)."""
    return frozenset(w for w in key.split() if w not in _CACHE_STOPWORDS)


class AnswerCache:
    """Caches answers keyed by normalised query text, with a fuzzy fallback so
    near-identical phrasings ("what is emd" vs "explain emd") hit the same entry.
    Thread-safe; entries expire after `ttl_seconds`."""

    def __init__(self, ttl_seconds: int = 86400, max_entries: int = 500,
                 fuzzy_cutoff: float = 0.9):
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self.cutoff = fuzzy_cutoff
        self._store = {}   # key -> {answer, sources, ts}
        self._lock = threading.Lock()

    def _evict(self, now):
        stale = [k for k, v in self._store.items() if now - v["ts"] > self.ttl]
        for k in stale:
            self._store.pop(k, None)
        if len(self._store) > self.max_entries:
            for k in sorted(self._store, key=lambda k: self._store[k]["ts"])[
                    :len(self._store) - self.max_entries]:
                self._store.pop(k, None)

    def get(self, query: str):
        key = _norm_cache_key(query)
        if not key:
            return None
        now = time.time()
        with self._lock:
            self._evict(now)
            entry = self._store.get(key)
            if entry:
                return {"answer": entry["answer"], "sources": entry["sources"],
                        "exact": True}
            # Fuzzy fallback for paraphrases, but guarded: a high character
            # similarity is NOT enough, because two questions that differ only
            # by the document name ("…the dsc manual" vs "…the gem manual") are
            # ~94% identical yet semantically distinct. Only accept the match
            # when both queries carry the SAME set of topic words, so the
            # difference is purely filler/word-order/typo.
            want = _content_tokens(key)
            for cand in difflib.get_close_matches(
                    key, list(self._store.keys()), n=5, cutoff=self.cutoff):
                if _content_tokens(cand) == want:
                    entry = self._store[cand]
                    return {"answer": entry["answer"],
                            "sources": entry["sources"], "exact": False}
        return None

    def put(self, query: str, answer: str, sources):
        key = _norm_cache_key(query)
        if not key or not (answer or "").strip():
            return
        with self._lock:
            self._store[key] = {"answer": answer, "sources": list(sources or []),
                                "ts": time.time()}
            self._evict(time.time())


# ════════════════════════════════════════════════════════════════════════════
# 12. MULTI-TURN TASK FLOW (VENDOR REGISTRATION WIZARD)  (Tier 3)
# ════════════════════════════════════════════════════════════════════════════

# A flow is an ordered list of (slot, prompt) steps. The wizard collects each
# slot in turn, then emits a summary. Flow state lives on the session in
# ConversationMemory (see flow methods there).
FLOWS = {
    "vendor_registration": {
        "title": "Vendor Registration",
        "steps": [
            ("person",  "Let's begin your vendor registration. What is your full name?"),
            ("company", "Thanks! What is your company / firm name?"),
            ("pan",     "Got it. What is your PAN number? (format AAAAA0000A)"),
            ("email",   "Almost done - what email should be linked to the account?"),
        ],
    },
}

# Phrases that start a guided flow.
_FLOW_TRIGGERS = {
    "vendor_registration": (
        "register me", "start registration", "begin registration",
        "help me register", "guide me through registration", "mujhe register",
        "registration shuru", "registration start", "step by step registration",
        # NOTE: bare "register as a vendor" / "register as vendor" removed — those
        # phrases appear verbatim inside informational questions ("how do I
        # register as a vendor?") and wrongly launched the wizard instead of
        # answering from the manual. Only imperative "register me"-style requests
        # start the guided flow now.
    ),
}


def detect_flow_trigger(query: str):
    """Return a flow name if the query asks to start a guided flow, else None."""
    if not query:
        return None
    q = query.lower()
    for flow, triggers in _FLOW_TRIGGERS.items():
        if any(t in q for t in triggers):
            return flow
    return None


# ════════════════════════════════════════════════════════════════════════════
# 13. CONVERSATION SUMMARY HELPER  (Tier 2 #6)
# ════════════════════════════════════════════════════════════════════════════

def summarize_turns(turns) -> str:
    """Compress a list of turn objects into a one-line running summary (topics)
    without an LLM call."""
    if not turns:
        return ""
    topics = []
    for t in turns:
        topic = getattr(t, "topic", "") or ""
        if topic and topic not in topics:
            topics.append(topic)
    if not topics:
        return ""
    return "Earlier in this chat the user asked about: " + ", ".join(topics) + "."
