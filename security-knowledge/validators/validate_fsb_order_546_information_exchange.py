from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-546-2025-information-exchange-routing-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-546-2025-information-exchange-regression-v1.json"
EXPECTED_SHA256 = "30d1128e75ab07cab4b60d050d5ff14f41fc75e09c0dbb086929a5e92f0c0b81"


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    check(matrix.get("status") == "PRIMARY_VERIFIED", "matrix status drift")
    check(matrix.get("source", {}).get("sha256") == EXPECTED_SHA256, "source SHA-256 drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")
    check(fixture.get("matrix_id") == matrix.get("matrix_id"), "fixture matrix_id mismatch")

    numeric = matrix.get("numeric_rules", [])
    qualitative = matrix.get("qualitative_temporal_rules", [])
    routing = matrix.get("routing_rules", [])
    check(len(numeric) == 5, f"expected 5 numeric rules, got {len(numeric)}")
    check(len(qualitative) == 4, f"expected 4 qualitative temporal rules, got {len(qualitative)}")
    check(len(routing) == 6, f"expected 6 routing rules, got {len(routing)}")

    all_rules = numeric + qualitative + routing
    by_id = {rule.get("id"): rule for rule in all_rules}
    check(len(by_id) == len(all_rules) and None not in by_id, "rule IDs must be present and unique")

    expected_deadlines = {
        "FSB546-C15-NCCCI-REVIEW-FOREIGN-EXCHANGE-REQUEST-24H": (24, "RECEIPT_OF_FOREIGN_EXCHANGE_REQUEST_BY_NCCCI"),
        "FSB546-C16-NCCCI-NOTIFY-REFUSAL-24H": (24, "NCCCI_REFUSAL_DECISION"),
        "FSB546-C18-NCCCI-FORWARD-FOREIGN-RESPONSE-48H": (48, "RECEIPT_OF_FOREIGN_RESPONSE_BY_NCCCI"),
        "FSB546-C20-KII-SUBJECT-FORWARD-UNSOLICITED-FOREIGN-INFO-24H": (24, "RECEIPT_OF_UNSOLICITED_FOREIGN_INFORMATION_BY_KII_SUBJECT"),
        "FSB546-C21-KII-SUBJECT-FORWARD-OTHER-SUBJECT-INFO-12H": (12, "RECEIPT_OF_OTHER_SUBJECT_OBJECT_INFORMATION_BY_KII_SUBJECT"),
    }
    for rule_id, (value, trigger) in expected_deadlines.items():
        rule = by_id.get(rule_id, {})
        deadline = rule.get("deadline", {})
        check(deadline == {"kind": "MAXIMUM", "value": value, "unit": "HOUR", "trigger": trigger}, f"{rule_id}: deadline drift")
        check(rule.get("confidence") == "PRIMARY_VERIFIED", f"{rule_id}: confidence drift")

    for case in fixture.get("positive_cases", []):
        rule = by_id.get(case.get("rule_id"), {})
        deadline = rule.get("deadline", {})
        check(deadline.get("value") == case.get("value"), f"{case.get('rule_id')}: fixture value mismatch")
        check(deadline.get("unit") == case.get("unit"), f"{case.get('rule_id')}: fixture unit mismatch")
        check(deadline.get("trigger") == case.get("trigger"), f"{case.get('rule_id')}: fixture trigger mismatch")

    for rule in qualitative:
        rule_id = rule.get("id", "<missing>")
        check("deadline" not in rule, f"{rule_id}: arbitrary numeric deadline detected")
        check(rule.get("numeric_deadline_status"), f"{rule_id}: missing no-number guard")

    direct = by_id.get("FSB546-C19-TREATY-DIRECT-EXCHANGE-PARALLEL-NCCCI", {})
    via_nccci = by_id.get("FSB546-C11-C13-FOREIGN-EXCHANGE-VIA-NCCCI", {})
    simultaneous = by_id.get("FSB546-C8-SIMULTANEOUS-PARALLEL-NCCCI-NOTIFICATION", {})
    state_secret = by_id.get("FSB546-C7-STATE-SECRET-GATE", {})
    check("treaty" in direct.get("condition", "").lower(), "direct exchange treaty gate missing")
    check("no treaty" in via_nccci.get("condition", "").lower(), "NCCCI default foreign route guard missing")
    check(simultaneous.get("temporal_constraint") == "SIMULTANEOUS_WITH_EXCHANGE_TRANSMISSION", "parallel NCCCI simultaneity drift")
    check(state_secret.get("condition") == "Transferred information constitutes a state secret.", "state-secret gate drift")

    review = by_id.get("FSB546-C15-NCCCI-REVIEW-FOREIGN-EXCHANGE-REQUEST-24H", {})
    check(review.get("action") == "REVIEW_ATTACK_OR_INCIDENT_INFORMATION_IN_FOREIGN_EXCHANGE_REQUEST", "review converted to automatic approval")

    for rule in all_rules:
        pages = rule.get("pages", [])
        check(pages and all(isinstance(page, int) and 3 <= page <= 8 for page in pages), f"{rule.get('id')}: invalid primary page")
        check(rule.get("confidence") == "PRIMARY_VERIFIED", f"{rule.get('id')}: confidence drift")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS FSB Order 546: 5 numeric, 4 qualitative-temporal and 6 routing rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
