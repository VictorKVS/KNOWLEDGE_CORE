from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "governance" / "fsb547-response-plan-decision-workflow-regression-v1.yaml"


def evaluate(x):
    if not x.get("register_inclusion_date_present", False):
        return "NEEDS_REGISTER_INCLUSION_DATE"
    if x.get("plan_age_days", 0) > 90 and not x.get("plan_present", False):
        return "PLAN_90D_OVERDUE"
    if x.get("plan_present", False) and not x.get("plan_content_complete", False):
        return "NEEDS_PLAN_CONTENT_EVIDENCE"
    if x.get("approval_required", False):
        if not x.get("head_role_assignment_present", False):
            return "NEEDS_HEAD_ROLE_ASSIGNMENT"
        if not x.get("actor_is_head", False) and not x.get("valid_delegation_present", False):
            return "NEEDS_DECISION_RIGHT"
        if not x.get("signed_approval_present", False):
            return "NEEDS_SIGNED_APPROVAL"
        if not x.get("approval_date_present", False):
            return "NEEDS_APPROVAL_DATE"
    if x.get("approval_date_present", False):
        if x.get("days_since_approval", 0) > 7 and not x.get("delivery_confirmation_present", False):
            return "NKTSKI_COPY_7D_OVERDUE"
        if not x.get("delivery_confirmation_present", False):
            return "NEEDS_DELIVERY_EVIDENCE"
    if not x.get("annual_exercise_evidence_present", False):
        return "NEEDS_ANNUAL_EXERCISE_EVIDENCE"
    if x.get("exercise_deficiencies_found", False) and not x.get("amendment_evidence_present", False):
        return "NEEDS_PLAN_AMENDMENT_EVIDENCE"
    return "PASS"


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
    print(f"PASS: {len(data['cases'])} FSB 547 response-plan workflow regression cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
