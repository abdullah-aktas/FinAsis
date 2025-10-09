import pytest

pytestmark = pytest.mark.django_db


def test_homepage_ok(client):
    resp = client.get('/')
    assert resp.status_code == 200
    body = resp.content.lower()
    # Look for ROI calculator presence
    assert (b"roi" in body) or (b"h\xc4\xb1zl\xc4\xb1 roi" in body) or (b"roi hesaplay\xc4\xb1c\xc4\xb1" in body)


def test_audit_landing_ok(client):
    resp = client.get('/audit/')
    assert resp.status_code == 200
    body = resp.content.lower()
    # Turkish diacritics might vary in environments, check loosely
    assert (b"denetim" in body) or (b"ic denetim" in body)
