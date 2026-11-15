import base64, hashlib, uuid
from datetime import datetime, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.modules.publishing.manifest_builder import build_canonical_payload

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
MODIFIED = PNG[:-1] + b"\x01"       # one byte changed — different sha256


def _keypair():
    priv = Ed25519PrivateKey.generate()
    raw = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return priv, base64.b64encode(raw).decode(), hashlib.sha256(raw).hexdigest()


def _sign(priv, payload: str) -> str:
    return base64.b64encode(priv.sign(payload.encode())).decode()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


async def _publish(client, data: bytes, filename="cat.png"):
    r = await client.post("/api/v1/creators", json={"display_name": "Verifier"})
    cid = r.json()["id"]
    priv, pub_b64, key_id = _keypair()
    await client.post(f"/api/v1/creators/{cid}/keys",
                      json={"public_key": pub_b64})

    sha = hashlib.sha256(data).hexdigest()
    now = _now()
    canonical = build_canonical_payload(
        asset_sha256=sha, client_created_at=now, creator_id=cid,
        file_size=len(data), key_id=key_id, mime_type="image/png",
        original_filename=filename,
    )
    files = {"file": (filename, data, "image/png")}
    form = dict(creator_id=cid, key_id=key_id,
                client_created_at=now, signature=_sign(priv, canonical))
    r = await client.post("/api/v1/publish", files=files, data=form)
    assert r.status_code == 201, r.text
    return cid, key_id, r.json()["asset_id"]


async def test_verify_exact_match_verified(client):
    await _publish(client, PNG)
    r = await client.post(
        "/api/v1/verify",
        files={"file": ("cat.png", PNG, "image/png")},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["verdict"] == "verified"
    assert body["total_matches"] == 1
    assert body["matches"][0]["signature_valid"] is True
    assert body["matches"][0]["manifest_ok"] is True
    assert body["audit_id"] is not None


async def test_verify_unknown_file(client):
    r = await client.post(
        "/api/v1/verify",
        files={"file": ("ghost.png", PNG + b"x", "image/png")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "unknown"
    assert body["total_matches"] == 0
    assert body["matches"] == []


async def test_verify_modified_bytes_no_match(client):
    await _publish(client, PNG)
    r = await client.post(
        "/api/v1/verify",
        files={"file": ("modified.png", MODIFIED, "image/png")},
    )
    assert r.status_code == 200
    assert r.json()["verdict"] == "unknown"


async def test_verify_revoked_key(client):
    cid, key_id, _ = await _publish(client, PNG)
    await client.post(f"/api/v1/creators/{cid}/keys/{key_id}/revoke")
    r = await client.post(
        "/api/v1/verify",
        files={"file": ("cat.png", PNG, "image/png")},
    )
    body = r.json()
    assert body["verdict"] == "key_revoked"
    assert body["matches"][0]["key_status"] == "revoked"
    assert body["matches"][0]["signature_valid"] is True


async def test_verify_tampered_signature(client, db):
    _, _, asset_id = await _publish(client, PNG)

    # Corrupt the stored signature directly.
    from sqlalchemy import update
    from app.modules.media_assets.models import MediaAsset
    await db.execute(
        update(MediaAsset)
        .where(MediaAsset.id == uuid.UUID(asset_id))
        .values(signature=base64.b64encode(b"\x00" * 64).decode())
    )
    await db.commit()

    r = await client.post(
        "/api/v1/verify",
        files={"file": ("cat.png", PNG, "image/png")},
    )
    body = r.json()
    assert body["verdict"] == "signature_invalid"
    assert body["matches"][0]["signature_valid"] is False


async def test_verify_tampered_manifest(client, db):
    _, _, asset_id = await _publish(client, PNG)

    # Replace stored payload with a manifest for a different asset sha256.
    from sqlalchemy import update
    from app.modules.media_assets.models import MediaAsset
    await db.execute(
        update(MediaAsset)
        .where(MediaAsset.id == uuid.UUID(asset_id))
        .values(signed_payload='{"schema":"provenance/v1","asset_sha256":"' + "0"*64 + '"}')
    )
    await db.commit()

    r = await client.post(
        "/api/v1/verify",
        files={"file": ("cat.png", PNG, "image/png")},
    )
    body = r.json()
    assert body["verdict"] == "invalid_manifest"
    assert body["matches"][0]["manifest_ok"] is False


async def test_verify_same_bytes_two_creators(client):
    await _publish(client, PNG, filename="a.png")
    await _publish(client, PNG, filename="b.png")
    r = await client.post(
        "/api/v1/verify",
        files={"file": ("x.png", PNG, "image/png")},
    )
    body = r.json()
    assert body["verdict"] == "verified"
    assert body["total_matches"] == 2


async def test_verify_rejects_non_image(client):
    r = await client.post(
        "/api/v1/verify",
        files={"file": ("x.png", b"not an image" * 20, "image/png")},
    )
    assert r.status_code == 422