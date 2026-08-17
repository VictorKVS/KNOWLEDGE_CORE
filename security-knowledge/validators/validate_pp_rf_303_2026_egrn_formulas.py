from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    ROOT
    / "security-knowledge"
    / "classification"
    / "pp-rf-303-2026-egrn-formula-regression-v1.json"
)


def d(value: str) -> Decimal:
    return Decimal(value)


def text(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def indicator_2(case: dict) -> dict:
    service = d(case["T_service"])
    downtime = d(case["T_downtime"])
    if service < 0 or downtime < 0:
        return {"status": "INVALID_NEGATIVE_INPUT"}
    if service == 0:
        return {"status": "INVALID_ZERO_DENOMINATOR"}
    value = ((service - downtime) / service) * Decimal(100)
    status = "NEGATIVE_RESULT_REQUIRES_REVIEW" if value < 0 else "CALCULATED"
    return {"status": status, "value": text(value)}


def indicator_4(case: dict) -> dict:
    annual = d(case["annual_state_service_revenue"])
    days = d(case["max_disruption_days"])
    budget = d(case["average_federal_budget_revenue"])
    if annual < 0 or days < 0 or budget < 0:
        return {"status": "INVALID_NEGATIVE_INPUT"}
    if budget == 0:
        return {"status": "INVALID_ZERO_DENOMINATOR"}
    delta = (annual / Decimal(365)) * days
    value = (delta / budget) * Decimal(100)
    return {
        "status": "CALCULATED",
        "delta_budget_revenue": text(delta),
        "value": text(value),
    }


def evaluate(case: dict) -> dict:
    if case["formula"] == "indicator_2":
        return indicator_2(case)
    if case["formula"] == "indicator_4":
        return indicator_4(case)
    return {"status": "UNKNOWN_FORMULA"}


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected!r} actual={actual!r}")
        return 1
    print(f"PASS {len(data['cases'])} primary-backed PP 303 formula cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
