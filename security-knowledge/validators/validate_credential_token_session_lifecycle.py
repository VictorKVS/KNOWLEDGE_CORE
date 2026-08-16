import json
import sys
from pathlib import Path


def classify(case: dict) -> str:
    if not case["evidence_fresh"]:
        return "NOT_PROVEN"
    if not case["issued"]:
        if case["activated"] or case["session_active"]:
            return "STATE_CONFLICT"
        return "NOT_ISSUED"
    if not case["activated"]:
        if case["session_active"]:
            return "STATE_CONFLICT"
        return "ISSUED_NOT_ACTIVE"
    if case["revoked"]:
        if case["session_active"]:
            return "RESIDUAL_SESSION_RISK"
        return "REVOKED_CLOSED"
    if case["expired"]:
        if case["session_active"]:
            return "EXPIRED_ACTIVE_RISK"
        return "EXPIRED_CLOSED"
    if not case["owner_current"]:
        if case["session_active"]:
            return "ORPHANED_CREDENTIAL_RISK"
        return "NOT_PROVEN"
    return "ACTIVE_VALID"


def main(path: str) -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = classify(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected} actual={actual}")
        raise SystemExit(1)
    print(f"PASS {len(data['cases'])} credential lifecycle cases")


if __name__ == "__main__":
    main(sys.argv[1])
