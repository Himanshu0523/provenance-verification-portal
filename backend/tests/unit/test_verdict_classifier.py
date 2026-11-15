import pytest
from app.modules.verification.result_classifier import (
    classify_asset, best_verdict,
)

@pytest.mark.parametrize("manifest_ok,sig_valid,key_status,expected", [
    (True,  True,  "active",  "verified"),
    (True,  True,  "revoked", "key_revoked"),
    (True,  False, "active",  "signature_invalid"),
    (True,  False, "revoked", "signature_invalid"),  # invalid sig dominates revoked
    (False, True,  "active",  "invalid_manifest"),
    (False, False, "revoked", "invalid_manifest"),
])
def test_classify(manifest_ok, sig_valid, key_status, expected):
    assert classify_asset(
        manifest_ok=manifest_ok,
        signature_valid=sig_valid,
        key_status=key_status,
    ) == expected

def test_best_verdict_priority():
    assert best_verdict(["unknown", "key_revoked", "verified"]) == "verified"
    assert best_verdict(["unknown", "key_revoked"]) == "key_revoked"
    assert best_verdict(["signature_invalid", "key_revoked"]) == "key_revoked"
    assert best_verdict([]) == "unknown"