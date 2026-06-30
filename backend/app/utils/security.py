from __future__ import annotations

import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.models.contract import Contract

settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def validate_file_extension(filename: str) -> str:
    import os

    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "INVALID_FILE_TYPE",
                "message": "Only PDF and DOCX files are accepted.",
            },
        )
    return ext.lstrip(".")


def validate_file_size(size: int) -> None:
    if size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "FILE_TOO_LARGE",
                "message": f"File exceeds maximum size of {settings.max_file_size_mb} MB.",
            },
        )


def validate_magic_bytes(file_bytes: bytes, file_type: str) -> None:
    """
    Validate file magic bytes without requiring libmagic system library.
    Falls back to header-based detection for cross-platform compatibility.
    """
    if file_type == "pdf":
        if not file_bytes.startswith(b"%PDF"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_code": "INVALID_FILE_TYPE",
                    "message": "File content does not match declared type.",
                },
            )
    elif file_type == "docx":
        # DOCX is a ZIP archive starting with PK\x03\x04
        if not file_bytes.startswith(b"PK\x03\x04"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error_code": "INVALID_FILE_TYPE",
                    "message": "File content does not match declared type.",
                },
            )


async def validate_upload(file: UploadFile) -> tuple[bytes, str]:
    file_bytes = await file.read()
    await file.seek(0)

    validate_file_size(len(file_bytes))
    file_type = validate_file_extension(file.filename or "")
    validate_magic_bytes(file_bytes, file_type)

    return file_bytes, file_type


async def verify_contract_ownership(
    contract_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> Contract:
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": "Contract not found."},
        )

    if contract.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "FORBIDDEN", "message": "Access denied."},
        )

    return contract
