from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge/lifecycle/fstec-license-control-163-164-487-temporal-regression-v1.yaml"

START = date(2025, 7, 13)
AMENDMENT_START = date(2025, 12, 31)
END = date(2028, 12, 31)


def classify(order: int, query_date: str | None, amendment_state: str) -> str:
    if query_date is None:
        return "NEEDS_QUERY_DATE"
    try:
        qd = date.fromisoformat(query_date)
    except ValueError:
        return "NEEDS_QUERY_DATE"

    if order not in {163, 164, 487}:
        return "NEEDS_ORDER_REVIEW"

    if order == 487:
        return "NOT_EFFECTIVE" if qd < AMENDMENT_START else "EFFECTIVE_AMENDMENT"

    if qd < START:
        return "NOT_EFFECTIVE"
    if qd < AMENDMENT_START:
        return "CURRENT_ORIGINAL"
    if amendment_state == "UNKNOWN":
        return "NEEDS_AMENDMENT_REVIEW"
    if amendment_state != "VERIFIED":
        return "NEEDS_AMENDMENT_REVIEW"
    if qd <= END:
        return "CURRENT_AS_AMENDED"
    return "EXPIRED_OR_NEEDS_SUCCESSOR_REVIEW"


def main() -> int:
    data = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    failures: list[str] = []
    for case in data.get("cases", []):
        actual = classify(case["order"], case.get("query_date"), case.get("amendment_487_state", "UNKNOWN"))
        expected = case["expected"]
        if actual != expected:
            failures.append(f"{case['id']}: expected={expected} actual={actual}")

    if failures:
        print("FSTEC license-control temporal regression FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"FSTEC license-control temporal regression PASS: {len(data.get('cases', []))} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
