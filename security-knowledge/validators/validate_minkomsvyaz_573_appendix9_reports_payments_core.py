#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml

MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-payments-core-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-reports-payments-core-regression-v1.json")

def named(items,name): return next((x for x in items if x["name"]==name),None)

def evaluate(c,m):
    q=c["query"]; module=m["module"]
    if q=="temporal":
        d=date.fromisoformat(c["date"])
        if d<date(2024,3,1): return "HISTORICAL_PRE_REPLACEMENT"
        return "PASS_CURRENT_REPORTS_PAYMENTS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
    if q=="module": return "PASS" if module["name"]==c["name"] and module["tagging"]==c["tagging"] else "BLOCK_MODULE"
    if q=="export": return "PASS" if c["name"] in module["exports"] else "BLOCK_EXPORT"
    if q=="import": return "PASS" if any(c["name"] in x["names"] and x["from"]==c["from"] for x in module["imports"]) else "BLOCK_IMPORT"
    if q=="report":
        r=m["report"]; return "PASS" if (r["name"],r["kind"],len(r["fields"]))==(c["name"],c["kind"],c["field_count"]) else "BLOCK_REPORT"
    if q=="field":
        x=named(m["report"]["fields"],c["name"])
        return "PASS_REQUIRED" if x and not x["optional"] and (x["type"],x["selector"])==(c["type"],c["selector"]) else "BLOCK_FIELD"
    if q=="registry":
        r=m["registry"]; return "PASS" if (r["name"],r["class"],r["variant_count"])==(c["name"],c["class"],c["count"]) else "BLOCK_REGISTRY"
    if q=="variant":
        x=named(m["registry"]["variants"],c["name"])
        return "PASS" if x and (x["oid"],x["record_type"])==(c["oid"],c["record"]) else "BLOCK_VARIANT"
    if q=="variant-kind":
        x=named(m["registry"]["variants"],c["name"]); return "PASS" if x and x["data_kind"]==c["kind"] else "BLOCK_VARIANT_KIND"
    if q=="semantic": return "NOT_SPECIFIED"
    raise AssertionError(q)

def main():
    m=yaml.safe_load(MODEL.read_text(encoding="utf-8")); f=json.loads(FIXTURES.read_text(encoding="utf-8")); rules=m["atomic_rules"]; ev=m["evidence_model"]
    assert len(rules)==len({x["id"] for x in rules})==64 and [x["id"] for x in rules]==[f"MK573PC-R{i:03d}" for i in range(1,65)]
    assert len(ev)==len({x["id"] for x in ev})==18 and [r for n in ev for r in n["proves"]]==[x["id"] for x in rules]
    assert m["module"]["name"]=="ReportsPayments" and m["module"]["tagging"]=="IMPLICIT TAGS" and m["module"]["exports"]==["PaymentsReport"]
    assert sum(len(x["names"]) for x in m["module"]["imports"])==16 and len(m["module"]["imports"][0]["names"])==11
    assert m["report"]=={"name":"PaymentsReport","kind":"SEQUENCE","fields":[{"name":"id","type":"TAGGED.&id","object_set":"ReportedPaymentsVariants","selector":None,"optional":False},{"name":"data","type":"TAGGED.&Data","object_set":"ReportedPaymentsVariants","selector":"@id","optional":False}]}
    variants=m["registry"]["variants"]
    assert m["registry"]["name"]=="ReportedPaymentsVariants" and m["registry"]["class"]=="TAGGED" and m["registry"]["variant_count"]==len(variants)==10
    assert [(x["name"],x["oid"],x["record_type"]) for x in variants]==[
      ("bankTransactionReport","sorm-report-payment-bank-transaction","BankTransactionRecord"),("expressCardReport","sorm-report-payment-express-pays","ExpressPaysRecord"),
      ("publicTerminalReport","sorm-report-payment-terminal-pays","PublicTerminalRecord"),("serviceCenterReport","sorm-report-payment-service-center","ServiceCenterRecord"),
      ("crossAccountReport","sorm-report-payment-cross-account","CrossAccountRecord"),("telephoneCardReport","sorm-report-payment-telephone-card","ValidateTelephoneCardRecord"),
      ("balanceFillupReport","sorm-report-payment-balance-fillups","ValidateBalanceFillupRecord"),("bankDivisionTransferReport","sorm-report-payment-bank-division-transfer","ValidateBankDivisonTransferRecord"),
      ("bankCardTransferReport","sorm-report-payment-bank-card-transfer","ValidateBankCardTransferRecord"),("bankAccountTransferReport","sorm-report-payment-bank-account-transfer","ValidateBankAccountTransferRecord")]
    assert all(x["data_kind"]=="SEQUENCE OF" for x in variants)
    cases=f["cases"]; assert len(cases)==len({x["id"] for x in cases})==64 and [x["id"] for x in cases]==[f"MK573PC-T{i:03d}" for i in range(1,65)]
    failures=[(c["id"],c["expected"],evaluate(c,m)) for c in cases if evaluate(c,m)!=c["expected"]]
    if failures: print(*failures,sep="\n"); raise SystemExit(1)
    assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
    print("PASS: Order 573 ReportsPayments core; 64 rules, 18 evidence nodes, 2 report fields, 10 OID/data bindings, 64 cases")

if __name__=="__main__": main()
