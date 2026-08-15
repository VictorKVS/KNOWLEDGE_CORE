#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "evidence" / "pdn-repeat-offense-turnover-regression-v1.json"


def parse_date(value):
    return date.fromisoformat(value) if value else None


def add_one_year(d):
    try:
        return d.replace(year=d.year + 1)
    except ValueError:
        return d.replace(year=d.year + 1, day=28)


def prior_status(inp):
    target = inp.get("target_part")
    prior = inp.get("prior_part")
    relevant = {15: {12, 13, 14, 15, 16, 17, 18}, 18: {12, 13, 14, 15, 16, 17, 18}}
    if target not in relevant or prior not in relevant[target]:
        return "NEEDS_RELEVANCE_REVIEW"
    force = parse_date(inp.get("entered_into_force_date"))
    if not force:
        return "NEEDS_DECISION_FORCE_DATE"
    completed = parse_date(inp.get("execution_completed_date"))
    if not completed:
        return "NEEDS_EXECUTION_EVIDENCE"
    new_offense = parse_date(inp.get("new_offense_date"))
    end = add_one_year(completed)
    if new_offense and force <= new_offense <= end:
        return "VERIFIED_ACTIVE_SUBJECTED_PERIOD"
    return "VERIFIED_OUTSIDE_SUBJECTED_PERIOD"


def turnover_status(inp):
    if not inp.get("source_document_id"):
        return "NEEDS_ACCOUNTING_SOURCE"
    if inp.get("source_currency") != "RUB":
        return "NEEDS_CURRENCY_REVIEW"
    entity = inp.get("entity_type")
    base = inp.get("base_type")
    if entity == "CREDIT_INSTITUTION":
        if base != "CREDIT_INSTITUTION_OWN_FUNDS_CAPITAL_AT_VIOLATION_DATE":
            return "NEEDS_ENTITY_TYPE_REVIEW"
        return "VERIFIED"
    if entity != "LEGAL_ENTITY":
        return "NEEDS_ENTITY_TYPE_REVIEW"
    if inp.get("has_prior_year_sales"):
        if base != "PRIOR_CALENDAR_YEAR_REVENUE_FROM_ALL_GOODS_WORKS_SERVICES":
            return "NEEDS_PERIOD_REVIEW"
    else:
        if base != "CURRENT_YEAR_PRE_DETECTION_PERIOD_REVENUE_IF_NO_PRIOR_YEAR_SALES":
            return "NEEDS_PERIOD_REVIEW"
    return "VERIFIED"


def fine_range(inp):
    if inp.get("repeat_status") != "VERIFIED_ACTIVE_SUBJECTED_PERIOD":
        return {"state": "BLOCKED_REPEAT_EVIDENCE"}
    if inp.get("turnover_status") != "VERIFIED":
        return {"state": "BLOCKED_TURNOVER_EVIDENCE"}
    part = inp.get("target_part")
    base = inp.get("base_amount")
    if part == 15:
        floor = 20_000_000
    elif part == 18:
        floor = 25_000_000
    else:
        return {"state": "UNSUPPORTED_PART"}
    minimum = max(int(base * 0.01), floor)
    maximum = min(int(base * 0.03), 500_000_000)
    if maximum < minimum:
        maximum = minimum
    return {"state": "STATUTORY_RANGE_ONLY", "min_rub": minimum, "max_rub": maximum}


def evaluate(case):
    kind = case["type"]
    if kind == "prior_admin_punishment":
        return prior_status(case["input"])
    if kind == "turnover_base":
        return turnover_status(case["input"])
    if kind == "fine_range":
        return fine_range(case["input"])
    raise ValueError(f"unknown fixture type: {kind}")


def main():
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for cid, expected, actual in failures:
            print(f"FAIL {cid}: expected={expected!r}, actual={actual!r}")
        raise SystemExit(1)
    print(f"PASS: {len(data['cases'])} repeat-offense/turnover evidence fixtures")


if __name__ == "__main__":
    main()
