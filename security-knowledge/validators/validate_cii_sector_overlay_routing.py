#!/usr/bin/env python3
from pathlib import Path
import sys
import yaml

FIXTURE = Path("security-knowledge/classification/cii-sector-overlay-routing-regression-v1.yaml")

OVERLAYS = {
    "ATOMIC_ENERGY": "PP_RF_4_2026",
    "BANKING_AND_OTHER_FINANCIAL_MARKET": "PP_RF_92_2026",
    "SCIENCE": "PP_RF_246_2026",
    "STATE_REGISTRATION_OF_REAL_ESTATE_RIGHTS_AND_TRANSACTIONS": "PP_RF_303_2026",
    "ROCKET_AND_SPACE_INDUSTRY": "PP_RF_356_2026",
}


def route(facts):
    cii = facts.get("cii_subject_confirmed")
    sectors = facts.get("sectors") or []
    if cii is None:
        return {"status": "NEEDS_CII_APPLICABILITY_REVIEW", "sources": []}
    if cii is False:
        return {"status": "NOT_ROUTED_AS_CII", "sources": []}
    if not sectors:
        return {"status": "NEEDS_SECTOR_REVIEW", "sources": ["PP_RF_127_2018"]}

    matched = [OVERLAYS[s] for s in sectors if s in OVERLAYS]
    unresolved = [s for s in sectors if s not in OVERLAYS]
    sources = ["PP_RF_127_2018"] + matched
    if unresolved:
        return {"status": "NEEDS_SECTOR_REVIEW", "sources": sources}
    return {"status": "ROUTE", "sources": sources}


def main():
    doc = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in doc["fixtures"]:
        actual = route(case["facts"])
        expected = case["expected"]
        if actual != expected:
            failures.append((case["id"], expected, actual))

    if failures:
        for cid, expected, actual in failures:
            print(f"FAIL {cid}: expected={expected} actual={actual}")
        return 1
    print(f"PASS: {len(doc['fixtures'])} CII sector-overlay routing fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
