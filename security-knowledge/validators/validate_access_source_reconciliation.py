import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "security-knowledge" / "regression" / "access-source-reconciliation-regression-v1.json"


def classify(c):
    if c.get("identity_conflict"):
        return "IDENTITY_CONFLICT"
    if not c.get("fresh", False):
        return "STALE_EVIDENCE"
    if c.get("service") and not c.get("service_owner", False):
        return "SERVICE_ACCOUNT_REVIEW_REQUIRED"
    if c.get("privileged") and c.get("effective"):
        return "PRIVILEGED_REVIEW_REQUIRED"
    if not c.get("hr_active", True) and c.get("effective"):
        return "TERMINATION_DRIFT"
    if c.get("revocation_requested", False) and c.get("effective"):
        return "REVOCATION_DRIFT"
    if c.get("declared") and not c.get("effective"):
        return "DECLARED_ONLY"
    if not c.get("declared") and c.get("effective"):
        return "EFFECTIVE_ONLY"
    return "CONSISTENT_CURRENT"


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
