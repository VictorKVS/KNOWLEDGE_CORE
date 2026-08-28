#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-network-identifiers-core-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-network-identifiers-core-regression-v1.json")
def field(xs,n):return next((x for x in xs if x["name"]==n),None)
def evaluate(c,m):
 q=c["query"];t=m["types"]
 if q=="temporal":
  d=date.fromisoformat(c["date"])
  if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
  return "PASS_CURRENT_NETWORK_IDENTIFIERS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
 if q=="export":
  if c["name"] not in m["module"]["exports"]:return "BLOCK_NOT_EXPORTED"
  return "PASS_PENDING_DEEP_SLICE" if c["name"] in m["coverage"]["pending_exports"] else "PASS"
 if q=="choice":
  x=field(t[c["type"]]["variants"],c["name"])
  return "BLOCK_UNKNOWN_VARIANT" if x is None else ("PASS" if x["tag"]==c["tag"] else "BLOCK_TAG_MISMATCH")
 if q=="field":
  x=field(t[c["type"]]["fields"],c["name"])
  return "BLOCK_UNKNOWN_FIELD" if x is None else ("PASS_OPTIONAL" if x.get("optional") else "PASS_REQUIRED")
 if q=="boundary":
  lo,hi={"gsm-size":(1,32),"mac-size":(6,6),"vpi-size":(1,1),"vci-size":(2,2),"ipv4-size":(4,4),"ipv6-size":(16,16),"port-size":(2,2)}[c["target"]]
  return "PASS" if lo<=c["value"]<=hi else "BLOCK_SIZE"
 if q=="enum":
  vals=t[c["type"]]["values"]
  return "PASS" if vals.get(c["name"])==c["value"] else "BLOCK_UNKNOWN_ENUM"
 raise AssertionError(q)
def main():
 m=yaml.safe_load(MODEL.read_text());f=json.loads(FIXTURES.read_text());t=m["types"]
 assert len(m["atomic_rules"])==len({x["id"] for x in m["atomic_rules"]})==64
 assert [x["id"] for x in m["atomic_rules"]]==[f"MK573NI-R{i:03d}" for i in range(1,65)]
 assert len(m["evidence_model"])==len({x["id"] for x in m["evidence_model"]})==18
 assert len(m["module"]["exports"])==13 and len(m["coverage"]["atomized_exports"])==8 and len(m["coverage"]["pending_exports"])==5
 assert [(x["name"],x["tag"]) for x in t["Bunch"]["variants"]]==[("gsm",0),("cdma-umts",1)]
 assert [(x["name"],x["tag"]) for x in t["DataNetworkEquipment"]["variants"]]==[("mac",0),("atm",1)]
 assert t["DataNetworkATM"]["rendered_declaration"]=="DataNet work ATM"
 assert len(t["NetworkType"]["values"])==11 and list(t["NetworkType"]["values"].values())==list(range(11))
 assert [x["tag"] for x in t["IPAddress"]["variants"]]==[0,1,2]
 assert t["IPV4Address"]["size_exact"]==t["IPV4Mask"]["size_exact"]==4
 assert t["IPV6Address"]["size_exact"]==t["IPV6Mask"]["size_exact"]==16
 assert t["IPPort"]["size_exact"]==2 and t["IPPort"]["endianness"]=="NOT_SPECIFIED"
 assert t["IPAddressRange"]["ordering_constraint"]=="NOT_SPECIFIED" and t["PortRange"]["ordering_constraint"]=="NOT_SPECIFIED"
 assert t["IPAddressMask"]["consistency_constraint"]=="NOT_SPECIFIED"
 assert field(t["NetworkPeerInfo"]["fields"],"ip-port")["optional"] is True
 assert len(f["cases"])==len({x["id"] for x in f["cases"]})==64
 bad=[(c["id"],c["expected"],evaluate(c,m)) for c in f["cases"] if evaluate(c,m)!=c["expected"]]
 if bad:print(*bad,sep="\n");raise SystemExit(1)
 assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
 print("PASS: Order 573 NetworkIdentifiers core; 64 rules, 18 evidence nodes, 13 exports, 8 deep exports, 64 cases")
if __name__=="__main__":main()

