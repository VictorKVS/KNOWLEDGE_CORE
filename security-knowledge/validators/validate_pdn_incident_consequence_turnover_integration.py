#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "security-knowledge/legal-consequences/pdn-incident-consequence-router-v2-regression-v1.json"

ALLOWED = {
    "PREVIOUS_CALENDAR_YEAR_REVENUE",
    "CURRENT_YEAR_PARTIAL_REVENUE_WHEN_NO_PREVIOUS_YEAR_SALES",
    "CREDIT_INSTITUTION_CAPITAL",
}


def route(case):
    part = case["part"]
    if part not in (15, 18):
        return {"state": "USE_NON_TURNOVER_ADMINISTRATIVE_ROUTE"}
    if case.get("criminal_gated") and case.get("criminal_gate") != "RESOLVED":
        return {"state": "NEEDS_CRIMINAL_SIGNS_REVIEW"}
    if not case.get("prior"):
        return {"state": "NEEDS_PRIOR_PUNISHMENT_EVIDENCE"}
    if case.get("repeat") != "PROVEN":
        return {"state": "NEEDS_REPEATABILITY_PERIOD_REVIEW"}
    if case.get("base_type") is None or case.get("base") is None:
        return {"state": "NEEDS_TURNOVER_BASE"}
    if case.get("base_type") not in ALLOWED:
        return {"state": "INVALID_TURNOVER_BASE_TYPE"}

    base = int(case["base"])
    floor = 20_000_000 if part == 15 else 25_000_000
    ceiling = 500_000_000
    ordinary_min = min(ceiling, max(floor, base // 100))
    ordinary_max = min(ceiling, (base * 3) // 100)
    if ordinary_max < ordinary_min:
        ordinary_max = ordinary_min

    mitigated = None
    if case.get("mitigation"):
        if case.get("aggravating") == "UNKNOWN":
            return {"state": "NEEDS_AGGRAVATING_CIRCUMSTANCE_REVIEW"}
        if case.get("missing_condition") or case.get("evidence_after_decision"):
            return {"state": "MITIGATION_NOT_PROVEN"}
        mitigated = max(15_000_000, min(50_000_000, ordinary_min // 10))

    return {"ordinary_min": ordinary_min, "ordinary_max": ordinary_max, "mitigated": mitigated}


def main():
    suite = json.loads(FIX.read_text(encoding="utf-8"))
    failed = []
    for case in suite["cases"]:
        got = route(case)
        if "expected_state" in case:
            ok = got.get("state") == case["expected_state"]
        else:
            ok = got == case["expected"]
        if not ok:
            failed.append((case["id"], case.get("expected_state", case.get("expected")), got))
    if failed:
        for item in failed:
            print("FAIL", item)
        raise SystemExit(1)
    print(f"PASS {len(suite['cases'])} PDn turnover-integration regression cases")


if __name__ == "__main__":
    main()
