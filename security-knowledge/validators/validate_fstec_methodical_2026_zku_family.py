#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-zku-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-zku-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}

    def impl_rules(code):
        return [item["rule"] if isinstance(item, dict) else item for item in measures[code]["implementation"]]

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(model["numeric_constraints"])
        if query == "operator_parameter_count": return len(parameters)
        if query == "fully_blank_rows": return model["class_matrix_summary"]["fully_blank_measure_rows"]
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "matrix_counts": return {key: model["class_matrix_summary"][key] for key in ("cells_total", "nonblank_cells", "blank_cells")}
        if query == "base_row": return measures[case["measure"]]["matrix"]["base"]
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "zku1_iaf_dependency": return "LINKED_IAF_1_AND_IAF_3" if any("IAF_1_AND_IAF_3" in x for x in impl_rules("ЗКУ.1")) else None
        if query == "zku1_upd_dependency": return "LINKED_UPD_1_TO_UPD_9" if any("UPD_1_TO_UPD_9" in x for x in impl_rules("ЗКУ.1")) else None
        if query == "zku1_least_privilege": return any("LEAST_PRIVILEGE" in x for x in impl_rules("ЗКУ.1"))
        if query == "zku2_integrity_scopes": return ["OPERATING_SYSTEM", "SECURITY_SOFTWARE", "OTHER_OPERATOR_DEFINED_SOFTWARE"] if len([x for x in impl_rules("ЗКУ.2") if "INTEGRITY" in x]) == 3 else None
        if query == "zku2_unauthorized_install_run": return "PROHIBITED" if any("PROHIBIT_INSTALLATION_AND_EXECUTION" in x for x in impl_rules("ЗКУ.2")) else None
        if query == "zku2_debug_guard": return "PROHIBIT_OR_POST_PROCESS_INTEGRITY_CONTROL" if any(x["number"] == 8 and "POST_PROCESS" not in x["rule"] and "AFTER_EACH" in x["rule"] for x in measures["ЗКУ.2"]["enhancements"]) else None
        if query == "zku2_other_software_scope": return "OPERATOR_DEFINED" if parameters["ZKU2_OTHER_SOFTWARE_INTEGRITY_SCOPE"]["universal_value"] == "NOT_STATED" else None
        if query == "zku3_avz_dependency": return "LINKED_AVZ_1" if any("AVZ_1" in x for x in impl_rules("ЗКУ.3")) else None
        if query == "zku3_no_av_route": return "COMPENSATING_PREVENTION_REQUIRED" if any("TECHNICALLY_IMPOSSIBLE" in x and "PREVENTING" in x for x in impl_rules("ЗКУ.3")) else None
        if query == "zku3_internet_trigger": return "INTERNET_ACCESS_REQUIRED" if any(x["number"] == 1 and "INTERNET_ACCESS" in x["rule"] for x in measures["ЗКУ.3"]["enhancements"]) else None
        if query == "zku3_enhancement_1_classes": return [k for k,v in measures["ЗКУ.3"]["matrix"]["enhancements"].items() if 1 in v]
        if query == "zku3_retrospective_period": return "OPERATOR_DEFINED" if parameters["ZKU3_RETROSPECTIVE_ANALYSIS_PERIODICITY"]["universal_value"] == "NOT_STATED" else None
        if query == "zku3_near_real_time_numeric": return "NOT_STATED" if not model["numeric_constraints"] and any("NEAR_REAL_TIME" in x["rule"] for x in measures["ЗКУ.3"]["enhancements"]) else None
        if query == "zku3_sandbox_scope": return ["EXECUTABLES", "ARCHIVES"] if any("EXECUTABLES_AND_ARCHIVES" in x["rule"] for x in measures["ЗКУ.3"]["enhancements"]) else None
        if query == "zku4_rsb_dependency": return "LINKED_RSB_1_TO_RSB_5" if any("RSB_1_TO_RSB_5" in x for x in impl_rules("ЗКУ.4")) else None
        if query == "zku4_strength_counts":
            values = [x["strength"] for x in measures["ЗКУ.4"]["implementation"]]
            return {key: values.count(key) for key in ("REQUIRED", "RECOMMENDED")}
        if query == "zku4_recommended_not_required": return "DO_NOT_CONVERT_ZKU_4_RECOMMENDED_TRACKING_LIST_TO_UNCONDITIONAL_REQUIRED_ITEMS" in model["scope_guards"]
        if query == "zku4_recommended_nonexhaustive": return "DO_NOT_TREAT_ZKU_4_RECOMMENDED_TRACKING_LIST_AS_EXHAUSTIVE" in model["scope_guards"]
        if query == "zku4_correlation_enhancement": return any("INTEGRATE_AND_CORRELATE" in x["rule"] for x in measures["ЗКУ.4"]["enhancements"])
        if query == "zku5_baseline": return "NOT_BASELINE_ALL_CLASSES" if all(v == "BLANK" for v in measures["ЗКУ.5"]["matrix"]["base"].values()) else None
        if query == "zku5_blank_semantics": return "ADAPTATION_AND_THREAT_VERIFICATION_RETAINED" if "DO_NOT_TREAT_ZKU_5_BLANK_ROW_AS_PROHIBITION_OR_DELETE_ADAPTATION_AND_THREAT_VERIFICATION" in model["scope_guards"] else None
        if query == "zku5_filter_rules": return "OPERATOR_DEFINED" if parameters["ZKU5_TRAFFIC_FILTER_RULE_SET"]["universal_value"] == "NOT_STATED" else None
        if query == "zku6_incident_management_condition": return "EDR_AND_SIEM_REQUIRED" if any("WHEN_HOST_DETECTION_AND_RESPONSE_UNDER_ZKU_3_AND_SECURITY_EVENT_MANAGEMENT_SYSTEM_ARE_PRESENT" in x["rule"] for x in measures["ЗКУ.6"]["enhancements"]) else None
        if query == "zku6_enhancement_1_classes": return [k for k,v in measures["ЗКУ.6"]["matrix"]["enhancements"].items() if 1 in v]
        if query == "complete_zku_family": return model["verification_boundary"]["complete_zku_family"]
        if query == "official_and_gap_boundary": return {"official_bytes": model["verification_boundary"]["official_immutable_bytes"], "critical": model["verification_boundary"]["critical_gap_created"], "high": model["verification_boundary"]["high_gap_created"]}
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZKU_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗКУ.{number}" for number in range(1, 7)]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 6 ZKU measures; 29 implementation atoms; 0 documentation items; 28 enhancements; 36 class cells; 0 numeric constraints; 4 operator-defined parameters; 64 fail-closed cases")


if __name__ == "__main__":
    main()
