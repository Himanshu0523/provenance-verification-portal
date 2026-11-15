import base64
import hashlib
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

def make_keypair():
    priv = Ed25519PrivateKey.generate()
    raw_pub = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return priv, base64.b64encode(raw_pub).decode(), hashlib.sha256(raw_pub).hexdigest()

def sign(priv, payload: str) -> str:
    return base64.b64encode(priv.sign(payload.encode())).decode()

async def _creator(client):
    r = await client.post("/api/v1/creators", json={"display_name": "Signer"})
    return r.json()["id"]

async def test_register_key_and_verify_valid_signature(client):
    cid = await _creator(client)
    priv, pub_b64, key_id = make_keypair()

    r = await client.post(f"/api/v1/creators/{cid}/keys",
                          json={"public_key": pub_b64, "label": "laptop"})
    assert r.status_code == 201
    body = r.json()
    assert body["key_id"] == key_id and body["status"] == "active"

    payload = f"provenance-m2-test:{cid}"
    r = await client.post(
        f"/api/v1/creators/{cid}/verify-signature",
        json={"payload": payload, "signature": sign(priv, payload)},
    )
    assert r.status_code == 200
    assert r.json()["valid"] is True and r.json()["key_id"] == key_id

async def test_tampered_payload_rejected(client):
    cid = await _creator(client)
    priv, pub_b64, _ = make_keypair()
    await client.post(f"/api/v1/creators/{cid}/keys", json={"public_key": pub_b64})

    sig = sign(priv, "original")
    r = await client.post(
        f"/api/v1/creators/{cid}/verify-signature",
        json={"payload": "tampered", "signature": sig},
    )
    assert r.json()["valid"] is False and r.json()["reason"] == "signature_invalid"

async def test_revoked_key_does_not_verify(client):
    cid = await _creator(client)
    priv, pub_b64, key_id = make_keypair()
    await client.post(f"/api/v1/creators/{cid}/keys", json={"public_key": pub_b64})
    await client.post(f"/api/v1/creators/{cid}/keys/{key_id}/revoke")

    r = await client.post(
        f"/api/v1/creators/{cid}/verify-signature",
        json={"payload": "x", "signature": sign(priv, "x"), "key_id": key_id},
    )
    assert r.json()["valid"] is False and r.json()["reason"] == "key_revoked"

@pytest.mark.parametrize("bad", [
    "not-base64!!", base64.b64encode(b"short").decode(),
    base64.b64encode(b"\x00" * 32).decode(),
])
async def test_invalid_public_keys_rejected(client, bad):
    cid = await _creator(client)
    r = await client.post(f"/api/v1/creators/{cid}/keys", json={"public_key": bad})
    assert r.status_code == 422

async def test_duplicate_key_conflict(client):
    cid = await _creator(client)
    _, pub_b64, _ = make_keypair()
    assert (await client.post(f"/api/v1/creators/{cid}/keys",
                              json={"public_key": pub_b64})).status_code == 201
    assert (await client.post(f"/api/v1/creators/{cid}/keys",
                              json={"public_key": pub_b64})).status_code == 409