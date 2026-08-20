#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-upd-5-9-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-upd-5-9-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    numerics = {item["id"]: item for item in model["numeric_constraints"]}
    triggers = {item["id"]: item for item in model["event_triggers"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}
    variants = {item["selector"]: item for item in measures["УПД.7"]["enhancements"][0]["variants"]}

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(numerics)
        if query == "event_trigger_count": return len(triggers)
        if query == "operator_parameter_count": return len(parameters)
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "matrix_counts": return {k:model["class_matrix_summary"][k] for k in ("cells_total","nonblank_cells","blank_cells")}
        if query == "base_row": return measures[case["measure"]]["matrix"]["base"]
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "upd7_variant": return {k:variants[case["selector"]][k] for k in ("rule","maximum")}
        if query == "upd7_1b_class_listed": return any("1б" in row for row in measures["УПД.7"]["matrix"]["enhancements"].values())
        if query == "upd6_seven_day_minimum": return {k:numerics["UPD6_E3_LOOKBACK_MINIMUM"][k] for k in ("comparator","value","unit")}
        if query == "upd9_annual_review": return {k:numerics["UPD9_REVIEW_MINIMUM"][k] for k in ("comparator","value","unit")}
        if query == "upd9_access_model_trigger": return triggers["UPD9_ACCESS_MODEL_CHANGE"]["response"]
        if query == "upd6_immediate_trigger": return triggers["UPD6_UNAUTHORIZED_ACCESS_NOTICE"]["response"]
        if query == "upd8_inactivity_value": return "OPERATOR_DEFINED" if parameters["UPD8_INACTIVITY_TIME"]["universal_value"] == "NONE_STATED" else None
        if query == "upd8_failed_unlock_value": return "OPERATOR_DEFINED" if parameters["UPD8_FAILED_UNLOCK_ATTEMPTS"]["universal_value"] == "NONE_STATED" else None
        if query == "upd5_access_gate": return "CONFIRMATION_REQUIRED" if "ALLOW_ACCESS_ONLY_AFTER_USER_CONFIRMS_READING_WARNING" in measures["УПД.5"]["implementation"] else None
        if query == "upd6_minimum_notice_fields": return [x for x in ("DATE","TIME") if f"INCLUDE_AT_LEAST_{x}_OF_PREVIOUS_LOGIN" in measures["УПД.6"]["implementation"]]
        if query == "upd7_k3": return "NOT_BASELINE" if measures["УПД.7"]["matrix"]["base"]["K3"] == "BLANK" else None
        if query == "upd8_unlock": return "REPEAT_IAF_3_AUTHENTICATION" if "REQUIRE_REPEAT_AUTHENTICATION_UNDER_IAF_3_TO_UNLOCK" in measures["УПД.8"]["implementation"] else None
        if query == "upd9_public_information_exception": return "PRESERVED" if "DO_NOT_OMIT_UPD_9_PUBLIC_INFORMATION_LOGGING_EXCEPTION" in model["scope_guards"] else None
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "complete_upd_family": return model["verification_boundary"]["complete_upd_family"]
        if query == "other_families": return model["verification_boundary"]["other_measure_families"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "expert_review": return model["verification_boundary"]["independent_expert_review"]
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_UPD_5_9_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == ["УПД.5", "УПД.6", "УПД.7", "УПД.8", "УПД.9"]
    assert [x["number"] for x in measures["УПД.6"]["enhancements"]] == [1, 2, 3, 4, 5, 6]
    assert list(variants) == ["1а", "1б"]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 5 UPD measures; 26 implementation atoms; 17 documentation items; 9 enhancement entries; 30 class cells; 4 numeric constraints; 2 event triggers; 4 operator-defined parameters; 46 fail-closed cases")


if __name__ == "__main__":
    main()
