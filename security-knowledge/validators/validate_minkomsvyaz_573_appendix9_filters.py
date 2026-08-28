#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-filters-asn-core-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-filters-asn-core-regression-v1.json")
def field(xs,n):return next((x for x in xs if x["name"]==n),None)
def evaluate(c,m):
 q=c["query"]
 if q=="temporal":
  d=date.fromisoformat(c["date"])
  if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
  return "PASS_CURRENT_FILTERS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
 if q=="export":return "PASS" if c["name"] in m["module"]["exports"] else "BLOCK_NOT_EXPORTED"
 if q=="message_variant":
  x=field(m["filter_message"]["variants"],c["name"])
  return "BLOCK_UNKNOWN_VARIANT" if x is None else ("PASS" if x["tag"]==c["tag"] else "BLOCK_TAG_MISMATCH")
 if q=="field":
  x=field(m["types"][c["type"]]["fields"],c["name"])
  if x is None:return "BLOCK_UNKNOWN_FIELD"
  if x.get("optional"):return "PASS_OPTIONAL"
  if x.get("default") is True:return "PASS_REQUIRED_DEFAULT_TRUE"
  if x.get("default")=="NOT_SPECIFIED":return "PASS_REQUIRED_NO_DEFAULT"
  return "PASS_REQUIRED"
 if q=="boundary":
  lo,hi={"response-error":(1,256),"vlan":(0,4096),"mac":(6,6),"sni":(1,128),"http-content-type":(1,64)}[c["target"]]
  return "PASS" if lo<=c["value"]<=hi else ("BLOCK_RANGE" if c["target"]=="vlan" else "BLOCK_SIZE")
 if q=="single_criteria":
  x=field(m["types"]["FilterSingleCriteria"]["variants"],c["name"])
  return "BLOCK_UNKNOWN_CRITERIA" if x is None else ("PASS" if x["tag"]==c["tag"] else "BLOCK_TAG_MISMATCH")
 if q=="business_claim":return "BLOCK_NOT_SPECIFIED"
 if q=="syntax_claim":return "PENDING_PRIMARY_PDF"
 if q=="sequence_count":return "PASS_NO_COUNT_CONSTRAINT_NO_BUSINESS_INFERENCE" if c["count"]==0 else "PASS_NO_COUNT_CONSTRAINT"
 raise AssertionError(q)
def main():
 m=yaml.safe_load(MODEL.read_text());f=json.loads(FIXTURES.read_text());t=m["types"]
 assert len(m["atomic_rules"])==len({x["id"] for x in m["atomic_rules"]})==64
 assert [x["id"] for x in m["atomic_rules"]]==[f"MK573F-R{i:03d}" for i in range(1,65)]
 assert len(m["evidence_model"])==len({x["id"] for x in m["evidence_model"]})==18
 assert m["module"]["exports"]==["filterMessage"] and m["module"]["imports"]["NetworkIdentifiers"]==["IPAddress","IPPort","IPMask","PortRange"]
 assert [(x["name"],x["tag"]) for x in m["filter_message"]["variants"]]==[("create-filter-request",0),("create-filter-response",1),("drop-filter-request",2),("drop-filter-response",3),("get-filters-request",4),("get-filters-response",5)]
 assert len(t["CreateFilterRequest"]["fields"])==4 and field(t["CreateFilterRequest"]["fields"],"allow-only-mode")["default"] is True
 assert field(t["FilterResponse"]["fields"],"allow-only-mode")["default"]=="NOT_SPECIFIED"
 assert t["GetFiltersRequest"]["kind"]=="NULL" and t["GetFiltersResponse"]["count_constraint"]==t["FilterParameters"]["count_constraint"]=="NOT_SPECIFIED"
 assert [(x["name"],x["tag"]) for x in t["FilterParameter"]["variants"]]==[("single-criteria",0),("pair-criteria",1)]
 s=t["FilterSingleCriteria"]["variants"];assert len(s)==13 and [x["tag"] for x in s]==list(range(13))
 assert field(s,"vlan")["maximum"]==4096 and field(s,"mac")["size_exact"]==6 and field(s,"protocol-group")["comment_is_closed_enum"] is False
 assert t["FilterlD"]["literal_identifier_note"]=="LOWERCASE_L" and m["identifier_anomaly"]["referenced_but_not_defined_in_rendered_slice"]=="FilterID"
 assert len(f["cases"])==len({x["id"] for x in f["cases"]})==64
 bad=[(c["id"],c["expected"],evaluate(c,m)) for c in f["cases"] if evaluate(c,m)!=c["expected"]]
 if bad:print(*bad,sep="\n");raise SystemExit(1)
 assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
 print("PASS: Order 573 Filters.asn; 64 rules, 18 evidence nodes, 6 messages, 13 criteria, 64 cases")
if __name__=="__main__":main()

