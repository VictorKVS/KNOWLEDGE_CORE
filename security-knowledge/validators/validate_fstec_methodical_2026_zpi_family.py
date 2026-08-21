#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-zpi-family-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-zpi-family-regression-v1.json")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    measures = {item["code"]: item for item in model["measures"]}
    parameters = {item["id"]: item for item in model["operator_defined_parameters"]}
    numeric = {item["id"]: item for item in model["numeric_constraints"]}
    triggers = {item["id"]: item for item in model["event_triggers"]}

    def evaluate(case):
        query = case["query"]
        if query == "measure_count": return len(measures)
        if query == "implementation_total": return sum(len(x["implementation"]) for x in measures.values())
        if query == "documentation_total": return sum(len(x["documentation"]) for x in measures.values())
        if query == "enhancement_total": return sum(len(x["enhancements"]) for x in measures.values())
        if query == "numeric_count": return len(numeric)
        if query == "event_trigger_count": return len(triggers)
        if query == "operator_parameter_count": return len(parameters)
        if query == "source_anomaly_count": return len(model["source_anomalies"])
        if query == "measure_count_field": return len(measures[case["measure"]][case["field"]])
        if query == "matrix_counts": return {key: model["class_matrix_summary"][key] for key in ("cells_total", "nonblank_cells", "blank_cells")}
        if query == "base_all_classes": return all(value == "PLUS" for value in measures[case["measure"]]["matrix"]["base"].values())
        if query == "enhancement_row": return measures[case["measure"]]["matrix"]["enhancements"]
        if query == "zpi1_minimization_count": return len([x for x in measures["ЗПИ.1"]["implementation"] if x.startswith("MINIMIZE_")])
        if query == "zpi1_literal_zks_reference": return "ZKS_1_TO_ZKS_5" if any("ZKS_1_TO_ZKS_5" in x for x in measures["ЗПИ.1"]["implementation"]) else None
        if query == "zpi1_zks5_catalog_resolution": return "PENDING_FAIL_CLOSED" if model["source_anomalies"][0]["handling"] == "PRESERVE_LITERAL_REFERENCE_AND_BLOCK_AUTOMATIC_MAPPING_OF_ZKS_5" else None
        if query == "zpi1_api_lists_documented": return "LISTS_OF_APIS_PROVIDED_TO_EXTERNAL_AND_INTERNAL_USERS" in measures["ЗПИ.1"]["documentation"]
        if query == "zpi1_confidentiality_settings_documented": return any("CONFIDENTIALITY" in x for x in measures["ЗПИ.1"]["documentation"])
        if query == "zpi1_annual_review_classes": return [k for k,v in measures["ЗПИ.1"]["matrix"]["enhancements"].items() if 1 in v]
        if query == "zpi1_annual_interval": return {key: numeric["ZPI1_ANNUAL_CONFIGURATION_REVIEW"][key] for key in ("maximum_interval", "unit")}
        if query == "zpi2_iaf_dependency": return "LINKED_IAF_1_AND_IAF_3" if any("IAF_1_AND_IAF_3" in x for x in measures["ЗПИ.2"]["implementation"]) else None
        if query == "zpi2_upd_dependency_count": return len([x for x in measures["ЗПИ.2"]["implementation"] if "UPD_" in x])
        if query == "zpi2_every_request_check": return any("EVERY_API_REQUEST" in x for x in measures["ЗПИ.2"]["implementation"])
        if query == "zpi2_public_resource_exception": return any("EXCEPT_DEFINED_PUBLIC_RESOURCES" in x for x in measures["ЗПИ.2"]["implementation"])
        if query == "zpi2_request_frequency_limit": return "OPERATOR_DEFINED" if parameters["ZPI2_REQUEST_FREQUENCY_LIMIT"]["universal_value"] == "NOT_STATED" else None
        if query == "zpi2_request_volume_limit": return "OPERATOR_DEFINED" if parameters["ZPI2_REQUEST_VOLUME_LIMIT"]["universal_value"] == "NOT_STATED" else None
        if query == "zpi2_bruteforce_rules": return "OPERATOR_DEFINED" if parameters["ZPI2_BRUTE_FORCE_DETECTION_AND_SUPPRESSION_RULES"]["universal_value"] == "NOT_STATED" else None
        if query == "zpi2_numeric_limit_invented": return any(x["measure"] == "ЗПИ.2" for x in model["numeric_constraints"])
        if query == "zpi3_specification_defined": return "DEFINE_API_SPECIFICATION" in measures["ЗПИ.3"]["implementation"]
        if query == "zpi3_preimpact_block": return any("BEFORE_IMPACT" in x for x in measures["ЗПИ.3"]["implementation"])
        if query == "zpi3_base_review_routes": return ["ANNUAL", "API_CHANGE"] if any("ANNUALLY_OR_WHEN_API_CHANGES" in x for x in measures["ЗПИ.3"]["implementation"]) else None
        if query == "zpi3_annual_interval": return {key: numeric["ZPI3_ANNUAL_API_INVENTORY_SPECIFICATION_REVIEW"][key] for key in ("maximum_interval", "unit")}
        if query == "zpi3_application_change_trigger": return "ZPI3_APPLICATION_CHANGE_REVIEW" in triggers
        if query == "zpi3_traffic_analysis_enhancement_exists": return any(x["number"] == 2 and "ANALYZE_TRAFFIC" in x["rule"] for x in measures["ЗПИ.3"]["enhancements"])
        if query == "zpi3_class_listed_enhancements": return sorted(set(n for row in measures["ЗПИ.3"]["matrix"]["enhancements"].values() for n in row))
        if query == "zpi3_enhancement_2_class_listed": return any(2 in row for row in measures["ЗПИ.3"]["matrix"]["enhancements"].values())
        if query == "zpi3_undocumented_deprecated_unused_scope": return any(all(term in x for term in ("UNDOCUMENTED", "DEPRECATED", "UNUSED")) for x in measures["ЗПИ.3"]["implementation"] + [y["rule"] for y in measures["ЗПИ.3"]["enhancements"]])
        if query == "blank_cell_semantics": return "NOT_PROHIBITION" if "DO_NOT_TREAT_BLANK_CLASS_CELL_AS_PROHIBITION" in model["scope_guards"] else None
        if query == "complete_zpi_family": return model["verification_boundary"]["complete_zpi_family"]
        if query == "linked_iaf_upd_content": return model["verification_boundary"]["referenced_iaf_upd_content"]
        if query == "linked_zks_content": return model["verification_boundary"]["referenced_zks_content"]
        if query == "official_bytes": return model["verification_boundary"]["official_immutable_bytes"]
        if query == "product_profiles": return model["verification_boundary"]["product_specific_api_profiles"]
        if query == "critical_gap_created": return model["verification_boundary"]["critical_gap_created"]
        if query == "high_gap_created": return model["verification_boundary"]["high_gap_created"]
        raise AssertionError(f"Unhandled query: {query}")

    assert model["status"] == "VERIFIED_BOUNDED_COMPLETE_ZPI_PUBLIC_TEXT_CROSSCHECK"
    assert list(measures) == [f"ЗПИ.{number}" for number in range(1, 4)]
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 3 ZPI measures; 16 implementation atoms; 2 documentation items; 3 enhancements; 18 class cells; 2 annual constraints; 2 event triggers; 5 operator-defined parameters; 1 source anomaly; 56 fail-closed cases")


if __name__ == "__main__":
    main()
