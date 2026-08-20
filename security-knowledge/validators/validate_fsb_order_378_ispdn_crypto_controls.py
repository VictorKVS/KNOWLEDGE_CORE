#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/corpus/ru-personal-data/fsb-order-378-ispdn-crypto-controls-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/corpus/ru-personal-data/fsb-order-378-ispdn-crypto-controls-regression-v1.json")
PP1119 = Path("security-knowledge/classification/ispdn-protection-level-decision-table-pp1119-verified.yaml")
ARTICLE19 = Path("security-knowledge/corpus/ru-personal-data/fl-152-article-19-security-measures-atomic-v1.yaml")
FSTEC21 = Path("security-knowledge/corpus/ru-personal-data/fstec-order-21-ispdn-controls-atomic-v1.yaml")
LIBRARY = Path("security-knowledge/pdn/pdn-master-source-library-v1.yaml")
MATRIX = Path("security-knowledge/pdn/pdn-direction-coverage-matrix-v1.yaml")
DOCUMENT = Path("security-knowledge/legislation/RU/regulators/FSB/378-2014/document.yaml")
PLAN = Path("security-knowledge/legislation/RU/regulators/FSB/378-2014/atomization-plan.yaml")
REGISTRY = Path("security-knowledge/legislation/RU/regulators/FSB/registry.yaml")
LEGACY = Path("security-knowledge/legislation/RU/regulators/FSB/history/legacy-status.yaml")

CLASS_ORDER = ["KS1", "KS2", "KS3", "KV", "KA"]
CLASS_ROUTES = {
    (4, "TYPE_3"): "KS1",
    (3, "TYPE_2"): "KV",
    (3, "TYPE_3"): "KS1",
    (2, "TYPE_1"): "KA",
    (2, "TYPE_2"): "KV",
    (2, "TYPE_3"): "KS1",
    (1, "TYPE_1"): "KA",
    (1, "TYPE_2"): "KV",
}
CAPABILITIES = {
    "OUTSIDE_CONTROLLED_ZONE": "KS1",
    "INSIDE_CONTROLLED_ZONE": "KS2",
    "PHYSICAL_ACCESS_TO_COMPUTING_MEANS": "KS3",
    "APPLICATION_UNDOCUMENTED_SPECIALISTS": "KV",
    "SYSTEM_UNDOCUMENTED_SPECIALISTS": "KA",
}


def evaluate(case, model):
    query = case["query"]
    if query == "validity":
        as_of = date.fromisoformat(case["as_of"])
        if as_of < date(2014, 7, 10):
            return "NOT_SIGNED"
        if as_of < date(2014, 9, 28):
            return "SIGNED_NOT_EFFECTIVE"
        return "ACTIVE_CURRENT_ORIGINAL_EDITION"
    if query == "applicability":
        if not case["ispdn"]:
            return "OUTSIDE_ISPDN_SCOPE"
        return "ORDER378_APPLIES" if case["uses_skzi"] else "ORDER378_NOT_TRIGGERED"
    if query == "crypto_use_duty":
        return "REJECT_UNIVERSAL_CRYPTO_DUTY" if case["claimed_universal"] else "ROUTE_TO_APPLICABILITY_DECISION"
    if query == "class_route":
        return CLASS_ROUTES.get((case["level"], case["threat_type"]), "BLOCK_PP1119_LEVEL_THREAT_COMBINATION")
    if query == "class_sufficiency":
        return "PASS" if CLASS_ORDER.index(case["actual"]) >= CLASS_ORDER.index(case["required"]) else "BLOCK_CLASS_BELOW_THRESHOLD"
    if query == "measure_layers":
        return model["cumulative_measure_layers"].get(case["level"], "BLOCK_PP1119_LEVEL_REQUIRED")
    if query == "half_year_control":
        return "PASS" if case["months"] <= 6 else "BLOCK_SIX_MONTH_MAXIMUM_INTERVAL"
    if query == "monthly_control":
        return "PASS" if case["months"] <= 1 else "BLOCK_ONE_MONTH_MAXIMUM_INTERVAL"
    if query == "deadline_unit":
        return "MONTHS_NOT_WORKING_DAYS" if case["control"] == "JOURNAL_FUNCTION" else "MONTH_NOT_CALENDAR_DAY_COUNT"
    if query == "room_security":
        if not case["doors_locked"]:
            return "BLOCK_LOCKING_MISSING"
        if not case["authorized_only"]:
            return "BLOCK_AUTHORIZED_PASSAGE_CONTROL_MISSING"
        return "PASS" if case["tamper_evidence"] else "BLOCK_SEAL_OR_SIGNAL_MISSING"
    if query == "room_access_rules":
        return "PASS" if case["working"] and case["nonworking"] and case["abnormal"] else "BLOCK_ABNORMAL_RULE_MISSING"
    if query == "media_storage":
        if case["encrypted_only"] and not case["safe_or_cabinet"]:
            return "ALLOW_OUTSIDE_SAFE"
        return "PASS" if case["safe_or_cabinet"] else "BLOCK_SAFE_OR_CABINET_REQUIRED"
    if query == "media_accounting":
        if case["itemized"]:
            return "PASS"
        return "BLOCK_ITEMIZED_ACCOUNTING_STILL_REQUIRED" if case["encrypted_only"] else "BLOCK_ITEMIZED_ACCOUNTING_REQUIRED"
    if query == "duty_access_list":
        if not case["approved"]:
            return "BLOCK_APPROVAL_MISSING"
        return "PASS" if case["current"] else "BLOCK_CURRENT_STATE_MISSING"
    if query == "responsible_person":
        if not case["appointed"]:
            return "BLOCK_APPOINTMENT_MISSING"
        return "PASS" if case["sufficient_skills"] else "BLOCK_SKILLS_UNPROVEN"
    if query == "security_unit":
        if not case["analysis"]:
            return "BLOCK_ANALYSIS_MISSING"
        return "PASS" if case["unit_or_assignment"] else "BLOCK_UNIT_OR_ASSIGNMENT_MISSING"
    if query == "message_journal":
        checks = [
            ("approved_list", "BLOCK_APPROVED_JOURNAL_LIST_MISSING"),
            ("logs_requests", "BLOCK_REQUEST_LOGGING_MISSING"),
            ("logs_provision", "BLOCK_PROVISION_LOGGING_MISSING"),
            ("restricts_access", "BLOCK_JOURNAL_ACCESS_RESTRICTION_MISSING"),
        ]
        for field, result in checks:
            if not case[field]:
                return result
        return "PASS"
    if query == "security_journal":
        checks = [
            ("auto_permission_changes", "BLOCK_AUTOMATIC_PERMISSION_CHANGE_LOGGING_MISSING"),
            ("powers_recorded", "BLOCK_PERMISSION_RECORD_MISSING"),
            ("aligned_to_duties", "BLOCK_DUTY_ALIGNMENT_MISSING"),
            ("responsible_reviewer", "BLOCK_RESPONSIBLE_REVIEWER_MISSING"),
        ]
        for field, result in checks:
            if not case[field]:
                return result
        return "PASS"
    if query == "capability_profile":
        return CAPABILITIES.get(case["capability"], "NO_CLASS_PROCEDURE_CHANGE")
    if query == "reverse_inference":
        return "REJECT_CLASS_DOES_NOT_PROVE_THREAT_TYPE"
    if query == "fixed_period":
        return "NOT_STATED_DO_NOT_INVENT"
    if query == "license":
        return "ROUTE_PP313_WORK_ITEM_REVIEW" if case["performs_regulated_external_work"] else "REJECT_MERE_USE_NOT_LICENSE_TRIGGER"
    if query == "product_status":
        return "PASS_SUBJECT_TO_FUNCTIONAL_AND_OPERATIONAL_FIT" if case["current_certificate_record"] else "BLOCK_CURRENT_PRODUCT_STATUS_UNPROVEN"
    if query == "conformity":
        if case["claimed_universal"]:
            return "REJECT_UNIVERSAL_CONFORMITY_CLAIM"
        return "APPLY_CONFORMITY_REQUIREMENT" if case["needed_for_current_threat"] else "NO_CURRENT_THREAT_CONFORMITY_TRIGGER"
    if query == "journal_semantics":
        return "REJECT_MESSAGE_AND_SECURITY_JOURNALS_DISTINCT" if case["claimed_same_journal"] else "KEEP_DISTINCT_CONTROL_OBJECTS"
    if query == "class_rows":
        return len(model["level_threat_class_matrix"])
    if query == "atomic_rule_count":
        return len(model["atomic_rules"])
    if query == "numeric_deadline_count":
        return len(model["numeric_deadlines"])
    if query == "evidence_node_count":
        return len(model["evidence_model"])
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    pp1119 = yaml.safe_load(PP1119.read_text(encoding="utf-8"))
    article19 = yaml.safe_load(ARTICLE19.read_text(encoding="utf-8"))
    fstec21 = yaml.safe_load(FSTEC21.read_text(encoding="utf-8"))
    library = yaml.safe_load(LIBRARY.read_text(encoding="utf-8"))
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    document = yaml.safe_load(DOCUMENT.read_text(encoding="utf-8"))
    plan = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    legacy = yaml.safe_load(LEGACY.read_text(encoding="utf-8"))

    assert len(model["atomic_rules"]) == len({row["id"] for row in model["atomic_rules"]}) == 64
    assert len(model["numeric_deadlines"]) == 2
    assert {(row["maximum_interval"], row["unit"]) for row in model["numeric_deadlines"]} == {(6, "MONTHS"), (1, "MONTH")}
    assert len(model["temporal_model"]) == 5
    assert model["class_order_weak_to_strong"] == CLASS_ORDER
    assert len(model["level_threat_class_matrix"]) == 8
    assert len(model["invalid_level_threat_combinations_under_pp1119"]) == 4
    assert len(model["evidence_model"]) == len({row["id"] for row in model["evidence_model"]}) == 25
    assert len(model["conflict_and_definition_checks"]) == 24
    assert model["source"]["minjust_registration_number"] == "33620"
    assert model["source"]["official_print_publication"]["effective_from"] == "2014-09-28"
    assert model["source"]["current_legal_text"]["amendments_listed"] == []
    assert model["verification_boundary"]["immutable_official_current_bytes"] == "PENDING"
    assert model["red_team"]["critical_gap_created"] is False and model["red_team"]["high_gap_created"] is False

    assert pp1119["record_set_id"] == "ISPDN-PP1119-PROTECTION-LEVEL-VERIFIED"
    assert article19["verification_boundary"]["fsb_order_378_current_applicability"] == "REGRESSION_PROTECTED"
    assert fstec21["id"] == "RU-FSTEC21-ISPDN-CONTROLS-ATOMIC-V1"
    source = next(row for row in library["sources"] if row["id"] == "PDN-SRC-0012")
    assert source["state"] == "REGRESSION_PROTECTED"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]
    direction = next(row for row in matrix["directions"] if row["id"] == "PDN-DIR-20")
    assert direction["maturity"] == "REGRESSION_PROTECTED"
    assert document["status"]["atomization"] == "REGRESSION_PROTECTED"
    assert plan["status"] == "COMPLETED_REGRESSION_PROTECTED"
    reg = next(row for row in registry["entries"] if row["id"] == "FSB-378-2014")
    assert reg["source_status"] == "VERIFIED_SOURCE"
    historical = next(row for row in legacy["records"] if row["id"] == "FSB-378-2014")
    assert historical["status"] == "ACTIVE_ORIGINAL_EDITION"
    assert len(fixtures["cases"]) == 96

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 64 atomic rules; 2 numeric deadlines; 5 class profiles; 8 class routes; 25 evidence nodes; 24 conflict checks; 96 cases")


if __name__ == "__main__":
    main()
