#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-payments-records-b-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-payments-records-b-regression-v1.json")

def named(items,name): return next((x for x in items if x["name"]==name),None)

def evaluate(c,m):
    q=c["query"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_PAYMENT_RECORDS_B_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="summary":
        s=m["field_summary"]; return "PASS" if (s["structures"],s["fields"],s["required"],s["optional"])==(c["structures"],c["fields"],c["required"],c["optional"]) else "BLOCK_SUMMARY"
    if q=="structure":
        s=m["structures"].get(c["name"])
        if not s: return "BLOCK_STRUCTURE"
        fs=s["fields"]; return "PASS" if (len(fs),sum(not x["optional"] for x in fs),sum(x["optional"] for x in fs))==(c["count"],c["required"],c["optional"]) else "BLOCK_STRUCTURE"
    if q=="literal": return "PASS_LITERAL" if c["value"] in m["field_summary"]["literal_anomalies"] else "BLOCK_LITERAL"
    if q=="field":
        s=m["structures"].get(c["structure"]); x=named(s["fields"],c["name"]) if s else None
        if not x or x["type"]!=c["type"] or x["optional"]!=c["optional"]: return "BLOCK_FIELD"
        if "min" in c and x.get("size")!={"min":c["min"],"max":c["max"]}: return "BLOCK_FIELD"
        if "range_min" in c and x.get("range")!={"min":c["range_min"],"max":c["range_max"]}: return "BLOCK_FIELD"
        if "min" not in c and "range_min" not in c and ("size" in x or "range" in x): return "BLOCK_FIELD"
        return "PASS_OPTIONAL" if x["optional"] else "PASS_REQUIRED"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573PB-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    expected_counts={"ValidateTelephoneCardRecord":(5,5,0),"ValidateBalanceFillupRecord":(6,5,1),"ValidateBankDivisonTransferRecord":(8,8,0),"ValidateBankCardTransferRecord":(5,5,0),"ValidateBankAccountTransferRecord":(6,6,0)}
    assert set(m["structures"])==set(expected_counts)
    for name,counts in expected_counts.items():
        fs=m["structures"][name]["fields"]; assert (len(fs),sum(not x["optional"] for x in fs),sum(x["optional"] for x in fs))==counts
    all_fields=[x for s in m["structures"].values() for x in s["fields"]]
    assert len(all_fields)==30 and sum(not x["optional"] for x in all_fields)==29 and sum(x["optional"] for x in all_fields)==1
    assert named(m["structures"]["ValidateBalanceFillupRecord"]["fields"],"pay-type-id")=={"name":"pay-type-id","type":"INTEGER","range":{"min":0,"max":4294967295},"optional":False}
    assert named(m["structures"]["ValidateBalanceFillupRecord"]["fields"],"pay-parameters")=={"name":"pay-parameters","type":"UTF8String","size":{"min":1,"max":512},"optional":True}
    assert named(m["structures"]["ValidateBankDivisonTransferRecord"]["fields"],"person-recieved")["size"]=={"min":1,"max":512}
    assert named(m["structures"]["ValidateBankCardTransferRecord"]["fields"],"bank-card-id")["size"]=={"min":1,"max":12}
    assert all(named(m["structures"][n]["fields"],"amount")=={"name":"amount","type":"UTF8String","size":{"min":1,"max":64},"optional":False} for n in m["structures"])
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573PB-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 payment records B; 64 rules, 18 evidence nodes, 5 structures, 30 fields, 64 cases")

if __name__=="__main__": main()
