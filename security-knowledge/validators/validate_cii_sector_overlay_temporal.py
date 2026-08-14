#!/usr/bin/env python3
from datetime import date
from pathlib import Path
import sys
import yaml

REGISTRY = Path("security-knowledge/classification/cii-sector-overlay-effective-dates-2026-verified.yaml")
FIXTURE = Path("security-knowledge/classification/cii-sector-overlay-temporal-regression-v1.yaml")
BASE = "PP_RF_127_2018"


def load_overlays():
    doc = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return {
        row["sector"]: {
            "source_id": row["source_id"],
            "effective_from": date.fromisoformat(row["effective_from"]),
        }
        for row in doc["records"]
    }


def route(facts, overlays):
    sector = facts.get("sector")
    raw_date = facts.get("event_date")
    if sector not in overlays:
        return {"status": "NEEDS_SECTOR_REVIEW", "sources": [BASE]}
    if not raw_date:
        return {"status": "NEEDS_TEMPORAL_REVIEW", "sources": [BASE]}

    event_date = date.fromisoformat(raw_date)
    overlay = overlays[sector]
    if event_date < overlay["effective_from"]:
        return {"status": "BASE_ONLY_WITH_HISTORICAL_REVIEW", "sources": [BASE]}
    return {"status": "ROUTE", "sources": [BASE, overlay["source_id"]]}


def main():
    overlays = load_overlays()
    doc = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in doc["fixtures"]:
        actual = route(case["facts"], overlays)
        expected = case["expected"]
        if actual != expected:
            failures.append((case["id"], expected, actual))

    if failures:
        for cid, expected, actual in failures:
            print(f"FAIL {cid}: expected={expected} actual={actual}")
        return 1
    print(f"PASS: {len(doc['fixtures'])} CII sector-overlay temporal fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
