#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

AUDIT=Path("security-knowledge/audits/order573-order630-primary-pdf-retrieval-audit-2026-08-30.yaml")
FIXTURES=Path("security-knowledge/audits/order573-order630-primary-pdf-retrieval-regression-2026-08-30.json")

def evaluate(case,audit):
    q=case["query"]
    if q=="temporal":
        d=date.fromisoformat(case["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_EFFECTIVE"
        if d>=date(2030,3,1): return "EXPIRED_ROUTE"
        return "PASS_CURRENT_ROUTE"
    if q=="legal-identity":
        return "PASS" if audit["legal_identity"][case["field"]]==case["value"] else "BLOCK"
    if q=="route":
        item=next((x for x in audit["retrieval_attempts"] if x["id"]==case["route_id"]),None)
        return "PASS" if item and item[case["field"]]==case["value"] else "BLOCK"
    if q=="discovery":
        return "PASS" if audit["official_discovery"][case["route"]][case["field"]]==case["value"] else "BLOCK"
    if q=="artifact-boundary":
        if case["field"] in audit["transport_receipt"]:
            actual=audit["transport_receipt"][case["field"]]
        else:
            actual=audit["artifact_acceptance"][case["field"]]
        return "PASS" if actual==case["value"] else "BLOCK"
    if q=="finding-count":
        return "PASS" if audit["carryover_findings"][case["field"]]==case["value"] else "BLOCK"
    if q=="blocked-claim":
        return "BLOCKED" if case["value"] in audit["blocked_claims"] else "MISSING"
    raise AssertionError(q)

def main():
    audit=yaml.safe_load(AUDIT.read_text(encoding="utf-8"))
    cases=json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]
    rules=audit["atomic_rules"]; evidence=audit["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573PDF-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18
    assert [r for node in evidence for r in node["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573PDF-T{i:03d}" for i in range(1,65)]
    assert len(audit["retrieval_attempts"])==6
    assert audit["artifact_acceptance"]["accepted_primary_artifacts"]==0
    assert audit["carryover_findings"]=={"critical":0,"high":0,"medium":7,"pending":7,"adjudicated_this_run":0,"automatic_repairs":0}
    failures=[]
    for case in cases:
        actual=evaluate(case,audit)
        if actual!=case["expected"]: failures.append((case["id"],case["expected"],actual))
    if failures:
        print(*failures,sep="\n"); raise SystemExit(1)
    print("PASS: Order 630 primary-PDF retrieval; 64 rules, 18 evidence nodes, 64 cases; 2 official routes, 6 attempts, 0 accepted artifacts; 7 Medium/PENDING unchanged")

if __name__=="__main__": main()
