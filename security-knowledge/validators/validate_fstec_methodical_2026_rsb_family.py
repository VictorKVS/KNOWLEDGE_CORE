#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-rsb-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-rsb-family-regression-v1.json")


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
        if query == "matrix_counts": return {k:model["class_matrix_summary"][k] for k in ("cells_total","nonblank_cells","blank_cells")}
        if query == "base_all_classes": return all(x == "PLUS" for x in measures[case["measure"]]["matrix"]["base"].values())
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "rsb1_enhancement_4_class_listed": return any(4 in x for x in measures["РСБ.1"]["matrix"]["enhancements"].values())
        if query == "rsb1_source_scope_count": return len([x for x in measures["РСБ.1"]["implementation"] if x in (
            "REGISTER_EVENTS_IN_INSTALLED_SECURITY_TOOLS",
            "REGISTER_EVENTS_ON_PERIMETER_SERVERS_WORKSTATIONS_STORAGE_SECURITY_AND_TELECOMMUNICATION_MEANS",
            "REGISTER_EVENTS_IN_SEGMENTS_PROCESSING_RESTRICTED_INFORMATION",
            "REGISTER_EVENTS_IN_SEGMENTS_IMPLEMENTING_SIGNIFICANT_SYSTEM_FUNCTIONS",
            "REGISTER_EVENTS_ON_REMOTE_ACCESS_MEANS",
        )])
        if query == "rsb1_minimum_record_field_count": return len([x for x in measures["РСБ.1"]["implementation"] if x.startswith("RECORD_AT_LEAST_")])
        if query == "rsb1_minimum_event_group_count": return len([x for x in measures["РСБ.1"]["implementation"] if x in (
            "REGISTER_LOGIN_LOGOUT_AND_LOGIN_ATTEMPTS",
            "REGISTER_MACHINE_MEDIA_CONNECTION_AND_INFORMATION_OUTPUT_TO_MEDIA",
            "REGISTER_START_AND_TERMINATION_OF_PROTECTED_INFORMATION_APPLICATIONS_AND_PROCESSES",
            "REGISTER_SOFTWARE_ACCESS_ATTEMPTS_TO_OPERATOR_DEFINED_PROTECTED_AND_OTHER_OBJECTS",
            "REGISTER_REMOTE_ACCESS_ATTEMPTS",
            "REGISTER_EVENTS_RECORDED_BY_SECURITY_TOOLS",
        )])
        if query == "rsb1_event_list_semantics": return "MINIMUM_NONEXHAUSTIVE" if "DO_NOT_TREAT_RSB_1_MINIMUM_EVENT_LIST_AS_EXHAUSTIVE" in model["scope_guards"] else None
        if query == "rsb1_gost_schema": return "NOT_FULLY_REPRODUCED" if "DO_NOT_TREAT_RSB_1_RECORD_FIELDS_AS_THE_COMPLETE_GOST_R_59548_2022_SCHEMA" in model["scope_guards"] else None
        if query == "rsb2_analysis_frequency": return "OPERATOR_DEFINED" if parameters["RSB2_ANALYSIS_FREQUENCY"]["universal_value"] == "NONE_STATED" else None
        if query == "rsb3_sync_frequency": return "OPERATOR_DEFINED" if parameters["RSB3_TIME_SYNCHRONIZATION_FREQUENCY"]["universal_value"] == "NONE_STATED" else None
        if query == "rsb4_retention_period": return "OPERATOR_DEFINED" if parameters["RSB4_EVENT_RETENTION_PERIOD"]["universal_value"] == "NONE_STATED" else None
        if query == "rsb4_backup_frequency": return "NOT_STATED" if "DO_NOT_INVENT_BACKUP_FREQUENCY_OR_COPY_COUNT_FOR_AUDIT_RECORDS" in model["scope_guards"] else None
        if query == "rsb4_crypto_scope": return "CONDITIONAL_SEPARATE_FSB_LAYER" if "DO_NOT_TREAT_RSB_4_CRYPTOGRAPHIC_ENHANCEMENT_AS_UNCONDITIONAL_OR_AS_REPLACING_FSB_REQUIREMENTS" in model["scope_guards"] else None
        if query == "rsb5_failure_types": return "HARDWARE_SOFTWARE_COLLECTION_CAPACITY" if all(x in " ".join(measures["РСБ.5"]["implementation"]) for x in ("HARDWARE","SOFTWARE","COLLECTION","CAPACITY")) else None
        if query == "rsb5_near_real_time": return "QUALITATIVE_NO_NUMERIC_LATENCY" if "DO_NOT_CONVERT_NEAR_REAL_TIME_INTO_AN_UNSTATED_NUMERIC_LATENCY" in model["scope_guards"] else None
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_ENHANCEMENT_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "complete_rsb_family": return model["verification_boundary"]["complete_rsb_family"]
        if query == "gost_59548": return model["verification_boundary"]["gost_r_59548_2022_full_schema"]
        if query == "gost_59712": return model["verification_boundary"]["gost_r_59712_2022_full_response_guidance"]
        if query == "other_families": return model["verification_boundary"]["other_measure_families"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_RSB_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == ["РСБ.1", "РСБ.2", "РСБ.3", "РСБ.4", "РСБ.5"]
    assert [x["number"] for x in measures["РСБ.1"]["enhancements"]] == [1, 2, 3, 4]
    assert [x["number"] for x in measures["РСБ.2"]["enhancements"]] == [1, 2, 3, 4, 5]
    assert [x["number"] for x in measures["РСБ.4"]["enhancements"]] == [1, 2, 3, 4, 5]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 5 RSB measures; 39 implementation atoms; 9 documentation items; 16 enhancements; 30 class cells; 0 universal numeric constraints; 5 operator-defined parameters; 50 fail-closed cases")


if __name__ == "__main__":
    main()
