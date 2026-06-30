from __future__ import annotations

import io

import fitz  # PyMuPDF


class ParseError(Exception):
    pass


def parse_pdf(file_bytes: bytes) -> dict:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise ParseError(f"Cannot open PDF: {exc}") from exc

    if doc.page_count == 0:
        raise ParseError("PDF contains no pages.")

    pages: list[str] = []
    for page in doc:
        pages.append(page.get_text())

    document_text = "\n\n".join(pages).strip()
    if not document_text:
        raise ParseError("PDF contains no extractable text.")

    metadata_raw = doc.metadata or {}
    metadata = {
        "author": metadata_raw.get("author", ""),
        "created_at": metadata_raw.get("creationDate", ""),
        "title": metadata_raw.get("title", ""),
        "subject": metadata_raw.get("subject", ""),
    }

    return {
        "document_text": document_text,
        "page_count": doc.page_count,
        "metadata": metadata,
    }


def parse_docx(file_bytes: bytes) -> dict:
    try:
        from docx import Document  # python-docx

        doc = Document(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ParseError(f"Cannot open DOCX: {exc}") from exc

    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    document_text = "\n\n".join(paragraphs).strip()

    if not document_text:
        raise ParseError("DOCX contains no extractable text.")

    core_props = doc.core_properties
    metadata = {
        "author": core_props.author or "",
        "created_at": str(core_props.created) if core_props.created else "",
        "title": core_props.title or "",
        "subject": core_props.subject or "",
    }

    return {
        "document_text": document_text,
        "page_count": None,
        "metadata": metadata,
    }
