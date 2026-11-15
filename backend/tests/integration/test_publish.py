import base64, hashlib, uuid
from datetime import datetime, timezone

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.modules.publishing.manifest_builder import build_canonical_payload

# Valid PNG magic; enough to pass validators
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64

def _keypair():
    priv = Ed25519PrivateKey.generate()
    raw = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return priv, base64.b64encode(raw).decode(), hashlib.sha256(raw).hexdigest()

def _now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

async def _setup(client):
    r = await client.post("/api/v1/creators", json={"display_name": "Pub"})
    cid = r.json()["id"]
    priv, pub_b64, key_id = _keypair()
    await client.post(f"/api/v1/creators/{cid}/keys",
                      json={"public_key": pub_b64})
    return cid, priv, key_id

def _sign(priv, canonical: str) -> str:
    return base64.b64encode(priv.sign(canonical.encode())).decode()

def _canonical(cid, key_id, sha, created_at, filename, mime, size):
    return build_canonical_payload(
        asset_sha256=sha, client_created_at=created_at, creator_id=cid,
        file_size=size, key_id=key_id, mime_type=mime,
        original_filename=filename,
    )

async def test_publish_happy_path(client):
    cid, priv, key_id = await _setup(client)
    sha = hashlib.sha256(PNG).hexdigest()
    now = _now_str()
    canonical = _canonical(cid, key_id, sha, now, "cat.png", "image/png", len(PNG))
    sig = _sign(priv, canonical)

    files = {"file": ("cat.png", PNG, "image/png")}
    data = dict(creator_id=cid, key_id=key_id,
                client_created_at=now, signature=sig)
    r = await client.post("/api/v1/publish", files=files, data=data)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["sha256"] == sha
    assert body["signature_verified"] is True
    assert body["canonical_payload"] == canonical
    assert body["verification_url"] == f"/verify?asset_id={body['asset_id']}"

async def test_publish_duplicate_409(client):
    cid, priv, key_id = await _setup(client)
    sha = hashlib.sha256(PNG).hexdigest()
    now = _now_str()
    sig = _sign(priv, _canonical(cid, key_id, sha, now, "cat.png",
                                 "image/png", len(PNG)))
    files = {"file": ("cat.png", PNG, "image/png")}
    data = dict(creator_id=cid, key_id=key_id,
                client_created_at=now, signature=sig)
    assert (await client.post("/api/v1/publish", files=files, data=data)).status_code == 201
    r = await client.post("/api/v1/publish", files=files, data=data)
    assert r.status_code == 409

async def test_publish_bad_signature_422(client):
    cid, _, key_id = await _setup(client)
    sha = hashlib.sha256(PNG).hexdigest()
    now = _now_str()
    files = {"file": ("cat.png", PNG, "image/png")}
    data = dict(creator_id=cid, key_id=key_id, client_created_at=now,
                signature=base64.b64encode(b"\x00" * 64).decode())
    r = await client.post("/api/v1/publish", files=files, data=data)
    assert r.status_code == 422
    assert "signature" in r.json()["error"]["message"].lower()

async def test_publish_bad_magic_422(client):
    cid, priv, key_id = await _setup(client)
    junk = b"not-an-image" * 10
    sha = hashlib.sha256(junk).hexdigest()
    now = _now_str()
    canonical = _canonical(cid, key_id, sha, now, "x.png", "image/png", len(junk))
    files = {"file": ("x.png", junk, "image/png")}
    data = dict(creator_id=cid, key_id=key_id,
                client_created_at=now, signature=_sign(priv, canonical))
    r = await client.post("/api/v1/publish", files=files, data=data)
    assert r.status_code == 422

async def test_publish_skew_rejected(client):
    cid, priv, key_id = await _setup(client)
    old = "2020-01-01T00:00:00Z"
    sha = hashlib.sha256(PNG).hexdigest()
    canonical = _canonical(cid, key_id, sha, old, "cat.png", "image/png", len(PNG))
    files = {"file": ("cat.png", PNG, "image/png")}
    data = dict(creator_id=cid, key_id=key_id, client_created_at=old,
                signature=_sign(priv, canonical))
    r = await client.post("/api/v1/publish", files=files, data=data)
    assert r.status_code == 422

async def test_publish_revoked_key_422(client):
    cid, priv, key_id = await _setup(client)
    await client.post(f"/api/v1/creators/{cid}/keys/{key_id}/revoke")
    sha = hashlib.sha256(PNG).hexdigest()
    now = _now_str()
    canonical = _canonical(cid, key_id, sha, now, "cat.png", "image/png", len(PNG))
    files = {"file": ("cat.png", PNG, "image/png")}
    data = dict(creator_id=cid, key_id=key_id, client_created_at=now,
                signature=_sign(priv, canonical))
    r = await client.post("/api/v1/publish", files=files, data=data)
    assert r.status_code == 422