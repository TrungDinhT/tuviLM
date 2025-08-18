import json, faiss
from pathlib import Path
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
    import sys

    if len(sys.argv) < 2:
        print("Usage: python search.py <query>")
        print("Example: python search.py 'cung phụ mẫu'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"🔍 Searching for: '{query}'")
    print("=" * 60)

    results = search(query, )
    if not results:
        print("No results found.")
    else:
        for hit in results:
            print(f"• Score: {hit['score']:.3f}")
            if hit.get('header_1'):
                print(f"  Header 1: {hit['header_1']}")
            if hit.get('header_2'):
                print(f"  Header 2: {hit['header_2']}")
            if hit.get('header_3'):
                print(f"  Header 3: {hit['header_3']}")
            print(f"  Text: {hit['text'][:500]}...")
            print("  " + "-" * 60)
