from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-548-2025-continuous-interaction-routing-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-548-2025-continuous-interaction-regression-v1.json"
EXPECTED_SHA256 = "61b0d81c56cfa8aa76ac335d98237efd9a4768ae05c0cdf7fe83a2137ca79430"


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    check(matrix.get("status") == "PRIMARY_VERIFIED", "matrix status drift")
    check(matrix.get("source", {}).get("sha256") == EXPECTED_SHA256, "source SHA-256 drift")
    check(matrix.get("source", {}).get("effective_date") == "2026-01-30", "effective date drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")
    check(fixture.get("matrix_id") == matrix.get("matrix_id"), "fixture matrix_id mismatch")

    numeric = matrix.get("numeric_rules", [])
    routing = matrix.get("routing_rules", [])
    check(len(numeric) == 3, f"expected 3 numeric rules, got {len(numeric)}")
    check(len(routing) == 8, f"expected 8 routing rules, got {len(routing)}")

    all_rules = numeric + routing
    by_id = {rule.get("id"): rule for rule in all_rules}
    check(len(by_id) == len(all_rules) and None not in by_id, "rule IDs must be present and unique")

    expected_deadlines = {
        "FSB548-C6-NCCCI-ASSIGN-ATTACK-OR-INCIDENT-ID-24H": "RECEIPT_OF_ATTACK_AND_INCIDENT_INFORMATION_IN_PERSONAL_ACCOUNT",
        "FSB548-C9-SUBJECT-REPORT-PREVENTIVE-MEASURES-24H": "RECEIPT_OF_RELEVANT_THREAT_INFORMATION_FROM_NCCCI",
        "FSB548-C10-SUBJECT-RESPOND-TO-ADDITIONAL-INFORMATION-REQUEST-24H": "RECEIPT_OF_NCCCI_ADDITIONAL_INFORMATION_REQUEST",
    }
    for rule_id, trigger in expected_deadlines.items():
        rule = by_id.get(rule_id, {})
        check(rule.get("deadline") == {"kind": "MAXIMUM", "value": 24, "unit": "HOUR", "trigger": trigger}, f"{rule_id}: deadline drift")

    for case in fixture.get("positive_cases", []):
        deadline = by_id.get(case.get("rule_id"), {}).get("deadline", {})
        check(deadline.get("value") == case.get("value"), f"{case.get('rule_id')}: fixture value mismatch")
        check(deadline.get("unit") == case.get("unit"), f"{case.get('rule_id')}: fixture unit mismatch")
        check(deadline.get("trigger") == case.get("trigger"), f"{case.get('rule_id')}: fixture trigger mismatch")

    external = by_id.get("FSB548-C5-PRIMARY-INFORMING-DEADLINES-EXTERNAL-ORDER", {})
    check("deadline" not in external, "clause 5 external deadline was invented")
    check(external.get("numeric_deadline_status") == "NO_NUMERICAL_DEADLINE_STATED_IN_ORDER_548_CLAUSE_5", "clause 5 external-dependency guard drift")

    failover = by_id.get("FSB548-C3-RESERVE-CHANNEL-FAILOVER", {})
    check(failover.get("condition") == "Technical failure and/or absence of communication with the personal account.", "reserve-channel trigger drift")
    check(failover.get("channel") == "POSTAL_ADDRESS_OR_EMAIL_ADDRESS_RECORDED_IN_PERSONAL_ACCOUNT", "reserve-channel route drift")

    identifier = by_id.get("FSB548-C6-NCCCI-ASSIGN-ATTACK-OR-INCIDENT-ID-24H", {})
    check(identifier.get("deadline", {}).get("trigger") != "RECEIPT_THROUGH_ANY_CHANNEL", "identifier trigger widened")
    confirmation = by_id.get("FSB548-C6-IDENTIFIER-CONFIRMS-TRANSFER", {})
    check(confirmation.get("action") == "CONFIRM_TRANSFER_BY_ASSIGNING_ATTACK_AND_OR_INCIDENT_IDENTIFIER", "identifier converted to resolution confirmation")

    optional = by_id.get("FSB548-C7-SUBJECT-MAY-REQUEST-GOSSOPKA-ASSISTANCE", {})
    check(optional.get("obligation_type") == "RIGHT_NOT_DUTY", "optional assistance request converted to duty")

    request = by_id.get("FSB548-C10-SUBJECT-RESPOND-TO-ADDITIONAL-INFORMATION-REQUEST-24H", {})
    check(request.get("response_branches") == ["REQUESTED_INFORMATION", "INABILITY_NOTICE_WITH_REASON_AND_TIME_WHEN_INFORMATION_WILL_BE_PROVIDED"], "clause 10 response branches drift")

    for rule in all_rules:
        pages = rule.get("pages", [])
        check(pages and all(isinstance(page, int) and 3 <= page <= 8 for page in pages), f"{rule.get('id')}: invalid primary page")
        check(rule.get("confidence") == "PRIMARY_VERIFIED", f"{rule.get('id')}: confidence drift")

    for rule in routing:
        if rule.get("numeric_deadline_status"):
            check("deadline" not in rule, f"{rule.get('id')}: arbitrary numeric deadline detected")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS FSB Order 548: 3 numeric and 8 routing/dependency rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
