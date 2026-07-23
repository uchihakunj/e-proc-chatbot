"""Small, dependency-free helpers shared by chatbot streaming providers."""

import re


_EMPTY_OPTIONAL_SECTION = re.compile(
    r"(?im)^[ \t]*(?:📋[ \t]*)?"
    r"(?:Process|प्रक्रिया|Rule[ \t]*/?[ \t]*Provision|Explanation|"
    r"नियम[ \t]*/[ \t]*प्रावधान|व्याख्या)[ \t]*:?[ \t]*\r?\n"
    r"[ \t]*\(?[ \t]*(?:omitted\b|not[ \t]+(?:applicable|required|available)\b|"
    r"none\b|n/?a\b|no[ \t]+(?:process|rule|provision|explanation)\b)"
    r"[^\r\n]*\)?[ \t]*(?:\r?\n|$)"
)

_OUT_OF_SCOPE_TOPIC = re.compile(
    r"\b(?:weather|forecast|temperature|rainfall|climate|mars|moon|planet|"
    r"solar[ -]system|space[ -]travel|cricket|football|sports?|match[ -]score|"
    r"recipe|cooking|movie|song|joke|horoscope|astrology)\b",
    re.IGNORECASE,
)
_DOMAIN_ANCHOR = re.compile(
    r"\b(?:e[- ]?procurement|procure(?:ment)?|tenders?|bids?|bidder|emd|"
    r"earnest[ -]money|vendors?|suppliers?|auction|gfr|gem|dsc|nit|boq|"
    r"contracts?|quotations?|bank[ -]guarantee|store[ -]purchase|it[ -]act)\b",
    re.IGNORECASE,
)


def is_explicitly_out_of_scope(query):
    """Identify common non-procurement topics unless a real domain anchor exists."""
    text = query or ""
    return bool(_OUT_OF_SCOPE_TOPIC.search(text) and not _DOMAIN_ANCHOR.search(text))


def new_stream_state():
    """Return a complete state object for a primary or fallback model attempt."""
    return {
        "content_streamed": False,
        "failed_before_output": False,
        "answer_buf": [],
        "provider_text": "",
        "fallback_reason": "",
    }


def should_retry_with_fallback(state, fallback_enabled, fallback_model):
    """Return True when a second model attempt is worth trying."""
    if not fallback_enabled:
        return False

    model = (fallback_model or "").strip()
    if not model:
        return False

    return bool(
        state.get("failed_before_output")
        or not state.get("content_streamed")
    )


def record_stream_content(state, content):
    """Record provider output and return only the new text to emit.

    Providers may stream either token deltas (``"Answer"``, ``" text"``) or
    cumulative message snapshots (``"Answer"``, ``"Answer text"``).  Normalize
    both forms so cumulative snapshots are not appended repeatedly. Whitespace is
    retained for exact reconstruction, but does not count as a usable answer.
    ``setdefault`` keeps this safe for state objects produced by older callers.
    """
    if content is None:
        return ""

    text = content if isinstance(content, str) else str(content)
    if not text:
        return ""

    previous = state.setdefault("provider_text", "")
    if previous and text.startswith(previous):
        normalized = text[len(previous):]
        state["provider_text"] = text
    elif previous and previous.startswith(text):
        # Exact duplicate or an older cumulative snapshot arriving out of order.
        normalized = ""
    else:
        normalized = text
        state["provider_text"] = previous + text

    if not normalized:
        return ""

    state.setdefault("answer_buf", []).append(normalized)
    if normalized.strip():
        state["content_streamed"] = True
    return normalized


def sanitize_model_answer(text, refusal_lines=()):
    """Remove known formatting artifacts from an otherwise grounded answer."""
    if not text:
        return text or ""

    cleaned = _EMPTY_OPTIONAL_SECTION.sub("", text).rstrip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Small models occasionally answer correctly and then echo the refusal example
    # from the prompt.  A genuine refusal consists only of that line, so remove it
    # only when substantive answer text precedes it.
    for refusal in refusal_lines:
        refusal = (refusal or "").strip()
        if refusal and cleaned != refusal and cleaned.endswith(refusal):
            prefix = cleaned[:-len(refusal)].rstrip()
            if prefix:
                cleaned = prefix
                break

    return cleaned
