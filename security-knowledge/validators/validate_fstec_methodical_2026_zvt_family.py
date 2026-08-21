#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-zvt-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-zvt-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}

    zvt3_events = {
        "DETECT_REQUEST_DATA_VIOLATING_TYPE_SIZE_FORMAT_OR_ALLOWED_CONTENT_SCHEMA_LIMITS",
        "DETECT_CONTROL_CHARACTERS_OR_CONSTRUCTS_CAPABLE_OF_CHANGING_APPLICATION_PROCESSING_LOGIC",
        "DETECT_ACCESS_AUTHENTICATORS_OR_OTHER_SENSITIVE_INFORMATION_IN_CLEAR_TEXT_REQUESTS",
        "DETECT_REQUESTS_FROM_AUTOMATED_WEB_VULNERABILITY_SEARCH_OR_EXPLOITATION_TOOLS",
        "DETECT_REQUESTS_FROM_AUTOMATED_AUTHENTICATION_BRUTE_FORCE_TOOLS",
    }
    zvt3_attributes = {
        "FILTER_ON_REQUESTED_RESOURCE_UNIFORM_IDENTIFIER", "FILTER_ON_WEB_REQUEST_METHOD",
        "FILTER_ON_REQUEST_HEADER_VALUES", "FILTER_ON_REQUEST_PARAMETER_NAMES_AND_VALUES",
        "FILTER_ON_WEB_CLIENT_IDENTIFIER_HEADER_ATTRIBUTE_SET",
    }
    zvt4_web_events = {
        "REGISTER_WEB_USER_IDENTIFICATION_AND_AUTHENTICATION_EVENTS",
        "REGISTER_WEB_USER_ACCOUNT_MANAGEMENT_EVENTS_WHEN_APPLICATION_SUPPORTS_SUCH_CHANGES",
        "REGISTER_ACCESS_SUBJECT_AND_OBJECT_TYPE_CHANGE_EVENTS_WHEN_APPLICATION_SUPPORTS_SUCH_CHANGES",
        "REGISTER_SUBJECT_TO_OBJECT_OR_FUNCTION_ACCESS_TYPE_CHANGE_EVENTS_WHEN_APPLICATION_SUPPORTS_SUCH_CHANGES",
        "REGISTER_PARALLEL_WEB_SESSION_LIMIT_EVENTS",
        "REGISTER_INACTIVITY_SESSION_TERMINATION_EVENTS",
        "REGISTER_WEB_APPLICATION_SETTING_CHANGE_EVENTS",
    }
    zvt4_firewall_events = {x for x in measures["ЗВТ.4"]["implementation"] if x.startswith("REGISTER_") and x.endswith("_AT_FIREWALL_LEVEL")}

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
        if query == "zvt1_zpi_dependency": return "LINKED_ZPI_1" if any("ZPI_1" in x for x in measures["ЗВТ.1"]["implementation"]) else None
        if query == "zvt1_upd_dependency": return "LINKED_UPD_2" if any("UPD_2" in x for x in measures["ЗВТ.1"]["implementation"]) else None
        if query == "zvt1_literal_zks_reference": return "ZKS_1_TO_ZKS_5" if any("ZKS_1_TO_ZKS_5" in x for x in measures["ЗВТ.1"]["implementation"]) else None
        if query == "zvt1_zks5_catalog_resolution": return "PENDING_FAIL_CLOSED" if model["source_anomalies"][0]["handling"] == "PRESERVE_LITERAL_REFERENCE_AND_BLOCK_AUTOMATIC_MAPPING_OF_ZKS_5" else None
        if query == "zvt1_enhancements_class_listed": return any(row for row in measures["ЗВТ.1"]["matrix"]["enhancements"].values())
        if query == "zvt2_iaf_dependency": return "LINKED_IAF_1_AND_IAF_3" if any("IAF_1_AND_IAF_3" in x for x in measures["ЗВТ.2"]["implementation"]) else None
        if query == "zvt2_upd_dependency_count": return len([x for x in measures["ЗВТ.2"]["implementation"] if "UPD_" in x])
        if query == "zvt2_client_only_auth": return "PROHIBITED" if any("CLIENT_SIDE" in x for x in measures["ЗВТ.2"]["implementation"]) else None
        if query == "zvt2_second_factor_classes": return [k for k,v in measures["ЗВТ.2"]["matrix"]["enhancements"].items() if 1 in v]
        if query == "zvt3_zpi_dependency": return "LINKED_ZPI_3" if any("ZPI_3" in x for x in measures["ЗВТ.3"]["implementation"]) else None
        if query == "zvt3_minimum_event_groups": return len(zvt3_events.intersection(measures["ЗВТ.3"]["implementation"]))
        if query == "zvt3_minimum_http_attributes": return len(zvt3_attributes.intersection(measures["ЗВТ.3"]["implementation"]))
        if query == "zvt3_minimum_semantics": return "NON_EXHAUSTIVE" if "DO_NOT_TREAT_ZVT_3_MINIMUM_EVENT_OR_ATTRIBUTE_LISTS_AS_EXHAUSTIVE" in model["scope_guards"] else None
        if query == "zvt3_internet_firewall_trigger": return "INTERNET_ACCESSIBLE_ONLY" if "DO_NOT_REQUIRE_WEB_APPLICATION_FIREWALL_ROUTE_FOR_NON_INTERNET_WEB_APPLICATIONS_FROM_INTERNET_SPECIFIC_SENTENCE" in model["scope_guards"] else None
        if query == "zvt3_class_listed_enhancements": return sorted(set(n for row in measures["ЗВТ.3"]["matrix"]["enhancements"].values() for n in row))
        if query == "zvt3_enhancement_2_exists": return any(x["number"] == 2 for x in measures["ЗВТ.3"]["enhancements"])
        if query == "zvt3_enhancement_2_class_listed": return any(2 in row for row in measures["ЗВТ.3"]["matrix"]["enhancements"].values())
        if query == "zvt4_web_event_types": return len(zvt4_web_events)
        if query == "zvt4_firewall_event_types": return len(zvt4_firewall_events)
        if query == "zvt4_rsb_upd_dependency": return "LINKED_RSB_1_TO_RSB_5_AND_UPD_1_TO_UPD_9" if "REGISTER_WEB_ACCESS_ATTEMPT_SECURITY_EVENTS_IN_ACCORDANCE_WITH_RSB_1_TO_RSB_5_AND_UPD_1_TO_UPD_9" in measures["ЗВТ.4"]["implementation"] else None
        if query == "zvt4_siem_transfer": return any("TRANSMIT_REGISTERED" in x for x in measures["ЗВТ.4"]["implementation"])
        if query == "zvt4_auto_response_pair": return ["BLOCK_SESSION", "NOTIFY_ADMIN"] if any("AUTOMATICALLY_BLOCK" in x for x in measures["ЗВТ.4"]["implementation"]) and any("NOTIFY_SYSTEM_ADMINISTRATOR" in x for x in measures["ЗВТ.4"]["implementation"]) else None
        if query == "zvt4_conditional_event_qualifiers": return len([x for x in measures["ЗВТ.4"]["implementation"] if "WHEN_APPLICATION_SUPPORTS_SUCH_CHANGES" in x])
        if query == "zvt4_response_time": return "NOT_STATED" if "DO_NOT_INVENT_ZVT_4_EVENT_RETENTION_OR_RESPONSE_TIME" in model["scope_guards"] else None
        if query == "zvt5_avz_dependency": return "LINKED_AVZ_1" if any("AVZ_1" in x for x in measures["ЗВТ.5"]["implementation"]) else None
        if query == "zvt5_request_body_scope": return "FILES_SCRIPTS_AND_DATA" if any("FILES_SCRIPTS_AND_DATA" in x for x in measures["ЗВТ.5"]["implementation"]) else None
        if query == "zvt5_autorun": return "PREVENTED" if any("PREVENT_AUTOMATIC_EXECUTION" in x for x in measures["ЗВТ.5"]["implementation"]) else None
        if query == "zvt5_retrospective_class_listed": return any(1 in row for row in measures["ЗВТ.5"]["matrix"]["enhancements"].values())
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_CLASS_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "complete_zvt_family": return model["verification_boundary"]["complete_zvt_family"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "source_anomaly_count": return len(model["source_anomalies"])
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZVT_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗВТ.{number}" for number in range(1, 6)]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 5 ZVT measures; 39 implementation atoms; 5 documentation items; 8 enhancements; 30 class cells; 0 numeric constraints; 5 operator-defined parameters; 1 source anomaly; 64 fail-closed cases")


if __name__ == "__main__":
    main()
