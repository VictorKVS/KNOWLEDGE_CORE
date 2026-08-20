#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/gis-fstec-117-process-details-50-61-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/gis-fstec-117-process-details-50-61-regression-v1.json")
TEMPORAL = Path("security-knowledge/classification/gis-fstec-117-137-temporal-amendment-atomic-v1.yaml")


def evaluate(case, rules):
    query = case["query"]
    if query == "rule_exists":
        return "PRESENT" if case["rule_id"] in rules else "ABSENT"
    if query == "secure_development":
        if not case["used_in_is"]:
            return "NO_POINT50_INFORMATION_SYSTEM_USE_TRIGGER"
        if case["mode"] == "SELF":
            return "PASS_SELF_GOST_SECTIONS_4_5" if case["gost_sections_4_5"] else "BLOCK_SELF_GOST_SECTIONS_4_5_REQUIRED"
        if case["mode"] == "PROCURED":
            return "NO_POINT50_SELF_DEVELOPMENT_TRIGGER"
        if not case["head_decision"]:
            return "OPTIONAL_TZ_DECISION_NOT_EXERCISED"
        return "PASS_CONTRACTOR_TZ_REQUIREMENTS_INCLUDED" if case["tz_included"] else "BLOCK_HEAD_DECISION_NOT_IMPLEMENTED_IN_TZ"
    if query == "physical_access":
        return "ALLOW_NEEDED_ACCESS" if case["needed_for_duties"] else "BLOCK_UNNEEDED_PHYSICAL_ACCESS"
    if query == "storage_location":
        return "PASS" if case["unauthorized_access_excluded"] else "BLOCK_PROTECTED_LOCATION_REQUIRED"
    if query == "removable_media":
        if not case["operator_issued"]:
            return "BLOCK_OPERATOR_ISSUED_MEDIA_ONLY"
        if not case["accounted"]:
            return "BLOCK_MEDIA_ACCOUNTING_REQUIRED"
        return "PASS" if case["controlled"] else "BLOCK_MEDIA_USE_CONTROL_REQUIRED"
    if query == "unknown_media":
        if case["connected"]:
            return "BLOCK_UNKNOWN_MEDIA_CONNECTION"
        if not case["transferred"]:
            return "BLOCK_TRANSFER_TO_SECURITY_REQUIRED"
        return "PASS_TRANSFER_AND_SECURITY_ANALYSIS" if case["analyzed"] else "BLOCK_SECURITY_ANALYSIS_REQUIRED"
    if query == "continuity_scope":
        return "RECOVERY_INTERVAL_ROUTE_REQUIRED" if case["significant_function"] else "NO_POINT53_CLASS_CLOCK_FROM_CLAUSE52_ALONE"
    if query == "recovery":
        return {
            "K1": "24_HOURS_FROM_DETECTION",
            "K2": "7_CALENDAR_DAYS_FROM_DETECTION",
            "K3": "4_WEEKS_FROM_DETECTION",
        }[case["class"]]
    if query == "recovery_start":
        return "DISRUPTION_DETECTION"
    if query == "fault_tolerance":
        if not case["deployed"]:
            return "BLOCK_FAULT_TOLERANT_CONFIGURATION_REQUIRED"
        return "PASS" if case["meets_interval"] else "BLOCK_RECOVERY_INTERVAL_NOT_MET"
    if query == "backup":
        if not case["technical"]:
            return "BLOCK_TECHNICAL_BACKUPS_REQUIRED"
        if not case["information"]:
            return "BLOCK_INFORMATION_BACKUPS_REQUIRED"
        if not case["different_media_types"]:
            return "BLOCK_DIFFERENT_MEDIA_TYPES_REQUIRED"
        if not case["protected_location"]:
            return "BLOCK_PROTECTED_BACKUP_LOCATION_REQUIRED"
        return "PASS" if case["periodic_operability_test"] else "BLOCK_PERIODIC_OPERABILITY_TEST_REQUIRED"
    if query == "backup_parameters":
        return "INTERNAL_STANDARDS_AND_REGULATIONS_NO_UNIVERSAL_NUMBER"
    if query == "recovery_drill":
        return "PASS_AT_MAXIMUM_INTERVAL" if case["years_since_last"] <= 2 else "BLOCK_MORE_THAN_TWO_YEARS"
    if query == "fallback":
        if not case["recovery_interval_exceeded"]:
            return "NO_EXCEEDED_INTERVAL_FALLBACK_TRIGGER"
        return "PASS_NON_AUTOMATED_FALLBACK" if case["non_automated_available"] and case["internal_regulation"] else "BLOCK_FALLBACK_REQUIRED"
    if query == "awareness_activities":
        if not case["simulated_messages"]:
            return "BLOCK_SIMULATED_MESSAGES_MISSING"
        return "PASS_ALL_FOUR_ACTIVITY_TYPES" if all(case[key] for key in ("materials", "education", "drills")) else "BLOCK_INCOMPLETE_AWARENESS_ACTIVITIES"
    if query == "knowledge_assessment":
        if case["incident"]:
            return "ASSESS_AFTER_INCIDENT"
        return "ASSESS_AT_MAXIMUM_INTERVAL" if case["years_since_last"] <= 3 else "BLOCK_MORE_THAN_THREE_YEARS"
    if query == "repeat_training":
        if not case["lacks_knowledge"]:
            return "NO_REPEAT_TRAINING_TRIGGER"
        return "PASS_REPEAT_TRAINING" if case["organized"] else "BLOCK_REPEAT_TRAINING_REQUIRED"
    if query == "contractor_access":
        if not case["requirements_set"]:
            return "BLOCK_CONTRACTOR_REQUIREMENTS_REQUIRED"
        return "PASS" if case["means_channels_interfaces_protected"] else "BLOCK_CONTRACTOR_ACCESS_PATH_PROTECTION_REQUIRED"
    if query == "contractor_copy":
        if case["copied"] and not case["authorized_in_access_documents"]:
            return "BLOCK_UNAUTHORIZED_COPY"
        return "ALLOW_DOCUMENTED_COPY"
    if query == "contractor_system":
        if not case["protected"]:
            return "BLOCK_CONTRACTOR_SYSTEM_PROTECTION_REQUIRED"
        return "PASS" if case["composition_purpose_classes_defined"] else "BLOCK_OPERATOR_SCOPE_AND_CLASS_DEFINITION_REQUIRED"
    if query == "contractor_environment":
        if case["target"] == "PRODUCTION":
            return "BLOCK_DEVELOPMENT_OR_TEST_IN_PRODUCTION"
        if not case["isolated"]:
            return "BLOCK_STAND_ISOLATION_REQUIRED"
        return "PASS_ISOLATED_STAND" if case["access_control"] else "BLOCK_STAND_ACCESS_CONTROL_REQUIRED"
    if query == "ddos_scope":
        return "DDOS_PROTECTION_REQUIRED" if case["always_internet_accessible"] else "REQUIRE_SCOPE_FACTS"
    if query == "ddos_interaction":
        if not case["gossopka"]:
            return "BLOCK_GOSSOPKA_INTERACTION_MISSING"
        return "PASS_BOTH_DISTINCT_INTERACTIONS" if case["public_network_center_automated"] else "BLOCK_AUTOMATED_CENTER_INTERACTION_MISSING"
    if query == "ddos_service":
        allowed = {"HOSTING", "TELECOM", "DDOS_FILTERING"}
        return "PASS_ALLOWED_PROVIDER_TYPE" if case["engaged"] and case["provider_type"] in allowed else "BLOCK_EXTERNAL_SERVICE_ORGANIZATION_REQUIRED"
    if query == "ddos_location":
        return "PASS" if case["filtering_means_in_russia"] else "BLOCK_FILTERING_MEANS_RUSSIA_LOCATION"
    if query == "ddos_availability":
        if not case["security_approval"]:
            return "BLOCK_SECURITY_APPROVAL_REQUIRED"
        return "PASS" if all(case[key] for key in ("internal_regulation", "traffic_filtering", "resource_flow_list")) else "BLOCK_INCOMPLETE_INTERNET_AVAILABILITY_CONTROL"
    if query == "ai_asset_protection":
        return "PASS_ALL_AI_ASSET_GROUPS" if all(case[key] for key in ("data", "models", "parameters", "processes_services")) else "BLOCK_INCOMPLETE_AI_ASSET_PROTECTION"
    if query == "ai_transfer":
        if case["restricted_information"] and case["recipient"] == "MODEL_DEVELOPER":
            return "BLOCK_RESTRICTED_INFORMATION_TRANSFER"
        return "REQUIRE_INFORMATION_CLASSIFICATION_REVIEW"
    if query == "ai_interaction":
        if case["mode"] == "STRICT_TEMPLATE":
            return "PASS_TEMPLATE_ROUTE" if case["request_control"] and case["response_control"] else "BLOCK_TEMPLATE_CONTROL_REQUIRED"
        if not case["request_control"]:
            return "BLOCK_ALLOWED_TOPIC_CONTROL_REQUIRED"
        return "PASS_TOPIC_AND_FORMAT_ROUTE" if case["response_control"] else "BLOCK_RESPONSE_FORMAT_AND_TOPIC_CONTROL_REQUIRED"
    if query == "ai_unreliable":
        return "PASS" if all(case[key] for key in ("criteria", "collected_analyzed", "response_limitation")) else "BLOCK_UNRELIABLE_RESPONSE_CONTROL_INCOMPLETE"
    if query == "ai_trust":
        if not case["trusted_technology_or_component"]:
            return "BLOCK_TRUSTED_AI_REQUIRED_IN_SYSTEM"
        return "PASS" if case["unregulated_influence_excluded"] else "BLOCK_UNREGULATED_INFLUENCE"
    if query == "temporal":
        when = date.fromisoformat(case["as_of"])
        return "ORIGINAL_POINTS_50_TO_61" if when < date(2026, 9, 1) else "ORDER137_GENERAL_AMENDMENTS_APPLY"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    temporal = yaml.safe_load(TEMPORAL.read_text(encoding="utf-8"))
    rules = {item["id"]: item for item in model["atomic_rules"]}

    assert model["status"] == "VERIFIED_CURRENT_BOUNDED_SLICE"
    assert len(rules) == len(model["atomic_rules"]) == 79
    assert len(model["evidence_model"]) == 14
    numeric = {
        (item["maximum"]["value"], item["maximum"]["unit"])
        for item in model["atomic_rules"]
        if "maximum" in item
    }
    assert numeric == {(24, "HOURS"), (7, "CALENDAR_DAYS"), (4, "WEEKS"), (2, "YEARS"), (3, "YEARS")}
    assert sum("event_trigger" in item for item in model["atomic_rules"]) == 1
    assert model["verification_boundary"]["clauses_50_to_61_atomization"] == "VERIFIED"
    assert model["verification_boundary"]["gost_r_56939_2024_sections_4_and_5_atomization"] == "PENDING_SEPARATE_STANDARD_MODEL"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert temporal["id"] == "RU-FSTEC117-137-GIS-TEMPORAL-AMENDMENT-ATOMIC-V1"
    future = json.dumps(temporal, ensure_ascii=False)
    assert "point_55_paragraph_3" in future
    assert "point_58_paragraph_2" in future
    assert len(fixtures["cases"]) == 80

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, rules)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 79 process rules; 5 numeric deadlines; 1 event trigger; 14 evidence nodes; 80 cases")


if __name__ == "__main__":
    main()
