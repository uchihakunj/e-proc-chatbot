"""Concurrency regressions for the shared OpenVINO inference wrappers."""

from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import threading
import time
import unittest

import numpy as np

from ov_embedder import OVEmbedder
from ov_reranker import OVReranker


class BusyModel:
    """Stub that reproduces OpenVINO's failure on concurrent infer calls."""

    def __init__(self, output_factory):
        self._busy = False
        self._state_lock = threading.Lock()
        self._output_factory = output_factory

    def __call__(self, **inputs):
        with self._state_lock:
            if self._busy:
                raise RuntimeError("Infer Request is busy")
            self._busy = True
        try:
            time.sleep(0.01)
            return self._output_factory(inputs)
        finally:
            with self._state_lock:
                self._busy = False


class TokenizerStub:
    def __call__(self, first, second=None, **_kwargs):
        size = len(first)
        return {
            "input_ids": np.ones((size, 2), dtype=np.int64),
            "attention_mask": np.ones((size, 2), dtype=np.int64),
        }


class OpenVINOThreadSafetyTests(unittest.TestCase):
    def test_reranker_serializes_shared_infer_request(self):
        reranker = OVReranker.__new__(OVReranker)
        reranker.max_length = 32
        reranker.tokenizer = TokenizerStub()
        reranker._inference_lock = threading.Lock()
        reranker.model = BusyModel(
            lambda inputs: SimpleNamespace(logits=np.ones((len(inputs["input_ids"]), 1)))
        )

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(
                lambda _: reranker.compute_score([["query", "document"]], normalize=True),
                range(12),
            ))

        self.assertEqual(len(results), 12)
        self.assertTrue(all(len(result) == 1 for result in results))

    def test_embedder_serializes_shared_infer_request(self):
        embedder = OVEmbedder.__new__(OVEmbedder)
        embedder.max_length = 32
        embedder.tokenizer = TokenizerStub()
        embedder._inference_lock = threading.Lock()
        embedder.sparse_w = np.ones((1, 2), dtype=np.float32)
        embedder.sparse_b = np.zeros((1,), dtype=np.float32)
        embedder.unused = set()
        embedder.model = BusyModel(
            lambda inputs: SimpleNamespace(
                last_hidden_state=np.ones((len(inputs["input_ids"]), 2, 2), dtype=np.float32)
            )
        )

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: embedder.encode(["query"]), range(12)))

        self.assertEqual(len(results), 12)
        self.assertTrue(all(result["dense_vecs"].shape == (1, 2) for result in results))


if __name__ == "__main__":
    unittest.main()
