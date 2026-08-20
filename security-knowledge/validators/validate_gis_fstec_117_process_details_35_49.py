#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/gis-fstec-117-process-details-35-49-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/gis-fstec-117-process-details-35-49-regression-v1.json")
TEMPORAL = Path("security-knowledge/classification/gis-fstec-117-137-temporal-amendment-atomic-v1.yaml")


def evaluate(case, rules):
    query = case["query"]
    if query == "rule_exists":
        return "PRESENT" if case["rule_id"] in rules else "ABSENT"
    if query == "threat_model":
        if case["system"] == "GOVERNMENT":
            return "REQUIRED_BY_PP676_ROUTE" if case["pp676_requires"] else "REQUIRE_PP676_APPLICABILITY_REVIEW"
        return (
            "REQUIRED_BY_HEAD_OR_RESPONSIBLE_PERSON_DECISION"
            if case["head_decision"]
            else "NOT_AUTOMATICALLY_REQUIRED_BY_CLAUSE36"
        )
    if query == "threat_operation":
        if case["indicators"] and not case["neutralize"]:
            return "BLOCK_MISSING_NEUTRALIZATION"
        return "PASS" if all(case[key] for key in ("search", "prioritize", "notify")) else "BLOCK_INCOMPLETE_THREAT_OPERATION"
    if query == "vulnerability":
        if not case["exploitable"]:
            return "REQUIRE_EXPLOITABILITY_FACTS_NO_CLOCK_INVENTED"
        return {
            "CRITICAL": "24_HOURS_REMEDIATE_OR_COMPENSATE",
            "HIGH": "7_CALENDAR_DAYS_REMEDIATE_OR_COMPENSATE",
            "MEDIUM": "INTERNAL_REGULATION_PERIOD_AND_PROCEDURE",
            "LOW": "INTERNAL_REGULATION_PERIOD_AND_PROCEDURE",
        }[case["level"]]
    if query == "bdu_notice":
        return "NO_CLAUSE38_NEW_BDU_NOTICE_TRIGGER" if case["in_bdu"] else "5_WORKING_DAYS_FROM_DETECTION"
    if query == "compensating_measure":
        return "BLOCK_NO_AUTOMATIC_EXTENSION" if case["automatic_extension"] else "ALLOW_WITHIN_ORIGINAL_CLOCK"
    if query == "update":
        if not case["tested"]:
            return "BLOCK_TEST_BEFORE_PRODUCTION"
        if not case["authorized"]:
            return "BLOCK_UNCONTROLLED_INSTALLATION"
        return "PASS" if case["authenticity"] and case["integrity"] else "BLOCK_AUTHENTICITY_OR_INTEGRITY"
    if query == "update_period":
        return "INTERNAL_REGULATION_FROM_VULNERABILITY_PERIOD_AND_RISK"
    if query == "restricted_notice":
        return "IMMEDIATE_EVENT_NO_NUMERIC_VALUE" if case["event"] else "NO_NOTICE_TRIGGER"
    if query == "restricted_access":
        if not case["access_logged"]:
            return "BLOCK_ALL_ACCESS_FACTS_MUST_BE_REGISTERED"
        return "PASS" if all(case[key] for key in ("inventory", "storage_tools", "controlled")) else "BLOCK_INCOMPLETE_RESTRICTED_INFORMATION_CONTROL"
    if query == "mobile_work":
        if not case["channel_protected"]:
            return "BLOCK_CHANNEL_PROTECTION"
        if not case["strong_auth"]:
            return "BLOCK_STRONG_AUTHENTICATION"
        return "PASS" if case["device_access_protected"] else "BLOCK_DEVICE_ACCESS_PROTECTION"
    if query == "personal_mobile_work":
        if not case["compliant"]:
            return "BLOCK_DEVICE_COMPLIANCE_REQUIRED"
        return "ALLOW" if case["operator_can_control"] else "BLOCK_OPERATOR_CONTROL_REQUIRED"
    if query == "mobile_nonwork":
        if case["channel_needed"] and not case["channel_protected"]:
            return "BLOCK_NEEDED_CHANNEL_PROTECTION"
        return "PASS" if case["system_protection"] else "BLOCK_SYSTEM_PROTECTION"
    if query == "remote_work":
        return "ALLOW" if case["compliant"] else "BLOCK_COMPLIANT_TOOL_REQUIRED"
    if query == "personal_remote_work":
        if not case["security_approval"]:
            return "BLOCK_SECURITY_UNIT_APPROVAL"
        if not case["certified_safe_remote"]:
            return "BLOCK_CERTIFIED_SAFE_REMOTE_CONTROL"
        return "ALLOW" if case["antivirus"] and case["other_controls"] else "BLOCK_REQUIRED_CONTROLS"
    if query == "remote_network":
        if not case["located_in_russia"]:
            return "BLOCK_NETWORK_LOCATION"
        if not case["channel_protected"]:
            return "BLOCK_CHANNEL_PROTECTION"
        return "PASS" if case["strong_auth"] else "BLOCK_STRONG_AUTHENTICATION"
    if query == "remote_nonwork":
        if case["channel_needed"] and not case["channel_protected"]:
            return "BLOCK_NEEDED_CHANNEL_PROTECTION"
        return "PASS" if case["system_protection"] else "BLOCK_SYSTEM_PROTECTION"
    if query == "wireless_work":
        if not case["identified"]:
            return "BLOCK_ACCESS_POINT_IDENTIFICATION"
        if not case["isolated"]:
            return "BLOCK_WORK_PUBLIC_NETWORK_ISOLATION"
        return "PASS" if case["protected"] and case["location_defined"] else "BLOCK_INCOMPLETE_WIRELESS_CONTROL"
    if query == "privileged_auth":
        if case["strong_possible"]:
            return "PASS_STRONG" if case["strong_used"] else "BLOCK_FALLBACK_REQUIRES_TECHNICAL_IMPOSSIBILITY"
        return "PASS_ENHANCED_MFA_FALLBACK" if case["enhanced_mfa"] else "BLOCK_AUTHENTICATION"
    if query == "privileged_roles":
        return "BLOCK_ROLE_COMBINATION" if case["combined"] else "PASS"
    if query == "built_in_privileged":
        if not case["disabled"] and not case["renamed_when_disable_impossible"]:
            return "BLOCK_DISABLE_OR_RENAME"
        return "PASS" if case["auth_changed"] else "BLOCK_CHANGE_AUTHENTICATION_INFORMATION"
    if query == "privileged_logging":
        return "PASS" if case["all_actions_logged"] else "BLOCK_ALL_ACTIONS_MUST_BE_LOGGED"
    if query == "monitoring_scope":
        if case["system"] == "LOCAL_OR_ISOLATED":
            return "PASS_LOG_CONTROL_EXCEPTION" if case["log_control"] else "BLOCK_EVENT_LOG_CONTROL_REQUIRED"
        return "PASS_MONITORING" if case["monitoring"] else "BLOCK_MONITORING_REQUIRED"
    if query == "monitoring_ai":
        return "OPTIONAL_ALLOWED" if case["trusted"] else "DO_NOT_TREAT_UNTRUSTED_AI_AS_CLAUSE49_ROUTE"
    if query == "monitoring_deadline":
        return "INTERNAL_PERIOD_NO_ORDER_NUMERIC_VALUE"
    if query == "fstec_year_report":
        return "SEND_EVENT_NO_NUMERIC_DAY" if case["presented_to_head"] and case["last_or_annual"] else "NO_SEND_EVENT"
    if query == "temporal":
        when = date.fromisoformat(case["as_of"])
        return "ORIGINAL_POINTS_35_TO_49" if when < date(2026, 9, 1) else "ORDER137_GENERAL_AMENDMENTS_APPLY"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    temporal = yaml.safe_load(TEMPORAL.read_text(encoding="utf-8"))
    rules = {item["id"]: item for item in model["atomic_rules"]}

    assert model["status"] == "VERIFIED_CURRENT_BOUNDED_SLICE"
    assert len(rules) == len(model["atomic_rules"]) == 81
    assert len(model["evidence_model"]) == 15
    numeric = {
        (item["maximum"]["value"], item["maximum"]["unit"])
        for item in model["atomic_rules"]
        if "maximum" in item
    }
    assert numeric == {(24, "HOURS"), (7, "CALENDAR_DAYS"), (5, "WORKING_DAYS")}
    event_types = {item["deadline_type"] for item in model["atomic_rules"] if "deadline_type" in item}
    assert event_types == {"EVENT_IMMEDIATE_NO_NUMERIC_VALUE", "EVENT_NO_NUMERIC_VALUE"}
    assert model["verification_boundary"]["clauses_35_to_49_atomization"] == "VERIFIED"
    assert model["verification_boundary"]["clauses_50_to_61_atomization"] == "PENDING_NEXT_SLICE"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert temporal["id"] == "RU-FSTEC117-137-GIS-TEMPORAL-AMENDMENT-ATOMIC-V1"
    future = json.dumps(temporal, ensure_ascii=False)
    for point in ("point_35", "point_42_paragraph_4", "point_46_paragraph_4"):
        assert point in future
    assert len(fixtures["cases"]) == 72

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, rules)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 81 process rules; 3 numeric deadlines; 2 event deadlines; 15 evidence nodes; 72 cases")


if __name__ == "__main__":
    main()
