#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-management-asn-core-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-management-asn-core-regression-v1.json")
def field(xs,n):return next((x for x in xs if x["name"]==n),None)
def evaluate(c,m):
 q=c["query"];t=m["types"]
 if q=="temporal":
  d=date.fromisoformat(c["date"])
  if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
  return "PASS_CURRENT_MANAGEMENT_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
 if q=="export":return "PASS" if c["name"] in m["module"]["exports"] else "BLOCK_NOT_EXPORTED"
 if q=="top_variant":xs=m["management_message"]["variants"]
 elif q=="request_variant":xs=t["ManagementRequest"]["variants"]
 elif q=="response_variant":xs=t["ManagementResponse"]["variants"]
 elif q=="choice":xs=t[c["type"]]["variants"]
 else:xs=None
 if xs is not None:
  x=field(xs,c["name"])
  return "BLOCK_UNKNOWN_VARIANT" if x is None else ("PASS" if x["tag"]==c["tag"] else "BLOCK_TAG_MISMATCH")
 if q=="field":
  x=field(t[c["type"]]["fields"],c["name"])
  return "BLOCK_UNKNOWN_FIELD" if x is None else ("PASS_OPTIONAL" if x.get("optional") else "PASS_REQUIRED")
 if q=="boundary":
  lo,hi={"module-id-size":(8,8),"parameter-name-size":(1,256),"parameter-integer":(0,999999999)}[c["target"]]
  return "PASS" if lo<=c["value"]<=hi else ("BLOCK_SIZE" if "size" in c["target"] else "BLOCK_RANGE")
 if q=="business_claim":return "BLOCK_NOT_SPECIFIED"
 raise AssertionError(q)
def main():
 m=yaml.safe_load(MODEL.read_text());f=json.loads(FIXTURES.read_text());t=m["types"]
 assert len(m["atomic_rules"])==len({x["id"] for x in m["atomic_rules"]})==64
 assert [x["id"] for x in m["atomic_rules"]]==[f"MK573MG-R{i:03d}" for i in range(1,65)]
 assert len(m["evidence_model"])==len({x["id"] for x in m["evidence_model"]})==18
 assert m["module"]["exports"]==["managementMessage"] and m["module"]["imports"]=={"Classification":["TAGGED","sorm-message-management"]}
 assert [(x["name"],x["tag"]) for x in m["management_message"]["variants"]]==[("request",0),("response",1)]
 assert [x["tag"] for x in t["ManagementRequest"]["variants"]]==list(range(5))
 assert [x["tag"] for x in t["ManagementResponse"]["variants"]]==list(range(5))
 assert t["GetStructureRequest"]["kind"]==t["GetModuleTypesRequest"]["kind"]=="NULL"
 assert t["RequestedHardwareModules"]["rendered_token"]==t["RequestedSoftwareModules"]["rendered_token"]=="SEQUENCEOFModuleId"
 assert t["ConfiguratedModule"]["syntax_status"]=="PENDING_PRIMARY_PDF_MISSING_ASSIGNMENT_OPERATOR"
 assert t["ModuleId"]["size_exact"]==8
 p=t["ParameterValue"]["variants"];assert [(x["name"],x["tag"]) for x in p]==[("string",0),("integer",1),("boolean",2)]
 assert field(p,"integer")["maximum"]==999999999
 sw=t["SormSoftwareModule"]["fields"];assert len(sw)==7 and sum(not x["optional"] for x in sw)==6
 assert field(sw,"block-name")["maximum"]==1024 and field(sw,"module-name")["size_max"]==512 and field(sw,"module-type")["maximum"]==512
 hw=t["SormHardwareModule"]["fields"];assert len(hw)==4 and all(not x["optional"] for x in hw)
 assert t["SubmodulesList"]["recursion_depth_constraint"]=="NOT_SPECIFIED"
 mt=t["ModuleType"]["fields"];assert field(mt,"module-type")["maximum"]==512 and field(mt,"type-description")["size_max"]==128
 assert len(f["cases"])==len({x["id"] for x in f["cases"]})==64
 bad=[(c["id"],c["expected"],evaluate(c,m)) for c in f["cases"] if evaluate(c,m)!=c["expected"]]
 if bad:print(*bad,sep="\n");raise SystemExit(1)
 assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
 print("PASS: Order 573 Management.asn; 64 rules, 18 evidence nodes, 5 requests, 5 responses, 64 cases")
if __name__=="__main__":main()

