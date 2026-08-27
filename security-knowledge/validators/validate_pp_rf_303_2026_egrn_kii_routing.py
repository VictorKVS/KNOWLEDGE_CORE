from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    ROOT
    / "security-knowledge"
    / "classification"
    / "pp-rf-303-2026-egrn-kii-routing-regression-v1.json"
)
EFFECTIVE_FROM = date.fromisoformat("2026-04-01")
ALLOWED_SUBJECTS = {"ROSREESTR", "ROSKADASTR"}
ALLOWED_OBJECTS = {
    "FGIS_EGRN",
    "TECHNICAL_MEANS_SUPPORTING_FGIS_EGRN",
    "SOFTWARE_MEANS_SUPPORTING_FGIS_EGRN",
}


def evaluate(case: dict) -> str:
    if date.fromisoformat(case["date"]) < EFFECTIVE_FROM:
        return "PRE_EFFECTIVE_EDITION_REVIEW"
    if case.get("subject") not in ALLOWED_SUBJECTS:
        return "OUT_OF_SCOPE_SUBJECT"
    if case.get("object") not in ALLOWED_OBJECTS:
        return "OUT_OF_SCOPE_OBJECT"

    lawful_basis = case.get("lawful_basis")
    if lawful_basis == "UNKNOWN":
        return "NOT_PROVEN_LAWFUL_BASIS"
    if lawful_basis != "CONFIRMED":
        return "NOT_ROUTED_NO_LAWFUL_BASIS"

    if case.get("automatic_category_claim"):
        return "REJECT_AUTOMATIC_CATEGORY_INFERENCE"
    if case.get("exact_formula_requested") and not case.get(
        "exact_primary_formula_available", False
    ):
        return "EXACT_FORMULA_NOT_PROVEN"
    if case.get("indicator_3_function_failure"):
        return "CATEGORY_II_FROM_INDICATOR_3"
    if case.get("all_indicator_matches") is False:
        return "NO_CATEGORY"

    indicator = case.get("evaluate_indicator")
    if indicator == 1 and case.get("recovery_time_hours") is None:
        return "NEEDS_RECOVERY_TIME_HOURS"
    if indicator == 2:
        if case.get("recovery_time_hours") is None:
            return "NEEDS_RECOVERY_TIME_HOURS"
        if case.get("statutory_service_time_hours") is None:
            return "NEEDS_STATUTORY_SERVICE_TIME_HOURS"
        if str(case.get("statutory_service_time_hours")) == "0":
            return "FAIL_CLOSED_ZERO_DENOMINATOR"
    if indicator == 4 and not case.get("economic_inputs_complete", False):
        return "NEEDS_EXPERT_ECONOMIC_ASSESSMENT_INPUTS"
    if indicator == 4 and str(case.get("average_federal_budget_revenue")) == "0":
        return "FAIL_CLOSED_ZERO_DENOMINATOR"

    return "EVALUATE_INDICATORS_1_2_3_4"


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))

    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected} actual={actual}")
        return 1

    print(f"PASS {len(data['cases'])} PP 303/2026 EGRN KII routing cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
