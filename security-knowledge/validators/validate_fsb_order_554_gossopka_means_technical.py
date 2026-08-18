from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "security-knowledge" / "controls" / "fsb-order-554-2025-gossopka-means-technical-requirements-v1.json"
FIXTURE_PATH = ROOT / "security-knowledge" / "controls" / "fsb-order-554-2025-gossopka-means-technical-regression-v1.json"
EXPECTED_SHA256 = "818c6d2774bdccda0167f81c8c94fae2d4a2939a5a2c1290322c7783fba9e3f9"


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
    check(source.get("supersedes") == "FSB_ORDER_196_2019", "superseded order drift")
    check(matrix.get("extraction", {}).get("ocr_is_evidence") is False, "OCR must not be evidence")
    check(fixture.get("matrix_id") == matrix.get("matrix_id"), "fixture matrix_id mismatch")

    numeric = matrix.get("numeric_requirements", [])
    controls = matrix.get("capability_and_control_groups", [])
    check(len(numeric) == 4, f"expected 4 numeric requirements, got {len(numeric)}")
    check(len(controls) == 21, f"expected 21 capability/control groups, got {len(controls)}")
    all_rules = numeric + controls
    by_id = {rule.get("id"): rule for rule in all_rules}
    check(len(by_id) == len(all_rules) and None not in by_id, "rule IDs must be present and unique")

    for case in fixture.get("positive_cases", []):
        rule_id = case.get("rule_id")
        value = by_id.get(rule_id, {}).get(case.get("field"), {})
        for field in ("kind", "value", "unit", "trigger"):
            check(value.get(field) == case.get(field), f"{rule_id}: fixture mismatch for {field}")

    c11 = by_id.get("FSB554-C11-DETECTION-STORE-AGGREGATED-SECURITY-EVENTS-MIN-6CM", {})
    check(c11.get("scope") == "AGGREGATED_INFORMATION_SECURITY_EVENTS", "clause 11 scope widened")
    check(c11.get("retention", {}).get("unit") == "CALENDAR_MONTH", "clause 11 month unit drift")

    c17 = by_id.get("FSB554-C17-PREVENTION-CHECK-SOURCE-UPDATES-EVERY-24H", {})
    check(c17.get("action") == "CHECK_FOR_UPDATES_IN_CLAUSE_14_INFORMATION_SOURCES_AND_LOAD_AVAILABLE_UPDATES", "clause 17 converted to incident deadline")
    check(c17.get("frequency") == {"kind": "MAXIMUM_INTERVAL", "value": 24, "unit": "HOUR", "trigger": "ONGOING_OPERATION"}, "clause 17 frequency drift")

    telecom = by_id.get("FSB554-C23-TELECOM-PPKA-STORE-DETECTED-TRAFFIC-COPIES-MIN-6CM", {})
    other = by_id.get("FSB554-C25-PPKA-STORE-DETECTED-TRAFFIC-COPIES-MIN-7CD", {})
    check(telecom.get("component") == "TELECOMMUNICATION_NETWORK_PPKA", "telecom PPKA scope drift")
    check(telecom.get("retention", {}).get("value") == 6 and telecom.get("retention", {}).get("unit") == "CALENDAR_MONTH", "telecom PPKA retention drift")
    check(other.get("component") == "PPKA_EXCLUDING_TELECOMMUNICATION_NETWORK_PPKA", "other PPKA scope drift")
    check(other.get("retention", {}).get("value") == 7 and other.get("retention", {}).get("unit") == "CALENDAR_DAY", "other PPKA retention drift")

    for rule_id in ("FSB554-C31-ROLE_ACCESS-SESSION-ACCOUNT-AND-USER-AUDIT", "FSB554-C32-SECURITY-AND-TECHNICAL-STATE-LOGGING"):
        rule = by_id.get(rule_id, {})
        check("deadline" not in rule and "retention" not in rule and "frequency" not in rule, f"{rule_id}: synthetic number detected")
        check(rule.get("numeric_deadline_status"), f"{rule_id}: missing no-number guard")

    supply = by_id.get("FSB554-C4-RUSSIAN-LEGAL-ENTITY-SUPPLY-CHAIN", {})
    check("SOFTWARE_REGISTRY" not in supply.get("requirement", ""), "software-registry requirement invented")
    remote = by_id.get("FSB554-C5-C7-REMOTE-CONTROL-DATA-TRANSFER-AND-MONITORING-GUARDS", {})
    check(len(remote.get("authorized_personnel_boundary", [])) == 3, "authorized remote-control personnel boundary drift")

    certificate_components = {
        by_id.get("FSB554-C12-DETECTION-MEANS-FSB-CERTIFICATE", {}).get("component"),
        by_id.get("FSB554-C26-PPKA-FSB-CERTIFICATE", {}).get("component"),
        by_id.get("FSB554-C28-CRYPTOGRAPHIC-MEANS-FSB-CERTIFICATION", {}).get("component"),
    }
    check(certificate_components == {"COMPUTER_ATTACK_DETECTION_MEANS", "PPKA_EXCLUDING_TELECOMMUNICATION_NETWORK_PPKA", "CRYPTOGRAPHIC_INFORMATION_PROTECTION_MEANS"}, "certification scope drift")

    supersession = by_id.get("FSB554-ORDER-C2-SUPERSEDE-ORDER-196-2019", {})
    check(supersession.get("requirement") == "RECOGNIZE_FSB_ORDER_196_2019_AS_NO_LONGER_IN_FORCE", "Order 196 supersession drift")

    for rule in all_rules:
        pages = rule.get("pages", [])
        check(pages and all(isinstance(page, int) and 2 <= page <= 17 for page in pages), f"{rule.get('id')}: invalid primary page")
        check(rule.get("confidence") == "PRIMARY_VERIFIED", f"{rule.get('id')}: confidence drift")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS FSB Order 554: 4 numeric and 21 capability/control groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
