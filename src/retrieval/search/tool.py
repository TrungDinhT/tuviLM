
from whoosh import index as wix
from whoosh.qparser import MultifieldParser
from src.retrieval.constant import WHOOSH_DIR

def search(query: str, k: int = 10):
    print(f"Searching for: '{query}'")

    results = []

    whoosh_idx = wix.open_dir(WHOOSH_DIR)

    # keyword search --------------------------------------------------------------
    with whoosh_idx.searcher() as s:
        # qp   = MultifieldParser(["content", "title"], schema=whoosh_idx.schema)
        qp   = MultifieldParser(["all"], schema=whoosh_idx.schema)
        hits = s.search(qp.parse(query), limit=k)

        for hit in hits:
            results.append({
                "id": hit["id"],
                "content": hit["content"],
                "title": hit["title"],
                "score": hit.score
            })

    return results

def search_start_info(name : str) -> dict[str, str]:
    return search(f"Đặc tính sao {name}", k=1)

def search_start_role_info(name : str, role : str) -> dict[str, str]:
    return search(f"sao {name} tại cung {role}", k=3)

def search_role_info(role : str) -> dict[str, str]:
    return search(f"Cung {role}", k=2)
