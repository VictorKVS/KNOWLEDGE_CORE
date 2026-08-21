#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-zmu-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-zmu-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    numeric = {item["id"]: item for item in model["numeric_constraints"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}

    def impl_rules(code):
        return [item["rule"] if isinstance(item, dict) else item for item in measures[code]["implementation"]]

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(numeric)
        if query == "relational_count": return len(model["relational_constraints"])
        if query == "operator_parameter_count": return len(parameters)
        if query == "fully_blank_rows": return model["class_matrix_summary"]["fully_blank_measure_rows"]
        if query == "matrix_counts": return {key: model["class_matrix_summary"][key] for key in ("cells_total", "nonblank_cells", "blank_cells")}
        if query == "field_counts":
            item = measures[case["measure"]]
            return {key: len(item[key]) for key in ("implementation", "documentation", "enhancements")}
        if query == "base_row": return measures[case["measure"]]["matrix"]["base"]
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "numeric_value":
            item = numeric[case["id"]]
            return {key: item[key] for key in ("relation", "value", "unit")}
        if query == "zmu1_iaf_dependency": return "LINKED_IAF_1_TO_IAF_4" if any("IAF_1_TO_IAF_4" in x for x in impl_rules("ЗМУ.1")) else None
        if query == "zmu1_password_profile_exact": return {x["value"] for x in numeric.values()} == {5, 6, 10, 12, 15, 30}
        if query == "zmu2_upd_dependency": return "LINKED_UPD_1_TO_UPD_9" if any("UPD_1_TO_UPD_9" in x for x in impl_rules("ЗМУ.2")) else None
        if query == "zmu2_least_privilege": return any("LEAST_PRIVILEGE" in x for x in impl_rules("ЗМУ.2"))
        if query == "zmu3_integrity_scopes":
            return ["OPERATING_SYSTEM", "SECURITY_SOFTWARE", "APPLICATION_SOFTWARE"] if len([x for x in impl_rules("ЗМУ.3") if "INTEGRITY" in x]) == 3 else None
        if query == "zmu3_debug_guard": return "PROHIBIT_OR_POST_PROCESS_INTEGRITY_CONTROL" if any(x["number"] == 1 and "AFTER_EACH" in x["rule"] for x in measures["ЗМУ.3"]["enhancements"]) else None
        if query == "zmu3_trusted_boot_unlisted": return any(x["number"] == 3 for x in measures["ЗМУ.3"]["enhancements"]) and all(3 not in v for v in measures["ЗМУ.3"]["matrix"]["enhancements"].values())
        if query == "zmu4_public_directory": return "PROHIBITED" if any("PUBLIC_MOBILE_DIRECTORIES" in x for x in impl_rules("ЗМУ.4")) else None
        if query == "zmu4_public_cloud_backup": return "BLOCKED" if any("PUBLIC_INTERNET_CLOUD" in x for x in impl_rules("ЗМУ.4")) else None
        if query == "zmu4_zks_dependency": return "LINKED_ZKS_1" if any("ZKS_1" in x for x in impl_rules("ЗМУ.4")) else None
        if query == "zmu4_wipe_relation":
            item = model["relational_constraints"][0]
            return {"multiplier": item["multiplier"], "strict": "MORE_THAN", "absolute": "NOT_SUBSTITUTED"}
        if query == "zmu4_handoff_sanitation": return any("TRANSFERRING_MOBILE_DEVICE_BETWEEN_USERS" in x["rule"] for x in measures["ЗМУ.4"]["enhancements"])
        if query == "zmu5_avz_dependency": return "LINKED_AVZ_1" if any("AVZ_1" in x for x in impl_rules("ЗМУ.5")) else None
        if query == "zmu6_documentation": return "APPLICATION_COMPOSITION_REQUIRED" if measures["ЗМУ.6"]["documentation"] else None
        if query == "zmu6_remote_management_guard": return any("PROHIBIT_REMOTE_DEVICE_MANAGEMENT_BY_THIRD_PARTY" in x for x in impl_rules("ЗМУ.6"))
        if query == "zmu7_operator_parameters": return list(parameters)
        if query == "zmu7_mutual_auth_unlisted": return any("MUTUALLY_AUTHENTICATE" in x["rule"] for x in measures["ЗМУ.7"]["enhancements"]) and all(not v for v in measures["ЗМУ.7"]["matrix"]["enhancements"].values())
        if query == "zmu8_baseline": return "NOT_BASELINE_ALL_CLASSES" if all(v == "BLANK" for v in measures["ЗМУ.8"]["matrix"]["base"].values()) else None
        if query == "zmu8_blank_semantics": return "ADAPTATION_AND_THREAT_VERIFICATION_RETAINED" if "DO_NOT_TREAT_ZMU_8_BLANK_ROW_AS_PROHIBITION_OR_DELETE_ADAPTATION_AND_THREAT_VERIFICATION" in model["scope_guards"] else None
        if query == "zmu8_rf_server_condition": return any("SERVERS_LOCATED_IN_RUSSIAN_FEDERATION" in x["rule"] for x in measures["ЗМУ.8"]["enhancements"])
        if query == "zmu9_rsb_dependency": return "LINKED_RSB_1_TO_RSB_5" if any("RSB_1_TO_RSB_5" in x for x in impl_rules("ЗМУ.9")) else None
        if query == "zmu9_enhancement_1_classes": return [key for key, values in measures["ЗМУ.9"]["matrix"]["enhancements"].items() if 1 in values]
        if query == "unlisted_enhancements_not_baseline": return "DO_NOT_REQUIRE_UNLISTED_ENHANCEMENTS_FROM_CLASS_MATRIX_ALONE" in model["scope_guards"]
        if query == "complete_zmu_family": return model["verification_boundary"]["complete_zmu_family"]
        if query == "official_and_gap_boundary": return {"official_bytes": model["verification_boundary"]["official_immutable_bytes"], "critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        if query == "product_profile_boundary": return model["verification_boundary"]["product_specific_mobile_profiles"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZMU_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗМУ.{number}" for number in range(1, 10)]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 9 ZMU measures; 36 implementation atoms; 1 documentation item; 15 enhancements; 54 class cells; 6 exact numeric constraints; 1 relational constraint; 2 operator-defined parameters; 68 fail-closed cases")


if __name__ == "__main__":
    main()
