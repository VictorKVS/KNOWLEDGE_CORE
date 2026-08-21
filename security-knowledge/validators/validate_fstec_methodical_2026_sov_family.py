#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-sov-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-sov-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}

    def impl(code): return measures[code]["implementation"]
    def docs(code): return measures[code]["documentation"]
    def enh(code): return measures[code]["enhancements"]
    def contains(code, marker): return any(marker in item for item in impl(code))
    def erule(code, marker): return any(marker in item["rule"] for item in enh(code))
    def operator(pid): return "OPERATOR_DEFINED" if parameters[pid]["universal_value"] == "NOT_STATED" else None

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(model["numeric_constraints"])
        if query == "operator_parameter_count": return len(parameters)
        if query == "matrix_counts": return {k:model["class_matrix_summary"][k] for k in ("cells_total","nonblank_cells","blank_cells")}
        if query == "field_counts":
            item=measures[case["measure"]]
            return {k:len(item[k]) for k in ("implementation","documentation","enhancements")}
        if query == "base_row": return measures[case["measure"]]["matrix"]["base"]
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "sov1_receive_traffic": return contains("СОВ.1","RECEIVE_NETWORK_TRAFFIC")
        if query == "sov1_perimeter_detect_prevent": return contains("СОВ.1","AT_INFORMATION_SYSTEM_PERIMETER")
        if query == "sov1_documented_response": return contains("СОВ.1","DEFINED_IN_OPERATING_DOCUMENTATION")
        if query == "sov1_response_examples_nonexhaustive": return "DO_NOT_TREAT_NOTIFICATION_AND_TRAFFIC_BLOCKING_EXAMPLES_AS_EXHAUSTIVE_RESPONSE_ACTIONS" in model["scope_guards"]
        if query == "sov1_auto_update": return contains("СОВ.1","AUTOMATICALLY_OBTAIN_AND_UPDATE")
        if query == "sov1_source_alternatives": return ["VENDOR","LOCAL"] if contains("СОВ.1","VENDOR_AND_OR_CONFIGURABLE_LOCAL") else None
        if query == "sov1_update_modes": return ["SCHEDULE","ON_DEMAND"] if contains("СОВ.1","BY_SCHEDULE_AND_OR_ON_DEMAND") else None
        if query == "sov1_means": return ["NETWORK_IDS","NETWORK_FIREWALL","OTHER_SECURITY_MEANS"] if contains("СОВ.1","NETWORK_IDS_NETWORK_FIREWALLS_AND_OR_OTHER_SECURITY_MEANS") else None
        if query == "sov1_documentation": return len(docs("СОВ.1")) == 1
        if query == "sov1_enhancement_numbers": return [x["source_number"] for x in enh("СОВ.1")]
        if query == "sov1_unique_enhancement_instances": return len({x["instance_id"] for x in enh("СОВ.1")})
        if query == "sov1_duplicate_three": return sum(x["source_number"] == 3 for x in enh("СОВ.1"))
        if query == "sov1_missing_four_not_invented": return not any(x["source_number"] == 4 for x in enh("СОВ.1"))
        if query == "sov1_rule_development": return erule("СОВ.1","DEVELOP_OR_MODERNIZE")
        if query == "sov1_application_level": return erule("СОВ.1","APPLICATION_LEVEL")
        if query == "sov1_encoded_data": return erule("СОВ.1","ENCODED_DATA")
        if query == "sov1_store_fragments": return erule("СОВ.1","STORE_FRAGMENTS")
        if query == "sov1_retrospective": return erule("СОВ.1","RETROSPECTIVE")
        if query == "sov1_anomalies": return erule("СОВ.1","TRAFFIC_ANOMALIES")
        if query == "sov1_attachment_sandbox": return erule("СОВ.1","ATTACHMENTS_AND_OBJECTS")
        if query == "sov1_complex_security": return erule("СОВ.1","COMPLEX_SECURITY_MEANS")
        if query == "sov1_reputation": return erule("СОВ.1","THREAT_REPUTATION_DATABASE")
        if query == "sov1_one_way_tap": return erule("СОВ.1","ONE_WAY_TRAFFIC_TAPS")
        if query == "sov1_only_enhancement_one_class_listed": return measures["СОВ.1"]["matrix"]["enhancements"] == {"K3":[],"K2":[1],"K1":[1]}
        if query == "sov1_k3_no_direct_enhancement": return measures["СОВ.1"]["matrix"]["enhancements"]["K3"] == []
        if query == "sov1_retention_value": return operator("SOV1_TRAFFIC_FRAGMENT_RETENTION")
        if query == "sov1_near_real_time_value": return operator("SOV1_NEAR_REAL_TIME_THRESHOLD")
        if query == "sov1_update_schedule_value": return operator("SOV1_UPDATE_SCHEDULE")
        if query == "sov2_segment_detection": return contains("СОВ.2","IN_SEGMENTS_OR_AT_SEGMENT_BOUNDARIES")
        if query == "sov2_segment_types": return ["NETWORK","FUNCTIONAL","SIGNIFICANCE","PROTECTION_CLASS","DEVICE_TYPE"] if all(contains("СОВ.2",m) for m in ("NETWORK_SEGMENTS","FUNCTIONAL_SEGMENTS","SIGNIFICANCE_LEVELS","PROTECTION_CLASSES","DEVICE_TYPES")) else None
        if query == "sov2_segment_examples_nonexhaustive": return "DO_NOT_TREAT_SEGMENT_EXAMPLES_AS_EXHAUSTIVE_SEGMENT_TAXONOMY" in model["scope_guards"]
        if query == "sov2_intersegment_analysis": return contains("СОВ.2","BETWEEN_SEGMENTS")
        if query == "sov2_auto_update": return contains("СОВ.2","AUTOMATICALLY_OBTAIN_AND_UPDATE")
        if query == "sov2_source_alternatives": return ["VENDOR","LOCAL"] if contains("СОВ.2","VENDOR_AND_OR_CONFIGURABLE_LOCAL") else None
        if query == "sov2_update_modes": return ["SCHEDULE","ON_DEMAND"] if contains("СОВ.2","BY_SCHEDULE_AND_OR_ON_DEMAND") else None
        if query == "sov2_means": return ["NETWORK_IDS","NETWORK_FIREWALL","OTHER_SECURITY_MEANS"] if contains("СОВ.2","NETWORK_IDS_NETWORK_FIREWALLS_AND_OR_OTHER_SECURITY_MEANS") else None
        if query == "sov2_documentation": return len(docs("СОВ.2")) == 1
        if query == "sov2_block_or_isolate": return "OR" if erule("СОВ.2","BLOCK_NETWORK_TRAFFIC_OR_ISOLATE") else None
        if query == "sov2_centralized_management": return erule("СОВ.2","CENTRALLY_MANAGE")
        if query == "sov2_no_direct_enhancements": return all(not x for x in measures["СОВ.2"]["matrix"]["enhancements"].values())
        if query == "sov2_segment_set_value": return operator("SOV2_SEGMENT_SET")
        if query == "sov2_update_schedule_value": return operator("SOV2_UPDATE_SCHEDULE")
        if query == "all_base_rows_class_listed": return [c for c,x in measures.items() if all(v == "PLUS" for v in x["matrix"]["base"].values())]
        if query == "unlisted_not_required": return "DO_NOT_REQUIRE_UNLISTED_ENHANCEMENTS_FROM_CLASS_MATRIX_ALONE" in model["scope_guards"]
        if query == "numbering_anomaly_status": return model["source_anomalies"][0]["resolution"]
        if query == "numbering_guard": return "DO_NOT_SILENTLY_RENUMBER_DUPLICATE_SOV_1_ENHANCEMENT_3_AS_4" in model["scope_guards"]
        if query == "no_invented_numeric_values": return not model["numeric_constraints"] and all(x["universal_value"] == "NOT_STATED" for x in parameters.values())
        if query == "complete_sov_family": return model["verification_boundary"]["complete_sov_family"]
        if query == "exact_class_cells": return model["verification_boundary"]["exact_sov_class_cells"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "gap_boundary": return {"critical":model["verification_boundary"]["critical_gap_created"],"high":model["verification_boundary"]["high_gap_created"]}
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_SOV_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == ["СОВ.1", "СОВ.2"]
    failures=[]
    for case in fixtures["cases"]:
        actual=evaluate(case)
        if actual != case["expected"]: failures.append((case["id"],case["expected"],actual))
    if failures:
        for failure in failures: print("FAIL",failure)
        raise SystemExit(1)
    print("PASS: 2 SOV measures; 18 implementation atoms; 2 documentation items; 12 enhancement instances; 12 class cells; 0 numeric constraints; 11 operator-defined parameters; 64 fail-closed cases")


if __name__ == "__main__":
    main()
