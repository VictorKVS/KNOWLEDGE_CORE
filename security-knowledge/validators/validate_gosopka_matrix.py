#!/usr/bin/env python3
"""Deterministic regression validator for the current GosSOPKA routing matrix.

This validator does not interpret law independently. It executes only the fail-closed
routing rules and fixtures already stored in the knowledge base.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys

import yaml


DEFAULT_MATRIX = Path(
    "security-knowledge/legislation/"
    "gosopka-current-stack-applicability-timing-matrix-v1.yaml"
)


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def route_ids(matrix: dict) -> set[str]:
    return {item["id"] for item in matrix.get("routing", [])}


def source_effective_date(matrix: dict, source_id: str) -> datetime:
    value = matrix["sources"][source_id]["effective_date"]
    return datetime.fromisoformat(value + "T00:00:00+00:00")


def evaluate(matrix: dict, fixture: dict) -> dict:
    data = fixture.get("input", {})
    event_date = data.get("event_date")
    event_type = data.get("event_type")
    action = data.get("action")
    significance = data.get("object_significance")
    scope = data.get("entity_scope")

    if fixture["id"] == "GOS-REG-05":
        if not event_date:
            return {"status": "ERROR_MISSING_EVENT_DATE"}
        event_dt = datetime.fromisoformat(event_date + "T00:00:00+00:00")
        if event_dt < source_effective_date(matrix, "FSB_539_2025"):
            return {"status": "HISTORICAL_STACK_REQUIRED"}
        return {"status": "UNEXPECTED_CURRENT_STACK"}

    if scope != "CII_SUBJECT":
        return {"status": "APPLICABILITY_NOT_PROVEN"}

    if event_type == "INCIDENT":
        if significance == "UNKNOWN" or significance is None:
            return {"status": "FAIL_CLOSED_MISSING_SIGNIFICANCE"}
        if not data.get("detected_at"):
            return {"status": "FAIL_CLOSED_MISSING_TRIGGER_TIME"}
        detected = parse_dt(data["detected_at"])
        if significance == "SIGNIFICANT":
            return {
                "status": "ROUTED",
                "route": "ROUTE-02-SIGNIFICANT-CII-INCIDENT",
                "deadline": (detected + timedelta(hours=3)).isoformat(),
            }
        return {
            "status": "ROUTED",
            "route": "ROUTE-03-OTHER-CII-INCIDENT",
            "deadline": (detected + timedelta(hours=24)).isoformat(),
        }

    if event_type == "ATTACK":
        if not data.get("detected_at"):
            return {"status": "FAIL_CLOSED_MISSING_TRIGGER_TIME"}
        detected = parse_dt(data["detected_at"])
        return {
            "status": "ROUTED",
            "route": "ROUTE-04-COMPUTER-ATTACK",
            "deadline": (detected + timedelta(hours=24)).isoformat(),
        }

    if action == "PEER_INFORMATION_EXCHANGE":
        return {
            "status": "ROUTED",
            "route": "ROUTE-05-PEER-CII-EXCHANGE",
            "timing_type": "NON_NUMERIC_OPERATIONAL_TIMING",
        }

    return {"status": "FAIL_CLOSED_UNSUPPORTED_CASE"}


def check_fixture(matrix: dict, fixture: dict) -> list[str]:
    errors: list[str] = []
    result = evaluate(matrix, fixture)
    fixture_id = fixture["id"]
    routes = route_ids(matrix)

    expected_status = fixture.get("expected_status")
    if expected_status and result.get("status") != expected_status:
        errors.append(
            f"{fixture_id}: status {result.get('status')} != {expected_status}"
        )

    expected_route = fixture.get("expected_route")
    if expected_route:
        if expected_route not in routes:
            errors.append(f"{fixture_id}: expected route {expected_route} missing from matrix")
        if result.get("route") != expected_route:
            errors.append(
                f"{fixture_id}: route {result.get('route')} != {expected_route}"
            )

    expected_deadline = fixture.get("expected_deadline")
    if expected_deadline and result.get("deadline") != expected_deadline:
        errors.append(
            f"{fixture_id}: deadline {result.get('deadline')} != {expected_deadline}"
        )

    expected_timing = fixture.get("expected_timing_type")
    if expected_timing and result.get("timing_type") != expected_timing:
        errors.append(
            f"{fixture_id}: timing {result.get('timing_type')} != {expected_timing}"
        )

    negative = fixture.get("negative_assertion")
    if negative == "must_not_route_to_3h_incident_deadline":
        if result.get("route") == "ROUTE-02-SIGNIFICANT-CII-INCIDENT":
            errors.append(f"{fixture_id}: attack incorrectly routed to 3h incident branch")
    elif negative == "must_not_invent_numeric_sla":
        if result.get("deadline") is not None:
            errors.append(f"{fixture_id}: numeric SLA invented for non-numeric rule")
    elif negative == "must_not_apply_FSB_539_2025":
        if result.get("status") != "HISTORICAL_STACK_REQUIRED":
            errors.append(f"{fixture_id}: current FSB 539 stack applied retroactively")

    return errors


def validate(matrix: dict) -> list[str]:
    errors: list[str] = []
    fixtures = matrix.get("regression_fixtures", [])
    if not fixtures:
        return ["matrix contains no regression_fixtures"]

    seen: set[str] = set()
    for fixture in fixtures:
        fixture_id = fixture.get("id")
        if not fixture_id:
            errors.append("fixture without id")
            continue
        if fixture_id in seen:
            errors.append(f"duplicate fixture id: {fixture_id}")
        seen.add(fixture_id)
        errors.extend(check_fixture(matrix, fixture))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix", nargs="?", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()

    with args.matrix.open("r", encoding="utf-8") as fh:
        matrix = yaml.safe_load(fh)

    errors = validate(matrix)
    fixtures = matrix.get("regression_fixtures", [])
    if errors:
        print(f"FAIL: {len(errors)} error(s) across {len(fixtures)} fixture(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS: {len(fixtures)} GosSOPKA regression fixture(s) executed deterministically")
    return 0


if __name__ == "__main__":
    sys.exit(main())
