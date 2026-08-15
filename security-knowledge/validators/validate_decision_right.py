from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "governance" / "decision-right-regression-v1.yaml"


def dt(value):
    if value in (None, "", "null"):
        return None
    return datetime.fromisoformat(str(value))


def evaluate(x):
    status = x.get("status")
    if status == "SUSPENDED":
        return "AUTHORITY_SUSPENDED"
    if status == "REVOKED":
        return "AUTHORITY_REVOKED"
    if status == "EXPIRED":
        return "AUTHORITY_EXPIRED"
    if not x.get("authority_source_present", False):
        return "NEEDS_AUTHORITY_SOURCE"
    if not x.get("evidence_present", False):
        return "NEEDS_ROLE_ASSIGNMENT"
    if x.get("provenance_type") == "RECOMMENDATION_ONLY":
        return "NEEDS_DECISION_RIGHT"
    if x.get("delegated") and not x.get("delegation_evidence_present", False):
        return "NEEDS_DELEGATION_EVIDENCE"
    if x.get("substitute") and not x.get("substitute_evidence_present", False):
        return "NEEDS_SUBSTITUTE_EVIDENCE"
    if x.get("actor_role") != x.get("required_role") and not x.get("delegated") and not x.get("substitute"):
        return "NEEDS_DECISION_RIGHT"
    if not x.get("scope_match", False):
        return "NEEDS_SCOPE_MATCH"
    decision_time = dt(x.get("decision_time"))
    effective_from = dt(x.get("effective_from"))
    effective_to = dt(x.get("effective_to"))
    if decision_time is None or effective_from is None or decision_time < effective_from:
        return "NEEDS_EFFECTIVE_DATE"
    if effective_to is not None and decision_time > effective_to:
        return "AUTHORITY_EXPIRED"
    if not x.get("authority_ceiling_ok", True):
        return "AUTHORITY_CEILING_EXCEEDED"
    if not x.get("decision_allowed", True):
        return "DECISION_NOT_ALLOWED"
    return "AUTHORIZED"


def main():
    data = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = evaluate(case["input"])
        expected = case["expected"]
        if actual != expected:
            failures.append((case["id"], expected, actual))
    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected} actual={actual}")
        return 1
    print(f"PASS: {len(data['cases'])} decision-right regression cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
