import json, faiss, math
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from whoosh.qparser import MultifieldParser
from whoosh import index as wix
from src.retrieval.constant import FAISS_OUT, META_JSON, WHOOSH_DIR
from src.retrieval.indexing.embed import JinaEmbeddings


TOP_K      = 10
ALPHA      = 0.5        # weight on semantic vs keyword [0–1]

# 1. load artefacts -----------------------------------------------------------
model = JinaEmbeddings()
faiss_index = faiss.read_index(FAISS_OUT)
whoosh_idx  = wix.open_dir(WHOOSH_DIR)
meta        = {int(j["id"]): j for j in map(json.loads, Path(META_JSON).read_text().splitlines())}

def search(query: str, k: int = TOP_K, alpha: float = ALPHA):
    # 2. semantic -------------------------------------------------------------
    # emb = model.get_single_embedding(query)
    # emb = np.array(emb, dtype=np.float32).reshape(1, -1)  # ensure shape (1, dim)
    # D, I = faiss_index.search(emb, k)         # dot-product == cosine
    # sem_scores = {idx: float(score)           # already in [-1,1], higher = better
    #               for idx, score in zip(I[0], D[0])}

    # 3. keyword --------------------------------------------------------------
    with whoosh_idx.searcher() as s:
        qp   = MultifieldParser(["content"], schema=whoosh_idx.schema)
        hits = s.search(qp.parse(query), limit=k)
        max_kw = max((h.score for h in hits), default=1)
        kw_scores = {int(h["id"]): h.score / max_kw    # normalise 0-1
                     for h in hits}
        print(kw_scores)

    # 4. fuse both ------------------------------------------------------------
    fused = {}
    # for idx in set(sem_scores) | set(kw_scores):
    for idx in set(kw_scores):
        # fused[idx] = alpha * sem_scores.get(idx, 0) + \
        fused[idx] = (1 - alpha) * kw_scores.get(idx, 0)

    top = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:k]
    return [{"score": round(score, 3), **meta[idx]} for idx, score in top]

if __name__ == "__main__":
    while True:
        q = input("❓ Query (empty = quit): ").strip()
        if not q: break
        for hit in search(q):
            print(f"• p.{hit['page']:>3}  {hit['score']:.3f}  {hit['text']}")
            print("  " + "-" * 60)
        print("-" * 60)
