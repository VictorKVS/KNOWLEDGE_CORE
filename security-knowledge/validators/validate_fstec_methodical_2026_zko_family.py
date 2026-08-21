#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-zko-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-zko-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}

    event_groups = {
        "REGISTER_UNAUTHORIZED_ACCESS_ATTEMPTS_TO_CONTAINERIZATION_MEANS",
        "REGISTER_CONTAINERIZATION_USER_AUTHENTICATION_ATTEMPTS",
        "REGISTER_CONTAINER_IMAGE_CREATION_MODIFICATION_AND_DELETION",
        "REGISTER_ACCESS_TO_CONTAINER_IMAGES",
        "REGISTER_CONTAINERIZATION_MEANS_START_AND_STOP_WITH_STOP_REASON",
        "REGISTER_CONTAINER_START_AND_STOP_WITH_STOP_REASON",
        "REGISTER_ROLE_ASSIGNMENT_CHANGES",
        "REGISTER_RUNNING_CONTAINER_MODIFICATION",
        "REGISTER_KNOWN_IMAGE_VULNERABILITY_AND_INCORRECT_CONFIGURATION_DETECTION",
        "REGISTER_CONTROL_OBJECT_INTEGRITY_VIOLATIONS",
    }
    image_lifecycle = {
        "CREATE_CONTAINER_IMAGES", "MODIFY_CONTAINER_IMAGES", "STORE_CONTAINER_IMAGES",
        "RETRIEVE_CONTAINER_IMAGES", "DELETE_CONTAINER_IMAGES",
    }

    def interval(route_id):
        return next(item for item in model["numeric_constraints"] if item["id"] == route_id)

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(model["numeric_constraints"])
        if query == "operator_parameter_count": return len(model["operator_defined_parameters"])
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "matrix_counts": return {key: model["class_matrix_summary"][key] for key in ("cells_total", "nonblank_cells", "blank_cells")}
        if query == "base_all_classes": return all(value == "PLUS" for value in measures[case["measure"]]["matrix"]["base"].values())
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "zko1_weekly_routes": return len([x for x in model["numeric_constraints"] if x["measure"] == "ЗКО.1"])
        if query == "zko1_interval_semantics":
            routes = [x for x in model["numeric_constraints"] if x["measure"] == "ЗКО.1"]
            return "MAX_ONE_WEEK_OR_SHORTER" if all(x["comparator"] == "MAX_INTERVAL" and x["value"] == 1 and x["unit"] == "WEEK" for x in routes) else None
        if query == "zko1_enhancement_7_exists": return any(x["number"] == 7 for x in measures["ЗКО.1"]["enhancements"])
        if query == "zko1_enhancement_7_class_listed": return any(7 in row for row in measures["ЗКО.1"]["matrix"]["enhancements"].values())
        if query == "zko2_event_group_count": return len(event_groups.intersection(measures["ЗКО.2"]["implementation"]))
        if query == "zko2_container_id": return "REQUIRED_FOR_CONTAINER_RUNTIME_EVENTS" if "REGISTER_CONTAINER_RUNTIME_EVENTS_WITH_CONTAINER_IDENTIFIER" in measures["ЗКО.2"]["implementation"] else None
        if query == "zko2_rsb_dependency": return "LINKED_RSB_1_TO_RSB_5" if "REGISTER_CONTAINER_EVENTS_IN_ACCORDANCE_WITH_RSB_1_TO_RSB_5" in measures["ЗКО.2"]["implementation"] else None
        if query == "zko3_upd_dependency": return "LINKED_UPD_1_TO_UPD_4" if "APPLY_UPD_1_TO_UPD_4_TO_CONTAINERIZATION_USERS_AND_OTHER_SUBJECTS_ACCESSING_CONTAINERS_OR_IMAGES" in measures["ЗКО.3"]["implementation"] else None
        if query == "zko4_backup_numbers": return "NO_UNIVERSAL_FREQUENCY_COPY_RETENTION_OR_RECOVERY_TIME" if "DO_NOT_INVENT_ZKO_4_BACKUP_FREQUENCY_COPY_COUNT_RETENTION_OR_RECOVERY_TIME" in model["scope_guards"] else None
        if query == "zko5_namespace_subrequirements": return len(measures["ЗКО.5"]["enhancements"][0]["subrequirements"])
        if query == "zko6_iaf_dependency": return "LINKED_IAF_1_AND_IAF_3" if "APPLY_IAF_1_AND_IAF_3_TO_CONTAINER_ENVIRONMENT_USERS" in measures["ЗКО.6"]["implementation"] else None
        if query == "zko6_object_id_class_listed": return any(1 in row for row in measures["ЗКО.6"]["matrix"]["enhancements"].values())
        if query == "zko7_image_lifecycle_ops": return len(image_lifecycle.intersection(measures["ЗКО.7"]["implementation"]))
        if query == "zko7_system_resource_boundary": return "IMAGES_ONLY_ON_SYSTEM_TECHNICAL_RESOURCES" if "PLACE_IMAGES_LAUNCHED_IN_SYSTEM_ONLY_ON_TECHNICAL_RESOURCES_WITHIN_INFORMATION_SYSTEM" in measures["ЗКО.7"]["implementation"] else None
        if query == "zko8_base_interval":
            item = interval("ZKO8_BASE_INTERVAL")
            return "MAX_ONE_MONTH" if item["value"] == 1 and item["unit"] == "MONTH" else None
        if query == "zko8_enhanced_interval":
            item = interval("ZKO8_E1_INTERVAL")
            return "MAX_ONE_WEEK" if item["value"] == 1 and item["unit"] == "WEEK" else None
        if query == "zko8_remediation_deadline": return "NOT_STATED" if "DO_NOT_INVENT_ZKO_8_VULNERABILITY_REMEDIATION_DEADLINE" in model["scope_guards"] else None
        if query == "zko8_exception_semantics": return "ANTI_EXPLOITATION_ROUTE_WHEN_REMEDIATION_IMPOSSIBLE" if "DO_NOT_CONVERT_ZKO_8_ENHANCEMENT_2_INTO_UNCONDITIONAL_PROHIBITION_WHEN_REMEDIATION_IS_IMPOSSIBLE_AND_ANTI_EXPLOITATION_MEASURES_ARE_TAKEN" in model["scope_guards"] else None
        if query == "technology_applicability": return "CONTAINERIZATION_CONDITIONAL" if model["applicability"]["trigger"] == "CONTAINERIZATION_MEANS_OR_CONTAINER_ENVIRONMENT_USED" else None
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_CLASS_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "complete_zko_family": return model["verification_boundary"]["complete_zko_family"]
        if query == "linked_models": return model["verification_boundary"]["referenced_iaf_upd_rsb_content"]
        if query == "product_profiles": return model["verification_boundary"]["product_specific_container_platform_profiles"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZKO_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗКО.{number}" for number in range(1, 9)]
    assert [x["number"] for x in measures["ЗКО.1"]["enhancements"]] == list(range(1, 8))
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 8 ZKO measures; 53 implementation atoms; 5 documentation items; 13 enhancements; 48 class cells; 6 numeric constraints; 1 operator-defined parameter; 64 fail-closed cases")


if __name__ == "__main__":
    main()
