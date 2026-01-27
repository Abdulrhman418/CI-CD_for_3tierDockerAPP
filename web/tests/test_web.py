import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    client = flask_app.test_client()
    yield client

def test_home_page(monkeypatch):
    # Mock requests.get
    class DummyResponse:
        def json(self): return [{"id": 1, "name": "Test Product", "price": 10.0}]

    monkeypatch.setattr("requests.get", lambda url: DummyResponse())

    client = flask_app.test_client()
    rv = client.get("/")
    assert rv.status_code == 200
    assert "Test Product" in rv.get_data(as_text=True)

