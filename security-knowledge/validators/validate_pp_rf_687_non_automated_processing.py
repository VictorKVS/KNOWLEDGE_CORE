#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/pp-rf-687-non-automated-processing-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/pp-rf-687-non-automated-processing-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "mode":
        if case["direct_human_participation_per_subject"]:
            return "NON_AUTOMATED_PP687_APPLIES"
        if case.get("only_reason_is_is_storage"):
            return "NOT_AUTOMATED_BY_STORAGE_ALONE_NEED_FACTS"
        return "INSUFFICIENT_FACTS_DO_NOT_FORCE_PP687"
    if query == "legal_basis":
        return "NOT_CREATED_BY_PP687"
    if query == "other_information_separation":
        return "PASS" if case["separated"] else "BLOCK_SEPARATION_REQUIRED"
    if query == "purpose_carrier":
        return "BLOCK_INCOMPATIBLE_PURPOSES_ON_ONE_CARRIER" if not case["purposes_compatible"] and case["same_carrier"] else "PASS"
    if query == "category_carrier":
        return "PASS" if case["separate_carrier_per_category"] else "BLOCK_SEPARATE_CARRIER_REQUIRED"
    if query == "processor_briefing":
        return "PASS" if case["briefed_on_fact_categories_rules"] else "BLOCK_BRIEFING_EVIDENCE_MISSING"
    if query == "template":
        return "PASS_CONTENT" if case["all_clause_7a_fields"] else "BLOCK_MANDATORY_FORM_METADATA_MISSING"
    if query == "template_consent":
        if not case["written_consent_otherwise_required"]:
            return "NO_UNIVERSAL_CONSENT_FIELD_REQUIREMENT"
        return "PASS" if case["consent_mark_field"] else "BLOCK_CONSENT_MARK_FIELD_REQUIRED"
    if query == "subject_review":
        return "BLOCK_OTHER_SUBJECT_RIGHTS" if case["exposes_other_subject_data"] else "PASS"
    if query == "template_purpose_fields":
        return "BLOCK_INCOMPATIBLE_FIELDS" if case["combines_incompatible_purposes"] else "PASS"
    if query == "visitor_log":
        return "PASS" if case["operator_act_complete"] else "BLOCK_OPERATOR_ACT_MISSING_OR_INCOMPLETE"
    if query == "visitor_log_copy":
        return "BLOCK_COPY" if case["copy_requested"] else "PASS"
    if query == "visitor_log_frequency":
        return "PASS" if case["entries_for_same_access_instance"] <= 1 else "BLOCK_MORE_THAN_ONCE_PER_ACCESS_INSTANCE"
    if query == "selective_use":
        return "USE_OR_DISCLOSE_FILTERED_COPY" if case["copy_excludes_unselected_data"] else "BLOCK_SIMULTANEOUS_COPY"
    if query == "selective_destroy":
        return "COPY_REMAINDER_THEN_BLOCK_OR_DESTROY_CARRIER" if case["remaining_data_copied_without_affected_data"] else "BLOCK_SIMULTANEOUS_COPY"
    if query == "partial_destroy":
        if case["carrier_supports_selective_action"] and case["prevents_further_processing"]:
            return "ALLOW_DELETE_OR_REDACT_SELECTED_DATA"
        return "BLOCK_INEFFECTIVE_DESTRUCTION_OR_ANONYMIZATION"
    if query == "correction":
        if case["carrier_direct_update_supported"] or case["change_recorded_or_new_carrier"]:
            return "PASS_CORRECTION_ROUTE"
        return "BLOCK_NO_CORRECTION_ROUTE"
    if query == "storage_map":
        if not case["locations_by_category"]:
            return "BLOCK_STORAGE_LOCATION_MAP_MISSING"
        return "PASS" if case["persons_by_category"] else "BLOCK_ACCESS_LIST_MISSING"
    if query == "storage_purpose":
        return "PASS" if case["different_purposes_stored_separately"] else "BLOCK_SEPARATE_STORAGE_REQUIRED"
    if query == "security_governance":
        if not case["preservation_and_unauthorized_access_controls"]:
            return "BLOCK_STORAGE_CONTROLS_MISSING"
        return "PASS" if case["measures_procedure_responsible_persons_set"] else "BLOCK_GOVERNANCE_ARTIFACTS_MISSING"
    if query == "numeric_deadline":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "validity":
        return "CURRENT_SUBJECT_TO_VERSION_CHECK" if date.fromisoformat(case["as_of"]) < date(2030, 9, 1) else "SUNSET_REACHED_REQUIRE_SUCCESSOR_OR_EXTENSION_CHECK"
    if query == "universal_cabinet_spec":
        return "NOT_STATED_OPERATOR_DETERMINES_MEASURES"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({row["id"] for row in model["atomic_rules"]}) == 24
    assert len(model["temporal_model"]) == 3
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 14
    assert model["source"]["current_edition"] == "2025-01-18"
    assert model["source"]["current_edition_effective_from"] == "2025-01-26"
    assert model["source"]["valid_until_exclusive"] == "2030-09-01"
    assert model["source"]["amending_decree"]["official_publication_id"] == "0001202501180009"
    assert model["source"]["original_publication"]["electronic_publication_id"] is None
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0005")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-16")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert library["counts"]["registered_source_records"] == len(library["sources"]) == 37
    assert len(fixtures["cases"]) == 36

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 24 atomic rules; 3 temporal events; 14 evidence nodes; 36 cases")


if __name__ == "__main__":
    main()

