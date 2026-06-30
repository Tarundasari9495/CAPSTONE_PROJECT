from __future__ import annotations

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_contract(document_text: str, contract_id: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    texts = splitter.split_text(document_text)

    return [
        {
            "text": text,
            "contract_id": contract_id,
            "chunk_index": idx,
        }
        for idx, text in enumerate(texts)
    ]
