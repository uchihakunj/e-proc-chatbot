# -*- coding: utf-8 -*-
"""Parity probe: OVEmbedder (Arc/OpenVINO) vs CPU BGEM3FlagModel.

Confirms the OpenVINO embedder reproduces BGE-M3's dense vector and sparse
lexical weights closely enough that retrieval is unaffected, BEFORE enabling it
(EMBEDDER_BACKEND=openvino) in production. Reports, per query:
  * dense cosine similarity  (want >= ~0.999)
  * sparse token-id overlap  (Jaccard of the non-zero token sets)
  * sparse weight correlation on the shared tokens
"""
import sys, time
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUERIES = [
    "What is EMD and when is it exempted?",
    "What is the step-by-step process for CHiPS vendor registration?",
    "Under GFR and government rules, what is the procedure for MSME procurement?",
    "performance security in a work contract",
    "EMD रिफंड की प्रक्रिया क्या है?",
]


def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def main():
    from FlagEmbedding import BGEM3FlagModel
    from ov_embedder import OVEmbedder

    print("Loading CPU BGEM3FlagModel…")
    cpu = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
    cpu.return_sparse = True
    print("Loading OVEmbedder (Arc GPU)…")
    t0 = time.time()
    ov = OVEmbedder("BAAI/bge-m3", device="GPU")
    print(f"  OV ready in {time.time()-t0:.1f}s")

    dense_sims, jaccards, weight_corrs = [], [], []
    cpu_t, ov_t = 0.0, 0.0
    for q in QUERIES:
        t = time.time(); ce = cpu.encode([q], batch_size=1, max_length=512); cpu_t += time.time()-t
        t = time.time(); oe = ov.encode([q], batch_size=1, max_length=512); ov_t += time.time()-t

        ds = cosine(np.asarray(ce["dense_vecs"][0]), np.asarray(oe["dense_vecs"][0]))
        dense_sims.append(ds)

        cw = {k: float(v) for k, v in dict(ce["lexical_weights"][0]).items()}
        ow = oe["lexical_weights"][0]
        cs, os_ = set(cw), set(ow)
        jac = len(cs & os_) / len(cs | os_) if (cs | os_) else 1.0
        jaccards.append(jac)
        shared = sorted(cs & os_)
        if len(shared) >= 2:
            cc = np.corrcoef([cw[k] for k in shared], [ow[k] for k in shared])[0, 1]
            weight_corrs.append(float(cc))

        print(f"\nQ: {q[:55]}")
        print(f"  dense cosine     : {ds:.5f}")
        print(f"  sparse Jaccard   : {jac:.3f}  (cpu={len(cs)} ov={len(os_)} shared={len(cs & os_)})")
        if len(shared) >= 2:
            print(f"  sparse wt corr   : {weight_corrs[-1]:.3f}")

    print("\n===== SUMMARY =====")
    print(f"dense cosine  min/mean : {min(dense_sims):.5f} / {np.mean(dense_sims):.5f}")
    print(f"sparse Jaccard min/mean: {min(jaccards):.3f} / {np.mean(jaccards):.3f}")
    if weight_corrs:
        print(f"sparse wt corr mean    : {np.mean(weight_corrs):.3f}")
    print(f"latency  cpu/ov (5 q)  : {cpu_t:.2f}s / {ov_t:.2f}s")
    ok = min(dense_sims) >= 0.99 and min(jaccards) >= 0.8
    print(f"\nVERDICT: {'PASS — safe to enable EMBEDDER_BACKEND=openvino' if ok else 'FAIL — keep CPU embedder'}")


if __name__ == "__main__":
    main()
