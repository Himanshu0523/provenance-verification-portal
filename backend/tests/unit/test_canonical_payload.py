from app.modules.publishing.manifest_builder import build_canonical_payload

A = "a" * 64
B = "b" * 64
CID = "11111111-1111-4111-8111-111111111111"

def _build(**overrides):
    kwargs = dict(
        asset_sha256=A,
        client_created_at="2025-01-15T10:30:00Z",
        creator_id=CID,
        file_size=1234,
        key_id=B,
        mime_type="image/png",
        original_filename="cat.png",
    )
    kwargs.update(overrides)
    return build_canonical_payload(**kwargs)

def test_golden_bytes():
    expected = (
        '{"asset_sha256":"' + A + '",'
        '"client_created_at":"2025-01-15T10:30:00Z",'
        '"creator_id":"' + CID + '",'
        '"file_size":1234,'
        '"key_id":"' + B + '",'
        '"mime_type":"image/png",'
        '"original_filename":"cat.png",'
        '"schema":"provenance/v1"}'
    )
    assert _build() == expected

def test_utf8_not_escaped():
    p = _build(original_filename="café.png")
    assert "café.png" in p
    assert "\\u00e9" not in p

def test_sorted_key_order():
    p = _build()
    # schema must appear last, asset_sha256 first
    assert p.index('"asset_sha256"') < p.index('"schema"')