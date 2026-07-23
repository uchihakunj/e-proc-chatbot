# -*- coding: utf-8 -*-
"""OpenVINO-backed cross-encoder reranker (drop-in for FlagEmbedding.FlagReranker).

Runs BAAI/bge-reranker-v2-m3 on an OpenVINO device — the Intel Arc iGPU by
default — instead of CPU torch. Verified identical scores/ranking vs the CPU
FlagReranker (max score diff ~1e-4) at ~30x lower latency on this hardware,
which removes the reranker as the per-query latency floor.

Exposes the only method rag_pipeline.py calls:
    compute_score(pairs, normalize=False, max_length=256) -> list[float]

The exported IR is cached to disk on first run so subsequent startups skip the
~60s convert/compile step.
"""
from __future__ import annotations

import math
import os
import threading
from pathlib import Path
from typing import List, Sequence

_DEFAULT_CACHE = Path(__file__).resolve().parent / "ov_models" / "bge-reranker-v2-m3"


class OVReranker:
    def __init__(self, model_id: str = "BAAI/bge-reranker-v2-m3",
                 device: str = "GPU", cache_dir: str | os.PathLike | None = None,
                 max_length: int = 256):
        from optimum.intel import OVModelForSequenceClassification  # lazy: heavy import
        from transformers import AutoTokenizer

        self.max_length = max_length
        # A compiled OpenVINO model owns a default infer request which cannot be
        # used concurrently. Serialize only the device call; tokenization and
        # score conversion can still run in parallel.
        self._inference_lock = threading.Lock()
        cache = Path(cache_dir) if cache_dir else _DEFAULT_CACHE
        has_ir = cache.is_dir() and any(cache.glob("*.xml"))

        if has_ir:
            self.tokenizer = AutoTokenizer.from_pretrained(str(cache))
            self.model = OVModelForSequenceClassification.from_pretrained(
                str(cache), device=device)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = OVModelForSequenceClassification.from_pretrained(
                model_id, export=True, device=device)
            try:                       # persist IR so we don't re-export next launch
                cache.mkdir(parents=True, exist_ok=True)
                self.model.save_pretrained(str(cache))
                self.tokenizer.save_pretrained(str(cache))
            except Exception as e:
                print(f"[ov_reranker] could not cache IR to {cache}: {e}")

        self.device = device

    def compute_score(self, pairs: Sequence[Sequence[str]],
                      normalize: bool = False,
                      max_length: int | None = None, **_ignored) -> List[float]:
        """Score query↔document pairs. Mirrors FlagReranker.compute_score:
        returns a list of floats (sigmoid-normalised to 0-1 when normalize=True)."""
        import numpy as np
        if not pairs:
            return []
        ml = max_length or self.max_length
        queries = [p[0] for p in pairs]
        docs = [p[1] for p in pairs]
        enc = self.tokenizer(queries, docs, padding=True, truncation=True,
                             max_length=ml, return_tensors="np")
        with self._inference_lock:
            logits = self.model(**{k: enc[k] for k in enc}).logits
        logits = np.asarray(logits).reshape(-1)
        if normalize:
            return [1.0 / (1.0 + math.exp(-float(x))) for x in logits]
        return [float(x) for x in logits]
