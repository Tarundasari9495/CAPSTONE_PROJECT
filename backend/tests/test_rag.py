from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from app.services.rag.contract_chunker import chunk_contract


# ─────────────────────────────────────────────────────────────
# Chunker Tests
# ─────────────────────────────────────────────────────────────

def test_chunk_contract_returns_chunks():
    text = "This is a test contract. " * 200  # ~5000 chars
    chunks = chunk_contract(text, "test-contract-id")

    assert len(chunks) > 0
    for chunk in chunks:
        assert "text" in chunk
        assert "contract_id" in chunk
        assert "chunk_index" in chunk
        assert chunk["contract_id"] == "test-contract-id"


def test_chunk_contract_indexing():
    text = "Short contract text. " * 100
    chunks = chunk_contract(text, "id-123")

    indices = [c["chunk_index"] for c in chunks]
    assert indices == list(range(len(chunks)))


def test_chunk_contract_empty_text():
    chunks = chunk_contract("", "test-id")
    assert chunks == []


# ─────────────────────────────────────────────────────────────
# Embeddings Tests
# ─────────────────────────────────────────────────────────────

def test_embed_and_store_with_empty_chunks():
    from app.services.rag.contract_embeddings import embed_and_store

    # Should not raise even with empty list
    embed_and_store([], "test-contract-id")


def test_embed_and_store_calls_chromadb():
    from app.services.rag.contract_embeddings import embed_and_store

    chunks = [
        {"text": "Sample clause text.", "contract_id": "test-id", "chunk_index": 0}
    ]

    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_embeddings = MagicMock()
    mock_embeddings.embed_documents.return_value = [[0.1] * 10]

    with patch("app.services.rag.contract_embeddings._get_chroma_client", return_value=mock_client):
        with patch("app.services.rag.contract_embeddings._get_embeddings", return_value=mock_embeddings):
            embed_and_store(chunks, "test-id")

    mock_collection.add.assert_called_once()


# ─────────────────────────────────────────────────────────────
# Retriever Tests
# ─────────────────────────────────────────────────────────────

def test_retrieve_returns_empty_when_collection_missing():
    from app.services.rag.contract_retriever import retrieve_relevant_chunks

    with patch("app.services.rag.contract_retriever.chromadb.PersistentClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = Exception("Collection not found")
        mock_client_cls.return_value = mock_client

        result = retrieve_relevant_chunks("termination clause", "nonexistent-id")

    assert result == []


def test_retrieve_returns_top_k_results():
    from app.services.rag.contract_retriever import retrieve_relevant_chunks

    mock_collection = MagicMock()
    mock_collection.count.return_value = 10
    mock_collection.query.return_value = {
        "documents": [["chunk text 1", "chunk text 2"]],
        "metadatas": [[{"chunk_index": 0}, {"chunk_index": 1}]],
        "distances": [[0.1, 0.2]],
    }

    mock_client = MagicMock()
    mock_client.get_collection.return_value = mock_collection
    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.1] * 10

    with patch("app.services.rag.contract_retriever.chromadb.PersistentClient", return_value=mock_client):
        with patch("app.services.rag.contract_retriever.OpenAIEmbeddings", return_value=mock_embeddings):
            result = retrieve_relevant_chunks("termination clause", "test-id", top_k=2)

    assert len(result) == 2
    assert result[0]["text"] == "chunk text 1"
    assert result[0]["score"] == 0.9  # 1 - 0.1


# ─────────────────────────────────────────────────────────────
# File Parser Tests
# ─────────────────────────────────────────────────────────────

def test_parse_pdf_empty_raises():
    from app.utils.file_parser import ParseError, parse_pdf

    with pytest.raises(ParseError):
        parse_pdf(b"not a pdf")


def test_parse_docx_empty_raises():
    from app.utils.file_parser import ParseError, parse_docx

    with pytest.raises(ParseError):
        parse_docx(b"not a docx")
