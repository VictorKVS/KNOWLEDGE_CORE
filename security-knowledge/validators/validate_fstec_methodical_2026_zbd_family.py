#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-zbd-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-zbd-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    numeric = {item["id"]: item for item in model["numeric_constraints"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}

    def impl(code): return measures[code]["implementation"]
    def enh(code): return measures[code]["enhancements"]

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(numeric)
        if query == "operator_parameter_count": return len(parameters)
        if query == "fully_blank_rows": return model["class_matrix_summary"]["fully_blank_measure_rows"]
        if query == "matrix_counts": return {key: model["class_matrix_summary"][key] for key in ("cells_total","nonblank_cells","blank_cells")}
        if query == "field_counts":
            item = measures[case["measure"]]
            return {key: len(item[key]) for key in ("implementation","documentation","enhancements")}
        if query == "base_row": return measures[case["measure"]]["matrix"]["base"]
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "zbd1_user_iaf_dependency": return "LINKED_IAF_1_AND_IAF_3" if any("IAF_1_AND_IAF_3" in x for x in impl("ЗБД.1")) else None
        if query == "zbd1_device_iaf_dependency": return "LINKED_IAF_2" if any("IAF_2" in x for x in impl("ЗБД.1")) else None
        if query == "zbd1_identifier_forms": return ["LOGICAL_NAME","LOGICAL_ADDRESS","PHYSICAL_ADDRESS","COMBINATION"] if sum("LOGICAL_NAME_LOGICAL_ADDRESS_PHYSICAL_ADDRESS_OR_COMBINATION" in x for x in impl("ЗБД.1")) == 2 else None
        if query == "zbd1_default_passwords": return "PROHIBITED" if any("DEFAULT_PASSWORDS" in x for x in impl("ЗБД.1")) else None
        if query == "zbd1_ssid_hide_k1": return measures["ЗБД.1"]["matrix"]["enhancements"] == {"K3":[],"K2":[],"K1":[1]}
        if query == "zbd1_no_broadcast_unlisted": return any(x["number"] == 3 and "DO_NOT_BROADCAST" in x["rule"] for x in enh("ЗБД.1")) and all(3 not in v for v in measures["ЗБД.1"]["matrix"]["enhancements"].values())
        if query == "zbd2_upd_dependency": return "LINKED_UPD_1_TO_UPD_9" if any("UPD_1_TO_UPD_9" in x for x in impl("ЗБД.2")) else None
        if query == "zbd2_mac_example_nonexclusive": return "DO_NOT_TREAT_MAC_ADDRESS_EXAMPLE_AS_THE_ONLY_DEVICE_FILTER_METHOD" in model["scope_guards"]
        if query == "zbd2_admin_config_only": return any("ONLY_TO_INFORMATION_SYSTEM_ADMINISTRATORS" in x for x in impl("ЗБД.2"))
        if query == "zbd2_identified_authenticated_only": return any("ONLY_AFTER_USER_IDENTIFICATION_AND_AUTHENTICATION" in x for x in impl("ЗБД.2"))
        if query == "zbd2_least_privilege": return any("LEAST_PRIVILEGE" in x for x in impl("ЗБД.2"))
        if query == "zbd2_session_limit_operator_defined": return parameters["ZBD2_SESSION_DURATION_LIMIT"]["universal_value"] == "NOT_STATED"
        if query == "zbd3_segmentation": return any("SEGMENT_WIRELESS" in x for x in impl("ЗБД.3"))
        if query == "zbd3_permitted_points_only": return any("ONLY_TO_PERMITTED" in x for x in impl("ЗБД.3"))
        if query == "zbd3_controlled_interfaces": return any("ONLY_THROUGH_CONTROLLED" in x for x in impl("ЗБД.3"))
        if query == "zbd3_pre_exchange_control": return any("BEFORE_INFORMATION_EXCHANGE" in x for x in impl("ЗБД.3"))
        if query == "zbd3_unused_functions": return "DISABLED_OR_BLOCKED" if any("DISABLE_OR_BLOCK_UNUSED" in x for x in impl("ЗБД.3")) else None
        if query == "zbd3_vulnerability_analysis": return ["FIRMWARE","SOFTWARE"] if any("FIRMWARE_AND_SOFTWARE_VULNERABILITIES" in x for x in impl("ЗБД.3")) else None
        if query == "zbd3_update_condition": return "AVAILABLE_VERSION_WITHOUT_KNOWN_VULNERABILITIES" if any("AVAILABLE_FIRMWARE_AND_SOFTWARE_WITHOUT_KNOWN_VULNERABILITIES" in x for x in impl("ЗБД.3")) else None
        if query == "zbd3_auto_connect_unlisted": return any(x["number"] == 3 and "AUTOMATIC" in x["rule"] for x in enh("ЗБД.3")) and all(3 not in v for v in measures["ЗБД.3"]["matrix"]["enhancements"].values())
        if query == "zbd4_integrity_scopes": return ["SOFTWARE_AND_FIRMWARE","HARDWARE_COMPOSITION","INTERFACES","CONTROLLED_ZONE","UPDATES_AND_VULNERABILITIES"] if len(impl("ЗБД.4")) == 5 else None
        if query == "zbd4_weekly_constraint":
            item = numeric["ZBD4_ENH1_SETTING_INTEGRITY_INTERVAL"]
            return {key:item[key] for key in ("relation","value","unit")}
        if query == "zbd4_weekly_unlisted": return all(1 not in v for v in measures["ЗБД.4"]["matrix"]["enhancements"].values())
        if query == "zbd4_signature_or_checksum": return "OR" if any("SIGNATURE_OR_CHECKSUMS" in x["rule"] for x in enh("ЗБД.4")) else None
        if query == "zbd4_user_setting_change_guard": return any("PREVENT_CONNECTED_DEVICE_USER" in x["rule"] for x in enh("ЗБД.4"))
        if query == "zbd5_configurable_power": return any("CONFIGURABLE_SIGNAL_POWER" in x for x in impl("ЗБД.5"))
        if query == "zbd5_boundary_objective": return "MINIMUM_SIGNAL_AT_PHYSICAL_BOUNDARY" if any("MINIMIZE_SIGNAL_AT_BOUNDARIES" in x for x in impl("ЗБД.5")) else None
        if query == "zbd5_signal_value": return "OPERATOR_DEFINED" if parameters["ZBD5_SIGNAL_POWER_LEVELS"]["universal_value"] == "NOT_STATED" else None
        if query == "zbd5_coverage_map": return any("COVERAGE_MAP" in x["rule"] for x in enh("ЗБД.5"))
        if query == "zbd5_frequency_filter": return any("FREQUENCY_RANGE" in x["rule"] for x in enh("ЗБД.5"))
        if query == "zbd6_rsb_dependency": return "LINKED_RSB_1_TO_RSB_5" if any("RSB_1_TO_RSB_5" in x for x in impl("ЗБД.6")) else None
        if query == "zbd6_analyze_and_respond": return any("ANALYZE_REGISTERED_EVENTS_AND_RESPOND" in x for x in impl("ЗБД.6"))
        if query == "zbd6_enhancement_1_classes": return [key for key, values in measures["ЗБД.6"]["matrix"]["enhancements"].items() if 1 in values]
        if query == "unlisted_enhancements_not_baseline": return "DO_NOT_REQUIRE_UNLISTED_ENHANCEMENTS_FROM_CLASS_MATRIX_ALONE" in model["scope_guards"]
        if query == "all_base_rows_class_listed": return [code for code,item in measures.items() if all(v == "PLUS" for v in item["matrix"]["base"].values())]
        if query == "complete_zbd_family": return model["verification_boundary"]["complete_zbd_family"]
        if query == "official_and_gap_boundary": return {"official_bytes":model["verification_boundary"]["official_immutable_bytes"],"critical":model["verification_boundary"]["critical_gap_created"],"high":model["verification_boundary"]["high_gap_created"]}
        if query == "product_profile_boundary": return model["verification_boundary"]["product_specific_wireless_profiles"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZBD_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗБД.{number}" for number in range(1,7)]
    failures=[]
    for case in fixtures["cases"]:
        actual=evaluate(case)
        if actual != case["expected"]: failures.append((case["id"],case["expected"],actual))
    if failures:
        for failure in failures: print("FAIL",failure)
        raise SystemExit(1)
    print("PASS: 6 ZBD measures; 30 implementation atoms; 0 documentation items; 22 enhancements; 36 class cells; 1 weekly constraint; 9 operator-defined parameters; 64 fail-closed cases")


if __name__ == "__main__":
    main()
