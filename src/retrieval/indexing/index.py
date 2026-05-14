import numpy as np
import json, os, faiss, pdfplumber
from tqdm import tqdm
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemmingAnalyzer

from src.retrieval.constant import CHUNK_SIZE, FAISS_OUT, META_JSON, PDF_PATH, REMOVE_PHRASE, STRIDE, WHOOSH_DIR
from src.retrieval.indexing.chunking import extract_chunks_with_headers


# 1  /  6  Load + chunk --------------------------------------------------------
chunks, metas = extract_chunks_with_headers(PDF_PATH, start_page=31, end_page=270)
# 2  /  6  Embeddings ----------------------------------------------------------
# model = JinaEmbeddings()
# embeddings = []
# with open("data/index/faiss/jina_embeddings.jsonl") as fo:
#     for line in fo:
#         data = json.loads(line)
#         if "embedding" in data:
#             embeddings.append(data["embedding"])
#         else:
#             print(f"Warning: No embedding found for chunk {data.get('index', 'unknown')}")

# embeddings = np.array(embeddings, dtype=np.float32)

# result = model.get_embeddings(chunks, batch_size=10)



# 3  /  6  FAISS index ---------------------------------------------------------
# index_flat = faiss.IndexFlatIP(embeddings.shape[1])      # cosine sim (because normalised)
# index_flat.add(embeddings)
# faiss.write_index(index_flat, FAISS_OUT)

# 4  /  6  Whoosh index --------------------------------------------------------
schema = Schema(id=ID(stored=True),
                content=TEXT(stored=False, analyzer=StemmingAnalyzer()))
if not os.path.exists(WHOOSH_DIR): os.mkdir(WHOOSH_DIR)
ix = index.create_in(WHOOSH_DIR, schema)
w = ix.writer()
for i, (chunk, meta) in tqdm(enumerate(zip(chunks, metas))):
    w.add_document(id=str(i), content=f"Metadata: {json.dumps(meta)}. Text: {chunk}")
w.commit()

# 5  /  6  Persist chunk text + metadata --------------------------------------
with open(META_JSON, "w") as f:
    for i, meta in enumerate(metas):
        f.write(json.dumps({"id": i, "text": chunks[i], **meta}) + "\n")

print(f"✅  {len(chunks)} chunks indexed")
