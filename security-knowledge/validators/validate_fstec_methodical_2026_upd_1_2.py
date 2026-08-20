#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-upd-1-2-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-upd-1-2-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    numerics = {item["id"]: item for item in model["numeric_constraints"]}

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(numerics)
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "base_cell": return measures[case["measure"]]["matrix"]["base"][case["class"]]
        if query == "enhancement_cell": return measures[case["measure"]]["matrix"]["enhancements"][case["class"]]
        if query == "matrix_counts": return {k:model["class_matrix_summary"][k] for k in ("cells_total","nonblank_cells","blank_cells")}
        if query == "numeric": return {k:numerics[case["id"]][k] for k in ("value","unit","comparator")}
        if query == "event_trigger_count": return len(numerics[case["id"]]["additional_event_triggers"])
        if query == "method_semantics": return "ONE_OR_MORE_NOT_ALL_FOUR" if "DO_NOT_TREAT_AVAILABLE_ACCESS_CONTROL_METHODS_AS_A_REQUIREMENT_TO_IMPLEMENT_ALL_FOUR" in model["scope_guards"] else None
        if query == "review_semantics": return "ANNUAL_OR_TRIGGERED" if "DO_NOT_TREAT_ANNUAL_REVIEW_AS_REPLACING_EVENT_TRIGGERED_REVIEW" in model["scope_guards"] else None
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_ENHANCEMENT_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "enhancement_3_matrix": return "NOT_CLASS_LISTED_MAY_APPLY_LATER" if all(3 not in x for x in measures[case["measure"]]["matrix"]["enhancements"].values()) else None
        if query == "shared_account_rule": return "PROHIBITED_AND_DISABLED_OR_DELETED" if all(x in measures["УПД.2"]["implementation"] for x in ("PROHIBIT_SHARED_OR_GROUP_USER_ACCOUNTS","DISABLE_OR_DELETE_PROHIBITED_SHARED_AND_DEFAULT_ACCOUNTS")) else None
        if query == "default_account_rule": return "PROHIBITED_AND_DISABLED_OR_DELETED" if all(x in measures["УПД.2"]["implementation"] for x in ("PROHIBIT_DEFAULT_USER_ACCOUNTS","DISABLE_OR_DELETE_PROHIBITED_SHARED_AND_DEFAULT_ACCOUNTS")) else None
        if query == "least_privilege": return "REQUIRED" if "MINIMIZE_SUBJECT_RIGHTS_TO_OBJECTS" in measures["УПД.2"]["implementation"] else None
        if query == "access_target_count": return len([x for x in measures["УПД.2"]["implementation"] if x.startswith("CONTROL_ACCESS_TO_")])
        if query == "upd_3_9": return model["verification_boundary"]["upd_3_9"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "expert_review": return model["verification_boundary"]["independent_expert_review"]
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_UPD_1_2_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == ["УПД.1", "УПД.2"]
    assert [x["number"] for x in measures["УПД.1"]["enhancements"]] == [1, 2, 3]
    assert [x["number"] for x in measures["УПД.2"]["enhancements"]] == [1, 2, 3]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 2 UPD measures; 41 implementation atoms; 9 documentation items; 6 enhancements; 12 class cells; 2 numeric constraints; 42 fail-closed cases")


if __name__ == "__main__":
    main()
