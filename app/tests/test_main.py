import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(autouse=True)
def mock_db():
    """Mock asyncpg pour tous les tests — pas besoin de vraie DB en CI"""
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = []
    mock_conn.fetchrow.return_value = None
    mock_conn.execute.return_value = "OK"
    with patch("asyncpg.connect", return_value=mock_conn):
        yield mock_conn

def test_health():
    with patch("asyncpg.connect", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = AsyncMock()
        mock_connect.return_value.execute = AsyncMock()
        import importlib
        import main
        importlib.reload(main)
        client = TestClient(main.app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_list_products_empty():
    import main
    client = TestClient(main.app)
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == []
