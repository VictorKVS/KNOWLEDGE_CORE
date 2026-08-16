import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "security-knowledge" / "regression" / "segregation-of-duties-conflict-regression-v1.json"

CONFLICTS = [
    frozenset(("REQUEST_CHANGE", "APPROVE_CHANGE")),
    frozenset(("MODIFY_CODE", "DEPLOY_PRODUCTION")),
    frozenset(("ADMINISTER_SECURITY_CONTROL", "AUDIT_SAME_CONTROL")),
    frozenset(("CREATE_AUDIT_EVIDENCE", "CERTIFY_AUDIT_EVIDENCE")),
    frozenset(("GRANT_ACCESS", "REVIEW_OWN_ACCESS_GRANTS")),
    frozenset(("CONTROL_BACKUP", "DELETE_PRIMARY_AND_BACKUP")),
]


def has_conflict(capabilities):
    caps = set(capabilities)
    return any(pair.issubset(caps) for pair in CONFLICTS)


def classify(case):
    if case.get("identity_conflict"):
        return "SOD_IDENTITY_CONFLICT"
    if not case.get("observed_path", False):
        return "SOD_PATH_NOT_PROVEN"
    if not case.get("fresh", False) or not case.get("temporal_valid", False):
        return "SOD_PATH_STALE"
    if not has_conflict(case.get("capabilities", [])):
        return "SOD_CLEAR"
    if case.get("compensating_control"):
        proven = (
            case.get("independent_approver_or_reviewer", False)
            and bool(case.get("evidence_locator"))
            and case.get("evidence_fresh", False)
        )
        return "SOD_CONFLICT_COMPENSATED" if proven else "SOD_COMPENSATING_CONTROL_NOT_PROVEN"
    return "SOD_CONFLICT"


def main():
    data = json.loads(SUITE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        got = classify(case)
        if got != case["expected"]:
            failures.append((case["id"], case["expected"], got))
    if failures:
        for item in failures:
            print("FAIL", *item)
        raise SystemExit(1)
    print(f"PASS {data['suite_id']}: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
