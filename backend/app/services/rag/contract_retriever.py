from __future__ import annotations

import chromadb
from langchain_openai import OpenAIEmbeddings

from app.config import get_settings

settings = get_settings()


def retrieve_relevant_chunks(
    query: str,
    contract_id: str,
    top_k: int = 5,
) -> list[dict]:
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection_name = f"contract_{contract_id.replace('-', '_')}"

    try:
        collection = client.get_collection(collection_name)
    except Exception:
        return []

    embeddings_model = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )
    query_embedding = embeddings_model.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks: list[dict] = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, distances):
        chunks.append(
            {
                "text": doc,
                "chunk_index": meta.get("chunk_index", 0),
                "score": round(1 - dist, 4),  # Convert distance to similarity
            }
        )

    return chunks
