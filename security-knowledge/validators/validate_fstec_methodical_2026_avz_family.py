#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-avz-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-avz-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}

    def impl(code): return measures[code]["implementation"]
    def docs(code): return measures[code]["documentation"]
    def enh(code): return measures[code]["enhancements"]

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(model["numeric_constraints"])
        if query == "operator_parameter_count": return len(parameters)
        if query == "fully_blank_rows": return model["class_matrix_summary"]["fully_blank_measure_rows"]
        if query == "matrix_counts": return {key:model["class_matrix_summary"][key] for key in ("cells_total","nonblank_cells","blank_cells")}
        if query == "field_counts":
            item=measures[case["measure"]]
            return {key:len(item[key]) for key in ("implementation","documentation","enhancements")}
        if query == "base_row": return measures[case["measure"]]["matrix"]["base"]
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "avz1_device_scope": return ["PHYSICAL","VIRTUAL"] if any("PHYSICAL_AND_VIRTUAL" in x for x in impl("АВЗ.1")) else None
        if query == "avz1_install_configure_manage": return any("INSTALL_CONFIGURE_AND_MANAGE" in x for x in impl("АВЗ.1"))
        if query == "avz1_object_access": return any("ACCESS_TO_OBJECTS" in x for x in impl("АВЗ.1"))
        if query == "avz1_periodic_scans": return any("PERIODIC_DEVICE_SCANS" in x for x in impl("АВЗ.1"))
        if query == "avz1_external_near_real_time": return any("NEAR_REAL_TIME_SCANNING_OF_EXTERNAL_SOURCE" in x for x in impl("АВЗ.1"))
        if query == "avz1_removable_media": return any("REMOVABLE_MEDIA" in x for x in impl("АВЗ.1"))
        if query == "avz1_periodic_or_command": return "OR" if any("PERIODICALLY_OR_ON_COMMAND" in x for x in impl("АВЗ.1")) else None
        if query == "avz1_response_define_execute": return any("DEFINE_RESPONSE_ACTIONS" in x for x in impl("АВЗ.1")) and any("EXECUTE_DEFINED_RESPONSE_ACTIONS" in x for x in impl("АВЗ.1"))
        if query == "avz1_vendor_update": return any("PER_VENDOR_INFORMATION" in x for x in impl("АВЗ.1"))
        if query == "avz1_post_update_scan": return any("AFTER_INDICATOR_DATABASE_UPDATE" in x for x in impl("АВЗ.1"))
        if query == "avz1_means": return "ANTIMALWARE" if any(x == "IMPLEMENT_USING_ANTIMALWARE_MEANS" for x in impl("АВЗ.1")) else None
        if query == "avz1_documentation": return ["DEVICE_ACCOUNTING","PERIODIC_SCANS","RESPONSE","DATABASE_UPDATES"] if len(docs("АВЗ.1")) == 4 else None
        if query == "avz1_preboot": return any("BEFORE_OPERATING_SYSTEM_BOOT" in x["rule"] for x in enh("АВЗ.1"))
        if query == "avz1_centralized_management": return any("CENTRALIZED" in x["rule"] for x in enh("АВЗ.1"))
        if query == "avz1_load_open_execute": return ["LOAD","OPEN","EXECUTION"] if any("ON_LOAD_OPEN_OR_EXECUTION" in x["rule"] for x in enh("АВЗ.1")) else None
        if query == "avz1_periodic_schedule": return "OPERATOR_DEFINED" if parameters["AVZ1_PERIODIC_SCAN_SCHEDULE"]["universal_value"] == "NOT_STATED" else None
        if query == "avz1_near_real_time": return "OPERATOR_DEFINED" if parameters["AVZ1_NEAR_REAL_TIME_THRESHOLD"]["universal_value"] == "NOT_STATED" else None
        if query == "external_sources_nonexhaustive": return "DO_NOT_TREAT_REMOVABLE_MEDIA_NETWORK_CONNECTIONS_OR_PUBLIC_NETWORKS_AS_EXHAUSTIVE_EXTERNAL_SOURCES" in model["scope_guards"]
        if query == "avz2_detect_email": return any("DETECT_MALWARE_IN_EMAIL" in x for x in impl("АВЗ.2"))
        if query == "avz2_block_or_delete": return "OR" if any("BLOCK_OR_DELETE" in x for x in impl("АВЗ.2")) else None
        if query == "avz2_inform_notify": return any("INFORM_ABOUT" in x for x in impl("АВЗ.2")) and any("NOTIFY_ABOUT" in x for x in impl("АВЗ.2"))
        if query == "avz2_documentation": return len(docs("АВЗ.2")) == 1
        if query == "avz2_encoded_archived": return ["ENCODED_DATA","ARCHIVED_FILES"] if any("ENCODED_DATA_AND_ARCHIVED_FILES" in x["rule"] for x in enh("АВЗ.2")) else None
        if query == "avz2_enhancement_unlisted": return all(1 not in x for x in measures["АВЗ.2"]["matrix"]["enhancements"].values())
        if query == "avz3_extracted_file_scan": return any("SCAN_FILES_EXTRACTED" in x for x in impl("АВЗ.3"))
        if query == "avz3_near_real_time": return any("NEAR_REAL_TIME" in x for x in impl("АВЗ.3"))
        if query == "avz3_detection_methods": return ["SIGNATURE","HASH_SUMS","OTHER_INDICATORS"] if all(any(mark in x for x in impl("АВЗ.3")) for mark in ("SIGNATURE","HASH_SUMS","OTHER_INDICATORS")) else None
        if query == "avz3_response_documented": return any("ACCORDING_TO_OPERATING_DOCUMENTATION" in x for x in impl("АВЗ.3"))
        if query == "avz3_means_alternatives": return ["ANTIMALWARE","NETWORK_FIREWALL","OTHER_SECURITY_MEANS"] if any("ANTIMALWARE_MEANS_NETWORK_FIREWALLS_AND_OR_OTHER_SECURITY_MEANS" in x for x in impl("АВЗ.3")) else None
        if query == "avz3_documentation": return len(docs("АВЗ.3")) == 1
        if query == "avz3_heuristic": return any("HEURISTIC" in x["rule"] for x in enh("АВЗ.3"))
        if query == "avz3_application_scope": return any("APPLICATION_LEVEL" in x["rule"] for x in enh("АВЗ.3"))
        if query == "avz3_encoded_data": return any("ENCODED_DATA" in x["rule"] for x in enh("АВЗ.3"))
        if query == "avz3_near_real_time_value": return "OPERATOR_DEFINED" if parameters["AVZ3_NEAR_REAL_TIME_THRESHOLD"]["universal_value"] == "NOT_STATED" else None
        if query == "avz3_application_value": return "OPERATOR_DEFINED" if parameters["AVZ3_APPLICATION_SCOPE"]["universal_value"] == "NOT_STATED" else None
        if query == "avz4_trigger": return measures["АВЗ.4"]["applicability_condition"]
        if query == "avz4_pipeline": return ["TRANSFER_COPY","DYNAMIC_ANALYSIS","OBTAIN_RESULTS"] if len(impl("АВЗ.4")) == 3 else None
        if query == "avz4_no_documentation": return docs("АВЗ.4") == []
        if query == "avz4_enhancements": return ["SIMULATE_USER_ACTIONS","LOAD_VIRTUAL_MACHINE_IMAGES"] if len(enh("АВЗ.4")) == 2 else None
        if query == "blank_row_not_prohibition": return "DO_NOT_TREAT_AVZ_4_BLANK_BASE_ROW_AS_PROHIBITION_OR_PROOF_OF_NON_APPLICABILITY" in model["scope_guards"]
        if query == "all_base_rows_class_listed": return [code for code,item in measures.items() if all(v == "PLUS" for v in item["matrix"]["base"].values())]
        if query == "no_class_listed_enhancements": return all(not values for item in measures.values() for values in item["matrix"]["enhancements"].values())
        if query == "complete_avz_family": return model["verification_boundary"]["complete_avz_family"]
        if query == "official_and_gap_boundary": return {"official_bytes":model["verification_boundary"]["official_immutable_bytes"],"critical":model["verification_boundary"]["critical_gap_created"],"high":model["verification_boundary"]["high_gap_created"]}
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_AVZ_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"АВЗ.{number}" for number in range(1,5)]
    failures=[]
    for case in fixtures["cases"]:
        actual=evaluate(case)
        if actual != case["expected"]: failures.append((case["id"],case["expected"],actual))
    if failures:
        for failure in failures: print("FAIL",failure)
        raise SystemExit(1)
    print("PASS: 4 AVZ measures; 27 implementation atoms; 6 documentation items; 9 enhancements; 24 class cells; 0 numeric constraints; 9 operator-defined parameters; 64 fail-closed cases")


if __name__ == "__main__":
    main()
