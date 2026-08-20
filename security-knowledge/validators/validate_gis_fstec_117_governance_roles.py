#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/governance/gis-fstec-117-governance-roles-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/gis-fstec-117-governance-roles-regression-v1.json")
TEMPORAL = Path("security-knowledge/classification/gis-fstec-117-137-temporal-amendment-atomic-v1.yaml")


def evaluate(case, model):
    query = case["query"]
    if query == "governance_required":
        return "REQUIRED"
    if query == "policy_approver":
        return "ALLOW" if case["actor"] in {"HEAD", "AUTHORIZED_BY_HEAD"} else "BLOCK"
    if query == "contractor_policy":
        if not case["relevant_access_or_work"]:
            return "OUTSIDE_CLAUSE16_TRIGGER"
        return "PASS" if case["documented_binding"] else "BLOCK_MISSING_DOCUMENTED_BINDING"
    if query == "tzki_license":
        if case["route"] == "INTERNAL_SECURITY_UNIT":
            return "DO_NOT_INFER_LICENSE_FROM_CLAUSE24"
        return "ALLOW_OPTIONAL_ENGAGEMENT" if case["licensed"] else "BLOCK_SPECIALIZED_ORGANIZATION_ROUTE"
    if query == "policy_content":
        return "REQUIRED" if case["item"] in model["required_policy_contents_clause_14a"] else "BLOCK_UNKNOWN_ITEM"
    if query == "standard_topic":
        return "REQUIRED" if case["item"] in model["required_internal_standard_topics_clause_14g"] else "BLOCK_UNKNOWN_ITEM"
    if query == "regulation_topic":
        item = case["item"]
        if item not in model["required_internal_regulation_topics_clause_14d"]:
            return "BLOCK_UNKNOWN_ITEM"
        if item in {"SECURE_SOFTWARE_DEVELOPMENT_IF_SELF_DEVELOPED", "INTERNET_SERVICE_PRODUCTION_RELEASE_IF_PRESENT"}:
            return "REQUIRED_CONDITIONAL_TOPIC"
        return "REQUIRED"
    if query == "objective":
        item = case["item"]
        if item not in model["security_objectives_clause_30"]:
            return "BLOCK_UNKNOWN_ITEM"
        if item.startswith("RECOVER_"):
            return "REQUIRED_OPERATOR_DEFINED_PERIOD"
        return "REQUIRED"
    if query == "education_share":
        population = case["population"]
        if population <= 0:
            return "REQUIRE_POPULATION_FACTS"
        return "PASS_AT_LEAST_30_PERCENT" if case["qualified"] * 100 >= 30 * population else "BLOCK_BELOW_30_PERCENT"
    if query == "clock":
        return {
            "KZI": "MAXIMUM_6_MONTHS",
            "PZI": "MAXIMUM_2_YEARS",
            "HEAD_NOTICE_NONCONFORMITY": "3_CALENDAR_DAYS_FROM_ASSESSMENT_COMPLETION",
            "FSTEC_RESULTS": "5_WORKING_DAYS_AFTER_CALCULATION_DAY",
            "POLICY_REVIEW": "NOT_STATED_DO_NOT_INVENT",
            "USER_AWARENESS": "NOT_STATED_DO_NOT_INVENT",
            "CLAUSE30_RECOVERY": "OPERATOR_DEFINED_NOT_ORDER_NUMERIC",
            "CONTRACTOR_ACKNOWLEDGEMENT": "NOT_STATED_DO_NOT_INVENT",
        }[case["clock"]]
    if query == "temporal":
        as_of = date.fromisoformat(case["as_of"])
        if as_of < date(2026, 3, 1):
            return "NOT_YET_EFFECTIVE"
        if as_of < date(2026, 9, 1):
            return "ORIGINAL_ORDER117"
        return "ORDER117_WITH_ORDER137_GENERAL_ROUTE"
    if query == "point32_actor":
        as_of = date.fromisoformat(case["as_of"])
        if as_of < date(2026, 9, 1):
            return "OPERATOR_OR_INFORMATION_HOLDER_KZI_AND_PZI"
        if as_of < date(2027, 3, 1):
            return "KEEP_ORIGINAL_POINT32_DURING_HYBRID_WINDOW"
        return "FUTURE_KZI_AND_CONTRACTOR_UZI_ROUTE"
    if query == "normalized_values":
        return "PENDING_DO_NOT_INVENT" if not case["methodical_documents_ingested"] else "ROUTE_TO_INGESTED_METHOD"
    if query == "responsible_person":
        return "PASS" if case["job_duties_documented"] else "BLOCK_JOB_DUTIES_REQUIRED"
    if query == "improvement_plan":
        required = ["decision", "names", "deadlines", "responsible_parties", "approved", "distributed"]
        return "PASS" if all(case[field] for field in required) else "BLOCK_INCOMPLETE_PLAN_EVIDENCE"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    temporal = yaml.safe_load(TEMPORAL.read_text(encoding="utf-8"))

    rules = model["atomic_rules"]
    assert len(rules) == len({row["id"] for row in rules}) == 60
    assert len(model["required_policy_contents_clause_14a"]) == 7
    assert len(model["required_internal_standard_topics_clause_14g"]) == 13
    assert len(model["required_internal_regulation_topics_clause_14d"]) == 17
    assert len(model["security_objectives_clause_30"]) == 11
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 20
    numeric = [row for row in rules if "maximum" in row]
    assert len(numeric) == 4
    assert {(row["maximum"]["value"], row["maximum"]["unit"]) for row in numeric} == {
        (6, "MONTHS"), (2, "YEARS"), (3, "CALENDAR_DAYS"), (5, "WORKING_DAYS")
    }
    assert model["verification_boundary"]["normalized_kzi_pzi_values"] == "PENDING_METHODICAL_DOCUMENT_INGEST"
    assert temporal["point_32_temporal_semantics"]["before_2027_03_01"]["maturity_indicator_interval"]["indicator"] == "PZI"
    assert temporal["point_32_temporal_semantics"]["from_2027_03_01"]["contractor_maturity_assessment"]["indicator"] == "UZI"
    assert len(fixtures["cases"]) == 80

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 60 governance rules; 37 clause-14 content items; 11 objectives; 4 clocks; 20 evidence nodes; 80 cases")


if __name__ == "__main__":
    main()
