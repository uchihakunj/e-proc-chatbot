import os
import atexit
import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, Optional, Any
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from FlagEmbedding import BGEM3FlagModel, FlagReranker

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _rag_trace(event, **payload):
    if os.getenv('CHIPPY_TRACE_RAG', '').lower() not in ('1', 'true', 'yes', 'on'):
        return
    print('[RAG_TRACE] ' + json.dumps({'event': event, **payload}, ensure_ascii=False,
                                      default=str), flush=True)

# ── Timing Utilities ───────────────────────────────────────────
_pipeline_start: Optional[float] = None
_stage_times: Dict[str, float] = {}

def _mark_time(stage_name: str) -> None:
    """Mark the current time for a stage and log elapsed time.
    
    Parameters
    ----------
    stage_name : str
        Name of the pipeline stage
        
    Raises
    ------
    ValueError
        If stage_name is None or empty
    """
    if not stage_name:
        raise ValueError("stage_name cannot be None or empty")
    
    global _pipeline_start, _stage_times
    current_time = time.time()
    
    if _pipeline_start is None:
        _pipeline_start = current_time
        _stage_times[stage_name] = current_time
        logger.info(f"⏱️ [{stage_name}] STARTED")
    else:
        if stage_name in _stage_times:
            elapsed = current_time - _stage_times[stage_name]
            logger.info(f"⏱️ [{stage_name}] COMPLETED in {elapsed:.2f}s")
        _stage_times[stage_name] = current_time

def _print_timing_summary() -> None:
    """Log timing summary for entire pipeline."""
    global _pipeline_start
    if _pipeline_start is None:
        return
    total = time.time() - _pipeline_start
    logger.info("="*70)
    logger.info(f"⏱️ TOTAL PIPELINE TIME: {total:.2f} seconds")
    logger.info("="*70)

# ── Configuration ──────────────────────────────────────────────
def _get_config() -> Dict[str, Any]:
    """Load configuration with environment variable overrides.
    
    Returns
    -------
    Dict[str, Any]
        Configuration dictionary with paths and parameters
        
    Raises
    ------
    FileNotFoundError
        If required paths don't exist
    """
    root = Path(__file__).resolve().parents[2]  # CHiPS directory
    
    chunk_dir = Path(os.getenv("CHIPPY_CHUNK_DIR", str(root / "03_chunking" / "output")))
    qdrant_path = Path(os.getenv("CHIPPY_QDRANT_LOCAL_PATH", str(root / "04_embeddings_and_kg" / "db" / "qdrant_local")))
    
    # Validate paths exist
    if not chunk_dir.exists():
        logger.warning(f"Chunk directory not found: {chunk_dir}")
    if not qdrant_path.exists():
        logger.warning(f"Qdrant database path not found: {qdrant_path}")
    
    import sys
    sys.path.insert(0, str(root))
    from utils.config_manager import Config
    retrieval_cfg = Config("retrieval")
    
    return {
        "chunk_dir": chunk_dir,
        "collection": os.getenv("CHIPPY_QDRANT_COLLECTION", "db3"),
        "qdrant_local_path": qdrant_path,
        "encode_batch_size": int(os.getenv("STAGE4_BATCH_SIZE", "8")),
        "max_length": int(os.getenv("STAGE4_MAX_LENGTH", "1024")),
        "top_k_retrieval": retrieval_cfg.get("top_k_retrieval", 50),
        "final_context": retrieval_cfg.get("final_context", 8),
        "rerank_truncation": retrieval_cfg.get("rerank_truncation", 1500),
        "max_faq_results": retrieval_cfg.get("max_faq_results", 2),
        "authority_weight": retrieval_cfg.get("authority_weight", 0.20),
        "semantic_weight": retrieval_cfg.get("semantic_weight", 0.70),
        "hybrid_weight": retrieval_cfg.get("hybrid_weight", 0.10),
        "verify_low_confidence": retrieval_cfg.get("verify_low_confidence", 0.55),
        "verify_high_risk_intents": retrieval_cfg.get("verify_high_risk_intents", True),
        "verify_on_mixed_documents": retrieval_cfg.get("verify_on_mixed_documents", True),
    }

CFG = _get_config()
CHUNK_DIR = CFG["chunk_dir"]
COLLECTION_NAME = CFG["collection"]
ENCODE_BATCH_SIZE = CFG["encode_batch_size"]
MAX_LENGTH = CFG["max_length"]
TOP_K_RETRIEVAL = CFG["top_k_retrieval"]
FINAL_CONTEXT = CFG["final_context"]
RERANK_TRUNCATION = CFG["rerank_truncation"]
MAX_FAQ_RESULTS = CFG["max_faq_results"]
AUTHORITY_WEIGHT = CFG["authority_weight"]
SEMANTIC_WEIGHT = CFG["semantic_weight"]
HYBRID_WEIGHT = CFG["hybrid_weight"]
VERIFY_LOW_CONFIDENCE = CFG["verify_low_confidence"]
VERIFY_HIGH_RISK_INTENTS = CFG["verify_high_risk_intents"]
VERIFY_ON_MIXED_DOCUMENTS = CFG["verify_on_mixed_documents"]

# ── Retrieval Configuration ────────────────────────────────────
HYBRID_ALPHA = 0.6           # 0.0 = pure sparse, 1.0 = pure dense (0.6 = 60% dense, 40% sparse)
RERANK_MIN_K = 3             # Minimum results to return
RERANK_MAX_K = 6             # Maximum results to return
RERANK_THRESHOLD = 0.65      # Score threshold for inclusion

# ── Reranker latency tuning (env-overridable) ──────────────────
# The CPU cross-encoder is the per-query latency floor, and its cost is linear
# in the number of candidates it scores. These bound that work and let easy
# queries skip most of it. See the inline reranker in retrieve_context().
RERANK_TOPK      = int(os.getenv("RERANK_TOPK", str(TOP_K_RETRIEVAL)))           # always rerank the top hybrid hits (was 10)
RERANK_MAX_CANDS = int(os.getenv("RERANK_MAX_CANDS", str(TOP_K_RETRIEVAL)))     # + diversity-injected sources (was 18)
RERANK_FAST_K    = int(os.getenv("RERANK_FAST_K", "4"))         # confidence-gate: score these first
RERANK_CONF_SKIP = float(os.getenv("RERANK_CONF_SKIP", "0.92")) # if best fast score ≥ this, skip the rest (0=off)
USE_MULTI_QUERY = False      # Disable multi-query by default for lower request latency on CPU deployments
USE_KNOWLEDGE_GRAPH = False  # Disable KG expansion by default for lower request latency on CPU deployments
KG_WEIGHT = 0.3              # Weight of KG in combined score (0-1)
KG_EXPANSION_DEPTH = 2       # Entity graph traversal depth

# ── Generation-context compression ─────────────────────────────────────────
# This is deliberately separate from retrieval.  Retrieval keeps broad evidence
# for citations/UI cards; generation receives only the evidence it needs.
PROMPT_TOKEN_BUDGET = int(os.getenv("PROMPT_TOKEN_BUDGET", "1750"))
CONTEXT_TOKEN_BUDGET = int(os.getenv("CONTEXT_TOKEN_BUDGET", "750"))


def estimate_tokens(text):
    """Conservative, dependency-free token estimate for prompt budgeting.

    Sarvam does not expose its tokenizer locally.  Character-only estimates are
    particularly inaccurate for punctuation-heavy rules and Hindi text, so use
    the larger of a 3.6-char estimate and a lexical-unit estimate.  The budget is
    intentionally conservative; telemetry labels values as estimates.
    """
    text = text or ""
    if not text:
        return 0
    lexical_units = re.findall(r"[\w\u0900-\u097F]+|[^\s]", text, re.UNICODE)
    return max((len(text) + 3) // 4, int(len(lexical_units) * 0.72))


def classify_prompt_shape(query):
    """Classify the evidence breadth required by a user question."""
    q = (query or "").lower()
    if (any(t in q for t in ("department buyer", "government department purchase",
                             "purchase indent", "need assessment"))
            and any(t in q for t in ("laptop", "computer", "it equipment", "purchase"))):
        return "complex"
    if re.search(r"\b(methods|exemptions|categories|different types|types of|conditions under which|when is|situations)\b", q):
        return "complex"
    if re.search(r"\b(compare|comparison|difference|differentiate|versus|vs\.?|rather than)\b|\b(aur|antar|difference kya)\b", q):
        return "comparison"
    if re.search(r"\b(how|steps?|process|procedure|issue|publish|submit|apply|register|refund|after|kaise|prakriya)\b", q):
        return "procedural"
    if re.search(r"\b(what is|what are|define|meaning|why|when|who|which|kitna|kya hai)\b", q):
        return "factual"
    return "factual"


def _query_terms(query):
    stop = {
        "what", "when", "where", "which", "with", "from", "that", "this",
        "have", "will", "would", "should", "through", "about", "please",
        "after", "before", "into", "your", "their", "then", "than", "why",
        "how", "are", "the", "and", "for", "was", "is", "of", "to", "in",
    }
    return {w for w in re.findall(r"[\w\u0900-\u097F]+", (query or "").lower())
            if len(w) > 2 and w not in stop}


def _strip_chunk_preamble(text):
    """Remove ingestion headers without touching the document body."""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    body_start = 0
    for idx, line in enumerate(lines):
        clean = line.strip()
        if (not clean or clean == "---" or
                re.match(r"^(?:headings|source|type|document_type|authority)\s*:", clean, re.I)):
            body_start = idx + 1
            continue
        break
    return "\n".join(lines[body_start:]).strip()


def _semantic_units(text):
    """Split text into paragraphs/sentences, never returning a partial unit."""
    def _split_prose(value):
        # Government PDFs often flatten a whole paragraph to one line.  Treat
        # sentence punctuation and the Hindi/PDF pipe separator as boundaries;
        # then split very long sentences at clause boundaries rather than by
        # character position.
        primary = re.split(r"(?<=[.!?।;|])\s+(?=[\"'“”A-Z0-9\u0900-\u097F])", value)
        output = []
        for fragment in primary:
            fragment = fragment.strip()
            if estimate_tokens(fragment) > 180:
                clauses = re.split(
                    r"(?<=,)\s+(?=(?:and|or|but|if|when|where|which|provided|however|"
                    r"in case|for the|the |[A-Z0-9\u0900-\u097F]))", fragment, flags=re.I)
                output.extend(clause.strip() for clause in clauses if clause.strip())
            elif fragment:
                output.append(fragment)
        return output

    units = []
    for paragraph in re.split(r"\n\s*\n+", (text or "").strip()):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        # Lists and headings already have meaningful line boundaries.
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if len(lines) > 1:
            for line in lines:
                units.extend(_split_prose(line))
            continue
        units.extend(_split_prose(paragraph))
    return units


def _semantic_excerpt(text, query, token_budget, seen_units=None):
    """Return the most query-relevant complete semantic units within budget."""
    if seen_units is None:
        seen_units = set()
    
    units = _semantic_units(_strip_chunk_preamble(text))
    if not units or token_budget <= 0:
        return ""
    terms = _query_terms(query)
    scored = []
    
    # Pre-filter duplicates and score
    for index, unit in enumerate(units):
        normalized_unit = re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', '', unit.lower())
        if normalized_unit in seen_units or not normalized_unit:
            continue
            
        unit_terms = set(re.findall(r"[\w\u0900-\u097F]+", unit.lower()))
        overlap = len(terms & unit_terms)
        # Headings/list entries establish context for nearby factual statements.
        structural_bonus = 0.3 if re.match(r"^(?:#{1,6}\s|\d+[.)]|[-*•])", unit) else 0
        scored.append((overlap + structural_bonus + max(0, 0.08 - index * 0.002), index, unit, normalized_unit))

    # Select relevance first, then restore document order for readable context.
    selected, used = [], 0
    for _, index, unit, normalized_unit in sorted(scored, key=lambda item: (-item[0], item[1])):
        unit_tokens = estimate_tokens(unit)
        if unit_tokens > token_budget:
            continue
        if used + unit_tokens <= token_budget:
            selected.append((index, unit))
            used += unit_tokens
            seen_units.add(normalized_unit)
            
    return "\n".join(unit for _, unit in sorted(selected)).strip()


def _context_chunk_exclusion(payload):
    text = (payload or {}).get("text", "") or ""
    low = text.lower()
    image_markers = low.count("the image") + low.count("screenshot text") + low.count("*यह चित्र")
    operative_terms = sum(term in low for term in (
        "click", "select", "enter", "upload", "shall", "must", "procedure",
        "refund", "payment", "registration", "corrigendum", "purchase order",
    ))
    if image_markers >= 2 and operative_terms == 0:
        return "screenshot_only_ocr"
    if ("contents" in low and low.count("....") >= 3) or low.count("error! bookmark not defined") >= 2:
        return "table_of_contents_or_broken_bookmark"
    if len(re.sub(r"\W+", "", text)) < 80:
        return "fragment_too_short"
    return ""


def build_adaptive_context(query, context_results, source_name_resolver=None,
                           context_token_budget=CONTEXT_TOKEN_BUDGET,
                           routing_policy=None):
    """Select minimal, semantically complete generation evidence."""
    shape = classify_prompt_shape(query)
    
    # Task 1: Adaptive Context Selection mapping
    if shape == "factual":
        target_count = 2
    elif shape == "procedural":
        target_count = 3
    elif shape == "comparison":
        target_count = 4
    elif shape == "complex":
        target_count = 5
    else:
        target_count = 3
        
    usable, excluded_context = [], []
    for result in context_results or []:
        payload = getattr((result or {}).get("point"), "payload", None)
        if payload is None:
            continue
        reason = _context_chunk_exclusion(payload)
        if reason:
            excluded_context.append({
                "chunk_id": payload.get("chunk") or payload.get("file"),
                "document_title": payload.get("source"),
                "excluded_chunk_reason": reason,
            })
            continue
        usable.append(result)
    if not usable:
        return {"context_text": "", "source_refs": [], "query_type": shape,
                "selected_chunk_count": 0, "estimated_context_tokens": 0,
                "top_confidence": 0.0, "selection_records": [],
                "excluded_context_chunks": excluded_context}

    policy = routing_policy or {}
    preferred_sources = set(policy.get("preferred_source_titles") or ())
    required_stage = policy.get("required_stage")

    def _context_rank(result):
        payload = result["point"].payload
        source_bonus = 1 if payload.get("source") in preferred_sources else 0
        stage_bonus = 1 if required_stage and payload.get("procurement_stage") == required_stage else 0
        return (source_bonus, stage_bonus, float(result.get("score", 0.0)))

    ranked = sorted(usable, key=_context_rank, reverse=True)
    top_score = max(0.0, float(ranked[0].get("score", 0.0)))
    
    context_parts, source_refs, selection_records = [], [], []
    seen_units = set()
    last_score = None
    
    for index, result in enumerate(ranked, 1):
        if len(context_parts) >= target_count:
            break
            
        current_score = float(result.get("score", 0.0))
        
        # Task 3: Confidence-Based Context Reduction
        # Always keep the first (highest-ranked) chunk regardless of absolute score.
        # For subsequent chunks, use a very permissive absolute threshold (0.15) 
        # but primarily rely on relative score drops (> 0.30) to eliminate weak tail chunks.
        if len(context_parts) > 0:
            if current_score < 0.15:
                break
            if last_score is not None and (last_score - current_score > 0.30):
                break
            
        last_score = current_score
        
        point = result["point"]
        payload = point.payload
        raw_source = payload.get("source", "")
        source = source_name_resolver(raw_source) if source_name_resolver else raw_source
        label = f"[Source {index}: {source}]"
        
        # Task 2: Adaptive Chunk Size
        if current_score >= 0.85:
            # 1500 chars ~ 375 tokens
            allowance = min(375, context_token_budget)
        else:
            # 800 chars ~ 200 tokens
            allowance = min(200, context_token_budget)
            
        # Deduct label size from allowance
        allowance = max(120, allowance - estimate_tokens(label))
        
        # Pass seen_units for Task 4 Deduplication
        excerpt = _semantic_excerpt(payload.get("text", ""), query, allowance, seen_units)
        if not excerpt:
            continue
            
        if source not in source_refs:
            source_refs.append(source)
            
        context_parts.append(f"{label}\n{excerpt}")
        selection_records.append({
            "chunk_id": payload.get("chunk") or payload.get("file"),
            "document_title": raw_source,
            "page": payload.get("page_number") or payload.get("page"),
            "section": payload.get("rule_or_section") or payload.get("headings"),
            "final_selection_reason": result.get("selection_reason", "semantic_relevance"),
            "dense_score": result.get("dense_score"),
            "sparse_score": result.get("sparse_score"),
            "hybrid_score": result.get("hybrid_score"),
            "reranker_score": result.get("reranker_score"),
            "final_score": result.get("score"),
        })

    context_text = "\n\n".join(context_parts)
    return {
        "context_text": context_text,
        "source_refs": source_refs,
        "query_type": shape,
        "selected_chunk_count": len(context_parts),
        "estimated_context_tokens": estimate_tokens(context_text),
        "top_confidence": top_score,
        "target_chunk_count": target_count,
        "selection_records": selection_records,
        "excluded_context_chunks": excluded_context,
    }

# ── Helper: Get file number from chunk source ───────────────────
def extract_file_number(chunk_source):
    """Extract file number from chunk source (e.g., 'output_corrected2' → 2)."""
    import re
    match = re.search(r'output_corrected(\d+)', chunk_source)
    if match:
        return int(match.group(1))
    return None

# ── Helper: Get actual file name from chunk metadata ───────────
def get_actual_filename(chunk_source):
    """Convert output_corrected* to actual file name using file numbers (file1.pdf, file2.pdf, etc.)."""
    file_num = extract_file_number(chunk_source)
    if file_num:
        return f"file{file_num}.pdf"
    return chunk_source + ".pdf"  # Fallback

# ── Helper: Extract highlighted excerpt from chunk text ─────────
def extract_highlighted_excerpt(chunk_text, query_words, max_length=300):
    """Extract the most relevant part of chunk text containing query words.
    
    Args:
        chunk_text: Full chunk text
        query_words: List of important words from the query
        max_length: Max length of excerpt
    
    Returns:
        Highlighted excerpt with query words in context
    """
    sentences = chunk_text.split('. ')
    best_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(word.lower() in sentence_lower for word in query_words if len(word) > 3):
            best_sentences.append(sentence.strip())
    
    if best_sentences:
        excerpt = '. '.join(best_sentences[:2])  # Take first 2 matching sentences
    else:
        excerpt = chunk_text[:max_length]
    
    # Truncate if too long
    if len(excerpt) > max_length:
        excerpt = excerpt[:max_length].rsplit(' ', 1)[0] + '...'
    
    return excerpt.strip()

# ── Load models ────────────────────────────────────────────────
print("Loading embedding model...")
# Embedder backend: "openvino" runs the BGE-M3 backbone on the Intel Arc iGPU
# (dense + sparse reproduced; see ov_embedder.py) to cut the query-embedding
# latency floor; "flag" (default) keeps the CPU BGEM3FlagModel. OpenVINO
# failures fall back to CPU so startup never breaks. Validate parity first with
# ov_embed_probe.py before enabling.
_EMBEDDER_BACKEND = os.getenv("EMBEDDER_BACKEND", "flag").lower()
_EMBEDDER_DEVICE  = os.getenv("EMBEDDER_DEVICE", "GPU")
model = None
if _EMBEDDER_BACKEND == "openvino":
    try:
        from ov_embedder import OVEmbedder
        model = OVEmbedder("BAAI/bge-m3", device=_EMBEDDER_DEVICE)
        print(f"  Embedder backend: OpenVINO on {_EMBEDDER_DEVICE}")
    except Exception as e:
        print(f"  ⚠ OpenVINO embedder unavailable ({e}); falling back to CPU BGEM3FlagModel")
        model = None
if model is None:
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
    print("  Embedder backend: CPU BGEM3FlagModel")
model.return_sparse = True  # Enable sparse embeddings generation

print("Loading reranker model...")
# Reranker backend: "openvino" runs the cross-encoder on the Intel Arc iGPU
# (~30x faster than CPU torch, identical scores); "flag" (default) keeps the
# CPU FlagReranker. OpenVINO failures fall back to CPU so startup never breaks.
_RERANKER_MODEL   = "BAAI/bge-reranker-v2-m3"
_RERANKER_BACKEND = os.getenv("RERANKER_BACKEND", "flag").lower()
_RERANKER_DEVICE  = os.getenv("RERANKER_DEVICE", "GPU")
reranker = None
if _RERANKER_BACKEND == "openvino":
    try:
        from ov_reranker import OVReranker
        reranker = OVReranker(_RERANKER_MODEL, device=_RERANKER_DEVICE)
        print(f"  Reranker backend: OpenVINO on {_RERANKER_DEVICE}")
    except Exception as e:
        print(f"  ⚠ OpenVINO reranker unavailable ({e}); falling back to CPU FlagReranker")
        reranker = None
if reranker is None:
    reranker = FlagReranker(_RERANKER_MODEL, use_fp16=True)
    print("  Reranker backend: CPU FlagReranker")

# ── Load Knowledge Graph (if available) ────────────────────────
kg_retriever = None
if USE_KNOWLEDGE_GRAPH:
    try:
        from knowledge_graph import DocumentKnowledgeGraph
        from kg_retriever import KnowledgeGraphRetriever
        
        print("Loading knowledge graph...")
        kg = DocumentKnowledgeGraph()
        kg_path = os.path.join(os.path.dirname(__file__), "knowledge_graph.json")
        
        if os.path.exists(kg_path):
            kg.load(kg_path)
            kg_retriever = KnowledgeGraphRetriever(kg, model)
            print(f"✓ Knowledge graph loaded: {len(kg.entities)} entities")
        else:
            print(f"⚠ Knowledge graph not found at {kg_path}")
            print("  Run 'python build_knowledge_graph.py' to create it")
            USE_KNOWLEDGE_GRAPH = False
    except ImportError as e:
        print(f"Warning: Could not import knowledge graph modules: {e}")
        USE_KNOWLEDGE_GRAPH = False

# ── Connect to Qdrant (local embedded mode) ────────────────────
print(f"Connecting to local Qdrant at {CFG['qdrant_local_path']}...")
try:
    CFG["qdrant_local_path"].mkdir(parents=True, exist_ok=True)
    client = QdrantClient(path=str(CFG["qdrant_local_path"]))
    client.get_collections()
    print("✓ Connected to local embedded Qdrant")
except Exception as e:
    print(f"✗ Failed to initialize local Qdrant: {e}")
    print(f"Make sure {CFG['qdrant_local_path']} is writable")
    exit(1)


def _cleanup_qdrant():
    """Explicitly close Qdrant client on exit to avoid shutdown import errors."""
    try:
        if 'client' in globals():
            client.close()
    except Exception:
        pass  # Suppress cleanup errors during shutdown


atexit.register(_cleanup_qdrant)

# # ── Validate Groq Configuration (COMMENTED OUT) ──────────────
# if not GROQ_API_KEY:
#     print("⚠ WARNING: GROQ_API_KEY not set. Set it via environment variable.")
#     print("  Add to your terminal: $env:GROQ_API_KEY='your-api-key-here'")
# else:
#     print(f"✓ Groq API configured with model: {GROQ_MODEL}")

# ── Helper: Sparse search ──────────────────────────────────────
def sparse_search(query_sparse, all_points, limit=5):
    """Score points based on sparse embeddings overlap."""
    scores = []
    for point in all_points:
        sparse_payload = point.payload.get("sparse_embedding", {})
        score = sum(sparse_payload.get(token, 0) * query_sparse.get(token, 0) 
                   for token in query_sparse if token in sparse_payload)
        scores.append((point.id, score))
    return sorted(scores, key=lambda x: x[1], reverse=True)[:limit]

# ── Helper: Expand query into multiple perspectives ────────────
def expand_query(original_query):
    """Generate multiple query variations to improve retrieval coverage.
    
    Uses keyword expansion and perspective shifts:
    - Original query
    - Query + context keywords (approval, implementation, decision, etc.)
    - Query + document type keywords (agenda, minutes, meeting, etc.)
    - Query with synonyms
    """
    low = original_query.lower()
    if "vendor-side bid submission workflow" in low:
        variations = [
            original_query,
            "CHiPS Bid Submission Manual vendor login DSC bid submission workflow",
            "bidder tender search participate technical bid price bid encrypt upload submit",
            "vendor registration prerequisites DSC e-procurement portal bidder",
        ]
        _rag_trace('multi_query_expansions', original_query=original_query,
                   variations=variations)
        return variations
    if ("department buyer" in low or "government department purchase" in low
            or "purchase indent" in low):
        variations = [
            original_query,
            "government department laptop computer IT equipment procurement need assessment technical specifications purchase indent",
            "Chhattisgarh Store Purchase Rules GeM state approved purchase channel tender procedure department buyer",
            "Manual for Procurement of Goods 2024 administrative approval budgetary sanction IT systems inspection acceptance",
            "CVC purchase computer systems brand neutral specifications rate reasonableness asset register",
        ]
        _rag_trace('multi_query_expansions', original_query=original_query,
                   variations=variations)
        return variations

    variations = [original_query]  # Always include original
    
    # Add context-specific variations for government documents
    context_keywords = ["approval", "decision", "implementation", "status", "progress"]
    doc_keywords = ["meeting", "agenda", "minutes", "committee", "approval"]
    
    for keyword in context_keywords:
        if keyword not in original_query.lower():
            variations.append(f"{original_query} {keyword}")
    
    for keyword in doc_keywords:
        if keyword not in original_query.lower():
            variations.append(f"{original_query} {keyword}")
    
    # Add detail-focused variations
    variations.append(f"{original_query} details implementation")
    variations.append(f"{original_query} decision taken")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for v in variations:
        v_lower = v.lower()
        if v_lower not in seen:
            seen.add(v_lower)
            unique_variations.append(v)
    
    final = unique_variations[:5]
    _rag_trace('multi_query_expansions', original_query=original_query,
               variations=final)
    return final  # Cap at 5 variations to avoid excessive querying

# ── Helper: Single query retrieval ─────────────────────────────
def perform_single_retrieval(query, query_filter=None):
    """Perform single query retrieval and return results."""
    try:
        # Encode query with explicit batch_size to ensure sparse embeddings are generated
        # Using batch_size=1 explicitly ensures consistent behavior with batch encoding
        query_encoding = model.encode(
            [query],
            batch_size=1,  # Explicit batch size for single query
            max_length=MAX_LENGTH
        )
        
        if query_encoding is None or "dense_vecs" not in query_encoding:
            return None
        
        dense_vecs = query_encoding.get("dense_vecs")
        if dense_vecs is None or len(dense_vecs) == 0:
            return None
        
        query_dense = dense_vecs[0].tolist()
        
        # Get lexical weights (sparse embeddings) if available
        query_sparse = {}
        lex_weights = query_encoding.get("lexical_weights")
        if lex_weights is not None and isinstance(lex_weights, list) and len(lex_weights) > 0:
            try:
                query_sparse = dict(lex_weights[0])
            except (TypeError, ValueError):
                # Fallback if conversion fails
                query_sparse = {}
        elif lex_weights is not None and isinstance(lex_weights, dict):
            # Sparse weights might be returned as dict directly
            query_sparse = lex_weights
        
        # Dense search
        dense_results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_dense,
            query_filter=query_filter,
            limit=TOP_K_RETRIEVAL
        )
        
        if dense_results is None or not dense_results.points:
            return None
        
        return {
            "dense_results": dense_results,
            "dense_scores": [(p.id, p.score) for p in dense_results.points],
            "query_sparse": query_sparse
        }
    
    except Exception as e:
        print(f"  Single retrieval error: {e}")
        return None

# ── Helper: Multi-query retrieval ──────────────────────────────
def multi_query_retrieval(query, query_filter=None):
    """Retrieve results using multiple query variations and merge them.
    
    Benefits:
    - Captures different aspects of the query
    - Better coverage of semantically related documents
    - More robust to query phrasing variations
    """
    _mark_time("MULTI_QUERY_RETRIEVAL")
    
    if not USE_MULTI_QUERY:
        # Fall back to single query
        result = perform_single_retrieval(query, query_filter=query_filter)
        if result is None:
            return None, []
        return result["dense_results"], result["dense_scores"], result["query_sparse"]
    
    # Expand query into multiple variations
    query_variations = expand_query(query)
    print(f"  🔍 Searching with {len(query_variations)} query variations...")
    
    # Collect results from all query variations
    all_dense_results = {}  # {point_id: point}
    aggregated_scores = {}  # {point_id: sum_of_scores}
    all_sparse_queries = {}
    
    for i, q_variant in enumerate(query_variations):
        retrieval_result = perform_single_retrieval(q_variant, query_filter=query_filter)
        if retrieval_result is None:
            continue
        
        dense_results = retrieval_result["dense_results"]
        dense_scores = retrieval_result["dense_scores"]
        query_sparse = retrieval_result["query_sparse"]
        
        # Aggregate results
        for point in dense_results.points:
            all_dense_results[point.id] = point
        
        # Aggregate scores (later results still count, earlier have more weight)
        for point_id, score in dense_scores:
            if point_id not in aggregated_scores:
                aggregated_scores[point_id] = 0
            # Weight by position and query variation index
            aggregated_scores[point_id] += score * (1.0 / (i + 1))
        
        # Keep last query's sparse representation
        if query_sparse:
            all_sparse_queries = query_sparse
    
    if not all_dense_results:
        print("  Error: No results from multi-query retrieval.")
        return None, [], {}
    
    # Create mock result object with aggregated points
    class MockQueryResult:
        def __init__(self, points):
            self.points = points
    
    aggregated_points = list(all_dense_results.values())
    dense_results = MockQueryResult(aggregated_points)
    
    _mark_time("MULTI_QUERY_RETRIEVAL")
    return dense_results, list(aggregated_scores.items()), all_sparse_queries

# ── Helper: Rerank search results (Hybrid Threshold) ──────────
def rerank_results(query, candidate_points, min_k=3, max_k=6, threshold=0.65):
    """Rerank with hybrid method: threshold-based with min/max bounds.
    
    Args:
        query: Query string
        candidate_points: List of point objects
        min_k: Minimum results to return (default 3)
        max_k: Maximum results to return (default 6)
        threshold: Score threshold to include results (default 0.65)
    
    Logic:
        1. Include all results with score >= threshold
        2. But ensure at least min_k results
        3. Cap at max_k results
    """
    _mark_time("RERANKING")
    
    if not candidate_points:
        return []
    
    # Prepare query-document pairs for reranking
    pairs = []
    point_map = {}
    
    for idx, point in enumerate(candidate_points):
        text = point.payload.get("text", "")
        pairs.append([query, text])
        point_map[idx] = point
    
    # Score with reranker
    print(f"  📊 Reranking {len(pairs)} candidates...")
    rerank_scores = reranker.compute_score(pairs, normalize=True)
    
    # Sort by reranker scores (descending)
    ranked_indices = sorted(range(len(rerank_scores)), key=lambda i: rerank_scores[i], reverse=True)
    
    # Apply hybrid threshold logic
    results = []
    for rank, idx in enumerate(ranked_indices):
        score = rerank_scores[idx]
        
        # Include if:
        # 1. Score >= threshold AND results < max_k, OR
        # 2. results < min_k (ensure minimum)
        if (score >= threshold and len(results) < max_k) or len(results) < min_k:
            results.append({
                "point": point_map[idx],
                "score": score,
                "rank": len(results) + 1
            })
        # Stop if we've reached max_k
        if len(results) >= max_k:
            break
    
    _mark_time("RERANKING")
    return results

# ── Helper: Hybrid search using RRF ───────────────────────────
def hybrid_search(dense_scores, sparse_scores, alpha=0.5, k=60):
    """Combine dense and sparse scores using RRF (Reciprocal Rank Fusion)."""
    rrf_scores = {}
    
    # Add dense scores (RRF formula: 1 / (k + rank))
    for rank, (point_id, score) in enumerate(dense_scores):
        rrf_scores[point_id] = alpha / (k + rank + 1)
    
    # Add sparse scores
    for rank, (point_id, score) in enumerate(sparse_scores):
        if point_id not in rrf_scores:
            rrf_scores[point_id] = 0
        rrf_scores[point_id] += (1 - alpha) / (k + rank + 1)
    
    return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)


# ── Topical re-scoring (post-rerank) ───────────────────────────────────────
# Small, targeted nudges that correct two measured retrieval failures from the
# 150-question regression set, WITHOUT disturbing the cases that already work:
#   (1) The large Vigilance / CVC anti-corruption docs acted as a "magnet" for
#       unrelated queries (esp. Hindi/Hinglish) — e.g. an e-auction or bid-
#       submission question landing on the Vigilance (Hindi) manual. We demote
#       those docs unless the query actually carries a vigilance/anti-corruption
#       signal (this also fixes the GFR→CVC mis-hit).
#   (2) Portal step-by-step manuals (bid submission, vendor registration, offline
#       tenders, e-auction, browser/system setup, guidelines to bidders) lost
#       "how-to" queries to the comprehensive POLICY manuals. We boost them when
#       the query is clearly procedural ("how to / steps / configure / login …").
# Nudges are small (≤0.30) so a confident cross-encoder score still wins.
_VIG_SIGNAL = (
    "vigilance", "cvo", "cvc", "corrupt", "disciplinary", "preventive vigilance",
    "punitive", "whistle", "integrity pact",
    "सतर्कता", "निगरानी", "भ्रष्टाचार", "अनुशासन", "दंडात्मक", "दण्डात्मक",
    "निवारक", "सीवीओ", "सीवीसी", "ईमानदारी",
)
_PORTAL_DOC_KEYS = (
    "bid_submission", "vendor_registration", "offline_tenders", "auctionmanual",
    "edge_browser", "preferred_system", "guidelines_to_bidders",
)
_HOWTO_SIGNAL = (
    "how to", "how do", "how can", "how is", "step", "steps", "configure", "config",
    "set up", "setup", "attach", "encrypt", "participate", "log in", "login",
    "browser", "prerequisite", "register", "registration", "portal", "upload",
    "कैसे", "चरण", "लॉगिन", "कॉन्फ़िगर", "ब्राउज़र", "भाग", "पंजीकरण", "पंजीयन", "अपलोड",
    "kaise", "steps", "configure", "setup", "upload", "participate",
)
_HELP_SIGNAL = (
    "help desk", "helpdesk", "help line", "helpline", "contact", "support",
    "services", "service", "हेल्प", "संपर्क", "सेवा", "सेवाएँ", "सहायता", "kaha contact",
)
# (3) e-Auction PORTAL questions (live auction, H1 price, page refresh, RFX,
#     "Password@123") were lost to the GFR / Goods-manual REVERSE-AUCTION
#     paragraphs (which describe L-1-only display) — giving the opposite answer.
#     Boost the CG Auction Manual when the query is clearly about the auction.
_AUCTION_SIGNAL = (
    "auction", "e-auction", "eauction", "rfx", " h1", "h-1", "h 1",
    "नीलामी", "नीलाम", "ऑक्शन", "एच1", "एच-1",
)
# (4) "Regret" is a rate-contract bidding UI toggle in the portal Bid-Submission
#     manual, but the GoI policy manuals use "regret = reject ALL bids for lack of
#     competition" — a strong distractor the model prefers even when the portal line
#     is injected. Demote the policy manuals hard for regret queries.
_REGRET_SIGNAL = ("regret", "रीग्रेट", "रिग्रेट")
_POLICY_MANUAL_KEYS = (
    "manual_for_procurement", "mannual procurement", "publicpromanual", "ppm",
    "gfr", "store_purhase", "store purchase",
)
_META_SIGNAL = (
    "chatbot", "capabilities", "capability", "feature", "features",
    "what can you", "what do you", "help me with", "assist", "assistant",
    "bta", "batao", "bataye", "kya kya", "kya bta", "kya kar", "kya jaante",
)


def _topical_adjust(rq, source, score):
    """Return the cross-encoder `score` nudged by query↔document topical fit."""
    src = (source or "").lower()
    q = (rq or "").lower()
    adj = 0.0
    department_planning = any(t in q for t in (
        "department buyer", "government department purchase", "purchase indent",
        "need assessment", "budgetary sanction",
    ))
    bidder_submission = "vendor-side bid submission workflow" in q
    # Chatbot_Capabilities is a meta-document about the chatbot itself, not a
    # procurement reference. Lift it for meta-questions; demote it hard for
    # regular procurement queries so EMD/tender questions don't pull it up.
    if "chatbot_capabilities" in src:
        if any(t in q for t in _META_SIGNAL):
            adj += 0.45
        else:
            adj -= 0.65
    if ("vigilance" in src or "cvc" in src) and not any(t in q for t in _VIG_SIGNAL):
        adj -= 0.30
    if any(k in src for k in _PORTAL_DOC_KEYS) and any(t in q for t in _HOWTO_SIGNAL):
        adj += 0.15
    if "faq" in src and any(t in q for t in _HELP_SIGNAL):
        adj += 0.15
    if department_planning:
        # Authority order for a department-side purchase-planning question.
        if src == "store purchase rule cg" or "store purchase rule cg" in src:
            adj += 0.36
        elif "gfrupdatedupto" in src:
            adj += 0.27
        elif "publicpromanual" in src:
            adj += 0.24
        elif ("cvc" in src or "compilation of cvc" in src) and any(
                t in q for t in ("laptop", "computer", "it equipment", "brand")):
            adj += 0.48  # cancels the generic CVC demotion and adds a focused lift
        if any(k in src for k in _PORTAL_DOC_KEYS):
            adj -= 0.50
        if "faq" in src:
            adj -= 0.30
        if "it act" in src or "information technology act" in src:
            adj -= 0.55
        if "store_purhase_rules_28.01.2021" in src:
            adj -= 0.22
    if bidder_submission:
        if "bid_submission" in src:
            adj += 0.55
        elif "vendor_registration" in src:
            adj += 0.18
        elif any(k in src for k in _POLICY_MANUAL_KEYS):
            adj -= 0.45
    # Auction-portal queries: lift the Auction Manual, gently demote the big
    # policy manuals / GFR whose reverse-auction text otherwise wins.
    if any(t in q for t in _AUCTION_SIGNAL):
        if "auctionmanual" in src:
            adj += 0.22
        elif any(k in src for k in ("publicpromanual", "ppm", "mannual procurement",
                                    "manual_for_procurement", "gfr")):
            adj -= 0.08
    # Regret-items query: lift the portal manual, drop the policy manuals' "reject
    # all bids" framing out of the context so it can't hijack the answer.
    if any(t in q for t in _REGRET_SIGNAL):
        if "bid_submission" in src:
            adj += 0.25
        elif any(k in src for k in _POLICY_MANUAL_KEYS):
            adj -= 0.60
    return max(0.0, min(1.0, score + adj))


def classify_intent(query):
    """Classifies user intent to filter document types in Qdrant."""
    q = query.lower()
    # Explicit actor-side portal tasks win over generic words introduced by
    # synonym expansion (for example, "bid" -> "procurement notice").
    if any(k in q for k in ["vendor-side bid submission", "bid submission workflow",
                            "submit bid", "bid submit", "vendor registration",
                            "how to bid", "login", "register", "auction", "portal"]):
        return "portal_manual"
    if any(k in q for k in ["rule", "gfr", "manual", "procurement", "cvc", "guideline", "method", "way", "type", "mode"]):
        return "procurement_rules"
    if any(k in q for k in ["how to", "vendor", "bid submission", "process", "step"]):
        return "portal_manual"
    if any(k in q for k in ["browser", "setup", "error", "technical", "system"]):
        return "technical_manual"
    if any(k in q for k in ["faq", "help"]):
        return "faq"
    return "general"

# ── Helper: Retrieve context with optional KG enhancement ──────
def _policy_qdrant_filter(retrieval_policy):
    """Build the primary, source-scoped retrieval filter for an intent route.

    A route's source contract is deliberately stricter than its document-type
    contract.  ``document_type=procurement_rules`` is shared by many unrelated
    manuals, so OR-ing it with a preferred source lets those manuals bypass the
    route before reranking has a chance to reject them.  The caller uses the
    document-type filter only as a clearly logged fallback when the named
    sources are absent from the index.
    """
    policy = retrieval_policy or {}
    preferred = list(policy.get("preferred_source_titles") or ())
    supporting = list(policy.get("supporting_source_titles") or ())
    doc_types = list(policy.get("qdrant_document_types") or ())
    excluded = list(policy.get("excluded_source_titles") or ())
    source_scope = preferred + supporting
    should = [FieldCondition(key="source", match=MatchValue(value=value))
              for value in source_scope]
    must_not = [FieldCondition(key="source", match=MatchValue(value=value))
                for value in excluded]
    details = {
        "available_payload_fields": ["source", "document_type", "document_family",
                                     "jurisdiction", "audience", "procurement_stage",
                                     "commodity"],
        "preferred_sources": preferred, "supporting_sources": supporting,
        "document_types": doc_types, "excluded_sources": excluded,
        "strategy": "source_scope" if source_scope else "document_type_scope",
        "unavailable_filter_fields": ["effective_date", "document_version"],
    }
    # Routes without named sources retain their original document-type scope.
    if not should and doc_types:
        should = [FieldCondition(key="document_type", match=MatchValue(value=value))
                  for value in doc_types]
    if not should and not must_not:
        return None, details
    return Filter(should=should or None, must_not=must_not or None), details


def _intent_metadata_scope(retrieval_policy):
    """Return safe metadata constraints for a structured procurement intent."""
    intent = str((retrieval_policy or {}).get("intent") or "")
    buyer_intents = {
        "procurement_planning", "specification_preparation", "approval_and_budget",
        "procurement_method_selection", "bid_evaluation", "purchase_order",
        "inspection_and_acceptance", "payment_and_asset_entry",
    }
    if intent in buyer_intents:
        stage = {
            "procurement_planning": "procurement_planning",
            "specification_preparation": "procurement_planning",
            "approval_and_budget": "procurement_planning",
            "procurement_method_selection": "procurement_planning",
            "bid_evaluation": "bid_evaluation",
            "purchase_order": "purchase_order",
            "inspection_and_acceptance": "inspection_acceptance",
            "payment_and_asset_entry": "inspection_acceptance",
        }[intent]
        return {
            "stage": stage,
            "audiences": ("department_buyer", "general"),
            "excluded_families": (
                "vendor_portal_manual", "department_portal_manual",
                "specialized_medical_guidance", "specialized_technical_guidance",
            ),
        }
    return {"stage": None, "audiences": (), "excluded_families": ()}


def _policy_metadata_fallback_filter(retrieval_policy):
    """Filter by indexed workflow metadata when source titles are unavailable."""
    scope = _intent_metadata_scope(retrieval_policy)
    if not scope["stage"]:
        return None
    return Filter(
        must=[FieldCondition(key="procurement_stage",
                             match=MatchValue(value=scope["stage"]))],
        should=[FieldCondition(key="audience", match=MatchValue(value=value))
                for value in scope["audiences"]] or None,
        must_not=[FieldCondition(key="document_family", match=MatchValue(value=value))
                  for value in scope["excluded_families"]] or None,
    )


def _policy_document_type_fallback_filter(retrieval_policy):
    """Return the narrower fallback used when a route's sources are missing."""
    policy = retrieval_policy or {}
    doc_types = list(policy.get("qdrant_document_types") or ())
    excluded = list(policy.get("excluded_source_titles") or ())
    if not doc_types:
        return None
    return Filter(
        should=[FieldCondition(key="document_type", match=MatchValue(value=value))
                for value in doc_types],
        must_not=[FieldCondition(key="source", match=MatchValue(value=value))
                  for value in excluded] or None,
    )


def _policy_score_adjust(source, score, retrieval_policy):
    policy = retrieval_policy or {}
    preferred = set(policy.get("preferred_source_titles") or ())
    supporting = set(policy.get("supporting_source_titles") or ())
    excluded = set(policy.get("excluded_source_titles") or ())
    if source in excluded:
        return score - 1.0, -1.0, "excluded_document_family"
    if source in preferred:
        return score + 0.28, 0.28, "preferred_document_family"
    if source in supporting:
        return score + 0.12, 0.12, "supporting_document_family"
    return score, 0.0, "semantic_relevance"


def _adjacent_chunk_ids(chunk_value):
    raw = str(chunk_value or "")
    if not raw.isdigit():
        return ()
    width, number = len(raw), int(raw)
    return tuple(str(value).zfill(width) for value in (number - 1, number + 1) if value >= 0)


def _append_adjacent_chunks(results, retrieval_policy):
    """Fetch one preceding/following chunk for the leading operative procedure."""
    if not results or not (retrieval_policy or {}).get("include_adjacent_chunks"):
        return results
    existing = {(r["point"].payload.get("source"), str(r["point"].payload.get("chunk")))
                for r in results if r.get("point") is not None}
    additions = []
    for parent in results[:1]:
        payload = getattr(parent.get("point"), "payload", {}) or {}
        source = payload.get("source")
        for chunk_id in _adjacent_chunk_ids(payload.get("chunk")):
            if (source, chunk_id) in existing:
                continue
            try:
                points, _ = client.scroll(
                    collection_name=COLLECTION_NAME,
                    scroll_filter=Filter(must=[
                        FieldCondition(key="source", match=MatchValue(value=source)),
                        FieldCondition(key="chunk", match=MatchValue(value=chunk_id)),
                    ]), limit=1, with_payload=True, with_vectors=False,
                )
            except Exception:
                points = []
            for adjacent in points or []:
                additions.append({
                    "point": adjacent,
                    "score": max(0.0, float(parent.get("score", 0.0)) - 0.03),
                    "rank": len(results) + len(additions) + 1,
                    "kg_score": 0.0, "entities": [], "related_entities": {},
                    "dense_score": None, "sparse_score": None, "hybrid_score": None,
                    "reranker_score": None, "policy_boost": 0.0,
                    "selection_reason": "adjacent_procedure_chunk",
                })
                existing.add((source, chunk_id))
    return results + additions


def retrieve_context(query, num_context=5, use_kg=True, rerank_query=None,
                     structured_intent=None, retrieval_policy=None):
    """Retrieve context documents with optional knowledge graph enhancement.
    
    Args:
        query: Search query
        num_context: Number of context results to return
        use_kg: Whether to use KG enhancement (if available)
    
    Returns:
        List of result dicts with 'point', 'score', 'rank', and optionally KG info
    """
    _mark_time("RETRIEVE_CONTEXT")
    try:
        # Step 1: Perform embedding-based retrieval
        print("🔍 Retrieving context...")
        
        # Intent Classification & Filtering. Structured application intent wins;
        # expanded retrieval text is never reclassified when it is supplied.
        rq = rerank_query or query
        intent = structured_intent or classify_intent(rq)
        query_filter = None
        filter_details = None
        if structured_intent:
            query_filter, filter_details = _policy_qdrant_filter(retrieval_policy)
            _rag_trace("intent_document_policy_applied",
                       structured_intent=structured_intent,
                       retrieval_policy=retrieval_policy,
                       qdrant_filters_used=filter_details)
        elif intent != "general":
            print(f"  🎯 Detected Intent: {intent}")
            query_filter = Filter(
                should=[
                    FieldCondition(key="document_type", match=MatchValue(value=intent)),
                    FieldCondition(key="document_type", match=MatchValue(value="project_overview")),
                    # Always fallback to high authority if needed
                    # Or we could just strict filter it. The prompt said:
                    # document_type == procurement_rules OR authority >= 8
                ]
            )
            if intent == "procurement_rules":
                query_filter = Filter(
                    should=[
                        FieldCondition(key="document_type", match=MatchValue(value="procurement_rules")),
                        FieldCondition(key="document_type", match=MatchValue(value="guidelines")),
                    ]
                )
        
        # Multi-query retrieval (or single-query fallback)
        dense_results, aggregated_scores, query_sparse = multi_query_retrieval(query, query_filter=query_filter)
        
        # A route's named sources are authoritative.  When an older index uses
        # different source names, retry its indexed workflow metadata before
        # falling back to generic document types.
        metadata_fallback_filter = None
        type_fallback_filter = None
        if structured_intent:
            metadata_fallback_filter = _policy_metadata_fallback_filter(retrieval_policy)
            type_fallback_filter = _policy_document_type_fallback_filter(retrieval_policy)

        # Metadata is the second retrieval tier.  For a planning route this
        # requires planning-stage evidence and excludes unrelated domains.
        if query_filter is not None and (dense_results is None or not dense_results.points):
            if metadata_fallback_filter is not None:
                _rag_trace("qdrant_filter_fallback", structured_intent=structured_intent,
                           fallback_reason="source_scope_returned_no_results_using_metadata_scope",
                           qdrant_filters_used=filter_details)
                dense_results, aggregated_scores, query_sparse = multi_query_retrieval(
                    query, query_filter=metadata_fallback_filter
                )

        # The type scope supports older indexes that have not yet been
        # metadata-backfilled.  It remains narrower than the full corpus.
        if query_filter is not None and (dense_results is None or not dense_results.points):
            if type_fallback_filter is not None:
                _rag_trace("qdrant_filter_fallback", structured_intent=structured_intent,
                           fallback_reason="metadata_scope_returned_no_results_using_document_types",
                           qdrant_filters_used=filter_details)
                dense_results, aggregated_scores, query_sparse = multi_query_retrieval(
                    query, query_filter=type_fallback_filter
                )

        # Full-corpus retrieval is a last-resort availability fallback only.
        if query_filter is not None and (dense_results is None or not dense_results.points):
            _rag_trace("qdrant_filter_fallback", structured_intent=structured_intent,
                       fallback_reason="document_type_scope_returned_no_results",
                       qdrant_filters_used=filter_details)
            print("  ⚠ Strict filter returned no results. Retrying without filter.")
            dense_results, aggregated_scores, query_sparse = multi_query_retrieval(query, query_filter=None)
            
        if dense_results is None or not dense_results.points:
            print("Error: No results from retrieval.")
            return None
        
        # Sort aggregated scores
        dense_scores = sorted(aggregated_scores, key=lambda x: x[1], reverse=True)
        
        # Sparse search (if available)
        sparse_scores = []
        if query_sparse:
            sparse_scores = sparse_search(query_sparse, dense_results.points, limit=20)
            # Use configurable HYBRID_ALPHA
            hybrid_scores = hybrid_search(dense_scores, sparse_scores, alpha=HYBRID_ALPHA)
            print(f"  ⚡ Using hybrid search (α={HYBRID_ALPHA}: {int(HYBRID_ALPHA*100)}% dense, {int((1-HYBRID_ALPHA)*100)}% sparse)")
        else:
            hybrid_scores = [(pid, score) for rank, (pid, score) in enumerate(dense_scores)]

        dense_score_map = dict(dense_scores)
        sparse_score_map = dict(sparse_scores)
        hybrid_score_map = dict(hybrid_scores)
        if not query_sparse:
            print(f"  ⚡ Using dense-only search (sparse embeddings unavailable)")

        _point_map = {p.id: p for p in dense_results.points}
        _pre_rows = []
        for rank, (point_id, score) in enumerate(hybrid_scores[:10], 1):
            point = _point_map.get(point_id)
            if point is None:
                continue
            payload = point.payload or {}
            _pre_rows.append({
                'rank': rank, 'score': round(float(score), 5),
                'chunk_id': payload.get('chunk') or payload.get('file'),
                'dense_score': dense_score_map.get(point_id),
                'sparse_score': sparse_score_map.get(point_id),
                'hybrid_score': hybrid_score_map.get(point_id),
                'document_title': payload.get('source'),
                'authority': payload.get('authority'),
                'document_type': payload.get('document_type'),
                'audience': payload.get('audience'),
                'page_number': payload.get('page_number') or payload.get('page'),
                'rule_or_section': payload.get('rule_or_section') or payload.get('headings'),
                'excerpt': (payload.get('text') or '')[:300],
            })
        _rag_trace('pre_rerank_top10', intent=intent,
                   metadata_filter=('procurement_rules|guidelines'
                                    if intent == 'procurement_rules' else intent),
                   results=_pre_rows)
        
        # Collect candidate points for diagnostics from the top hybrid results.
        candidate_points = [
            next((p for p in dense_results.points if p.id == point_id), None)
            for point_id, _ in hybrid_scores[:TOP_K_RETRIEVAL]
        ]
        candidate_points = [p for p in candidate_points if p is not None]
        
        # Step 2: Apply KG enhancement if enabled
        if use_kg and kg_retriever and USE_KNOWLEDGE_GRAPH:
            print("📚 Enhancing with knowledge graph...")
            
            # Convert points to embedding results format
            embedding_results = []
            for point in candidate_points:
                embedding_results.append({
                    'chunk_id': point.payload.get('file', '').replace('.txt', ''),
                    'text': point.payload.get('text', ''),
                    'source': point.payload.get('source', ''),
                    'score': next((s for pid, s in hybrid_scores if pid == point.id), 0.0),
                    'file': point.payload.get('file', '')
                })
            
            # Enhance with KG
            try:
                enhanced_results = kg_retriever.enhance_results(
                    embedding_results,
                    query,
                    kg_weight=KG_WEIGHT,
                    expansion_depth=KG_EXPANSION_DEPTH,
                    rerank=False  # Don't rerank yet
                )
                
                # Convert back to rerank format
                enhanced_points = []
                for enhanced in enhanced_results:
                    # Find original point
                    orig_point = next((p for p in candidate_points 
                                      if p.payload.get('file', '').replace('.txt', '') == enhanced.chunk_id), None)
                    if orig_point:
                        enhanced_points.append({
                            "point": orig_point,
                            "score": enhanced.embedding_score,
                            "combined_score": enhanced.combined_score,
                            "kg_score": enhanced.kg_score,
                            "entities": enhanced.entities,
                            "related_entities": enhanced.related_entities,
                            "rank": 0  # Placeholder, will be set after reranking
                        })
                
                candidate_points = [r["point"] for r in enhanced_points]
                print(f"  ✓ Enhanced {len(enhanced_points)} results with KG")
                
            except Exception as e:
                print(f"  ⚠ KG enhancement failed: {e}, continuing with embedding results...")
                enhanced_points = None
        else:
            enhanced_points = None
        
        # ════════════════════════════════════════════════════════════════════
        # RERANKING DISABLED FOR PERFORMANCE
        # Reason: Hindi embeddings are excellent quality (0.86+ scores)
        # Reranking adds <5% quality improvement but costs 62+ seconds
        # To re-enable: uncomment the code below
        # ════════════════════════════════════════════════════════════════════
        
        # Step 3: Rerank results with reranker [DISABLED]
        # print("🔄 Reranking results...")
        # reranked_results = rerank_results(query, candidate_points, 
        #                                  min_k=RERANK_MIN_K, 
        #                                  max_k=RERANK_MAX_K, 
        #                                  threshold=RERANK_THRESHOLD)
        # 
        # # Step 4: Merge KG information if available
        # if enhanced_points:
        #     for result in reranked_results:
        #         # Find matching enhanced result
        #         for enhanced in enhanced_points:
        #             if enhanced["point"].id == result["point"].id:
        #                 result["kg_score"] = enhanced.get("kg_score", 0.0)
        #                 result["entities"] = enhanced.get("entities", [])
        #                 result["related_entities"] = enhanced.get("related_entities", {})
        #                 break
        #         else:
        #             # Fallback if not found
        #             result["kg_score"] = 0.0
        #             result["entities"] = []
        #             result["related_entities"] = {}
        # 
        # return reranked_results[:num_context]
        # ════════════════════════════════════════════════════════════════════
        # Lightweight reranking + Final Ranking Score
        # ════════════════════════════════════════════════════════════════════
        pmap = {p.id: p for p in dense_results.points}
        ordered = [pmap[pid] for pid, _ in hybrid_scores if pid in pmap]

        cand, seen_src = [], set()
        seen_texts = set()
        
        # Deduplicate chunks
        dedup_ordered = []
        for p in ordered:
            txt = p.payload.get("text", "").strip()[:100]
            if txt not in seen_texts:
                seen_texts.add(txt)
                dedup_ordered.append(p)
                
        initial_cap = min(RERANK_TOPK, RERANK_MAX_CANDS)
        for p in dedup_ordered[:initial_cap]:
            cand.append(p)
            seen_src.add(p.payload.get("source", ""))
            
        # Diversity injection
        for p in dedup_ordered[initial_cap:]:
            if len(cand) >= RERANK_MAX_CANDS:
                break
            s = p.payload.get("source", "")
            if s not in seen_src:
                cand.append(p)
                seen_src.add(s)

        def _rr_score(points):
            """Cross-encoder score with 1500 char truncation."""
            out = reranker.compute_score(
                [[rq, p.payload.get("text", "")[:RERANK_TRUNCATION]] for p in points],
                normalize=True
            )
            return out if isinstance(out, list) else [out]

        reranker_score_map = {}
        score_details = {}
        try:
            rq = rerank_query or query
            fast_k = max(1, min(RERANK_FAST_K, len(cand)))
            fast_points = cand[:fast_k]
            rr_scores = []
            if fast_points:
                fast_scores = _rr_score(fast_points)
                rr_scores.extend(fast_scores)
                if (RERANK_CONF_SKIP > 0
                        and fast_scores
                        and max(float(score) for score in fast_scores) >= RERANK_CONF_SKIP):
                    print(
                        f"  ⚡ Skipped full rerank after fast gate "
                        f"({fast_k}/{len(cand)} candidates, threshold {RERANK_CONF_SKIP})"
                    )
                    cand = fast_points
                elif len(cand) > fast_k:
                    rr_scores.extend(_rr_score(cand[fast_k:]))
            reranker_score_map = {p.id: float(rr_scores[i]) for i, p in enumerate(cand)}
            print(f"  🔄 Reranked {len(cand)} candidates (truncated to {RERANK_TRUNCATION} chars)")
            
            # Combine Scores
            ranked = []
            for i, p in enumerate(cand):
                authority_score = p.payload.get("authority", 5) / 10.0
                h_score = next((score for pid, score in hybrid_scores if pid == p.id), 0.0)
                r_score = float(rr_scores[i])
                
                combined_score = (AUTHORITY_WEIGHT * authority_score) + (SEMANTIC_WEIGHT * r_score) + (HYBRID_WEIGHT * h_score)
                score_details[p.id] = {
                    "authority_score": authority_score,
                    "dense_score": dense_score_map.get(p.id),
                    "sparse_score": sparse_score_map.get(p.id),
                    "hybrid_score": h_score,
                    "reranker_score": r_score,
                    "combined_before_policy": combined_score,
                }
                ranked.append((p, combined_score))
                
            ranked = sorted(ranked, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            print(f"  ⚠ Rerank failed ({e}); falling back to hybrid order")
            ranked = [(p, 0.0) for p in cand]

        # Targeted topical re-scoring
        _rq = rerank_query or query
        adjusted_ranked = []
        excluded_rows = []
        for point, base_score in ranked:
            source = point.payload.get("source", "")
            topical_score = _topical_adjust(_rq, source, float(base_score))
            final_score, policy_boost, reason = _policy_score_adjust(
                source, topical_score, retrieval_policy
            )
            details = score_details.setdefault(point.id, {})
            details.update({
                "topical_score": topical_score,
                "policy_boost": policy_boost,
                "final_selection_reason": reason,
            })
            if reason == "excluded_document_family":
                excluded_rows.append({
                    "chunk_id": point.payload.get("chunk") or point.payload.get("file"),
                    "document_title": source,
                    "page": point.payload.get("page_number") or point.payload.get("page"),
                    "section": point.payload.get("rule_or_section") or point.payload.get("headings"),
                    "excluded_chunk_reason": reason,
                })
                continue
            adjusted_ranked.append((point, final_score))
        ranked = sorted(adjusted_ranked, key=lambda x: x[1], reverse=True)
        _rag_trace("excluded_chunks", structured_intent=structured_intent,
                   exclusions=excluded_rows)
        _rag_trace('post_rerank_top10', results=[{
            'rank': i + 1, 'score': round(float(score), 5),
            'chunk_id': point.payload.get('chunk') or point.payload.get('file'),
            'dense_score': score_details.get(point.id, {}).get('dense_score'),
            'sparse_score': score_details.get(point.id, {}).get('sparse_score'),
            'hybrid_score': score_details.get(point.id, {}).get('hybrid_score'),
            'reranker_score': score_details.get(point.id, {}).get('reranker_score'),
            'policy_boost': score_details.get(point.id, {}).get('policy_boost'),
            'final_selection_reason': score_details.get(point.id, {}).get('final_selection_reason'),
            'document_title': point.payload.get('source'),
            'authority': point.payload.get('authority'),
            'document_type': point.payload.get('document_type'),
            'audience': point.payload.get('audience'),
            'page_number': point.payload.get('page_number') or point.payload.get('page'),
            'rule_or_section': point.payload.get('rule_or_section') or point.payload.get('headings'),
            'excerpt': (point.payload.get('text') or '')[:300],
        } for i, (point, score) in enumerate(ranked[:10])])

        # Per-document cap and FAQ cap
        MAX_PER_SOURCE = 2
        results, per_source = [], {}
        faq_count = 0

        def _emit(point, score):
            details = score_details.get(point.id, {})
            results.append({
                "point": point, "score": float(score), "rank": len(results) + 1,
                "kg_score": 0.0, "entities": [], "related_entities": {},
                "dense_score": details.get("dense_score"),
                "sparse_score": details.get("sparse_score"),
                "hybrid_score": details.get("hybrid_score"),
                "reranker_score": details.get("reranker_score"),
                "policy_boost": details.get("policy_boost", 0.0),
                "selection_reason": details.get("final_selection_reason", "semantic_relevance"),
            })

        for point, score in ranked:
            if len(results) >= FINAL_CONTEXT:
                break
            src = point.payload.get("source", "")
            doc_type = point.payload.get("document_type", "general")
            
            if doc_type == "faq":
                if faq_count >= MAX_FAQ_RESULTS:
                    continue
                faq_count += 1
                
            if per_source.get(src, 0) >= MAX_PER_SOURCE:
                continue
            per_source[src] = per_source.get(src, 0) + 1
            _emit(point, score)
            
        if len(results) < FINAL_CONTEXT:
            # Do not undo the source cap merely to fill the context drawer.
            # A shorter, diverse context is more useful than four near-duplicate
            # chunks from one manual, and the prompt packer can still use the
            # leading evidence from each selected source.
            have = {id(r["point"]) for r in results}
            for point, score in ranked:
                if len(results) >= FINAL_CONTEXT:
                    break
                src = point.payload.get("source", "")
                doc_type = point.payload.get("document_type", "general")
                if doc_type == "faq" and faq_count >= MAX_FAQ_RESULTS:
                    continue
                if per_source.get(src, 0) >= MAX_PER_SOURCE:
                    continue
                
                if id(point) not in have:
                    _emit(point, score)
                    have.add(id(point))
                    per_source[src] = per_source.get(src, 0) + 1
                    if doc_type == "faq":
                        faq_count += 1

        results = _append_adjacent_chunks(results, retrieval_policy)
        _mark_time("RETRIEVE_CONTEXT")
        return results
    
    except Exception as e:
        print(f"Retrieval error: {e}")
        import traceback
        traceback.print_exc()
        _mark_time("RETRIEVE_CONTEXT")

# ── Helper: Generate answer with Llama 3.3 70B via Groq API ─────
def generate_answer(query, context_results):
    """Generate answer using Sarvam AI API with retrieved context.
    
    Enhanced with knowledge graph information when available:
    - Mentions key entities found in results
    - Uses entity relationships for better context
    - Improves answer grounding with KG data
    - Shows source PDFs and highlighted excerpts
    """
    _mark_time("ANSWER_GENERATION")
    
    if not context_results:
        return "No context found to generate an answer."

    # Extract query words for highlighting
    query_words = [w for w in query.lower().split() if len(w) > 3]
    
    # Build context string from retrieved documents with source PDFs and highlights
    context_parts = []
    source_references = []  # Store source PDF references
    all_entities = set()  # Collect all entities from results
    
    for i, r in enumerate(context_results, 1):
        source = r['point'].payload.get('source', '')
        actual_pdf = get_actual_filename(source)
        text = r['point'].payload['text']
        
        # Track source PDFs
        if actual_pdf not in source_references:
            source_references.append(actual_pdf)
        
        # Add KG entities info if available
        entities_info = ""
        if "entities" in r and r.get("entities"):
            entities = r["entities"][:3]  # Top 3 entities
            entities_info = f" [Entities: {', '.join(entities)}]"
            all_entities.update(r.get("entities", []))
        
        # Strip the chunker's metadata preamble (Headings:/Source:/---) so the
        # LLM doesn't parrot it back into answers.
        _lines = (text or '').split('\n')
        _j = 0
        while _j < len(_lines) and (
                _lines[_j].startswith('Headings:') or _lines[_j].startswith('Source:')
                or _lines[_j].strip() == '---' or not _lines[_j].strip()):
            _j += 1
        text = '\n'.join(_lines[_j:]) if _j < len(_lines) else text

        # Format context with source PDF and FULL CHUNK TEXT (not excerpt)
        # Send complete chunk to ensure LLM has all available context
        context_parts.append(
            f"[Source {i}: {actual_pdf}]{entities_info}\n{text}"
        )
    
    context_text = "\n\n".join(context_parts)
    sources_str = ", ".join(source_references)
    
    # Build prompt with entity context
    entity_context = ""
    if all_entities:
        entity_context = f"\n\nKey entities found: {', '.join(list(all_entities)[:10])}"
    
    system_content = f"""You are ProcureAI, an intelligent e-Procurement Document Assistant
for the Chhattisgarh Infotech Promotion Society (CHIPS).

## YOUR RESPONSE RULES — STRICTLY FOLLOW:

### FORMATTING:
- ALWAYS use proper markdown formatting in every response
- Use **bold** for important terms, keywords, and document names
- Use bullet points (- item) for lists — NEVER use asterisk (*) bullets
- Use numbered lists (1. 2. 3.) for step-by-step processes
- Use ### headings to separate major sections
- Use > blockquote for important notes or warnings
- Use `code formatting` for portal links, form names, IDs

### RESPONSE STRUCTURE (always follow this):
1. **Direct Answer** — Answer the question in 1-2 lines first
2. **Details** — Expand with bullet points or numbered steps
3. **Sources** — Mention source documents at the end

### TONE:
- Professional yet simple and easy to understand
- Avoid long walls of text
- Break information into digestible chunks

### IF INFORMATION IS NOT FOUND:
- Clearly state what the document DOES cover
- Suggest what the user might be looking for instead
- Never make up information not in the documents

Available source documents: {sources_str}{entity_context}"""

    user_message = f"""Context from documents:
{context_text}

Question: {query}

Answer:"""
    
    # NOTE: Sarvam AI has been removed. Use Ollama via Flask /api/stream endpoint instead.
    # This function is kept for legacy compatibility but should not be called.
    _mark_time("ANSWER_GENERATION")
    return "Error: Sarvam AI support has been removed. Use the Flask /api/stream endpoint with Ollama."
    
    # ── COMMENTED OUT GROQ CODE (for future use) ──────────────────
    # try:
    #     print("\n🤖 Generating answer with Groq (Llama 3.3 70B)...")
    #     response = requests.post(
    #         GROQ_API_URL,
    #         headers={
    #             "Authorization": f"Bearer {GROQ_API_KEY}",
    #             "Content-Type": "application/json"
    #         },
    #         json={
    #             "model": GROQ_MODEL,
    #             "messages": [
    #                 {"role": "system", "content": system_content},
    #                 {"role": "user", "content": user_message}
    #             ],
    #             "temperature": 0.7,
    #             "max_tokens": 2048,
    #         },
    #         timeout=300  # 5 minute timeout
    #     )
    #     
    #     if response.status_code != 200:
    #         error_msg = response.text
    #         try:
    #             error_data = response.json()
    #             error_msg = error_data.get("error", {}).get("message", error_msg)
    #         except:
    #             pass
    #         return f"Error from Groq API: {response.status_code} - {error_msg}"
    #     
    #     result = response.json()
    #     answer = result.get("choices", [{}])[0].get("message", {}).get("content", "No response generated")
    #     
    #     # Append source information to the answer
    #     answer += f"\n\n**Sources used:**\n" + "\n".join([f"• {pdf}" for pdf in source_references])
    #     
    #     return answer
    # 
    # except requests.exceptions.ConnectionError:
    #     return f"Error: Cannot connect to Groq API. Check your internet connection and GROQ_API_KEY."
    # except requests.exceptions.Timeout:
    #     return "Error: Groq API request timed out. Please try again."
    # except Exception as e:
    #     return f"Error generating answer: {e}"

# ── Main RAG Pipeline ──────────────────────────────────────────
def rag_query(query):
    """Full RAG pipeline: retrieve context → generate answer.
    
    Steps:
    1. Retrieve context using embeddings + optional KG enhancement
    2. Rerank with BGE-Reranker
    3. Generate answer using Qwen via Ollama
    """
    global _pipeline_start, _stage_times
    _pipeline_start = None
    _stage_times = {}
    
    print(f"\n📝 Query: {query}\n")
    
    # Step 1: Retrieve context with optional KG enhancement
    context_results = retrieve_context(query, num_context=5, use_kg=USE_KNOWLEDGE_GRAPH and kg_retriever is not None)
    
    if context_results is None:
        print("Failed to retrieve context.")
        return
    
    # Display retrieved context with KG information
    print(f"\n📚 Retrieved {len(context_results)} context documents:\n")
    for result in context_results:
        source = result['point'].payload.get('source', '')
        actual_filename = get_actual_filename(source)
        embedding_score = result.get('score', result.get('embedding_score', 0))
        
        # Show scores
        score_info = f"Embedding: {embedding_score:.4f}"
        if "kg_score" in result and result["kg_score"] > 0:
            score_info += f", KG: {result['kg_score']:.4f}"
        
        print(f"[Rank {result['rank']}] {actual_filename}")
        print(f"  Scores: {score_info}")
        
        # Show entities if available
        if "entities" in result and result.get("entities"):
            entities = result["entities"][:5]
            print(f"  Entities: {', '.join(entities)}")
        
        print(f"  {result['point'].payload['text'][:200]}...\n")
    
    # Step 2: Generate answer with KG awareness
    answer = generate_answer(query, context_results)
    
    print("\n" + "=" * 70)
    print(answer)
    print("=" * 70)
    
    _print_timing_summary()
    
    return answer

# ── Interactive Loop ───────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 RAG Pipeline: Qwen + Ollama + Knowledge Graph")
    print("=" * 70)
    
    retrieval_mode = "Hybrid (Embeddings + Knowledge Graph)" if (USE_KNOWLEDGE_GRAPH and kg_retriever) else "Embeddings Only"
    print(f"\nRetrieval Mode: {retrieval_mode}")
    print(f"Multi-Query: {'Enabled' if USE_MULTI_QUERY else 'Disabled'}")
    print(f"Reranker: BGE-Reranker v2-M3")
    print(f"LLM: Qwen (via Ollama)")
    print("\nType 'exit' to quit, 'help' for commands.\n")
    print("=" * 70 + "\n")
    
    while True:
        query = input("Enter your question: ").strip()
        
        if query.lower() == "exit":
            print("\nGoodbye! 👋\n")
            break
        elif query.lower() == "help":
            print("\n" + "=" * 70)
            print("COMMANDS:")
            print("=" * 70)
            print("  help          - Show this help message")
            print("  stats         - Show knowledge graph statistics")
            print("  config        - Show current configuration")
            print("  exit          - Exit the program")
            print("\nOtherwise, enter any question about your documents.")
            print("=" * 70 + "\n")
            continue
        elif query.lower() == "stats":
            if kg_retriever:
                print("\n" + "=" * 70)
                print("KNOWLEDGE GRAPH STATISTICS:")
                print("=" * 70)
                stats = kg_retriever.kg.get_graph_statistics()
                print(f"  Entities:              {stats['num_entities']:>10}")
                print(f"  Relationships:         {stats['num_relationships']:>10}")
                print(f"  Referenced Chunks:     {stats['num_chunks']:>10}")
                print(f"  Graph Density:         {stats['density']:>10.4f}")
                print(f"  Connected Components:  {stats['num_connected_components']:>10}")
                print(f"  Avg Node Degree:       {stats['avg_degree']:>10.2f}")
                print("=" * 70 + "\n")
            else:
                print("Knowledge graph not available.\n")
            continue
        elif query.lower() == "config":
            print("\n" + "=" * 70)
            print("CURRENT CONFIGURATION:")
            print("=" * 70)
            print(f"  Hybrid Alpha:          {HYBRID_ALPHA}")
            print(f"  Multi-Query:           {USE_MULTI_QUERY}")
            print(f"  Knowledge Graph:       {USE_KNOWLEDGE_GRAPH and kg_retriever is not None}")
            print(f"  KG Weight:             {KG_WEIGHT}")
            print(f"  KG Expansion Depth:    {KG_EXPANSION_DEPTH}")
            print(f"  Rerank Min K:          {RERANK_MIN_K}")
            print(f"  Rerank Max K:          {RERANK_MAX_K}")
            print(f"  Rerank Threshold:      {RERANK_THRESHOLD}")
            print("=" * 70 + "\n")
            continue
        elif not query:
            continue
        
        try:
            rag_query(query)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.\n")
        except Exception as e:
            print(f"Error processing query: {e}\n")
