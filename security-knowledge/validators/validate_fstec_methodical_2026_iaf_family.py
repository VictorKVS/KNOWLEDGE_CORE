#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-iaf-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-iaf-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    numerics = {item["id"]: item for item in model["numeric_constraints"]}
    tensions = {item["id"]: item for item in model["source_text_tensions"]}
    profiles = measures["ИАФ.3"]["minimum_authentication_profiles"]

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(numerics)
        if query == "profile_count": return len(profiles)
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "base_cell": return measures[case["measure"]]["matrix"]["base"][case["class"]]
        if query == "enhancement_cell": return measures[case["measure"]]["matrix"]["enhancements"][case["class"]]
        if query == "matrix_counts": return {k:model["class_matrix_summary"][k] for k in ("cells_total","nonblank_cells","blank_cells")}
        if query == "numeric": return {k:numerics[case["id"]][k] for k in ("value","unit","comparator")}
        if query == "profile": return {k:profiles[case["index"]][k] for k in ("K3","K2","K1")}
        if query == "tension_status": return tensions[case["id"]]["status"]
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_IAF2_OR_IAF4_BLANK_BASE_CELLS_AS_PROHIBITIONS" in model["scope_guards"] else None
        if query == "crypto_scope": return "SEPARATE_FSB_REQUIREMENTS" if "DO_NOT_USE_IAF_CRYPTO_REFERENCES_AS_A_SUBSTITUTE_FOR_APPLICABLE_FSB_REQUIREMENTS" in model["scope_guards"] else None
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_IAF_FAMILY_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == ["ИАФ.1", "ИАФ.2", "ИАФ.3", "ИАФ.4"]
    assert [x["number"] for x in measures["ИАФ.3"]["enhancements"]] == list(range(1, 12))
    assert model["class_matrix_summary"] == {"cells_total":24,"nonblank_cells":9,"blank_cells":15,"rule":"BLANK_IS_NOT_PROHIBITION_AND_DOES_NOT_DELETE_ADAPTATION_VERIFICATION_OR_COMPENSATION"}
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 4 IAF measures; 68 implementation atoms; 27 documentation items; 21 enhancements; 24 class cells; 11 numeric constraints; 48 fail-closed cases")


if __name__ == "__main__":
    main()
