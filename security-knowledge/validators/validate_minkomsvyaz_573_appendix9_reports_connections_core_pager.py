#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-core-pager-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-connections-core-pager-regression-v1.json")

def named(items,name): return next((item for item in items if item["name"]==name),None)

def evaluate(case,model):
    q=case["query"]; core=model["core"]; pager=model["pager_record"]
    if q=="temporal":
        d=date.fromisoformat(case["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_CONNECTIONS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="export": return "PASS" if case["name"] in model["module"]["exports"] else "BLOCK_NOT_EXPORTED"
    if q=="alias": return "PASS" if core.get(case["name"],{}).get("target")==case["target"] else "BLOCK_ALIAS"
    if q=="core-field":
        item=named(core["CallsRecords"]["fields"],case["name"])
        if not item:return "BLOCK_UNKNOWN_FIELD"
        return "PASS_OPTIONAL" if item["optional"] else "PASS_REQUIRED"
    if q=="core-field-count":
        fields=core["CallsRecords"]["fields"]
        return "PASS" if len(fields)==case["count"] and sum(not x["optional"] for x in fields)==case["required"] else "BLOCK_FIELD_CONTRACT"
    if q=="core-binding":
        item=named(core["CallsRecords"]["fields"],case["name"])
        ok=item and item["object_set"]==case["object_set"] and ("selector" not in case or item.get("selector")==case["selector"])
        return "PASS" if ok else "BLOCK_BINDING"
    if q=="variant": return "PASS" if case["name"] in core["reported_calls_variants"] else "BLOCK_UNKNOWN_VARIANT"
    if q=="variant-count": return "PASS" if len(core["reported_calls_variants"])==case["count"] else "BLOCK_COUNT"
    if q=="classification-oid-count": return "PASS" if core["imported_connection_oid_count"]==case["count"] else "BLOCK_COUNT"
    if q=="semantic": return "NOT_SPECIFIED"
    if q=="syntax": return "PENDING_PRIMARY_PDF"
    if q=="pager-oid": return "PASS" if pager["oid"]==case["value"] else "BLOCK_OID"
    if q=="pager-data": return "PASS" if pager["data_kind"]==case["kind"] and pager["element_type"]==case["element_type"] else "BLOCK_DATA_BINDING"
    if q=="pager-field-count": return "PASS" if len(pager["fields"])==case["count"] and sum(not x["optional"] for x in pager["fields"])==case["required"] else "BLOCK_FIELD_CONTRACT"
    if q=="pager-field":
        item=named(pager["fields"],case["name"])
        if not item or item["type"]!=case["type"]:return "BLOCK_FIELD"
        return "PASS_OPTIONAL" if item["optional"] else "PASS_REQUIRED"
    if q=="pager-boundary":
        item=named(pager["fields"],case["name"])
        return "PASS" if item["value_min"]<=case["value"]<=item["value_max"] else "BLOCK_RANGE"
    if q=="deep-status":
        b=model["verification_boundary"]
        return "PASS_SCOPE_BOUNDARY" if (b["deep_variants_completed"],b["deep_variants_pending"])==(case["completed"],case["pending"]) else "BLOCK_SCOPE"
    raise AssertionError(q)

def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rules=model["atomic_rules"]; evidence=model["evidence_model"]; core=model["core"]; pager=model["pager_record"]
    assert len(rules)==len({x["id"] for x in rules})==64
    assert [x["id"] for x in rules]==[f"MK573RCG-R{i:03d}" for i in range(1,65)]
    assert len(evidence)==len({x["id"] for x in evidence})==18
    assert [r for node in evidence for r in node["proves"]]==[x["id"] for x in rules]
    assert model["module"]["exports"]==["ConnectionsReport","CallsRecords"]
    assert core["ConnectionsReport"]=={"kind":"ALIAS","target":"CallsRecords"}
    assert [(x["name"],x["type"],x.get("selector")) for x in core["CallsRecords"]["fields"]]==[("id","TAGGED.&id",None),("data","TAGGED.&Data","@id")]
    expected=["pagerRecord","pstnRecord","mobileRecord","dataAAARecord","dataEmailRecord","dataImRecord","dataFileTransferRecord","dataTermAccessRecord","dataRawFlowsRecord","dataResourceRecord","dataVoipRecord","dataAddressTranslationRecord","dataEntranceRecord","smsRecord"]
    assert core["reported_calls_variants"]==expected and core["variant_count"]==14 and core["imported_connection_oid_count"]==15
    assert core["ipdr_header_registry_binding"]=="NOT_INFERRED_FROM_VARIANT_LIST"
    assert model["module"]["imports"]["NetworkIdentifiers"][3]=="Data VoipNumber"
    assert pager["oid"]=="sorm-report-connection-pager" and pager["data_kind"]=="SEQUENCE OF" and pager["count_constraint"] is None
    assert [(x["name"],x["type"]) for x in pager["fields"]]==[("telco-id","TelcoID"),("call-type-id","INTEGER"),("connection-time","DateAndTime"),("info","ReportedIdentifier"),("in-bytes-count","INTEGER"),("term-cause","INTEGER")]
    assert all(not x["optional"] for x in pager["fields"])
    assert [(named(pager["fields"],n)["value_min"],named(pager["fields"],n)["value_max"]) for n in ["call-type-id","in-bytes-count","term-cause"]]==[(0,4294967295),(0,1024),(0,16384)]
    cases=fixtures["cases"]
    assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573RCG-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,model)) for c in cases if evaluate(c,model)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not model["verification_boundary"]["critical_gap_created"] and not model["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsConnections core and pager; 64 rules, 18 evidence nodes, 14 variants, 6 pager fields, 64 cases")

if __name__=="__main__": main()
