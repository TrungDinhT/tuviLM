from whoosh.fields import Schema, TEXT, ID
from whoosh import index
from src.retrieval.constant import WHOOSH_DIR, PDF_PATH
from src.retrieval.indexing.chunking import extract_chunks_with_headers
import os, shutil

from src.retrieval.tool.vi_analyzer import get_schema


# --- Create Whoosh index directory if it doesn't exist ---
if os.path.exists(WHOOSH_DIR):
    shutil.rmtree(WHOOSH_DIR)

os.mkdir(WHOOSH_DIR)
ix = index.create_in(WHOOSH_DIR, get_schema())


# --- Load PDF and extract chunks with headers ---
chunks, metas = extract_chunks_with_headers(PDF_PATH, start_page=31, end_page=270, lower_only=True)

# --- Indexing (BM25 is default scorer; Whoosh supports BM25F for fields) ---
writer = ix.writer()
docs = [
    {
        "id": "chunk_" + str(idx),
        "title": f"Header 1 : {meta['header_1']}, header 2 : {meta['header_2']}, header 3 : {meta['header_3']}",
        "content": chunk,
        "all" : f"{meta['header_1']} {meta['header_2']} {meta['header_3']} {chunk}"
    } for idx, (chunk, meta) in enumerate(zip(chunks, metas, strict=True))
]

for d in docs:
    writer.add_document(**d)
writer.commit()
