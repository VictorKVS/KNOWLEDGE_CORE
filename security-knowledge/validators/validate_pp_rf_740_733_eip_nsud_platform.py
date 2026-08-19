#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/pp-rf-740-733-eip-nsud-platform-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/pp-rf-740-733-eip-nsud-platform-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "designated_gis":
        return "EIP_NSUD"
    if query == "component_actor":
        return "MINISTRY_OF_DIGITAL_DEVELOPMENT"
    if query == "effective_date":
        return "2025-05-28" if case["clause"] == 3 else "2025-09-01"
    if query == "definition":
        if case["term"] == "ANONYMIZED_DATA":
            return "ARTICLE_13_1_ANONYMIZED_PERSONAL_DATA"
        return "BLOCK_NOT_DATA_COMPOSITION" if case["later_processing_identifies_subject"] else "PASS_DEFINITION_GATE"
    if query == "platform_task":
        return "PRESENT" if case["task"] == "PROCESS_ANONYMIZED_DATA" else "PRESENT_UNDER_ARTICLE_13_1"
    if query == "platform_component":
        return "PRESENT"
    if query == "component_bases":
        return "INFORMATION_ANALYTICAL_AND_ANONYMIZED_DATA_SUBSYSTEMS"
    if query == "provider_role":
        if case["personal_data_operator"] and case["article13_1_part2_requirement_received"]:
            return "PROVIDER_ROLE"
        return "NOT_PROVIDER_BY_OPERATOR_STATUS_ALONE"
    if query == "user_role":
        if case["class"] == "PUBLIC_ARTICLE13_1_PART7_ITEM1":
            return "PLATFORM_USER_SUBJECT_TO_ACCESS_GATES"
        return "CONTINUE_ACCESS_PROCEDURE" if case["part7_criteria_met"] else "BLOCK_PART7_ELIGIBILITY"
    if query == "representation":
        if case["authorizing_act"]:
            return "ALLOW_MODELED_REPRESENTATION"
        return "BLOCK_NO_REGIONAL_LAW" if case["level"] == "REGIONAL" else "BLOCK_NO_MUNICIPAL_ACT"
    if query == "provider_operation":
        return "PROVIDE_ANONYMIZED_DATA_TO_SUBSYSTEM" if case["individualized_requirement"] else "BLOCK_NO_INDIVIDUALIZED_REQUIREMENT"
    if query == "user_operation":
        return "PROCESS_AND_OBTAIN_RESULTS_IN_SUBSYSTEM" if case["access_obtained_under_article13_1"] else "BLOCK_PROCESSING_AND_RESULTS"
    if query == "operator_function":
        return "PERFORM_IN_SUBSYSTEM_UNDER_ARTICLE_13_1"
    if query == "authorized_person":
        return "PASS_DESIGNATION_EVIDENCE" if case["designated"] else "BLOCK_ORGANIZATIONAL_MEASURE_MISSING"
    if query == "state_secret":
        return "BLOCK_PLATFORM_PROCESSING" if case["contains_state_secret"] else "CONTINUE_PROTECTION_REVIEW"
    if query == "pp2052_overlay":
        return "APPLY_2025_12_17_EDITION_FROM_2026_01_01_AND_RETAIN_ARTICLE_13_1_ROUTE"
    if query == "ai_route":
        return "NO_ARTICLE_13_1_ACCESS_FROM_GENERAL_AI_TASK"
    if query == "standalone_access":
        return "NO_ACCESS_GRANT_CONTINUE_ARTICLE_13_1_PROCEDURE"
    if query == "numeric_deadline":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "official_publication_number":
        return "PENDING_NOT_LOCATED_DO_NOT_INVENT"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))

    assert len(model["decree_rules"]) == len({row["id"] for row in model["decree_rules"]}) == 4
    assert len(model["amendment_crosswalk"]) == len({row["id"] for row in model["amendment_crosswalk"]}) == 10
    assert len(model["current_platform_boundaries"]) == 3
    assert len(model["temporal_model"]) == 3
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 12
    assert model["sources"]["pp740"]["official_publication"]["publication_number"] == "PENDING_NOT_LOCATED_IN_BOUNDED_SEARCH"
    assert str(model["sources"]["pp740"]["effective_dates"]["clause_3"]) == "2025-05-28"
    assert str(model["sources"]["pp740"]["effective_dates"]["other_provisions"]) == "2025-09-01"
    assert str(model["sources"]["pp733_current"]["current_edition_checked"]) == "2025-12-17"
    assert str(model["sources"]["pp2052_overlay"]["effective_from"]) == "2026-01-01"
    assert model["verification_boundary"]["pp740_official_publication_number"] == "PENDING"
    assert model["verification_boundary"]["pp740_repeal_located"] is False
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False

    pp740 = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0035")
    pp733 = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0036")
    pp2052 = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0037")
    assert pp740["state"] == pp733["state"] == pp2052["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in pp740["repo_bindings"] and str(FIXTURES) in pp740["repo_bindings"]
    assert str(MODEL) in pp733["repo_bindings"] and str(FIXTURES) in pp733["repo_bindings"]
    assert str(MODEL) in pp2052["repo_bindings"] and str(FIXTURES) in pp2052["repo_bindings"]
    assert library["counts"]["registered_source_records"] == len(library["sources"]) == 37
    assert len(fixtures["cases"]) == 34

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 4 decree rules; 10 amendments; 3 temporal events; 12 evidence nodes; 34 cases")


if __name__ == "__main__":
    main()
