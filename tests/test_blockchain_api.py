import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

ANCHOR_URL = "/blockchain/api/anchor/"
VERIFY_HASH_URL = "/blockchain/api/verify-hash/"
VERIFY_URL = "/blockchain/api/verify/"


def test_anchor_requires_post(client):
    resp = client.get(ANCHOR_URL)
    assert resp.status_code in (400, 405)


def test_anchor_missing_params(client):
    resp = client.post(ANCHOR_URL, data={})
    assert resp.status_code == 400
    assert b"reference and hash_hex required" in resp.content


def test_anchor_invalid_hash_hex(client):
    resp = client.post(ANCHOR_URL, data={"reference": "INV-1", "hash_hex": "not-a-hex"})
    assert resp.status_code == 400
    assert b"hash_hex must be 64 hex chars" in resp.content


def test_anchor_and_verify_hash_happy_path(client):
    # Precomputed sha256('hello')
    hash_hex = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    ref = "INV-1001"
    # Anchor
    r1 = client.post(ANCHOR_URL, data={"reference": ref, "hash_hex": hash_hex})
    assert r1.status_code == 200
    data = r1.json()
    assert data["created"] is True
    assert data["reference"] == ref
    assert data["hash_hex"] == hash_hex

    # Verify by hash only
    r2 = client.post(VERIFY_HASH_URL, data={"hash_hex": hash_hex})
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["verified"] is True
    assert data2["count"] >= 1

    # Verify by hash + reference
    r3 = client.post(VERIFY_HASH_URL, data={"reference": ref, "hash_hex": hash_hex})
    assert r3.status_code == 200
    data3 = r3.json()
    assert data3["verified"] is True


def test_verify_hash_validation(client):
    # Missing
    r1 = client.post(VERIFY_HASH_URL, data={})
    assert r1.status_code == 400
    assert b"hash_hex required" in r1.content

    # Wrong length
    r2 = client.post(VERIFY_HASH_URL, data={"hash_hex": "abcd"})
    assert r2.status_code == 400
    assert b"hash_hex must be 64 hex chars" in r2.content


def test_verify_reference_payload_roundtrip(client):
    ref = "DOC-42"
    payload = "my document content"
    # First verify should be false
    r1 = client.post(VERIFY_URL, data={"reference": ref, "payload": payload})
    assert r1.status_code == 200
    assert r1.json()["verified"] is False

    # Anchor via /records/create/ to simulate server-side hashing flow
    rcreate = client.post("/blockchain/records/create/", data={"reference": ref, "payload": payload, "status": "anchored"})
    assert rcreate.status_code in (302, 301)

    # Verify again should be true
    r2 = client.post(VERIFY_URL, data={"reference": ref, "payload": payload})
    assert r2.status_code == 200
    assert r2.json()["verified"] is True
