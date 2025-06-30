import os
import json
from uuid import uuid4
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from modules.pinecone_ops import index

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
VECTOR_DIR = os.path.join("data", "vectorized")
os.makedirs(VECTOR_DIR, exist_ok=True)

def upsert_documents_to_pinecone(items, file_id=None, namespace=""):
    texts = []
    metadatas = []

    for item in items:
        if hasattr(item, "page_content"):
            texts.append(item.page_content)
            meta = dict(item.metadata)
            meta["text"] = item.page_content
            metadatas.append(meta)
        else:
            texts.append(item["text"])
            meta = dict(item.get("metadata", {}))
            meta["text"] = item["text"]
            metadatas.append(meta)

    embeddings = embedding_model.embed_documents(texts)

    # ✅ Save each upsert with a unique file name (to prevent overwrite)
    file_name = f"{file_id or 'doc'}_{str(uuid4())}.json"
    with open(os.path.join(VECTOR_DIR, file_name), "w", encoding="utf-8") as f:
        json.dump([
            {"text": t, "metadata": m, "embedding": e}
            for t, m, e in zip(texts, metadatas, embeddings)
        ], f, indent=2)

    # ✅ Use unique UUIDs for vector IDs
    ids = [str(uuid4()) for _ in texts]

    response = index.upsert(
        vectors=[(ids[i], embeddings[i], metadatas[i]) for i in range(len(texts))],
        namespace=namespace
    )

    return response.get("upserted_count", 0)

def embed_text(text_list):
    return embedding_model.embed_documents(text_list)
