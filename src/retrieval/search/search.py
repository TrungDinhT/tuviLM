import faiss
from whoosh.qparser import MultifieldParser
from whoosh import index as wix
from src.retrieval.constant import FAISS_OUT,  WHOOSH_DIR
import sys


TOP_K      = 10

# 1. load artefacts -----------------------------------------------------------
faiss_index = faiss.read_index(FAISS_OUT)
whoosh_idx  = wix.open_dir(WHOOSH_DIR)

def search(query: str, k: int = TOP_K):

    results = []

    # keyword search --------------------------------------------------------------
    with whoosh_idx.searcher() as s:
        # qp   = MultifieldParser(["content", "title"], schema=whoosh_idx.schema)
        qp   = MultifieldParser(["all"], schema=whoosh_idx.schema)
        hits = s.search(qp.parse(query), limit=k)
        max_kw = max((h.score for h in hits), default=1)
        kw_scores = {h["id"]: h.score / max_kw    # normalise 0-1
                     for h in hits}
        print(kw_scores)
        for hit in hits:
            results.append({
                "id": hit["id"],
                "content": hit["content"],
                "title": hit["title"],
                "all": hit["all"],
                "score": hit.score
            })

    return results


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python search.py <query>")
        print("Example: python search.py 'cung phụ mẫu'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"🔍 Searching for: '{query}'")
    print("=" * 60)

    results = search(query)
    if not results:
        print("No results found.")
    else:
        for r in results:
            print(f"• Score: {r['score']:.3f}")
            print(f"  Title: {r['title']}")
            print(f"  Text: {r['content'][:200]}...")
            print(f"  All: {r['all'][:200]}...")
            print("  " + "-" * 60)
