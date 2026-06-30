from __future__ import annotations

import chromadb
from langchain_openai import OpenAIEmbeddings

from app.config import get_settings

settings = get_settings()


def _get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.litellm_embedding_model or settings.embedding_model,
        openai_api_key=settings.litellm_api_key or settings.openai_api_key,
        openai_api_base=settings.litellm_base_url or None,
    )


def embed_and_store(chunks: list[dict], contract_id: str) -> None:
    if not chunks:
        return

    client = _get_chroma_client()
    collection_name = f"contract_{contract_id.replace('-', '_')}"

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"contract_id": contract_id},
    )

    embeddings_model = _get_embeddings()
    texts = [c["text"] for c in chunks]
    embeddings = embeddings_model.embed_documents(texts)

    collection.add(
        ids=[f"{contract_id}_{c['chunk_index']}" for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {"contract_id": c["contract_id"], "chunk_index": c["chunk_index"]}
            for c in chunks
        ],
    )


def delete_contract_collection(contract_id: str) -> None:
    client = _get_chroma_client()
    collection_name = f"contract_{contract_id.replace('-', '_')}"
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
