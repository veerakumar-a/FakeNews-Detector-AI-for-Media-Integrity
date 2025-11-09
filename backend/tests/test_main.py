from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_analyze_with_text():
    payload = {"text": "This is a shocking secret miracle cure!"}
    r = client.post("/analyze", json=payload)
    assert r.status_code == 200
    data = r.json()
    # basic shape checks
    assert "label" in data
    assert "confidence" in data
    assert "sentiment" in data
    assert "highlighted" in data
    assert "keywords" in data


def test_analyze_requires_text_or_url():
    r = client.post("/analyze", json={})
    assert r.status_code == 400


def test_summarize_and_bias_and_factcheck():
    payload = {"text": "This is a simple test. The quick brown fox jumps over the lazy dog.\nThe miracle cure claim is suspicious and lacks evidence. Experts disagree."}
    r = client.post("/summarize", json=payload)
    assert r.status_code == 200
    assert "summary" in r.json()

    r2 = client.post("/bias", json=payload)
    assert r2.status_code == 200
    b = r2.json()
    assert "label" in b and "score" in b

    r3 = client.post("/fact-check", json=payload)
    assert r3.status_code == 200
    assert "results" in r3.json()
