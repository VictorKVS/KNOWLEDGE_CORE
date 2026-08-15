#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import yaml

FIXTURE = Path(__file__).parents[1] / "risk-methods" / "risk-criteria-governance-regression-v1.yaml"
ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def present(v):
    return v is not None and v != "" and v != [] and v != {}


def d(v):
    return date.fromisoformat(v) if present(v) else None


def governance(i):
    status = i.get("criteria_status")
    if status != "APPROVED" or not present(i.get("approval_evidence")):
        if status in {"RETIRED", "REVOKED"}:
            return "STALE_CRITERIA"
        return "NEEDS_CRITERIA_APPROVAL"

    assessment_date = d(i.get("assessment_date"))
    effective_from = d(i.get("effective_from"))
    effective_to = d(i.get("effective_to"))
    if assessment_date and effective_from and assessment_date < effective_from:
        return "NEEDS_TEMPORAL_RESOLUTION"
    if i.get("explicit_expiry_rule") and assessment_date and effective_to and assessment_date > effective_to:
        return "STALE_CRITERIA"
    if i.get("conflicting_active_version"):
        return "CONFLICT"
    if present(i.get("supersedes_version")) and i.get("supersession_chain_valid") is False:
        return "NEEDS_VERSION_REVIEW"

    review_due = d(i.get("review_due"))
    if assessment_date and review_due and assessment_date > review_due and not present(i.get("review_completed_evidence")):
        return "NEEDS_REVIEW"

    if i.get("action") != "ACCEPT_RESIDUAL_RISK":
        return "GOVERNANCE_READY"

    right = i.get("decision_right")
    if not present(right):
        return "NEEDS_DECISION_RIGHT"
    required = ("decision_right_id", "authorized_role", "authority_scope", "effective_from", "source_reference", "evidence_reference")
    if any(not present(right.get(k)) for k in required):
        return "NEEDS_DECISION_RIGHT"
    if right.get("authorized_role") != i.get("actor_role"):
        return "NEEDS_DECISION_RIGHT"
    if present(i.get("requested_scope")) and right.get("authority_scope") != i.get("requested_scope"):
        return "NEEDS_DECISION_RIGHT"
    right_from = d(right.get("effective_from"))
    right_to = d(right.get("effective_to"))
    if assessment_date and right_from and assessment_date < right_from:
        return "NEEDS_DECISION_RIGHT"
    if assessment_date and right_to and assessment_date > right_to:
        return "NEEDS_DECISION_RIGHT"
    maximum = right.get("maximum_risk_band")
    risk = i.get("risk_band")
    if maximum in ORDER and risk in ORDER and ORDER[risk] > ORDER[maximum]:
        return "NEEDS_ESCALATION"
    return "ACCEPTANCE_VALID"


def main():
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = governance(case["input"])
        if actual != case["expected_status"]:
            failures.append((case["id"], case["expected_status"], actual))
    if failures:
        for item in failures:
            print("FAIL", item)
        return 1
    print(f"PASS {len(data['cases'])} risk-criteria governance cases; approval/review/supersession/decision-right fail-closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
