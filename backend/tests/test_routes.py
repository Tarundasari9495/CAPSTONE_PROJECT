from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routers.auth import create_access_token


@pytest.fixture
def test_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def other_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def auth_headers(test_user_id) -> dict[str, str]:
    token = create_access_token(str(test_user_id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(other_user_id) -> dict[str, str]:
    token = create_access_token(str(other_user_id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_contract_id() -> uuid.UUID:
    return uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


# ─────────────────────────────────────────────────────────────
# Upload Tests
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_valid_pdf(auth_headers, test_user_id):
    mock_response = MagicMock()
    mock_response.contract_id = uuid.uuid4()
    mock_response.file_name = "test.pdf"
    mock_response.status = "pending"

    with patch("app.routers.contracts.validate_upload", return_value=(b"%PDF fake", "pdf")):
        with patch("app.routers.contracts.create_contract", return_value=mock_response):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                files = {"file": ("test.pdf", b"%PDF fake content", "application/pdf")}
                response = await client.post(
                    "/api/v1/contracts/upload", files=files, headers=auth_headers
                )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_upload_without_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        files = {"file": ("test.pdf", b"%PDF fake", "application/pdf")}
        response = await client.post("/api/v1/contracts/upload", files=files)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_invalid_file_type(auth_headers):
    from fastapi import HTTPException, status

    with patch(
        "app.routers.contracts.validate_upload",
        side_effect=HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "INVALID_FILE_TYPE", "message": "Only PDF and DOCX files are accepted."},
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {"file": ("test.txt", b"plain text", "text/plain")}
            response = await client.post(
                "/api/v1/contracts/upload", files=files, headers=auth_headers
            )

    assert response.status_code == 422
    assert response.json()["detail"]["error_code"] == "INVALID_FILE_TYPE"


@pytest.mark.asyncio
async def test_upload_file_too_large(auth_headers):
    from fastapi import HTTPException, status

    with patch(
        "app.routers.contracts.validate_upload",
        side_effect=HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": "FILE_TOO_LARGE", "message": "File exceeds maximum size of 20 MB."},
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            files = {"file": ("big.pdf", b"%PDF oversized", "application/pdf")}
            response = await client.post(
                "/api/v1/contracts/upload", files=files, headers=auth_headers
            )

    assert response.status_code == 422
    assert response.json()["detail"]["error_code"] == "FILE_TOO_LARGE"


# ─────────────────────────────────────────────────────────────
# Ownership / Authorization Tests
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_contract_other_user_forbidden(other_auth_headers, mock_contract_id, test_user_id):
    from fastapi import HTTPException, status

    with patch(
        "app.routers.contracts.get_contract",
        side_effect=HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "FORBIDDEN", "message": "Access denied."},
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/contracts/{mock_contract_id}", headers=other_auth_headers
            )

    assert response.status_code == 403
    assert response.json()["detail"]["error_code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_get_analysis_not_found(auth_headers, mock_contract_id):
    from fastapi import HTTPException, status

    with patch(
        "app.routers.contracts.get_analysis",
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "ANALYSIS_NOT_FOUND", "message": "Analysis has not been run."},
        ),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/contracts/{mock_contract_id}/analysis", headers=auth_headers
            )

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "ANALYSIS_NOT_FOUND"


# ─────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
