import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os

os.environ["DATABASE_URL"] = "postgresql://fake:fake@localhost/fake"

def test_health_endpoint():
    """Test /health sans démarrer l'app ni connecter la DB"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[])
    
    with patch("asyncpg.connect", return_value=mock_conn):
        from fastapi.testclient import TestClient
        import main
        
        # Override startup pour éviter la vraie connexion DB
        main.app.router.on_startup = []
        main.app.router.on_shutdown = []
        main.app.state.db = mock_conn
        
        client = TestClient(main.app, raise_server_exceptions=False)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

def test_products_requires_db():
    """Vérifie que l'endpoint /products existe"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    import main
    
    routes = [r.path for r in main.app.routes]
    assert "/products" in routes

def test_product_model():
    """Test le modèle Product sans DB"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import Product
    
    p = Product(name="Test Laptop", price=999.99, category="electronics", stock=10)
    assert p.name == "Test Laptop"
    assert p.price == 999.99
    assert p.stock == 10
