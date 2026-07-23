# -*- coding: utf-8 -*-
"""OpenVINO-backed BGE-M3 embedder (drop-in for FlagEmbedding.BGEM3FlagModel).

Runs the BAAI/bge-m3 transformer backbone on an OpenVINO device — the Intel Arc
iGPU by default — instead of CPU torch, to remove the query-embedding latency
floor. BGE-M3 produces BOTH a dense vector and sparse lexical weights; the query
path uses both, so this class reproduces both:

  * dense  : L2-normalised [CLS] hidden state (exactly what BGE-M3 returns).
  * sparse : ReLU(sparse_linear · hidden) per token, max-pooled per token id,
             special tokens dropped — the same `lexical_weights` dict BGE-M3
             emits, with str(token_id) keys so it matches the sparse vectors
             already stored in Qdrant (which were built by BGEM3FlagModel).

The transformer (the expensive part) runs on the Arc via OpenVINO; the tiny
sparse_linear head (1024->1) runs in NumPy on CPU.

Exposes only what rag_pipeline.py uses:
    .return_sparse  (attribute, settable)
    .encode(sentences, batch_size=12, max_length=None) ->
        {"dense_vecs": np.ndarray[N,1024], "lexical_weights": list[dict]}

The exported IR is cached to disk on first run so later startups skip the
~60s convert/compile step. Any failure should be caught by the caller, which
falls back to the CPU BGEM3FlagModel.
"""
from __future__ import annotations

import glob
import os
import threading
from pathlib import Path
from typing import List, Sequence

_DEFAULT_CACHE = Path(__file__).resolve().parent / "ov_models" / "bge-m3"


def _find_sparse_linear(model_id: str) -> str:
    """Locate the cached sparse_linear.pt head weights (offline-safe)."""
    try:
        from huggingface_hub import hf_hub_download
        return hf_hub_download(model_id, "sparse_linear.pt", local_files_only=True)
    except Exception:
        hits = glob.glob(os.path.join(
            os.path.expanduser("~"), ".cache", "huggingface", "hub",
            "models--BAAI--bge-m3", "snapshots", "*", "sparse_linear.pt"))
        if hits:
            return hits[0]
        raise FileNotFoundError("sparse_linear.pt not found in the HF cache")


class OVEmbedder:
    def __init__(self, model_id: str = "BAAI/bge-m3", device: str = "GPU",
                 cache_dir: str | os.PathLike | None = None, max_length: int = 512):
        from optimum.intel import OVModelForFeatureExtraction  # lazy: heavy import
        from transformers import AutoTokenizer
        import torch
        import numpy as np

        self.max_length = max_length
        self.return_sparse = True
        # Optimum's default OpenVINO infer request is not re-entrant. Waitress
        # may call this shared model from several request threads at once.
        self._inference_lock = threading.Lock()
        cache = Path(cache_dir) if cache_dir else _DEFAULT_CACHE
        has_ir = cache.is_dir() and any(cache.glob("*.xml"))

        if has_ir:
            self.tokenizer = AutoTokenizer.from_pretrained(str(cache))
            self.model = OVModelForFeatureExtraction.from_pretrained(str(cache), device=device)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = OVModelForFeatureExtraction.from_pretrained(
                model_id, export=True, device=device)
            try:                       # persist IR so we don't re-export next launch
                cache.mkdir(parents=True, exist_ok=True)
                self.model.save_pretrained(str(cache))
                self.tokenizer.save_pretrained(str(cache))
            except Exception as e:
                print(f"[ov_embedder] could not cache IR to {cache}: {e}")

        # Sparse head: a Linear(1024, 1). Apply in NumPy on the backbone output.
        sd = torch.load(_find_sparse_linear(model_id), map_location="cpu")
        self.sparse_w = sd["weight"].float().cpu().numpy()   # [1, 1024]
        self.sparse_b = sd["bias"].float().cpu().numpy()      # [1]

        # Special tokens excluded from sparse weights (matches BGE-M3).
        tk = self.tokenizer
        self.unused = {i for i in (tk.cls_token_id, tk.eos_token_id, tk.pad_token_id,
                                   tk.unk_token_id, tk.sep_token_id, tk.bos_token_id)
                       if i is not None}
        self.device = device

    def encode(self, sentences, batch_size: int = 12, max_length: int | None = None,
               **_ignored):
        import numpy as np
        if isinstance(sentences, str):
            sentences = [sentences]
        ml = max_length or self.max_length
        dense_all: List = []
        sparse_all: List[dict] = []

        for i in range(0, len(sentences), batch_size):
            batch = list(sentences[i:i + batch_size])
            enc = self.tokenizer(batch, padding=True, truncation=True,
                                 max_length=ml, return_tensors="np")
            feed = {k: enc[k] for k in enc if k in ("input_ids", "attention_mask", "token_type_ids")}
            with self._inference_lock:
                out = self.model(**feed)
            hidden = np.asarray(getattr(out, "last_hidden_state", None)
                                if hasattr(out, "last_hidden_state") else out[0])  # [B,L,1024]

            # Dense = L2-normalised [CLS] hidden state.
            cls = hidden[:, 0]                                  # [B,1024]
            norm = np.linalg.norm(cls, axis=1, keepdims=True)
            dense_all.append(cls / np.clip(norm, 1e-12, None))

            # Sparse = ReLU(sparse_linear · hidden), max-pooled per token id.
            tok_w = np.maximum(hidden @ self.sparse_w.T + self.sparse_b, 0.0)[..., 0]  # [B,L]
            ids = enc["input_ids"]
            for b in range(len(batch)):
                d: dict = {}
                for w, idx in zip(tok_w[b], ids[b]):
                    idx = int(idx)
                    if idx in self.unused:
                        continue
                    w = float(w)
                    if w <= 0:
                        continue
                    k = str(idx)
                    if w > d.get(k, 0.0):
                        d[k] = w
                sparse_all.append(d)

        return {"dense_vecs": np.vstack(dense_all) if dense_all else np.zeros((0, 1024)),
                "lexical_weights": sparse_all}
