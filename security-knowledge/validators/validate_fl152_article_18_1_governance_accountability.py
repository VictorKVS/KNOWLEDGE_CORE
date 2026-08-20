#!/usr/bin/env python3
import json
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-18-1-governance-accountability-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-18-1-governance-accountability-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")

DOCUMENT_FIELDS = [
    "policy", "purpose_structure", "data_categories_list", "subject_categories", "methods",
    "processing_terms", "storage_terms", "destruction_procedure",
    "violation_prevention_detection", "violation_remediation",
]


def evaluate(case):
    query = case["query"]
    if query == "measures":
        if case["illustrative_list_only"]:
            return "BLOCK_ILLUSTRATIVE_LIST_IS_NOT_COMPLETE_PROOF"
        if not case["necessary"]:
            return "BLOCK_NECESSITY_NOT_PROVED"
        if not case["sufficient"]:
            return "BLOCK_SUFFICIENCY_NOT_PROVED"
        return "PASS_NECESSARY_AND_SUFFICIENT_MEASURES"
    if query == "measure_selection":
        if case["federal_law_override"] and not case["override_respected"]:
            return "BLOCK_FEDERAL_LAW_OVERRIDE_IGNORED"
        return "PASS_OPERATOR_SELF_SELECTION"
    if query == "appointment":
        if not case["legal_entity"]:
            return "VOLUNTARY_ROLE_NOT_ARTICLE18_1_POINT1_PROOF" if case["appointed"] else "POINT1_LEGAL_ENTITY_SCOPE_NOT_TRIGGERED"
        if not case["appointed"]:
            return "BLOCK_RESPONSIBLE_PERSON_NOT_APPOINTED"
        return "PASS_RESPONSIBLE_PERSON_APPOINTED" if case["authority_defined"] else "BLOCK_RESPONSIBLE_PERSON_AUTHORITY_UNPROVEN"
    if query == "document_set":
        fields = set(case["fields"])
        for field in DOCUMENT_FIELDS:
            if field not in fields:
                return f"BLOCK_MISSING_{field.upper()}"
        return "PASS_COMPLETE_POINT2_DOCUMENT_SET"
    if query == "document_guard":
        if case["restricts_subject_rights"]:
            return "BLOCK_SUBJECT_RIGHTS_RESTRICTION"
        if case["creates_unsupported_powers_or_duties"]:
            return "BLOCK_UNSUPPORTED_OPERATOR_POWERS_OR_DUTIES"
        return "PASS_LOCAL_ACT_GUARDS"
    if query == "security":
        if case["policy_only"]:
            return "POLICY_DOES_NOT_REPLACE_ARTICLE19_MEASURES"
        return "PASS_ARTICLE19_SECURITY_CROSSWALK" if case["article19_crosswalk_complete"] else "BLOCK_ARTICLE19_MEASURES_UNPROVEN"
    if query == "control_audit":
        if case["external_certification_only"]:
            return "EXTERNAL_CERTIFICATION_NOT_INTERNAL_CONTROL_OR_AUDIT_PROOF"
        if not case["control"] and not case["audit"]:
            return "BLOCK_CONTROL_AND_AUDIT_MISSING"
        if not case["targets_complete"]:
            return "BLOCK_CONTROL_TARGETS_INCOMPLETE"
        return "PASS_INTERNAL_CONTROL_OR_AUDIT" if case["reports_present"] else "BLOCK_CONTROL_AUDIT_EXECUTION_UNPROVEN"
    if query == "harm":
        if not case["assessment_present"]:
            return "BLOCK_HARM_ASSESSMENT_MISSING"
        if not case["rkn_method"]:
            return "BLOCK_AUTHORIZED_HARM_REQUIREMENTS_UNPROVEN"
        if case["numeric_formula_invented"]:
            return "BLOCK_INVENTED_NUMERIC_HARM_RATIO"
        return "PASS_HARM_AND_MEASURE_RELATIONSHIP" if case["relationship_assessed"] else "BLOCK_HARM_MEASURE_RELATIONSHIP_MISSING"
    if query == "workers":
        if not case["direct_processor"]:
            return "POINT6_DIRECT_PROCESSOR_SCOPE_NOT_TRIGGERED"
        if case["trained"]:
            return "PASS_WORKER_FAMILIARIZATION_OR_TRAINING"
        if not any((case["familiarized_legislation"], case["familiarized_policy"], case["familiarized_local_acts"])):
            return "BLOCK_WORKER_FAMILIARIZATION_AND_TRAINING_MISSING"
        if not case["familiarized_legislation"]:
            return "BLOCK_WORKER_LEGISLATION_AWARENESS_MISSING"
        if not case["familiarized_policy"]:
            return "BLOCK_WORKER_POLICY_AWARENESS_MISSING"
        if not case["familiarized_local_acts"]:
            return "BLOCK_WORKER_LOCAL_ACT_AWARENESS_MISSING"
        return "PASS_WORKER_FAMILIARIZATION_OR_TRAINING"
    if query == "publication_general":
        if not case["policy_access"]:
            return "BLOCK_POLICY_ACCESS_MISSING"
        if not case["protection_info_access"]:
            return "BLOCK_PROTECTION_INFO_ACCESS_MISSING"
        return "PASS_UNRESTRICTED_POLICY_AND_PROTECTION_INFO" if case["unrestricted"] else "BLOCK_ACCESS_NOT_UNRESTRICTED"
    if query == "network_publication":
        if not case["network_collection"]:
            return "NETWORK_COLLECTION_SPECIAL_RULE_NOT_TRIGGERED"
        if not case["operator_owned_collection_page"]:
            return "BLOCK_OPERATOR_COLLECTION_PAGE_COVERAGE_MISSING"
        if not case["policy_published"]:
            return "BLOCK_NETWORK_POLICY_PUBLICATION_MISSING"
        if not case["protection_info_published"]:
            return "BLOCK_NETWORK_PROTECTION_INFO_MISSING"
        return "PASS_NETWORK_COLLECTION_PUBLICATION" if case["network_access"] else "BLOCK_NETWORK_ACCESS_CAPABILITY_MISSING"
    if query == "public_operator":
        if not case["state_or_municipal_body"]:
            return "PART3_PUBLIC_OPERATOR_SPECIALIZATION_NOT_TRIGGERED"
        return "PASS_PP211_GOVERNMENT_LIST_CROSSWALK" if case["pp211_crosswalk"] else "BLOCK_GOVERNMENT_MEASURES_LIST_UNPROVEN"
    if query == "regulator_request":
        if case["authorized_body_request"] == "OTHER_REGULATOR":
            return "ARTICLE18_1_AUTHORIZED_BODY_SCOPE_NOT_ESTABLISHED"
        if not case["authorized_body_request"]:
            return "PART4_REQUEST_TRIGGER_NOT_MET"
        if case["documents_provided"] and case["other_confirmation"]:
            return "PASS_COMBINED_CONFIRMATION_ROUTE"
        if case["documents_provided"]:
            return "PASS_DOCUMENT_PRODUCTION_ROUTE"
        if case["other_confirmation"]:
            return "PASS_OTHER_CONFIRMATION_ROUTE"
        return "BLOCK_MEASURES_NOT_CONFIRMED"
    constants = {
        "deadline": "NO_NUMERIC_DEADLINE_STATED",
        "control_interval": "NOT_STATED_DO_NOT_INVENT",
        "training_interval": "NOT_STATED_DO_NOT_INVENT",
        "measures_list_closed": "ILLUSTRATIVE_NOT_EXHAUSTIVE",
    }
    if query in constants:
        return constants[query]
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 36
    assert model["numeric_deadlines"] == []
    assert len(model["event_deadlines_without_numeric_value"]) == 1
    assert len(model["temporal_model"]) == 5
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 22
    assert len(model["conflict_and_definition_checks"]) == 22
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["verification_boundary"]["immutable_current_consolidated_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(item for item in library["sources"] if item["id"] == "PDN-SRC-0001")
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(item for item in matrix["directions"] if item["id"] == "PDN-DIR-14")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert len(fixtures["cases"]) == 72
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 36 atomic rules; 0 numeric deadlines; 1 event deadline; 22 evidence nodes; 22 conflict checks; 72 cases")


if __name__ == "__main__":
    main()
