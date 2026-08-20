#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-zsv-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-zsv-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}

    event_groups = {
        "REGISTER_SUCCESSFUL_AND_FAILED_VIRTUALIZATION_USER_AUTHENTICATION_ATTEMPTS",
        "REGISTER_USER_ACCESS_TO_VMS_THROUGH_VIRTUALIZATION_INTERFACE",
        "REGISTER_VM_CREATION_AND_DELETION",
        "REGISTER_VIRTUALIZATION_MEANS_START_AND_STOP_WITH_STOP_REASON",
        "REGISTER_VM_START_AND_STOP_WITH_STOP_REASON",
        "REGISTER_ROLE_ASSIGNMENT_CHANGES",
        "REGISTER_VIRTUALIZATION_CONFIGURATION_CHANGES",
        "REGISTER_VM_CONFIGURATION_CHANGES",
        "REGISTER_CONTROL_OBJECT_INTEGRITY_VIOLATIONS",
        "REGISTER_VM_MOVEMENT_EVENTS",
    }

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(model["numeric_constraints"])
        if query == "operator_parameter_count": return len(parameters)
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "matrix_counts": return {key: model["class_matrix_summary"][key] for key in ("cells_total", "nonblank_cells", "blank_cells")}
        if query == "base_row": return measures[case["measure"]]["matrix"]["base"]
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "zsv2_intervals": return len([x for x in model["numeric_constraints"] if x["measure"] == "ЗСВ.2"])
        if query == "zsv2_interval_semantics":
            valid = all(x["comparator"] == "MAX_INTERVAL" and x["value"] == 1 and x["unit"] == "WEEK" for x in model["numeric_constraints"])
            return "MAX_ONE_WEEK_OR_SHORTER" if valid else None
        if query == "zsv3_event_group_count": return len(event_groups.intersection(measures["ЗСВ.3"]["implementation"]))
        if query == "zsv3_rsb_dependency": return "LINKED_RSB_1_TO_RSB_5" if "REGISTER_VIRTUALIZATION_EVENTS_IN_ACCORDANCE_WITH_RSB_1_TO_RSB_5" in measures["ЗСВ.3"]["implementation"] else None
        if query == "zsv4_upd_dependency": return "LINKED_UPD_1_TO_UPD_4" if "APPLY_UPD_1_TO_UPD_4_ACCESS_CONTROL_IN_VIRTUALIZATION_ENVIRONMENT" in measures["ЗСВ.4"]["implementation"] else None
        if query == "zsv8_iaf_dependency": return "LINKED_IAF_1_AND_IAF_3" if "APPLY_IAF_1_AND_IAF_3_TO_VIRTUALIZATION_ACCESS_SUBJECTS" in measures["ЗСВ.8"]["implementation"] else None
        if query == "zsv5_backup_scope": return "OPERATOR_SELECTED_VM_IMAGES" if parameters["ZSV5_VM_IMAGE_BACKUP_SCOPE"]["universal_value"] == "NONE_OPERATOR_SELECTS" else None
        if query == "zsv5_backup_numbers": return "NO_UNIVERSAL_FREQUENCY_COPY_RETENTION_OR_RECOVERY_TIME" if "DO_NOT_INVENT_ZSV_5_BACKUP_FREQUENCY_COPY_COUNT_RETENTION_OR_RECOVERY_TIME" in model["scope_guards"] else None
        if query == "zsv7_overwrite_class_listed": return any(1 in row for row in measures["ЗСВ.7"]["matrix"]["enhancements"].values())
        if query == "zsv8_object_id_class_listed": return any(1 in row for row in measures["ЗСВ.8"]["matrix"]["enhancements"].values())
        if query == "technology_applicability": return "VIRTUALIZATION_CONDITIONAL" if model["applicability"]["trigger"] == "VIRTUALIZATION_MEANS_USED" else None
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_CLASS_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "complete_zsv_family": return model["verification_boundary"]["complete_zsv_family"]
        if query == "linked_models": return model["verification_boundary"]["referenced_iaf_upd_rsb_content"]
        if query == "cloud_profiles": return model["verification_boundary"]["cloud_service_role_and_shared_responsibility_profiles"]
        if query == "other_families": return model["verification_boundary"]["other_measure_families"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "expert_review": return model["verification_boundary"]["independent_expert_review"]
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZSV_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗСВ.{number}" for number in range(1, 10)]
    assert [x["number"] for x in measures["ЗСВ.1"]["enhancements"]] == [1, 2, 3, 4]
    assert [x["number"] for x in measures["ЗСВ.2"]["enhancements"]] == [1, 2, 3, 4]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 9 ZSV measures; 47 implementation atoms; 4 documentation items; 15 enhancements; 54 class cells; 5 weekly constraints; 2 operator-defined parameters; 60 fail-closed cases")


if __name__ == "__main__":
    main()
