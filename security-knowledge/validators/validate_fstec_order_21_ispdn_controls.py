#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/fstec-order-21-ispdn-controls-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fstec-order-21-ispdn-controls-regression-v1.json")
PP1119 = Path("security-knowledge/classification/ispdn-protection-level-decision-table-pp1119-verified.yaml")
ARTICLE19 = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-19-security-measures-atomic-v1.yaml")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")

AMENDMENTS = {"49": "0001201704260010", "68": "0001202007100002"}
THRESHOLDS = {
    1: {"security_class": 4, "trust_level": 4, "computer_class": 5},
    2: {"security_class": 5, "trust_level": 5, "computer_class": 5},
    3: {"security_class": 6, "trust_level": 6, "computer_class": 5},
    4: {"security_class": 6, "trust_level": 6, "computer_class": 6},
}


def flatten_catalog(model):
    return {control: levels for family in model["control_catalog"].values() for control, levels in family.items()}


def evaluate(case, model, catalog):
    query = case["query"]
    if query == "current_edition":
        return "PASS_CURRENT_EDITION" if case["edition"] == "2020-05-14" else "HISTORICAL_NOT_CURRENT"
    if query == "amendment":
        return "PASS" if AMENDMENTS.get(case["number"]) == case["publication"] else "BLOCK_IDENTITY_MISMATCH"
    if query == "effective_date":
        return "2021-01-01" if case["event"] == "ORDER68" else "NOT_CLAIMED"
    if query == "scope":
        if not case["ispdn"]:
            return "OUTSIDE_ISPDN_SCOPE"
        if case["state_secret"]:
            return "ROUTE_STATE_SECRET_REGIME"
        return "ROUTE_CRYPTO_SEPARATELY" if case["cryptographic_measure"] else "ORDER21_ROUTE"
    if query == "security_actor":
        return "ALLOW" if case["actor"] in {"OPERATOR", "PROCESSOR_ON_INSTRUCTION"} else "BLOCK_ACTOR_ROUTE_UNPROVEN"
    if query == "contractor":
        if not case["contracted_security_work"]:
            return "NO_CLAUSE2_CONTRACTOR_TRIGGER"
        return "ALLOW" if case["tzki_licensed"] else "BLOCK_TZKI_LICENSE_REQUIRED"
    if query == "effectiveness_interval":
        return "PASS" if case["years"] <= 3 else "BLOCK_THREE_YEAR_MAXIMUM_INTERVAL"
    if query == "effectiveness_interval_unit":
        return "YEARS_NOT_WORKING_DAYS"
    if query == "log_retention_period":
        return "OPERATOR_DEFINED_NO_UNIVERSAL_NUMBER"
    if query == "backup_frequency":
        return "PERIODIC_NO_UNIVERSAL_NUMBER"
    if query == "recovery_interval":
        return "ESTABLISHED_NO_UNIVERSAL_NUMBER"
    if query == "gis_route":
        return "ROUTE_FSTEC_GIS_REQUIREMENTS" if case["state_information_system"] else "ORDER21_GENERAL_ISPDN_ROUTE"
    if query == "selection_order":
        if case["steps"] == ["BASE", "ADAPT", "REFINE", "SUPPLEMENT"]:
            return "PASS"
        return "BLOCK_SUPPLEMENT_STEP_MISSING" if case["steps"] == ["BASE", "ADAPT", "REFINE"] else "BLOCK_WRONG_ORDER"
    if query == "base_input":
        return f"USE_LEVEL_{case['pp1119_level']}_PLUS_SET" if case["pp1119_level"] in {1, 2, 3, 4} else "BLOCK_LEVEL_REQUIRED"
    if query == "adapt_exclusion":
        if case["preference_only"]:
            return "BLOCK_CONVENIENCE_EXCLUSION"
        return "ALLOW_EXCLUSION_WITH_EVIDENCE" if case["technology_absent"] or case["characteristic_absent"] else "BLOCK_EXCLUSION_BASIS_MISSING"
    if query == "refinement":
        return "PASS" if case["all_current_threats_neutralized"] else "BLOCK_THREAT_COVERAGE_INCOMPLETE"
    if query == "supplement":
        return "PASS" if case["other_applicable_npa_reviewed"] else "BLOCK_OTHER_NPA_REVIEW_MISSING"
    if query == "compensation":
        if not (case["technical_impossibility"] or case["economic_feasibility"]):
            return "BLOCK_TRIGGER_MISSING"
        if not case["neutralizes_threat"]:
            return "BLOCK_THREAT_NOT_NEUTRALIZED"
        return "ALLOW_COMPENSATING_MEASURE" if case["justified"] else "BLOCK_JUSTIFICATION_MISSING"
    if query == "new_technology":
        return "DEVELOP_COMPENSATING_MEASURE" if case["additional_threat"] and not case["defined_measure_exists"] else "USE_DEFINED_SELECTION_PIPELINE"
    if query == "type12_addition":
        if case["threat_type"] not in {"TYPE_1", "TYPE_2"}:
            return "NO_CLAUSE11_TYPE_ROUTE"
        return "REJECT_MAY_NOT_SHALL" if case["claimed_mandatory"] else "ALLOW_OPTIONAL_ADDITION"
    if query == "certification_condition":
        if case["universal_certification_claimed"]:
            return "REJECT_UNIVERSAL_CERTIFICATION"
        return "NO_CLASS_TRUST_TABLE_TRIGGER" if not case["certified_tool_used"] else "APPLY_CLASS_TRUST_TABLE"
    if query == "certification_threshold":
        required = THRESHOLDS[case["level"]]
        if case["security_class"] > required["security_class"]:
            return "BLOCK_SECURITY_CLASS_TOO_LOW"
        if case["trust_level"] > required["trust_level"]:
            return "BLOCK_TRUST_LEVEL_TOO_LOW"
        if case["computer_class"] > required["computer_class"]:
            return "BLOCK_COMPUTER_CLASS_TOO_LOW"
        return "PASS"
    if query == "tool_function_fit":
        return "PASS" if case["implements_selected_measures"] else "BLOCK_FUNCTIONAL_FIT_UNPROVEN"
    if query == "base_count":
        return sum(case["level"] in levels for levels in catalog.values())
    if query == "catalog_count":
        return len(catalog)
    if query == "family_count":
        return len(model["family_objectives"])
    if query == "control_levels":
        return catalog[case["control"]]
    if query == "blank_cell":
        return "REJECT_BLANK_NOT_PROHIBITION" if case["claimed_prohibited"] else "ALLOW_REFINEMENT_OR_COMPENSATION_REVIEW"
    if query == "incident_route":
        return "REJECT_SEPARATE_NOTIFICATION_ROUTE" if case["claimed_replaces_article21_notice"] else "KEEP_ROUTES_SEPARATE"
    if query == "order58":
        return "REJECT_REPEALED_SOURCE" if case["used_as_current"] else "PASS"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    pp1119 = yaml.safe_load(PP1119.read_text(encoding="utf-8"))
    article19 = yaml.safe_load(ARTICLE19.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    catalog = flatten_catalog(model)

    assert len(model["atomic_rules"]) == len({row["id"] for row in model["atomic_rules"]}) == 38
    assert len(model["numeric_deadlines"]) == 1
    assert len(model["selection_pipeline"]) == 4
    assert sum(row["controls"] for row in model["family_objectives"]) == len(catalog) == 109
    assert len(model["family_objectives"]) == len(model["control_catalog"]) == 15
    assert model["base_set_counts"] == {"protection_level_4": 27, "protection_level_3": 41, "protection_level_2": 66, "protection_level_1": 69, "catalog_total": 109}
    assert {level: sum(level in levels for levels in catalog.values()) for level in [4, 3, 2, 1]} == {4: 27, 3: 41, 2: 66, 1: 69}
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 24
    assert len(model["conflict_and_definition_checks"]) == 20
    assert model["source"]["amendment_49"]["official_publication_number"] == "0001201704260010"
    assert model["source"]["amendment_68"]["official_publication_number"] == "0001202007100002"
    assert model["verification_boundary"]["immutable_current_consolidated_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False and model["red_team"]["high_gap_created"] is False
    assert pp1119["record_set_id"] == "ISPDN-PP1119-PROTECTION-LEVEL-VERIFIED"
    assert article19["id"] == "RU-FL152-ARTICLE19-SECURITY-MEASURES-ATOMIC-V1"

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0009")
    assert source["state"] == "ATOMIZED"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-18")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert library["counts"]["registered_source_records"] == len(library["sources"]) == 37
    assert len(fixtures["cases"]) == 90

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model, catalog)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 38 atomic rules; 1 numeric deadline; 15 families; 109 controls; 24 evidence nodes; 20 conflict checks; 90 cases")


if __name__ == "__main__":
    main()
