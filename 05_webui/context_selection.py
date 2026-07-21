"""Final-context selection for the answer prompt.

Retrieval intentionally remains broad so that the source drawer can expose the
best matching chunks.  This module chooses a smaller, diverse and authoritative
subset of those already-retrieved chunks for generation and citations.
"""

from collections import defaultdict
import re
from typing import Callable, Iterable, List, Sequence, Tuple

from fine_intent_policy import IntentRoute, source_family


_DISPOSAL_TERMS = (
    "surplus", "obsolete", "unserviceable", "residual value", "disposed of",
    "disposal of goods", "public auction",
)


def _payload(result):
    point = result.get("point", {}) if isinstance(result, dict) else {}
    return getattr(point, "payload", {}) or {}


def _source(result) -> str:
    return str(_payload(result).get("source", "") or "")


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def _is_disposal_distractor(result, query: str) -> bool:
    """Avoid a disposal rule answering a normal purchase question.

    A common false grounding case was a new-furniture query whose amount matched
    a GFR rule about disposing of surplus goods.  This is deliberately narrow:
    the passage is retained whenever the user asks about disposal, auction or
    surplus goods.
    """
    query_text = (query or "").lower()
    if any(term in query_text for term in _DISPOSAL_TERMS):
        return False
    text = str(_payload(result).get("text", "") or "").lower()
    return sum(term in text for term in _DISPOSAL_TERMS) >= 2


def _priority(result, route: IntentRoute) -> Tuple[int, float]:
    """Prefer the route's named source, then its documented source families."""
    source = _source(result)
    normalised = _normalise(source)
    preferred_titles = {_normalise(title) for title in route.preferred_source_titles}
    supporting_titles = {_normalise(title) for title in route.supporting_source_titles}
    family = source_family(source)

    if normalised in preferred_titles:
        tier = 0
    elif family in route.preferred_families:
        tier = 1
    elif normalised in supporting_titles:
        tier = 2
    elif family in route.supporting_families:
        tier = 3
    else:
        tier = 4
    return tier, -float(result.get("score", 0.0) or 0.0)


def select_context_results(results: Iterable[dict], route: IntentRoute, query: str,
                           *, max_chunks_per_source: int = 2) -> List[dict]:
    """Order already-retrieved chunks for grounded generation.

    The first pass emits one chunk per document so one duplicated source cannot
    consume the prompt.  A second pass admits a further chunk only when useful.
    No embedding, Qdrant, retrieval, or reranking score is changed.
    """
    usable = [r for r in (results or ()) if _source(r) and not _is_disposal_distractor(r, query)]
    if not usable:
        usable = [r for r in (results or ()) if _source(r)]

    by_source = defaultdict(list)
    for result in usable:
        by_source[_source(result)].append(result)
    for rows in by_source.values():
        rows.sort(key=lambda row: _priority(row, route))

    source_order = sorted(
        by_source,
        key=lambda source: _priority(by_source[source][0], route),
    )
    selected = []
    for source in source_order:
        selected.append(by_source[source][0])

    # Keep adjacent/procedural details available after source diversity has been
    # established.  This preserves the portal-manual use case without letting it
    # crowd out the principal policy source.
    for source in source_order:
        selected.extend(by_source[source][1:max_chunks_per_source])
    return selected


def pack_context(results: Sequence[dict], route: IntentRoute, query: str,
                 strip_header: Callable[[str], str],
                 friendly_name: Callable[[str], str], *,
                 char_budget: int, per_chunk_cap: int) -> Tuple[str, List[str], List[dict]]:
    """Return prompt text, exact citation sources, and selected evidence chunks."""
    parts, source_refs, selected = [], [], []
    used = 0
    for index, result in enumerate(select_context_results(results, route, query), 1):
        source = _source(result)
        body = strip_header(str(_payload(result).get("text", "") or ""))[:per_chunk_cap]
        if not body:
            continue
        friendly = friendly_name(source)
        part = f"[Source {index}: {friendly}]\n{body}"
        # Count the labels and separators too.  Sarvam's input limit applies to
        # the complete prompt text, not just the chunk bodies.
        separator_size = 2 if parts else 0
        if parts and used + separator_size + len(part) > char_budget:
            continue
        if friendly not in source_refs:
            source_refs.append(friendly)
        parts.append(part)
        selected.append(result)
        used += separator_size + len(part)
    return "\n\n".join(parts), source_refs, selected
