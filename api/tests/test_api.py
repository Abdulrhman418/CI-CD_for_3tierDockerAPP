import os
import sys
import pytest

# Add parent directory to path to import app module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    client = flask_app.test_client()
    yield client

def test_get_products_empty(monkeypatch):
    # Mock db connection to return empty list
    class DummyCursor:
        def execute(self, q): pass
        def fetchall(self): return []
        def close(self): pass

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("app.get_db_connection", lambda: DummyConn())

    client = flask_app.test_client()
    rv = client.get("/products")
    assert rv.status_code == 200
    assert rv.get_json() == []

