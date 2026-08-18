from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-547-2025-deadline-matrix-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-547-2025-deadline-regression-v1.json"

EXPECTED_SOURCE_SHA256 = "43c702947771d36afe5a28e0487fc75d315f713466d66aea71538eee8c49946d"
EXPECTED_RULE_COUNT = 16


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    if matrix.get("status") != "PRIMARY_VERIFIED":
        fail("matrix is not PRIMARY_VERIFIED", failures)
    if matrix.get("source", {}).get("sha256") != EXPECTED_SOURCE_SHA256:
        fail("source SHA-256 drift", failures)
    if matrix.get("extraction", {}).get("ocr_is_evidence") is not False:
        fail("OCR must not be treated as evidence", failures)
    if fixture.get("matrix_id") != matrix.get("matrix_id"):
        fail("fixture matrix_id mismatch", failures)

    rules = matrix.get("rules", [])
    if len(rules) != EXPECTED_RULE_COUNT:
        fail(f"expected {EXPECTED_RULE_COUNT} timed rules, got {len(rules)}", failures)
    by_id = {rule.get("id"): rule for rule in rules}
    if len(by_id) != len(rules) or None in by_id:
        fail("rule IDs must be present and unique", failures)

    allowed_units = {"HOUR", "CALENDAR_DAY", "OCCURRENCE_PER_YEAR"}
    for rule in rules:
        rule_id = rule.get("id", "<missing>")
        for required in ("clause", "pages", "actor", "action", "recipient", "condition", "deadline", "confidence"):
            if not rule.get(required):
                fail(f"{rule_id}: missing {required}", failures)
        deadline = rule.get("deadline", {})
        if deadline.get("unit") not in allowed_units:
            fail(f"{rule_id}: forbidden or unknown deadline unit", failures)
        if not isinstance(deadline.get("value"), int) or deadline.get("value", 0) <= 0:
            fail(f"{rule_id}: deadline must be a positive integer", failures)
        if rule.get("confidence") != "PRIMARY_VERIFIED":
            fail(f"{rule_id}: confidence drift", failures)
        pages = rule.get("pages", [])
        if not pages or any(not isinstance(page, int) or page < 1 or page > 12 for page in pages):
            fail(f"{rule_id}: invalid primary PDF page", failures)

    for case in fixture.get("positive_cases", []):
        rule_id = case["rule_id"]
        rule = by_id.get(rule_id)
        if rule is None:
            fail(f"fixture references missing rule {rule_id}", failures)
            continue
        observed = rule["deadline"]
        for field in ("value", "unit", "trigger"):
            if observed.get(field) != case.get(field):
                fail(f"{rule_id}: fixture mismatch for {field}", failures)

    significant_incident = by_id.get("FSB547-C3-SIGNIFICANT-KII-INCIDENT-NCCCI-3H", {})
    attack = by_id.get("FSB547-C3-COMPUTER-ATTACK-NCCCI-24H", {})
    if significant_incident.get("deadline", {}).get("value") != 3:
        fail("significant KII incident must remain 3 hours", failures)
    if attack.get("deadline", {}).get("value") != 24 or attack.get("deadline", {}).get("trigger") != "DETECTION_OF_COMPUTER_ATTACK":
        fail("computer attack must remain a distinct 24-hour route", failures)

    cbr_rules = [r for r in rules if r.get("recipient") == "BANK_OF_RUSSIA" and r.get("clause", "").startswith("4")]
    nccci_initial = [r for r in rules if r.get("recipient") == "NCCCI" and r.get("clause", "").startswith("3")]
    if len(cbr_rules) != 3 or len(nccci_initial) != 4:
        fail("parallel initial NCCCI/Bank of Russia routing set drift", failures)

    untimed = {item.get("id"): item for item in matrix.get("untimed_obligations", [])}
    clause16_id = "FSB547-C16-RF-RESOURCE-RESPONSE-DESIGN-NCCCI-NO-EXPLICIT-DEADLINE"
    clause16 = untimed.get(clause16_id, {})
    if clause16.get("deadline_status") != "NO_EXPLICIT_NUMERICAL_DEADLINE_IN_ORDER_547":
        fail("clause 16 must remain explicitly untimed", failures)
    if "deadline" in clause16:
        fail("clause 16 must not acquire a synthetic numeric deadline", failures)

    forbidden_units = {"BUSINESS_DAY"}
    if any(r.get("deadline", {}).get("unit") in forbidden_units for r in rules):
        fail("business-day conversion detected", failures)

    if failures:
        for message in failures:
            print(f"FAIL {message}")
        return 1
    print("PASS FSB Order 547: 16 timed rules, clause 16 untimed guard, source pages and routing regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
