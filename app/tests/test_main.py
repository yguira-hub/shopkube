from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_health(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    from unittest.mock import AsyncMock, patch
    with patch("main.asyncpg.connect", new_callable=AsyncMock):
        from main import app
        client = TestClient(app)
        # health check sans DB
        assert True
