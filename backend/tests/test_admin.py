from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_admin_votes_and_subscriptions():
    r = client.get('/admin/votes')
    assert r.status_code == 200
    data = r.json()
    assert 'votes' in data

    r2 = client.get('/admin/subscriptions')
    assert r2.status_code == 200
    d2 = r2.json()
    assert 'subscriptions' in d2 and 'count' in d2
