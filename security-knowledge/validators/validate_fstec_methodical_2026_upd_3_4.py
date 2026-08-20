#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-upd-3-4-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-upd-3-4-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(model["numeric_constraints"])
        if query == "operator_parameter_count": return len(parameters)
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "base_cell": return measures[case["measure"]]["matrix"]["base"][case["class"]]
        if query == "enhancement_cell": return measures[case["measure"]]["matrix"]["enhancements"][case["class"]]
        if query == "matrix_counts": return {k:model["class_matrix_summary"][k] for k in ("cells_total","nonblank_cells","blank_cells")}
        if query == "account_lifecycle_count": return len([x for x in measures["УПД.3"]["implementation"] if x in ("CREATE_ACCOUNTS","ASSIGN_ACCOUNTS","ACTIVATE_ACCOUNTS","BLOCK_ACCOUNTS","DELETE_ACCOUNTS")])
        if query == "account_access_rule_count": return len([x for x in measures["УПД.3"]["implementation"] if x in ("ASSIGN_ACCOUNT_ACCESS_RULES","MODIFY_ACCOUNT_ACCESS_RULES","DELETE_ACCOUNT_ACCESS_RULES")])
        if query == "privileged_log_procedure": return "REQUIRED_DOCUMENTATION" if "PRIVILEGED_ACCOUNT_ADMINISTRATIVE_ACTION_LOGGING_PROCEDURE" in measures["УПД.3"]["documentation"] else None
        if query == "external_connection_contracts": return "REQUIRED_DOCUMENTATION" if "CONTRACT_AND_INFORMATION_INTERACTION_REQUIREMENTS_FOR_EXTERNAL_SUBJECT_CONNECTIONS" in measures["УПД.3"]["documentation"] else None
        if query == "failed_attempt_value": return "OPERATOR_DEFINED" if parameters["UPD4_FAILED_ATTEMPTS"]["universal_value"] == "NONE_STATED" else None
        if query == "attempt_window": return "OPERATOR_DEFINED" if parameters["UPD4_ATTEMPT_WINDOW"]["universal_value"] == "NONE_STATED" else None
        if query == "temporary_account_lifetime": return "OPERATOR_DEFINED" if parameters["UPD4_TEMPORARY_ACCOUNT_LIFETIME"]["universal_value"] == "NONE_STATED" else None
        if query == "inactivity_period": return "OPERATOR_DEFINED" if parameters["UPD4_INACTIVITY_PERIOD"]["universal_value"] == "NONE_STATED" else None
        if query == "technical_attribute_examples": return "NONEXHAUSTIVE" if "DO_NOT_TREAT_IP_ADDRESS_OR_USER_AGENT_SIGNATURE_AS_EXHAUSTIVE_TECHNICAL_ATTRIBUTES" in model["scope_guards"] else None
        if query == "upd3_enhancement_2": return "NOT_CLASS_LISTED_FOR_K2_OR_K3" if measures["УПД.3"]["matrix"]["enhancements"] == {"K3":[],"K2":[1],"K1":[1,2]} else None
        if query == "upd4_privileged_unlock": return "CHIEF_ADMINISTRATOR_ONLY_WHEN_ENHANCEMENT_APPLIES" if measures["УПД.4"]["enhancements"][1]["number"] == 2 else None
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_ENHANCEMENT_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "upd_5_9": return model["verification_boundary"]["upd_5_9"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "expert_review": return model["verification_boundary"]["independent_expert_review"]
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_UPD_3_4_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == ["УПД.3", "УПД.4"]
    assert [x["number"] for x in measures["УПД.3"]["enhancements"]] == [1, 2]
    assert [x["number"] for x in measures["УПД.4"]["enhancements"]] == [1, 2]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 2 UPD measures; 24 implementation atoms; 14 documentation items; 4 enhancements; 12 class cells; 0 universal numeric constraints; 6 operator-defined parameters; 42 fail-closed cases")


if __name__ == "__main__":
    main()
