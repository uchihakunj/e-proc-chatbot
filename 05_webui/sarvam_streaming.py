"""Small, provider-specific helpers for Sarvam's OpenAI-compatible SSE stream."""

import json
import os
from typing import Optional, Tuple


def parse_sarvam_sse_line(line: str) -> Tuple[str, str, bool]:
    """Return ``(answer_content, reasoning_content, is_done)`` for one SSE line.

    Sarvam may stream hidden ``reasoning_content`` for several seconds before
    sending visible ``content``.  It is useful for timing but must never be sent
    to the end user as an answer.
    """
    if not line:
        return "", "", False
    raw = line.strip()
    if raw == "data: [DONE]":
        return "", "", True
    if not raw.startswith("data: "):
        return "", "", False
    try:
        payload = json.loads(raw[6:])
        choice = (payload.get("choices") or [{}])[0]
        delta = choice.get("delta") or {}
        return (delta.get("content") or "", delta.get("reasoning_content") or "", False)
    except (ValueError, TypeError, IndexError):
        return "", "", False


def configured_reasoning_effort() -> Optional[str]:
    """Return Sarvam's reasoning setting, defaulting to low-latency reasoning.

    Sarvam accepts JSON ``null`` to disable hidden reasoning.  This keeps the
    production RAG path responsive while retaining an opt-in environment switch
    for non-thinking chat or deeper model reasoning.
    """
    value = os.getenv("SARVAM_REASONING_EFFORT", "low").strip().lower()
    if value in {"", "none", "off", "false", "0", "disabled"}:
        return None
    return value if value in {"low", "medium", "high"} else None
