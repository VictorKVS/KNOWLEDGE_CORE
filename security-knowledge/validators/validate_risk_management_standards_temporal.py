#!/usr/bin/env python3
from datetime import date
from pathlib import Path
import sys
import yaml

FIXTURE = Path(__file__).parents[1] / "risk-methods" / "risk-management-standards-temporal-regression-v1.yaml"


def route(case):
    q = case["query_type"]
    d_raw = case.get("event_date")
    if d_raw is None:
        return ("NEEDS_TEMPORAL_REVIEW", None)
    d = date.fromisoformat(d_raw)

    if q == "TERMINOLOGY_SOURCE":
        if d < date(2025, 3, 1):
            return ("HISTORICAL_REVIEW", "ГОСТ Р 51897-2021")
        return ("ROUTE_CURRENT", "ГОСТ Р ИСО 31073-2024")
    if q == "RISK_PRINCIPLES":
        return ("ROUTE_CURRENT", "ГОСТ Р ИСО 31000-2019") if d >= date(2020, 3, 1) else ("NOT_YET_EFFECTIVE", "ГОСТ Р ИСО 31000-2019")
    if q == "RISK_ASSESSMENT_TECHNIQUES":
        return ("ROUTE_CURRENT", "ГОСТ Р 58771-2019") if d >= date(2020, 3, 1) else ("NOT_YET_EFFECTIVE", "ГОСТ Р 58771-2019")
    if q == "LEGAL_RISK_GUIDANCE":
        return ("ROUTE_CURRENT", "ГОСТ Р ИСО 31022-2025") if d >= date(2026, 3, 1) else ("NOT_YET_EFFECTIVE", "ГОСТ Р ИСО 31022-2025")
    if q == "MANDATORY_FOR_ORG":
        if not case.get("binding_edge_present", False):
            return ("NEEDS_APPLICABILITY_EVIDENCE", None)
        return ("BINDING_EDGE_REQUIRED_FOR_DECISION", None)
    return ("UNKNOWN_QUERY_TYPE", None)


def main():
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        status, std = route(case)
        if status != case["expected_status"] or ("expected_standard" in case and std != case["expected_standard"]):
            failures.append((case["id"], status, std))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        return 1
    print(f"PASS {len(data['cases'])} risk-management standard lifecycle cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
