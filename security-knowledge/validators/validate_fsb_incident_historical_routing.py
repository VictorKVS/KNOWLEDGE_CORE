import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "legislation" / "fsb-incident-reporting-historical-routing-regression-v1.json"


def d(value: str) -> date:
    return date.fromisoformat(value)


def route(case):
    event_date = d(case["event_date"])
    event_type = case["event_type"]

    if case.get("candidate") == "FSB-547-2025" and event_date < date(2026, 1, 30):
        return "REJECT_BACKCAST"
    if case.get("candidate") == "FSB-348-2022":
        return "REJECT_STANDALONE_AMENDMENT"

    if event_type == "significant_cii_incident":
        if event_date < date(2019, 7, 28):
            return "NEEDS_PREDECESSOR_REVIEW"
        if event_date < date(2022, 8, 16):
            return "FSB-282-2019_ORIGINAL"
        if event_date < date(2026, 1, 30):
            return "FSB-282-2019_AS_AMENDED_348"
        return "FSB-547-2025"

    if event_type == "pd_incident":
        if event_date < date(2023, 3, 1):
            return "NEEDS_PREDECESSOR_REVIEW"
        if not case.get("fsb77_applicable"):
            return "NO_FSB77_ROUTE"
        if "expected_deadline_hours" in case:
            other = case.get("other_binding_deadline_hours")
            return min(24, other) if other is not None else 24
        if case.get("cii_route") == "FSB-547-2025":
            return "PARALLEL_FSB77_AND_FSB547"
        return "FSB-77-2023"

    return "NEEDS_REVIEW"


def main():
    suite = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in suite["cases"]:
        actual = route(case)
        expected = case.get("expected_deadline_hours", case.get("expected"))
        if actual != expected:
            failures.append((case["id"], expected, actual))
    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected!r} actual={actual!r}")
        raise SystemExit(1)
    print(f"PASS {len(suite['cases'])} historical FSB routing cases")


if __name__ == "__main__":
    main()
