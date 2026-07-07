import os
import atexit
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Any
import requests
from qdrant_client import QdrantClient
from FlagEmbedding import BGEM3FlagModel, FlagReranker

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-20s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

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
    
    return {
        "chunk_dir": chunk_dir,
        "collection": os.getenv("CHIPPY_QDRANT_COLLECTION", "db3"),
        "qdrant_local_path": qdrant_path,
        "encode_batch_size": int(os.getenv("STAGE4_BATCH_SIZE", "8")),
        "max_length": int(os.getenv("STAGE4_MAX_LENGTH", "1024")),
    }

CFG = _get_config()
CHUNK_DIR = CFG["chunk_dir"]
COLLECTION_NAME = CFG["collection"]
ENCODE_BATCH_SIZE = CFG["encode_batch_size"]
MAX_LENGTH = CFG["max_length"]

# ── Retrieval Configuration ────────────────────────────────────
HYBRID_ALPHA = 0.6           # 0.0 = pure sparse, 1.0 = pure dense (0.6 = 60% dense, 40% sparse)
RERANK_MIN_K = 3             # Minimum results to return
RERANK_MAX_K = 6             # Maximum results to return
RERANK_THRESHOLD = 0.65      # Score threshold for inclusion

# ── Reranker latency tuning (env-overridable) ──────────────────
# The CPU cross-encoder is the per-query latency floor, and its cost is linear
# in the number of candidates it scores. These bound that work and let easy
# queries skip most of it. See the inline reranker in retrieve_context().
RERANK_TOPK      = int(os.getenv("RERANK_TOPK", "8"))           # always rerank the top hybrid hits (was 10)
RERANK_MAX_CANDS = int(os.getenv("RERANK_MAX_CANDS", "10"))     # + diversity-injected sources (was 18)
RERANK_FAST_K    = int(os.getenv("RERANK_FAST_K", "4"))         # confidence-gate: score these first
RERANK_CONF_SKIP = float(os.getenv("RERANK_CONF_SKIP", "0.92")) # if best fast score ≥ this, skip the rest (0=off)
USE_MULTI_QUERY = True       # Enable multi-query retrieval for better coverage
USE_KNOWLEDGE_GRAPH = True   # Enable knowledge graph enhancement
KG_WEIGHT = 0.3              # Weight of KG in combined score (0-1)
KG_EXPANSION_DEPTH = 2       # Entity graph traversal depth

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
        print(f"⚠ Could not import knowledge graph modules: {e}")
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
    
    return unique_variations[:5]  # Cap at 5 variations to avoid excessive querying

# ── Helper: Single query retrieval ─────────────────────────────
def perform_single_retrieval(query):
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
            limit=20
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
def multi_query_retrieval(query):
    """Retrieve results using multiple query variations and merge them.
    
    Benefits:
    - Captures different aspects of the query
    - Better coverage of semantically related documents
    - More robust to query phrasing variations
    """
    _mark_time("MULTI_QUERY_RETRIEVAL")
    
    if not USE_MULTI_QUERY:
        # Fall back to single query
        result = perform_single_retrieval(query)
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
        retrieval_result = perform_single_retrieval(q_variant)
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


# ── Helper: Retrieve context with optional KG enhancement ──────
def retrieve_context(query, num_context=5, use_kg=True, rerank_query=None):
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
        
        # Multi-query retrieval (or single-query fallback)
        dense_results, aggregated_scores, query_sparse = multi_query_retrieval(query)
        
        if dense_results is None or not dense_results.points:
            print("Error: No results from retrieval.")
            return None
        
        # Sort aggregated scores
        dense_scores = sorted(aggregated_scores, key=lambda x: x[1], reverse=True)
        
        # Sparse search (if available)
        if query_sparse:
            sparse_scores = sparse_search(query_sparse, dense_results.points, limit=20)
            # Use configurable HYBRID_ALPHA
            hybrid_scores = hybrid_search(dense_scores, sparse_scores, alpha=HYBRID_ALPHA)
            print(f"  ⚡ Using hybrid search (α={HYBRID_ALPHA}: {int(HYBRID_ALPHA*100)}% dense, {int((1-HYBRID_ALPHA)*100)}% sparse)")
        else:
            hybrid_scores = [(pid, score) for rank, (pid, score) in enumerate(dense_scores)]
            print(f"  ⚡ Using dense-only search (sparse embeddings unavailable)")
        
        # Collect candidate points for reranking (from top 20 hybrid results)
        candidate_points = [
            next((p for p in dense_results.points if p.id == point_id), None)
            for point_id, _ in hybrid_scores[:20]
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
        # Lightweight reranking + per-document cap
        # ════════════════════════════════════════════════════════════════════
        # Hybrid RRF buries small/specific docs (measured: the offline-tenders
        # manual sits at hybrid rank ~22 while a cross-encoder scores it 0.95).
        # Rerank a diversity-injected candidate set so true relevance wins, then
        # cap each source so one big manual can't fill every slot. Inputs are
        # truncated to 512 chars (max_length 256) — ~4x faster on CPU (~7s vs
        # ~30s for 18 candidates) with no measurable ranking loss.
        pmap = {p.id: p for p in dense_results.points}
        ordered = [pmap[pid] for pid, _ in hybrid_scores if pid in pmap]

        cand, seen_src = [], set()
        for p in ordered[:RERANK_TOPK]:
            cand.append(p)
            seen_src.add(p.payload.get("source", ""))
        # Diversity injection: the best hybrid chunk from each source not already
        # represented, so a low-ranked small doc still reaches the reranker.
        for p in ordered[RERANK_TOPK:]:
            if len(cand) >= RERANK_MAX_CANDS:
                break
            s = p.payload.get("source", "")
            if s not in seen_src:
                cand.append(p)
                seen_src.add(s)

        def _rr_score(points):
            """Cross-encoder score for query↔chunk pairs (normalised 0-1)."""
            out = reranker.compute_score(
                [[rq, p.payload.get("text", "")[:512]] for p in points],
                normalize=True, max_length=256,
            )
            return out if isinstance(out, list) else [out]

        try:
            # Rerank against the ORIGINAL user question (rerank_query), not the
            # synonym-expanded retrieval query — expansion aids recall but skews
            # the cross-encoder toward generic manuals.
            rq = rerank_query or query
            # Confidence gate: score the top RERANK_FAST_K first; if one is already
            # a strong match (≥ RERANK_CONF_SKIP) the answer is settled, so skip the
            # cross-encoder on the remaining (mostly diversity-injected) candidates —
            # they keep their hybrid order below the confident hit. On harder queries
            # the gate doesn't trip and we rerank everything as before.
            fast_n = min(RERANK_FAST_K, len(cand)) if RERANK_CONF_SKIP > 0 else len(cand)
            fast_scores = _rr_score(cand[:fast_n])
            if RERANK_CONF_SKIP > 0 and fast_n < len(cand) \
                    and max(fast_scores) >= RERANK_CONF_SKIP:
                print(f"  ⚡ Rerank early-exit: top={max(fast_scores):.2f} "
                      f">={RERANK_CONF_SKIP}, scored {fast_n}/{len(cand)} candidates")
                # Remaining candidates sit just below the reranked set, in hybrid order.
                tail = [(p, -1.0 - i * 1e-3) for i, p in enumerate(cand[fast_n:])]
                ranked = sorted(zip(cand[:fast_n], fast_scores),
                                key=lambda x: x[1], reverse=True) + tail
            else:
                rest_scores = _rr_score(cand[fast_n:]) if fast_n < len(cand) else []
                rr_scores = list(fast_scores) + list(rest_scores)
                print(f"  🔄 Reranked {len(cand)} candidates (truncated)")
                ranked = sorted(zip(cand, rr_scores), key=lambda x: x[1], reverse=True)
        except Exception as e:
            print(f"  ⚠ Rerank failed ({e}); falling back to hybrid order")
            ranked = [(p, 0.0) for p in ordered]

        # Targeted topical re-scoring (Vigilance/CVC magnet demotion + portal
        # how-to boost), then re-sort. See _topical_adjust for the rationale.
        _rq = rerank_query or query
        ranked = sorted(
            ((p, _topical_adjust(_rq, p.payload.get("source", ""), float(s))) for p, s in ranked),
            key=lambda x: x[1], reverse=True,
        )

        # Per-document cap over the reranked order.
        MAX_PER_SOURCE = 2
        results, per_source = [], {}

        def _emit(point, score):
            results.append({
                "point": point, "score": float(score), "rank": len(results) + 1,
                "kg_score": 0.0, "entities": [], "related_entities": {},
            })

        for point, score in ranked:
            if len(results) >= num_context:
                break
            src = point.payload.get("source", "")
            if per_source.get(src, 0) >= MAX_PER_SOURCE:
                continue
            per_source[src] = per_source.get(src, 0) + 1
            _emit(point, score)
        if len(results) < num_context:  # relax cap if corpus diversity is low
            have = {id(r["point"]) for r in results}
            for point, score in ranked:
                if len(results) >= num_context:
                    break
                if id(point) not in have:
                    _emit(point, score)
                    have.add(id(point))

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
