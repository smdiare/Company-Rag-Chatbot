from pinecone import Pinecone, ServerlessSpec
from utils.env_loader import get_env_var
from uuid import uuid4
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

# ✅ Initialize Pinecone client
pc = Pinecone(api_key=get_env_var("PINECONE_API_KEY"))

# ✅ Embedding setup
embedding = GoogleGenerativeAIEmbeddings(
    model=get_env_var("EMBEDDING_MODEL"),
    google_api_key=get_env_var("GOOGLE_API_KEY")
)

# ✅ Index configuration
INDEX_NAME = get_env_var("PINECONE_INDEX_NAME")
DIMENSION = 768

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)

def search_pinecone(embedding_vector, top_k=5, namespace=""):
    response = index.query(
        vector=embedding_vector,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
    return response

def upsert_documents_to_pinecone(documents, namespace="", file_id=None):
    texts = [doc.page_content for doc in documents]
    embeddings = embedding.embed_documents(texts)

    # ✅ Use UUIDs for every vector
    ids = [str(uuid4()) for _ in range(len(texts))]

    vectors = [
        (ids[i], embeddings[i], {"text": texts[i]})
        for i in range(len(texts))
    ]

    response = index.upsert(vectors=vectors, namespace=namespace)
    return response.get("upserted_count", 0)

def get_top_context(query_embedding, threshold=0.75, namespace=""):
    result = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True,
        namespace=namespace
    )

    relevant_chunks = [
        match['metadata']['text']
        for match in result['matches']
        if match['score'] >= threshold and 'text' in match['metadata']
    ]

    return "\n\n".join(relevant_chunks)
