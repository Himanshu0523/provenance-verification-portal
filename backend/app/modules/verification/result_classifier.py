from app.modules.verification.schemas import Verdict

_PRIORITY: dict[Verdict, int] = {
    "verified": 0,
    "key_revoked": 1,
    "signature_invalid": 2,
    "invalid_manifest": 3,
    "unknown": 4,
}

def classify_asset(
    *, manifest_ok: bool, signature_valid: bool, key_status: str,
) -> Verdict:
    """Per-asset verdict based purely on the three flags."""
    if not manifest_ok:
        return "invalid_manifest"
    if not signature_valid:
        return "signature_invalid"
    if key_status != "active":
        return "key_revoked"
    return "verified"

def best_verdict(verdicts: list[Verdict]) -> Verdict:
    if not verdicts:
        return "unknown"
    return min(verdicts, key=lambda v: _PRIORITY[v])