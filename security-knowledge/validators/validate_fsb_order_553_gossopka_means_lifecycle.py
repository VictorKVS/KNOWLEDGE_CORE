from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-553-2025-gossopka-means-lifecycle-matrix-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "roles" / "fsb-order-553-2025-gossopka-means-lifecycle-regression-v1.json"
EXPECTED_SHA256 = "3d825579897e4f06021c8cee9e3ff49e323f2ae833cb7658145ec9ddc54eb7ba"


def main() -> int:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    source = matrix.get("source", {})
    check(matrix.get("status") == "PRIMARY_VERIFIED", "matrix status drift")
    check(source.get("sha256") == EXPECTED_SHA256, "source SHA-256 drift")
    check(source.get("effective_date") == "2026-01-10", "effective date drift")
    check(source.get("effective_date_confidence") == "DERIVED_FROM_PRIMARY_AND_GENERAL_RULE", "derived effective-date confidence drift")
    check(source.get("supersedes") == "FSB_ORDER_281_2019", "superseded order drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")
    check(fixture.get("matrix_id") == matrix.get("matrix_id"), "fixture matrix_id mismatch")

    timed = matrix.get("timed_rules", [])
    lifecycle = matrix.get("routing_and_lifecycle_rules", [])
    check(len(timed) == 14, f"expected 14 timed rules, got {len(timed)}")
    check(len(lifecycle) == 13, f"expected 13 routing/lifecycle rules, got {len(lifecycle)}")
    all_rules = timed + lifecycle
    by_id = {rule.get("id"): rule for rule in all_rules}
    check(len(by_id) == len(all_rules) and None not in by_id, "rule IDs must be present and unique")

    allowed_units = {"CALENDAR_DAY", "CALENDAR_MONTH"}
    allowed_kinds = {"MAXIMUM", "MINIMUM_LEAD_TIME"}
    for rule in timed:
        rule_id = rule.get("id", "<missing>")
        deadline = rule.get("deadline", {})
        check(deadline.get("unit") in allowed_units, f"{rule_id}: forbidden deadline unit")
        check(deadline.get("kind") in allowed_kinds, f"{rule_id}: forbidden deadline kind")
        check(isinstance(deadline.get("value"), int) and deadline.get("value", 0) > 0, f"{rule_id}: deadline value invalid")
        check(deadline.get("trigger"), f"{rule_id}: missing trigger")
        check(rule.get("confidence") == "PRIMARY_VERIFIED", f"{rule_id}: confidence drift")

    for case in fixture.get("positive_cases", []):
        rule_id = case.get("rule_id")
        deadline = by_id.get(rule_id, {}).get("deadline", {})
        for field in ("value", "unit", "kind", "trigger"):
            check(deadline.get(field) == case.get(field), f"{rule_id}: fixture mismatch for {field}")

    check(all(rule.get("deadline", {}).get("unit") != "BUSINESS_DAY" for rule in timed), "business-day conversion detected")

    c5_nccci = by_id.get("FSB553-C5-SUBJECT-INFORM-NCCCI-USED-GOSSOPKA-MEANS-15CD", {})
    c5_cbr = by_id.get("FSB553-C5-FINANCIAL-SUBJECT-ALSO-INFORM-CBR-15CD", {})
    check(c5_nccci.get("recipient") == "NCCCI" and c5_cbr.get("recipient") == "BANK_OF_RUSSIA", "clause 5 parallel routing drift")

    c15 = by_id.get("FSB553-C15-FSB-DETERMINE-PPKA-LOCATIONS-OR-REQUEST-MORE-45CD", {})
    check(c15.get("response_branches") == ["APPROVED_REGULATION_WITH_PPKA_LOCATIONS", "REQUEST_ADDITIONAL_INFORMATION_FOR_LOCATION_DETERMINATION"], "clause 15 branches drift")

    c16_cap = by_id.get("FSB553-C16-PREPARATION-TIME-CAP-6CM", {})
    check(c16_cap.get("action") == "SET_INFORMATION_RESOURCE_PREPARATION_TIME_NO_LATER_THAN_CAP", "six-month cap changed into another obligation")
    check(c16_cap.get("deadline", {}).get("unit") == "CALENDAR_MONTH", "six-month unit drift")

    for rule_id in ("FSB553-C26-SUBJECT-NOTIFY-PLANNED-WORKS-MIN-7CD", "FSB553-C31-PPKA-DISMANTLING-BEFORE-REORGANIZATION-45CD"):
        check(by_id.get(rule_id, {}).get("deadline", {}).get("kind") == "MINIMUM_LEAD_TIME", f"{rule_id}: lead time converted to post-event maximum")

    round_clock = by_id.get("FSB553-A1-C34-FSB-PPKA-MONITORING-ROUND-THE-CLOCK", {})
    check("deadline" not in round_clock, "round-the-clock monitoring acquired numeric deadline")
    check(round_clock.get("numeric_deadline_status") == "CONTINUOUS_OPERATING_MODE_NOT_A_24_HOUR_DEADLINE", "round-the-clock guard drift")

    split = by_id.get("FSB553-A1-C22-C25-PPKA-OPERATIONS-RESPONSIBILITY-SPLIT", {}).get("responsibility_split", {})
    check("PPKA_OPERATION" in split.get("fsb", []) and "PPKA_TECHNICAL_MAINTENANCE" in split.get("fsb", []), "FSB PPKA responsibility drift")
    check("PPKA_SAFEGUARDING" in split.get("subject_or_body", []), "subject safeguarding responsibility drift")

    supersession = by_id.get("FSB553-ORDER-C2-SUPERSEDE-ORDER-281-2019", {})
    check(supersession.get("action") == "RECOGNIZE_FSB_ORDER_281_2019_AS_NO_LONGER_IN_FORCE", "Order 281 supersession drift")

    for rule in all_rules:
        pages = rule.get("pages", [])
        check(pages and all(isinstance(page, int) and 2 <= page <= 12 for page in pages), f"{rule.get('id')}: invalid primary page")
        check(rule.get("confidence") == "PRIMARY_VERIFIED", f"{rule.get('id')}: confidence drift")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS FSB Order 553: 14 timed and 13 routing/lifecycle rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
