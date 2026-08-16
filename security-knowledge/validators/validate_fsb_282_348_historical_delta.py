import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "regression" / "fsb-282-348-historical-delta-regression-v1.json"


def parse_date(value):
    return date.fromisoformat(value) if value else None


def route(case):
    event_date = parse_date(case.get("date"))
    query = case.get("query")

    if event_date is None:
        return "NEEDS_EVENT_DATE"

    if event_date < date(2019, 7, 28):
        return "NEEDS_PREDECESSOR_REVIEW"

    if query == "governing_regime":
        if event_date < date(2022, 8, 16):
            return "FSB_282_ORIGINAL"
        if event_date < date(2026, 1, 30):
            return "FSB_282_PLUS_348"
        return "FSB_547_2025"

    if query == "plan_copy_to_nkcki":
        if event_date < date(2022, 8, 16):
            return "NOT_APPLICABLE_348_YET"
        if event_date < date(2026, 1, 30):
            return "APPLICABLE_7_CALENDAR_DAYS"
        return "ROUTE_TO_FSB_547_CURRENT_MODEL"

    if query == "plan_approval_actor":
        if event_date < date(2022, 8, 16):
            return "NO_EXPLICIT_348_APPROVAL_RULE"
        if event_date < date(2026, 1, 30):
            return "HEAD_OF_CII_SUBJECT_OR_IE"
        return "ROUTE_TO_FSB_547_CURRENT_MODEL"

    if query == "nkcki_role_in_plan_p8":
        if event_date < date(2022, 8, 16):
            return "ORIGINAL_JOINT_WORDING"
        if event_date < date(2026, 1, 30):
            return "METHODOLOGICAL_SUPPORT_BEFORE_APPROVAL"
        return "ROUTE_TO_FSB_547_CURRENT_MODEL"

    if query == "significant_cii_incident_deadline":
        if event_date < date(2026, 1, 30):
            return "3_HOURS_FROM_DETECTION"
        return "ROUTE_TO_FSB_547_CURRENT_MODEL"

    if query == "other_cii_incident_deadline":
        if event_date < date(2026, 1, 30):
            return "24_HOURS_FROM_DETECTION"
        return "ROUTE_TO_FSB_547_CURRENT_MODEL"

    if query == "response_results_deadline":
        if event_date < date(2026, 1, 30):
            return "48_HOURS_AFTER_COMPLETION"
        return "ROUTE_TO_FSB_547_CURRENT_MODEL"

    return "NEEDS_REVIEW"


def main():
    suite = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in suite["cases"]:
        actual = route(case)
        expected = case["expected"]
        if actual != expected:
            failures.append((case["id"], expected, actual))

    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected!r} actual={actual!r}")
        raise SystemExit(1)

    print(f"PASS {len(suite['cases'])} FSB 282/348 historical delta cases")


if __name__ == "__main__":
    main()
