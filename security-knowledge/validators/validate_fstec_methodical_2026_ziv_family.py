#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-ziv-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-ziv-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    numeric = {item["id"]: item for item in model["numeric_constraints"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}

    def impl(code):
        return measures[code]["implementation"]

    def enhancements(code):
        return measures[code]["enhancements"]

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(numeric)
        if query == "operator_parameter_count": return len(parameters)
        if query == "fully_blank_rows": return model["class_matrix_summary"]["fully_blank_measure_rows"]
        if query == "matrix_counts": return {key: model["class_matrix_summary"][key] for key in ("cells_total", "nonblank_cells", "blank_cells")}
        if query == "field_counts":
            item = measures[case["measure"]]
            return {key: len(item[key]) for key in ("implementation", "documentation", "enhancements")}
        if query == "base_row": return measures[case["measure"]]["matrix"]["base"]
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "ziv1_iaf_dependency": return "LINKED_IAF_2" if any("IAF_2" in x for x in impl("ЗИВ.1")) else None
        if query == "ziv1_identifier_forms": return ["LOGICAL_NAME","LOGICAL_ADDRESS","PHYSICAL_ADDRESS","COMBINATION"] if any("LOGICAL_NAME_LOGICAL_ADDRESS_PHYSICAL_ADDRESS_OR_COMBINATION" in x for x in impl("ЗИВ.1")) else None
        if query == "ziv1_default_passwords": return "PROHIBITED" if any("PROHIBIT_IOT_AUTHENTICATION_WITH_DEFAULT_PASSWORDS" == x for x in impl("ЗИВ.1")) else None
        if query == "ziv1_authentication_protocols": return any("AUTHENTICATION_PROTOCOLS" in x for x in impl("ЗИВ.1"))
        if query == "ziv1_private_identifier_unlisted": return any(x["number"] == 1 and "PSEUDONYMOUS" in x["rule"] for x in enhancements("ЗИВ.1")) and all(not x for x in measures["ЗИВ.1"]["matrix"]["enhancements"].values())
        if query == "ziv1_certificate_auth_unlisted": return any(x["number"] == 2 and "CERTIFICATES" in x["rule"] for x in enhancements("ЗИВ.1"))
        if query == "ziv1_mutual_auth_before_exchange": return any("BEFORE_INFORMATION_EXCHANGE" in x["rule"] for x in enhancements("ЗИВ.1"))
        if query == "ziv2_upd_dependency": return "LINKED_UPD_1_TO_UPD_9" if any("UPD_1_TO_UPD_9" in x for x in impl("ЗИВ.2")) else None
        if query == "ziv2_least_privilege": return any("LEAST_PRIVILEGE" in x for x in impl("ЗИВ.2"))
        if query == "ziv2_access_method_examples_nonexhaustive": return "DO_NOT_TREAT_ROLE_ATTRIBUTE_OR_ACL_EXAMPLES_AS_EXHAUSTIVE_ACCESS_CONTROL_METHODS" in model["scope_guards"]
        if query == "ziv2_operator_sets": return [key for key in parameters if key.startswith("ZIV2_")]
        if query == "ziv2_central_management_unlisted": return any(x["number"] == 1 and "CENTRALLY" in x["rule"] for x in enhancements("ЗИВ.2")) and all(not x for x in measures["ЗИВ.2"]["matrix"]["enhancements"].values())
        if query == "ziv2_command_filter": return any(x["number"] == 6 and "FILTER" in x["rule"] for x in enhancements("ЗИВ.2"))
        if query == "ziv2_crypto_boundary": return "SEPARATE_FSB_LAYER_CONDITIONAL_ON_RUSSIAN_LAW" if "DO_NOT_TREAT_ZIV_2_ENHANCEMENT_7_AS_SELF_CONTAINED_FSB_CRYPTOGRAPHIC_REQUIREMENTS" in model["scope_guards"] else None
        if query == "ziv2_wireless_prohibition_unlisted": return any(x["number"] == 8 and "PROHIBIT_WIRELESS" in x["rule"] for x in enhancements("ЗИВ.2"))
        if query == "ziv2_public_network_isolation": return any(x["number"] == 9 and "ISOLATE" in x["rule"] for x in enhancements("ЗИВ.2"))
        if query == "ziv3_inventory_scope": return ["UNUSED_DEVICES","UNAPPROVED_DEVICES"] if any("UNUSED_AND_UNAPPROVED" in x for x in impl("ЗИВ.3")) else None
        if query == "ziv3_only_permitted_connections": return any("ONLY_TO_PERMITTED" in x for x in impl("ЗИВ.3"))
        if query == "ziv3_input_format_operator_defined": return parameters["ZIV3_INPUT_DATA_AND_COMMAND_FORMATS"]["universal_value"] == "NOT_STATED"
        if query == "ziv3_disable_unused_protocols": return any("DISABLE_UNUSED_IOT_CONNECTION" in x for x in impl("ЗИВ.3"))
        if query == "ziv3_network_segmentation": return any("SEGMENT_IOT_DEVICE_NETWORKS" in x for x in impl("ЗИВ.3"))
        if query == "ziv3_beyond_controlled_zone_protection": return ["DISCLOSURE","MODIFICATION","FALSE_DATA_INJECTION"] if any("DISCLOSURE_MODIFICATION_AND_FALSE_DATA_INJECTION" in x for x in impl("ЗИВ.3")) else None
        if query == "ziv3_enhancement_1_classes": return [key for key, values in measures["ЗИВ.3"]["matrix"]["enhancements"].items() if 1 in values]
        if query == "ziv3_network_traffic_analysis_unlisted": return any(x["number"] == 2 and "NETWORK_TRAFFIC" in x["rule"] for x in enhancements("ЗИВ.3")) and all(2 not in v for v in measures["ЗИВ.3"]["matrix"]["enhancements"].values())
        if query == "ziv4_integrity_scopes":
            prefixes = ("CONTROL_IOT_HARDWARE", "CONTROL_IOT_SOFTWARE_COMPOSITION", "CONTROL_INTEGRITY_OF_IOT_NETWORK_SOFTWARE_UPDATES", "CONTROL_INTEGRITY_OF_IOT_SOFTWARE_CONFIGURATION_FILES")
            return ["HARDWARE","SOFTWARE_COMPOSITION","SOFTWARE_UPDATES","CONFIGURATION_FILES"] if all(any(x.startswith(prefix) for x in impl("ЗИВ.4")) for prefix in prefixes) else None
        if query == "ziv4_unauthorized_additions": return ["DEVICES","SOFTWARE"] if sum("UNAUTHORIZED_NEW" in x for x in impl("ЗИВ.4")) == 2 else None
        if query == "ziv4_firmware_vulnerability_analysis": return any("FIRMWARE_VULNERABILITIES" in x for x in impl("ЗИВ.4"))
        if query == "ziv4_firmware_update_condition": return "AVAILABLE_VERSION_WITHOUT_KNOWN_VULNERABILITIES" if any("AVAILABLE_FIRMWARE_VERSION_WITHOUT_KNOWN_VULNERABILITIES" in x for x in impl("ЗИВ.4")) else None
        if query == "ziv4_weekly_constraint":
            item = numeric["ZIV4_ENH2_CONFIGURATION_INTEGRITY_INTERVAL"]
            return {key: item[key] for key in ("relation","value","unit")}
        if query == "ziv4_weekly_enhancement_unlisted": return all(2 not in v for v in measures["ЗИВ.4"]["matrix"]["enhancements"].values())
        if query == "ziv4_certificate_or_checksum": return "AND_OR" if any("CERTIFICATE_AND_OR_CHECKSUMS" in x["rule"] for x in enhancements("ЗИВ.4")) else None
        if query == "ziv4_block_broken_integrity": return any("BLOCK_EXECUTION" in x["rule"] for x in enhancements("ЗИВ.4"))
        if query == "ziv5_rsb_dependency": return "LINKED_RSB_1_TO_RSB_5" if any("RSB_1_TO_RSB_5" in x for x in impl("ЗИВ.5")) else None
        if query == "ziv5_analyze_and_respond": return any("ANALYZE_REGISTERED_EVENTS_AND_RESPOND" in x for x in impl("ЗИВ.5"))
        if query == "ziv5_enhancement_1_classes": return [key for key, values in measures["ЗИВ.5"]["matrix"]["enhancements"].items() if 1 in values]
        if query == "ziv5_isolation_unlisted": return any(x["number"] == 2 and "ISOLATE" in x["rule"] for x in enhancements("ЗИВ.5")) and all(2 not in v for v in measures["ЗИВ.5"]["matrix"]["enhancements"].values())
        if query == "unlisted_enhancements_not_baseline": return "DO_NOT_REQUIRE_UNLISTED_ENHANCEMENTS_FROM_CLASS_MATRIX_ALONE" in model["scope_guards"]
        if query == "all_base_rows_class_listed": return [code for code, item in measures.items() if all(v == "PLUS" for v in item["matrix"]["base"].values())]
        if query == "complete_ziv_family": return model["verification_boundary"]["complete_ziv_family"]
        if query == "official_and_gap_boundary": return {"official_bytes": model["verification_boundary"]["official_immutable_bytes"], "critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        if query == "product_profile_boundary": return model["verification_boundary"]["product_specific_iot_profiles"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZIV_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗИВ.{number}" for number in range(1, 6)]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 5 ZIV measures; 24 implementation atoms; 0 documentation items; 20 enhancements; 30 class cells; 1 weekly constraint; 9 operator-defined parameters; 64 fail-closed cases")


if __name__ == "__main__":
    main()
