#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

FIXTURE = Path(__file__).parents[1] / "risk-methods" / "security-risk-pipeline-regression-v1.yaml"


def present(v):
    return v is not None and v != "" and v != []


def route(i):
    if not present(i.get("risk_criteria_source")):
        return "NEEDS_RISK_CRITERIA"
    if not present(i.get("threat_model_reference")):
        return "NEEDS_THREAT_EVIDENCE"
    for key in ("negative_consequence_evidence", "affected_objects"):
        if not present(i.get(key)):
            return "NEEDS_THREAT_EVIDENCE"
    if not present(i.get("risk_statement")):
        return "NEEDS_RISK_IDENTIFICATION"
    if not present(i.get("assessment_technique")) or not present(i.get("technique_source")):
        return "NEEDS_ASSESSMENT_METHOD"
    if i.get("assessment_technique") == "LIKELIHOOD_X_IMPACT_DEFAULT":
        return "NEEDS_ASSESSMENT_METHOD"
    if not present(i.get("input_evidence")):
        return "NEEDS_ASSESSMENT_METHOD"
    if not present(i.get("analyzed_result")) or not present(i.get("risk_criteria")) or not present(i.get("comparison_result")):
        return "NEEDS_RISK_CRITERIA"
    if i.get("mandatory_control_inferred_only_from_bdu"):
        return "NEEDS_CONTROL_APPLICABILITY_EVIDENCE"
    for key in ("treatment_decision", "selected_controls", "responsible_role", "target_date"):
        if not present(i.get(key)):
            return "NEEDS_TREATMENT_DECISION"
    for key in ("residual_risk_result", "acceptance_decision", "decision_authority", "decision_evidence"):
        if not present(i.get(key)):
            return "NEEDS_DECISION_RIGHT"
    if not present(i.get("review_rule")):
        return "NEEDS_REVIEW_RULE"
    for key in ("provenance", "reasoning_trace", "reviewer", "observed_at"):
        if not present(i.get(key)):
            return "NEEDS_EVIDENCE_CLOSURE"
    return "RISK_PIPELINE_COMPLETE"


def main():
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = route(case["input"])
        if actual != case["expected_status"]:
            failures.append((case["id"], case["expected_status"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        return 1
    print(f"PASS {len(data['cases'])} security-risk pipeline cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
