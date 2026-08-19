#!/usr/bin/env python3
import json
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-15-marketing-agitation-rights-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-15-marketing-agitation-rights-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")


def evaluate(case):
    query = case["query"]
    if query == "scope":
        if case["purpose"] == "POLITICAL_AGITATION":
            return "ARTICLE15_POLITICAL_AGITATION_ROUTE"
        if case["purpose"] == "MARKET_PROMOTION":
            if case["direct_contact"] and case["communication_means"]:
                return "ARTICLE15_MARKETING_ROUTE"
            return "ARTICLE15_MARKETING_LIMB_NOT_ESTABLISHED_CHECK_OTHER_LAW"
        return "OUTSIDE_ARTICLE15_CHECK_OTHER_BASIS"
    if query in {"marketing_consent", "agitation_consent"}:
        if not case["operator_proves_consent"]:
            if query == "marketing_consent" and case.get("contract"):
                return "BLOCK_CONTRACT_DOES_NOT_REPLACE_PRIOR_CONSENT"
            return "BLOCK_DEEMED_WITHOUT_PRIOR_CONSENT"
        return "PASS_PRIOR_CONSENT" if case["obtained_before"] else "BLOCK_CONSENT_NOT_PRIOR"
    if query == "consent_form":
        return "DO_NOT_INVENT_UNIVERSAL_WRITTEN_FORM"
    if query == "proof_burden":
        if not case["operator_has_proof"]:
            return "DEEMED_WITHOUT_PRIOR_CONSENT"
        return "ROUTE_TO_CONSENT_VALIDITY_REVIEW" if case["subject_disproves"] else "PASS_OPERATOR_PROOF_PRESENT"
    if query == "cessation":
        if not case["demand_received"]:
            return "NO_ARTICLE15_CESSATION_TRIGGER"
        if not case["article15_processing_stopped"]:
            return "BLOCK_IMMEDIATE_CESSATION_REQUIRED"
        return "PASS_IMMEDIATE_CESSATION" if case["at_demand"] else "BLOCK_CESSATION_NOT_IMMEDIATE"
    if query == "cessation_scope":
        if not case["article15_processing_stopped"]:
            return "BLOCK_ARTICLE15_PROCESSING_MUST_STOP"
        if case["unrelated_lawful_processing_continues"]:
            return "PASS_SCOPED_CESSATION"
        return "DO_NOT_REQUIRE_UNRELATED_CESSATION_WITHOUT_SEPARATE_TRIGGER"
    if query == "destruction_deadline":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "immediate_semantics":
        return "EVENT_AT_DEMAND_NOT_NUMERIC_DAYS"
    if query == "cross_law_boundary":
        return "ARTICLE15_DOES_NOT_REPLACE_OTHER_APPLICABLE_LAWS"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({item["id"] for item in model["atomic_rules"]}) == 7
    assert model["numeric_deadlines"] == []
    assert len(model["event_deadlines_without_numeric_value"]) == 1
    assert len(model["temporal_model"]) == 3
    assert len(model["evidence_model"]) == len({item["id"] for item in model["evidence_model"]}) == 9
    assert len(model["conflict_and_definition_checks"]) == 10
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["verification_boundary"]["immutable_current_consolidated_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False
    source = next(item for item in library["sources"] if item["id"] == "PDN-SRC-0001")
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(item for item in matrix["directions"] if item["id"] == "PDN-DIR-11")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
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
    print("PASS: 7 atomic rules; 0 numeric deadlines; 1 event deadline; 9 evidence nodes; 10 conflict checks; 36 cases")


if __name__ == "__main__":
    main()
