from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "governance" / "fsb547-incident-notification-workflow-regression-v1.yaml"


def evaluate(x):
    if x.get("recovery_check", False):
        if not x.get("entity_is_covered_part4_article9_organ_or_org", False):
            return "NEEDS_APPLICABILITY_FACTS"
        if not x.get("recovery_completion_timestamp_present", False):
            return "NEEDS_RECOVERY_COMPLETION_TIMESTAMP"
        if x.get("hours_to_recovery_notification", 0) > 24:
            return "RECOVERY_NOTIFICATION_OVERDUE"
        if not x.get("recovery_delivery_evidence_present", False):
            return "NEEDS_RECOVERY_NOTIFICATION_EVIDENCE"
        return "PASS_RECOVERY"

    if x.get("post_response_check", False):
        if x.get("entity_is_cii_subject", False) and x.get("affected_resource_kind") == "CII_OBJECT" and x.get("cii_object_is_significant") is True:
            limit = 48
        elif x.get("entity_is_covered_part4_article9_organ_or_org", False) and x.get("affected_resource_kind") == "RUSSIAN_INFORMATION_RESOURCE":
            limit = 24
        else:
            return "NEEDS_APPLICABILITY_FACTS"
        if not x.get("response_completion_timestamp_present", False):
            return "NEEDS_RESPONSE_COMPLETION_TIMESTAMP"
        if x.get("hours_to_results_notification", 0) > limit:
            return "RESULTS_NOTIFICATION_OVERDUE"
        if not x.get("results_delivery_evidence_present", False):
            return "NEEDS_RESULTS_NOTIFICATION_EVIDENCE"
        return "PASS_RESULTS"

    applicable = x.get("entity_is_cii_subject", False) or x.get("entity_is_covered_part4_article9_organ_or_org", False)
    if not applicable:
        return "NEEDS_APPLICABILITY_FACTS"
    if not x.get("event_kind"):
        return "NEEDS_EVENT_KIND"
    if not x.get("detection_timestamp_present", False):
        return "NEEDS_DETECTION_TIMESTAMP"

    event_kind = x.get("event_kind")
    resource_kind = x.get("affected_resource_kind")

    if event_kind == "COMPUTER_INCIDENT":
        if x.get("entity_is_cii_subject", False) and resource_kind == "CII_OBJECT":
            if x.get("cii_object_is_significant") is None:
                return "NEEDS_SIGNIFICANCE_STATUS"
            limit = 3 if x.get("cii_object_is_significant") is True else 24
        elif x.get("entity_is_covered_part4_article9_organ_or_org", False) and resource_kind == "RUSSIAN_INFORMATION_RESOURCE":
            limit = 24
        else:
            return "NEEDS_ROUTING_DECISION"
    elif event_kind == "COMPUTER_ATTACK":
        if resource_kind not in ("CII_OBJECT", "RUSSIAN_INFORMATION_RESOURCE"):
            return "NEEDS_ROUTING_DECISION"
        limit = 24
    else:
        return "NEEDS_EVENT_KIND"

    if x.get("hours_to_initial_notification", 0) > limit:
        return "INITIAL_NOTIFICATION_OVERDUE"
    if not x.get("initial_delivery_evidence_present", False):
        return "NEEDS_NOTIFICATION_EVIDENCE"
    if x.get("entity_is_cii_subject", False) and x.get("financial_sector_branch", False) and resource_kind == "CII_OBJECT":
        if not x.get("bank_of_russia_delivery_evidence_present", False):
            return "NEEDS_FINANCIAL_PARALLEL_REPORTING_EVIDENCE"
    return "PASS_INITIAL"


def main():
    data = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = evaluate(case["input"])
        expected = case["expected"]
        if actual != expected:
            failures.append((case["id"], expected, actual))
    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected} actual={actual}")
        return 1
    print(f"PASS: {len(data['cases'])} FSB 547 incident-notification workflow regression cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
