#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

AUDIT=Path("security-knowledge/audits/order573-appendix9-cross-module-red-team-2026-08-30.yaml")
FIXTURES=Path("security-knowledge/audits/order573-appendix9-cross-module-red-team-regression-2026-08-30.json")

def evaluate(case, audit):
    query=case["query"]
    if query=="temporal":
        checked=date.fromisoformat(case["date"])
        if checked < date(2024,3,1):
            return "HISTORICAL_PRE_REPLACEMENT"
        if checked >= date(2030,3,1):
            return "EXPIRED_ROUTE"
        return "PASS_CURRENT_APPENDIX9_ROUTE"
    if query in {"corpus","serialization"}:
        return "PASS" if audit[query][case["field"]]==case["value"] else "BLOCK"
    if query=="anomalies":
        return "PASS" if audit["rendered_anomaly_occurrence_guards"][case["field"]]==case["value"] else "BLOCK"
    if query=="finding":
        item=next((x for x in audit["findings"] if x["id"]==case["finding_id"]),None)
        return "PASS" if item and item[case["field"]]==case["value"] else "BLOCK"
    if query=="severity-count":
        return "PASS" if audit["finding_summary"][case["field"]]==case["value"] else "BLOCK"
    if query=="mutual-pair":
        pairs={(x["a"],x["b"]) for x in audit["direct_mutual_import_pairs"]}
        return "PASS" if (case["a"],case["b"]) in pairs else "BLOCK"
    if query=="mutual-count":
        return "PASS" if audit["direct_mutual_import_pair_count"]==case["value"] else "BLOCK"
    if query=="blocked-claim":
        return "BLOCKED" if case["value"] in audit["blocked_claims"] else "MISSING"
    raise AssertionError(query)

def main():
    audit=yaml.safe_load(AUDIT.read_text(encoding="utf-8"))
    cases=json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]
    rules=audit["atomic_rules"]
    evidence=audit["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573XMOD-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==18
    assert [rule for node in evidence for rule in node["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573XMOD-T{i:03d}" for i in range(1,65)]
    assert audit["corpus"]=={"visible_numbered_headings":31,"mapped_headings":31,"unmapped_headings":0,"atomic_packages":57,"expected_package_paths_verified":57}
    assert audit["finding_summary"]=={"critical":0,"high":0,"medium":7,"pending":7,"automatic_repairs":0}
    assert audit["rendered_anomaly_occurrence_guards"]["total_package_local_occurrences"]==61
    assert audit["direct_mutual_import_pair_count"]==9
    failures=[]
    for case in cases:
        actual=evaluate(case,audit)
        if actual!=case["expected"]:
            failures.append((case["id"],case["expected"],actual))
    if failures:
        print(*failures,sep="\n")
        raise SystemExit(1)
    print("PASS: Order 573 Appendix 9 cross-module red-team; 64 rules, 18 evidence nodes, 64 cases; 7 Medium/PENDING, 0 Critical/High; 9 mutual pairs recorded as risk only")

if __name__=="__main__":
    main()
