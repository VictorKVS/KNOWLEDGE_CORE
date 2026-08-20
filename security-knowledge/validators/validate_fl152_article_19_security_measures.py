#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-19-security-measures-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-19-security-measures-regression-v1.json")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")


def evaluate(case):
    q = case["query"]
    if q == "operator_security":
        return "PASS_OPERATOR_DUTY" if case["takes_or_ensures"] else "BLOCK_OPERATOR_DUTY_UNPROVEN"
    if q == "measure_set":
        return "BLOCK_PART2_NOT_EXHAUSTIVE" if case["checklist_only"] else "PASS_NECESSARY_OUTCOME_REVIEW"
    if q == "protected_actions":
        required = {"ACCESS", "DESTRUCTION", "ALTERATION", "BLOCKING", "COPYING", "PROVISION", "DISSEMINATION", "OTHER_UNLAWFUL"}
        return "PASS" if set(case["covered"]) == required else "BLOCK_INCOMPLETE_ACTION_SET"
    if q == "threat_scope":
        if not case["ispdn"]:
            return "ROUTE_OUTSIDE_POINT1_ISPDN_LOCATOR"
        return "PASS" if case["threats_determined"] else "BLOCK_THREAT_DETERMINATION_MISSING"
    if q == "requirements_levels":
        if not case["requirements_applied"]:
            return "BLOCK_REQUIREMENTS_APPLICATION_UNPROVEN"
        return "PASS" if case["level_achieved"] else "BLOCK_LEVEL_OUTCOME_UNPROVEN"
    if q == "conformity":
        if not case["tool_used"]:
            return "NO_TOOL_CLAIM_REVIEW_APPLICABILITY"
        return "PASS" if case["conformity_passed"] else "BLOCK_CONFORMITY_UNPROVEN"
    if q == "destruction_tool":
        if not case["conformity_passed"]:
            return "BLOCK_CONFORMITY_UNPROVEN"
        return "PASS" if case["destruction_function"] else "BLOCK_DESTRUCTION_FUNCTION_MISSING"
    if q == "effectiveness":
        if not case["assessment_completed"]:
            return "BLOCK_ASSESSMENT_MISSING"
        if case["commissioned"] and not case.get("assessment_before_commissioning", False):
            return "BLOCK_LATE_ASSESSMENT"
        return "PASS_BEFORE_COMMISSIONING"
    if q == "media":
        return "PASS" if case["accounted"] else "BLOCK_MACHINE_MEDIA_ACCOUNTING_MISSING"
    if q == "incident_controls":
        checks = [
            ("unauthorized_access_detection", "BLOCK_UNAUTHORIZED_ACCESS_DETECTION"),
            ("attack_detection", "BLOCK_ATTACK_DETECTION"),
            ("attack_prevention", "BLOCK_ATTACK_PREVENTION"),
            ("consequence_elimination", "BLOCK_CONSEQUENCE_ELIMINATION"),
            ("incident_response", "BLOCK_INCIDENT_RESPONSE"),
        ]
        for field, result in checks:
            if not case[field]:
                return result
        return "PASS"
    if q == "recovery":
        if not case["unauthorized_access_caused_change_or_destruction"]:
            return "NO_TRIGGER_NO_RECOVERY_RESULT_CLAIM"
        return "PASS_RECOVERY_ROUTE" if case["recovery_capability"] else "BLOCK_RECOVERY_CAPABILITY_MISSING"
    if q == "access_logging":
        if not case["access_rules"]:
            return "BLOCK_ACCESS_RULES_MISSING"
        return "PASS" if case["all_actions_logged"] is True else "BLOCK_ALL_ACTIONS_LOGGING_MISSING"
    if q == "control":
        if not case["measures_controlled"]:
            return "BLOCK_MEASURE_CONTROL_MISSING"
        return "PASS" if case["level_controlled"] else "BLOCK_LEVEL_CONTROL_MISSING"
    if q == "government_factors":
        required = {"HARM", "VOLUME_CONTENT", "ACTIVITY", "THREAT_RELEVANCE"}
        return "PASS" if set(case["factors"]) == required else "BLOCK_INCOMPLETE_FACTOR_SET"
    if q == "delegation":
        return {
            "ARTICLE19_ASSIGN_LEVEL": "REJECT_ROUTE_TO_PP1119",
            "ARTICLE19_ENUMERATES_FSTEC_CONTROLS": "REJECT_ROUTE_TO_FSTEC_FSB_ACTS",
            "GOVERNMENT_SETS_LEVELS_REQUIREMENTS_BIOMETRIC_MEDIA": "PASS_DELEGATED_STRUCTURE",
        }[case["claim"]]
    if q == "sector_actor":
        allowed = {"FEDERAL_POLICY_BODY", "REGIONAL_AUTHORITY", "BANK_OF_RUSSIA", "STATE_EXTRA_BUDGETARY_FUND", "OTHER_STATE_BODY"}
        if case["actor"] not in allowed:
            return "BLOCK_NOT_PART5_ACTOR"
        return "ALLOW_PART5_ROUTE" if case["within_powers"] else "BLOCK_OUTSIDE_POWERS"
    if q == "sector_factors":
        return "PASS" if all(case[k] for k in ("content", "nature", "methods")) else "BLOCK_INCOMPLETE_FACTOR_SET"
    if q == "association":
        if not case["is_operator_association"]:
            return "BLOCK_NOT_ASSOCIATION_ROUTE"
        if not case["member_activity_scope"]:
            return "BLOCK_MEMBER_ACTIVITY_SCOPE_MISSING"
        return "ALLOW_OPTIONAL_ADDITIONAL_THREATS"
    if q == "association_mandatory":
        return "OPTIONAL_NOT_UNIVERSAL_DUTY"
    if q == "coordination":
        if not case["fsb"]:
            return "BLOCK_FSB_COORDINATION_MISSING"
        if not case["fstec"]:
            return "BLOCK_FSTEC_COORDINATION_MISSING"
        if case["route"] == "PART6_DECISION" and not case["government_procedure"]:
            return "BLOCK_GOVERNMENT_PROCEDURE_MISSING"
        return "PASS_PART6_COORDINATION" if case["route"] == "PART6_DECISION" else "PASS_PART5_COORDINATION"
    if q == "refusal":
        if case["route"] != "PART6_DECISION":
            return "NO_PART7_SENTENCE3_CLAIM_FOR_PART5"
        return "PASS_MOTIVATED_REFUSAL" if case["motivated"] else "BLOCK_UNMOTIVATED_REFUSAL"
    if q == "state_supervision":
        if not case["within_powers"]:
            return "BLOCK_OUTSIDE_POWERS"
        if case["authority"] == "FSTEC" and case["access_personal_data"]:
            return "BLOCK_FSTEC_PERSONAL_DATA_ACCESS"
        return "ALLOW_WITHOUT_PERSONAL_DATA_ACCESS" if case["authority"] == "FSTEC" else "ALLOW_WITHIN_FSB_POWERS_REVIEW"
    if q == "nonstate_supervision":
        if not case["government_decision"]:
            return "BLOCK_GOVERNMENT_DECISION_MISSING"
        if not case["selected_activity"]:
            return "BLOCK_ACTIVITY_SCOPE_MISSING"
        if case["authority"] == "FSTEC" and case["access_personal_data"]:
            return "BLOCK_FSTEC_PERSONAL_DATA_ACCESS"
        return "ALLOW_CONDITIONAL_FSB_ROUTE" if case["authority"] == "FSB" else "ALLOW_CONDITIONAL_FSTEC_ROUTE"
    if q == "biometric":
        if not case["outside_ispdn"]:
            return "ROUTE_TO_ISPDN_REGIME"
        if not case["compliant_media"]:
            return "BLOCK_MEDIA_REQUIREMENTS_UNPROVEN"
        return "PASS_OUTSIDE_ISPDN_ROUTE" if case["compliant_storage_technology"] else "BLOCK_STORAGE_TECH_REQUIREMENTS_UNPROVEN"
    if q == "definition":
        expected = {
            ("THREAT", "CONDITIONS_AND_FACTORS_CREATING_UNAUTHORIZED_ACCESS_DANGER"): "PASS",
            ("THREAT", "CONFIRMED_INCIDENT"): "REJECT_THREAT_NOT_INCIDENT",
            ("PROTECTION_LEVEL", "COMPOSITE_REQUIREMENTS_INDICATOR"): "PASS",
            ("PROTECTION_LEVEL", "NUMERIC_RISK_SCORE"): "REJECT_NOT_NUMERIC_RISK_SCORE",
        }
        return expected[(case["term"], case["candidate"])]
    if q == "gossopka":
        if not case["covered_incident"]:
            return "NO_ARTICLE19_PART12_NOTICE_TRIGGER"
        return "INFORM_GOSSOPKA" if case["procedure_followed"] else "BLOCK_PROCEDURE_UNPROVEN"
    if q == "gossopka_deadline":
        return "NOT_STATED_ROUTE_TO_FSB_PROCEDURE"
    if q == "notification_route":
        return "SEPARATE_FROM_GOSSOPKA" if case["route"] == "RKN_ARTICLE21" else "SEPARATE_FROM_RKN_ARTICLE21"
    if q == "forwarding":
        return "EXCLUDED_FROM_PART13_FORWARDING" if case["state_secret"] else "FSB_FORWARD_TO_AUTHORIZED_PDN_BODY"
    if q == "protected_person":
        routes = {
            "FSB_EMPLOYEE": "ROUTE_40_FZ",
            "FSB_CONFIDENTIAL_ASSISTANT_FORMER": "ROUTE_40_FZ",
            "PROTECTED_JUDGE": "ROUTE_45_FZ",
            "FOREIGN_INTELLIGENCE_EMPLOYEE": "ROUTE_5_FZ",
            "STATE_PROTECTION_OBJECT_FAMILY_MEMBER": "ROUTE_57_FZ",
            "PROTECTED_WITNESS": "ROUTE_119_FZ",
            "INTERNAL_AFFAIRS_EMPLOYEE": "ROUTE_3_FZ",
        }
        return routes.get(case["category"], "NO_PART15_ROUTE_BY_ANALOGY")
    if q == "family_scope":
        return "EXPRESS_PART15_FAMILY_ROUTE" if case["category"] == "STATE_PROTECTION_OBJECT_FAMILY_MEMBER" else "DO_NOT_GENERALIZE_FROM_ARTICLE19"
    if q == "special_law_detail":
        return "PENDING_SEPARATE_SIX_LAW_CROSSWALK"
    if q == "numeric_deadline":
        return "NONE_IN_ARTICLE19"
    if q == "part15_effective":
        return "EFFECTIVE" if date.fromisoformat(case["as_of"]) >= date(2025, 7, 1) else "NOT_YET_EFFECTIVE"
    raise AssertionError(f"Unhandled query: {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({r["id"] for r in model["atomic_rules"]}) == 54
    assert model["numeric_deadlines"] == []
    assert len(model["event_deadlines_without_numeric_value"]) == 2
    assert len(model["temporal_model"]) == 7
    assert len(model["evidence_model"]) == len({r["id"] for r in model["evidence_model"]}) == 30
    assert len(model["conflict_and_definition_checks"]) == 30
    assert model["source"]["current_edition_checked"] == "2026-07-26"
    assert model["source"]["official_233_fz_publication"]["publication_number"] == "0001202408080031"
    assert model["source"]["official_23_fz_publication"]["publication_number"] == "0001202502280034"
    assert model["verification_boundary"]["immutable_current_consolidated_bytes"] == "PENDING"
    assert model["verification_boundary"]["fstec_order_21_current_clause_map"] == "PENDING"
    assert model["verification_boundary"]["fsb_order_378_current_applicability"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False
    assert model["red_team"]["high_gap_created"] is False

    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0001")
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-18")
    assert direction["maturity"] == "EXECUTABLE"
    assert len(fixtures["cases"]) == 100

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 54 atomic rules; 0 numeric deadlines; 2 event deadlines; 30 evidence nodes; 30 conflict checks; 100 cases")


if __name__ == "__main__":
    main()
