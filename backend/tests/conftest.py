"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture(autouse=True)
def mock_db_lifespan():
    """Prevent lifespan from attempting real DB connections during tests."""
    with patch("app.main.engine") as mock_engine:
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_engine.connect.return_value = mock_conn
        mock_engine.dispose = AsyncMock()
        yield
