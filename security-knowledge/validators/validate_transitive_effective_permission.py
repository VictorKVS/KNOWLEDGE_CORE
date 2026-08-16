import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "security-knowledge" / "regression" / "transitive-effective-permission-regression-v1.json"


def classify(c):
    if c.get("identity_conflict"):
        return "PATH_IDENTITY_CONFLICT"
    if c.get("cycle"):
        return "CYCLE_REVIEW_REQUIRED"
    if not c.get("fresh", False) or not c.get("temporal_valid", False):
        return "STALE_TRANSITIVE_PATH"
    if c.get("service") and not c.get("service_owner", False):
        return "SERVICE_ACCOUNT_OWNER_REQUIRED"
    if c.get("revoked_declared") and c.get("residual_token_or_session"):
        return "TOKEN_OR_SESSION_RESIDUAL"
    if c.get("central_disabled") and c.get("local_account_effective"):
        return "LOCAL_ACCOUNT_UNMANAGED"
    if not c.get("observed_path", False):
        return "PATH_NOT_PROVEN"
    if c.get("privileged"):
        return "PRIVILEGED_PATH_REVIEW_REQUIRED"
    if not c.get("declared", False):
        return "TRANSITIVE_RIGHT_UNDECLARED"
    return "EFFECTIVE_PATH_CONFIRMED"


def main():
    data = json.loads(SUITE.read_text(encoding="utf-8"))
    failures = []
    for c in data["cases"]:
        got = classify(c)
        if got != c["expected"]:
            failures.append((c["id"], c["expected"], got))
    if failures:
        for item in failures:
            print("FAIL", *item)
        raise SystemExit(1)
    print(f"PASS {data['suite_id']}: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
