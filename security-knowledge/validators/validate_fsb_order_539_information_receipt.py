from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-539-2025-information-receipt-routing-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-539-2025-information-receipt-regression-v1.json"

EXPECTED_SOURCE_SHA256 = "d930504f21e10efc73f670fa7ffa1cb0594f402ec550767ec7ba99e7539a8710"


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    check(matrix.get("status") == "PRIMARY_VERIFIED", "matrix status drift")
    check(matrix.get("source", {}).get("sha256") == EXPECTED_SOURCE_SHA256, "source SHA-256 drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")
    check(fixture.get("matrix_id") == matrix.get("matrix_id"), "fixture matrix_id mismatch")

    timed = matrix.get("timed_rules", [])
    untimed = matrix.get("untimed_rules", [])
    check(len(timed) == 2, f"expected 2 channel-specific timed rules, got {len(timed)}")
    check(len(untimed) == 2, f"expected 2 explicitly untimed rules, got {len(untimed)}")
    timed_by_id = {rule.get("id"): rule for rule in timed}
    untimed_by_id = {rule.get("id"): rule for rule in untimed}
    check(len(timed_by_id) == len(timed) and None not in timed_by_id, "timed rule IDs must be unique")
    check(len(untimed_by_id) == len(untimed) and None not in untimed_by_id, "untimed rule IDs must be unique")

    for rule in timed:
        rule_id = rule.get("id", "<missing>")
        deadline = rule.get("deadline", {})
        check(rule.get("actor") == "NCCCI", f"{rule_id}: actor must be NCCCI")
        check(rule.get("recipient") == "KII_SUBJECT", f"{rule_id}: recipient must be KII_SUBJECT")
        check(deadline == {"kind": "MAXIMUM", "value": 30, "unit": "WORKING_DAY", "trigger": "RECEIPT_OF_REQUEST_BY_NCCCI"}, f"{rule_id}: deadline drift")
        check(rule.get("pages") == [4], f"{rule_id}: source page drift")
        check(rule.get("confidence") == "PRIMARY_VERIFIED", f"{rule_id}: confidence drift")

    connected = timed_by_id.get("FSB539-C2-NCCCI-REPLY-CONNECTED-30WD", {})
    disconnected = timed_by_id.get("FSB539-C2-NCCCI-REPLY-NOT-CONNECTED-30WD", {})
    check(connected.get("channel") == "NCCCI_TECHNICAL_INFRASTRUCTURE", "connected route drift")
    check(disconnected.get("channel") == "POSTAL_OR_EMAIL_TO_ADDRESS_SPECIFIED_IN_REQUEST", "fallback route drift")
    check("connected to" in connected.get("condition", ""), "connected condition missing")
    check("not connected" in disconnected.get("condition", ""), "fallback condition missing")

    for case in fixture.get("positive_cases", []):
        rule = timed_by_id.get(case.get("rule_id"))
        check(rule is not None, f"fixture references missing rule {case.get('rule_id')}")
        if rule is None:
            continue
        check(rule.get("actor") == case.get("expected_actor"), f"{rule['id']}: actor fixture mismatch")
        check(rule.get("recipient") == case.get("expected_recipient"), f"{rule['id']}: recipient fixture mismatch")
        check(rule.get("channel") == case.get("expected_channel"), f"{rule['id']}: channel fixture mismatch")
        expected = case.get("expected_deadline", {})
        observed = rule.get("deadline", {})
        check(all(observed.get(k) == v for k, v in expected.items()), f"{rule['id']}: deadline fixture mismatch")

    expected_untimed = {
        "FSB539-C1-KII-SUBJECT-OBTAIN-ATTACK-INFORMATION-NO-DEADLINE": "NO_EXPLICIT_NUMERICAL_DEADLINE_OR_FREQUENCY_IN_ORDER_539",
        "FSB539-C3-NCCCI-SEND-CONTEXT-RELEVANT-INFORMATION-NO-DEADLINE": "NO_EXPLICIT_NUMERICAL_DEADLINE_IN_ORDER_539",
    }
    for rule_id, status in expected_untimed.items():
        rule = untimed_by_id.get(rule_id, {})
        check(rule.get("deadline_status") == status, f"{rule_id}: untimed status drift")
        check("deadline" not in rule, f"{rule_id}: synthetic deadline detected")

    all_deadlines = [rule.get("deadline", {}) for rule in timed]
    check(not any(d.get("unit") == "CALENDAR_DAY" for d in all_deadlines), "calendar-day substitution detected")
    check(not any(d.get("unit") == "HOUR" and d.get("value") in {3, 24, 48} for d in all_deadlines), "Order 547 clock imported")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS FSB Order 539: two 30-working-day response routes and two no-deadline guards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
