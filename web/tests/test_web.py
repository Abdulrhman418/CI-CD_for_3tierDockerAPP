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

def test_home_page(monkeypatch):
    # Mock requests.get
    class DummyResponse:
        def __init__(self):
            self.status_code = 200  # Must have
        def json(self):
            return [{"id": 1, "name": "Test Product", "price": 10.0}]

    monkeypatch.setattr("requests.get", lambda url, **kwargs: DummyResponse())

    client = flask_app.test_client()
    rv = client.get("/")
    assert rv.status_code == 200
    assert "Test Product" in rv.get_data(as_text=True)


