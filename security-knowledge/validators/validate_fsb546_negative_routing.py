#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys
import yaml

FIXTURES = Path("security-knowledge/roles-deadlines-responsibility/fsb-546-negative-routing-regression-v1.yaml")


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def evaluate(case: dict) -> dict:
    data = case.get("input", {})
    if data.get("entity_scope") != "CII_SUBJECT":
        return {"status": "APPLICABILITY_NOT_PROVEN"}

    trigger = data.get("trigger")
    received_at = data.get("received_at")

    if trigger == "UNSOLICITED_FOREIGN_OR_INTERNATIONAL_INFO_RECEIVED_ABOUT_OWN_CII_OBJECT":
        if not received_at:
            return {"status": "FAIL_CLOSED_MISSING_TRIGGER_TIME"}
        dt = parse_dt(received_at)
        return {
            "status": "ROUTED",
            "route": "ROUTE-06-UNSOLICITED-FOREIGN-INFO-OWN-OBJECT",
            "deadline": (dt + timedelta(hours=24)).isoformat(),
        }

    if trigger == "INFO_RECEIVED_ABOUT_OTHER_CII_SUBJECT_OBJECT":
        if not received_at:
            return {"status": "FAIL_CLOSED_MISSING_TRIGGER_TIME"}
        dt = parse_dt(received_at)
        return {
            "status": "ROUTED",
            "route": "ROUTE-07-INFO-ABOUT-OTHER-CII-SUBJECT",
            "deadline": (dt + timedelta(hours=12)).isoformat(),
        }

    return {"status": "FAIL_CLOSED_UNSUPPORTED_TRIGGER"}


def main() -> int:
    with FIXTURES.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    errors = []
    cases = doc.get("negative_fixtures", [])
    for case in cases:
        result = evaluate(case)
        cid = case["id"]
        expected_status = case.get("expected_status", "ROUTED")
        if result.get("status") != expected_status:
            errors.append(f"{cid}: status {result.get('status')} != {expected_status}")
        if case.get("expected_route") and result.get("route") != case["expected_route"]:
            errors.append(f"{cid}: route {result.get('route')} != {case['expected_route']}")
        if case.get("expected_deadline") and result.get("deadline") != case["expected_deadline"]:
            errors.append(f"{cid}: deadline {result.get('deadline')} != {case['expected_deadline']}")
        for forbidden in case.get("forbidden_routes", []):
            if result.get("route") == forbidden:
                errors.append(f"{cid}: forbidden route selected: {forbidden}")

    if errors:
        print(f"FAIL: {len(errors)} error(s) across {len(cases)} FSB 546 negative routing fixture(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS: {len(cases)} FSB 546 negative routing fixture(s) executed deterministically")
    return 0


if __name__ == "__main__":
    sys.exit(main())
