#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/federal-laws/126-FZ/requirements/security-relevant-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/federal-laws/126-FZ/requirements/security-relevant-regression-v1.json")
DOCUMENT = Path("security-knowledge/legislation/RU/federal-laws/126-FZ/document.yaml")


def evaluate(case):
    q = case["query"]
    if q == "version":
        return "FUTURE_ARTICLE64_POINT2_PENDING" if date.fromisoformat(case["as_of"]) >= date(2027, 3, 1) else "CURRENT_SLICE"
    if q == "article7_build":
        if case["actor"] not in {"COMMUNICATIONS_OPERATOR", "DEVELOPER_BUILDER"}:
            return "NO_POINT2_ACTOR_ROUTE"
        return "CONSIDER_PROTECTION" if case["listed_activity"] else "NO_POINT2_ACTIVITY_ROUTE"
    if q == "article7_operation":
        if not case["operator"]:
            return "NO_POINT3_OPERATOR_ROUTE"
        return "PASS" if case["protected"] else "BLOCK_PROTECTION_UNPROVEN"
    if q == "article12_requirement":
        return "PASS_DEPENDENCY" if case["claim"] == "REGULATOR_REQUIREMENT_DEPENDENCY" else "REJECT_OVERCLAIM"
    if q == "article12_coordination":
        return "PASS" if case["security_authority"] else "BLOCK_COORDINATION_UNPROVEN"
    if q == "network_management":
        if not case["operator"]:
            return "NO_OPERATOR_ROUTE"
        return "PASS" if case["conforms"] else "BLOCK_CONFORMANCE_UNPROVEN"
    if q == "subscriber_protection":
        return "PASS" if case["protected"] else "BLOCK_PROTECTION_UNPROVEN"
    if q == "subscriber_scope":
        return "IN_SCOPE" if case["field"] in {"TRAFFIC", "PAYMENTS"} else "REVIEW"
    if q == "individual_disclosure":
        if not case["consent"] and not case["federal_law_exception"]:
            return "BLOCK_NO_BASIS"
        if not case["proof"]:
            return "BLOCK_PROOF_MISSING"
        return "PASS_CONSENT" if case["consent"] else "PASS_FEDERAL_LAW_EXCEPTION"
    if q == "public_individual_database":
        return "PASS" if case["written_consent"] else "BLOCK_WRITTEN_CONSENT_MISSING"
    if q == "correction_deadline":
        return "IMMEDIATELY_NO_NUMERIC_DAYS"
    if q == "public_removal":
        return "REMOVE" if case["trigger"] in {"INDIVIDUAL_DEMAND", "COURT_DECISION", "AUTHORIZED_STATE_BODY_DECISION"} else "NO_TRIGGER"
    if q == "secrecy":
        if not case["operator"]:
            return "NO_OPERATOR_ROUTE"
        return "PASS" if case["ensured"] else "BLOCK_SECRECY_UNPROVEN"
    if q == "communication_access":
        if case["court"]:
            return "PASS_COURT"
        return "PASS_FEDERAL_LAW_EXCEPTION" if case["federal_law_exception"] else "BLOCK_NO_BASIS"
    if q == "communication_release":
        allowed = {"SENDER", "RECIPIENT", "AUTHORIZED_REPRESENTATIVE"}
        return "PASS" if case["recipient_class"] in allowed or case["federal_law_exception"] else "BLOCK"
    if q == "retention":
        return {"METADATA": "THREE_YEARS_IN_RUSSIA", "CONTENT": "UP_TO_SIX_MONTHS_GOVERNMENT_DEPENDENCY"}.get(case["kind"], "REJECT_CONFLATION")
    if q == "content_claim":
        return "REJECT_MAXIMUM_NOT_EXACT_PERIOD"
    if q == "authority_provision":
        return "ALLOW_ROUTE" if case["federal_law_case"] else "BLOCK_NO_FEDERAL_LAW_CASE"
    if q == "suspension":
        return "SUSPEND" if all(case[k] for k in ("reasoned_written_decision", "authorized_actor", "federal_law_case")) else "BLOCK"
    if q == "resumption":
        return "RESUME" if case["court"] or case["same_authorized_actor"] else "BLOCK"
    if q == "completeness":
        return "REJECT_BOUNDED_SLICE_ONLY"
    raise AssertionError(f"Unhandled query: {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    document = yaml.safe_load(DOCUMENT.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({r["id"] for r in model["atomic_rules"]}) == 21
    assert len(model["evidence_model"]) == len({r["id"] for r in model["evidence_model"]}) == 15
    assert model["source"]["current_consolidated_revision"] == "2026-02-20"
    assert model["source"]["changes_effective_through"] == "2026-07-01"
    assert model["temporal_model"][1]["from"] == "2027-03-01"
    assert model["temporal_model"][2]["value"] == 3
    assert model["temporal_model"][3]["maximum_value"] == 6
    assert model["verification_boundary"]["full_126fz_structure_definitions_and_requirements"] == "PENDING"
    assert model["verification_boundary"]["official_immutable_current_consolidated_bytes"] == "PENDING"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert document["status"] == "PARTIAL_VERIFIED_SECURITY_SLICE"
    assert document["extraction_state"]["atomic_requirements_complete"] is False
    assert len(fixtures["cases"]) == 50

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 21 atomic rules; 4 temporal routes; 15 evidence nodes; 50 cases; full-law completion remains pending")


if __name__ == "__main__":
    main()
