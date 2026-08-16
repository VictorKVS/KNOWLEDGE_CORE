import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "regression" / "access-entitlement-evidence-chain-regression-v1.json"


def evaluate(c):
    if c["revocation_executed"]:
        return "UNAUTHORIZED_OR_STALE"
    if c["account_status"] != "ACTIVE" or not c["within_interval"]:
        return "UNAUTHORIZED_OR_STALE"
    if c["revocation_requested"]:
        return "REVOCATION_PENDING"
    if not c["business_need"]:
        return "EXCESSIVE_PRIVILEGE_SUSPECTED"
    if not c["approval"] or not c["approver_authority"]:
        return "NEEDS_APPROVAL_EVIDENCE"
    if c["role_changed"] or c["review_due"]:
        return "NEEDS_REVIEW"
    return "AUTHORIZED_CURRENT"


def main():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    if len(cases) < 12:
        raise SystemExit("fixture floor not met")
    seen = set()
    failures = []
    for c in cases:
        cid = c["id"]
        if cid in seen:
            failures.append(f"duplicate case id {cid}")
            continue
        seen.add(cid)
        got = evaluate(c)
        if got != c["expected"]:
            failures.append(f"{cid}: expected {c['expected']} got {got}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS: {len(cases)} access-entitlement evidence cases")


if __name__ == "__main__":
    main()
