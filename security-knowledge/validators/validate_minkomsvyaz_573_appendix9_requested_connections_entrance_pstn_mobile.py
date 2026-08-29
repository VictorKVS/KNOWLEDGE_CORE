#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-connections-entrance-pstn-mobile-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-requested-connections-entrance-pstn-mobile-regression-v1.json")
def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REQUESTED_CONNECTIONS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="object-count": return "PASS" if len(m["objects"])==c["count"] else "BLOCK"
    if q=="object":
        x=m["objects"].get(c["name"]); return "PASS" if x and x["oid"]==c["oid"] and len(x["branches"])==c["count"] else "BLOCK"
    if q=="branch":
        x=next((x for x in m["objects"][c["object"]]["branches"] if x["name"]==c["branch"]["name"]),None)
        return "PASS" if x==c["branch"] else "BLOCK"
    if q=="identifier":
        x=m["identifier_open_types"].get(c["name"])
        return "PASS" if x and x["variants"]==c["variants"] and x["visible_import_status"]==c["status"] and len(x["fields"])==2 else "BLOCK"
    if q=="literal": return "PENDING_PRIMARY_PDF" if c["value"] in m["rendered_anomalies"] else "BLOCK"
    if q=="missing-import":
        x=m["identifier_open_types"]["RequestedConnectionEntranceIdentifier"]
        return "PENDING_PRIMARY_PDF" if c["value"] in x["variants"] and x["visible_import_status"].startswith("MISSING") else "BLOCK"
    if q=="tag-order": return "PASS" if [x["tag"] for x in m["objects"][c["object"]]["branches"]]==c["tags"] else "BLOCK"
    raise AssertionError(q)
def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=m["atomic_rules"]; ev=m["evidence_model"]; cases=f["cases"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573RCPM-R{i:03d}" for i in range(1,65)]
    assert len(ev)==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert len(cases)==len({x["id"] for x in cases})==64
    assert [x["id"] for x in cases]==[f"MK573RCPM-T{i:03d}" for i in range(1,65)]
    assert sum(len(x["branches"]) for x in m["objects"].values())==48
    assert [len(m["objects"][n]["branches"]) for n in ("requestedConnectionEntrance","requestedConnectionPstn","requestedConnectionMobile")]==[13,16,19]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 RequestedConnections Entrance/PSTN/Mobile; 64 rules, 18 evidence nodes, 48 branches, 64 cases")
if __name__=="__main__": main()
