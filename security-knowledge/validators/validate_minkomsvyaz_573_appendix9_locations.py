#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-locations-asn-core-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/legislation/RU/ministry-orders/minkomsvyaz-573-2018/appendix9-locations-asn-core-regression-v1.json")
def field(xs,n):return next((x for x in xs if x["name"]==n),None)
def evaluate(c,m):
 q=c["query"];t=m["types"]
 if q=="temporal":
  d=date.fromisoformat(c["date"])
  if d<date(2024,3,1):return "HISTORICAL_PRE_REPLACEMENT"
  return "PASS_CURRENT_LOCATIONS_VERSION" if d<date(2030,3,1) else "EXPIRED_ROUTE"
 if q=="export":return "PASS" if c["name"] in m["module"]["exports"] else "BLOCK_NOT_EXPORTED"
 if q=="location_variant":
  x=field(t["Location"]["variants"],c["name"])
  return "BLOCK_UNKNOWN_VARIANT" if x is None else ("PASS" if x["tag"]==c["tag"] else "BLOCK_TAG_MISMATCH")
 if q=="field":
  x=field(t[c["type"]]["fields"],c["name"])
  if x is None:return "BLOCK_UNKNOWN_FIELD"
  return "PASS_OPTIONAL" if x.get("optional") else "PASS_REQUIRED"
 if q=="boundary":
  lo,hi={"lac":(0,65535),"mobile-cell":(0,100000000000),"ta":(0,63),"mcc-size":(3,3),"mnc-size":(3,3),"wireless-cell-size":(1,64),"mac-size":(6,6)}[c["target"]]
  return "PASS" if lo<=c["value"]<=hi else ("BLOCK_SIZE" if "size" in c["target"] else "BLOCK_RANGE")
 if q=="projection":
  values=t["GeoLocation"]["fields"][2]["values"]
  if c["name"] not in values:return "BLOCK_NORMALIZED_ALIAS" if c["name"]=="sks85" else "BLOCK_UNKNOWN_ENUM"
  return "PASS" if values[c["name"]]==c["value"] else "BLOCK_ENUM_VALUE"
 if q=="business_claim":return "BLOCK_NOT_SPECIFIED"
 if q=="syntax_claim":return "PENDING_PRIMARY_PDF"
 if q=="alias":return "PASS" if c["name"]=="IpLocation" else "BLOCK_NORMALIZED_ALIAS"
 if q=="import":return "PASS" if c["name"] in m["module"]["imports"].get(c["module"],[]) else "BLOCK_NOT_IMPORTED"
 raise AssertionError(q)
def main():
 m=yaml.safe_load(MODEL.read_text());f=json.loads(FIXTURES.read_text());t=m["types"]
 assert len(m["atomic_rules"])==len({x["id"] for x in m["atomic_rules"]})==48
 assert [x["id"] for x in m["atomic_rules"]]==[f"MK573L-R{i:03d}" for i in range(1,49)]
 assert len(m["evidence_model"])==len({x["id"] for x in m["evidence_model"]})==16
 assert m["module"]["exports"]==["Location","GeoLocation"] and m["module"]["imports"]=={"NetworkIdentifiers":["NetworkPeerInfo"]}
 assert [(x["name"],x["tag"]) for x in t["Location"]["variants"]]==[("mobile-location",0),("wireless-location",1),("geo-location",2),("ip-location",3)]
 mob=t["MobileLocation"]["fields"];assert len(mob)==5 and sum(not x["optional"] for x in mob)==2
 assert [(x["name"],x["tag"]) for x in mob if x["optional"]]==[("ta",0),("mcc",1),("mnc",2)]
 assert (field(mob,"lac")["minimum"],field(mob,"lac")["maximum"])==(0,65535)
 assert (field(mob,"cell")["minimum"],field(mob,"cell")["maximum"])==(0,100000000000)
 assert (field(mob,"ta")["minimum"],field(mob,"ta")["maximum"])==(0,63)
 w=t["WirelessLocation"]["fields"];assert len(w)==2 and field(w,"cell")["size_max"]==64 and field(w,"mac")["size_exact"]==6
 assert field(w,"mac")["rendered_token"]=="OCTETSTRING"
 g=t["GeoLocation"]["fields"];assert len(g)==3 and all(not x["optional"] for x in g)
 assert field(g,"latitude-grade")["range_constraint"]==field(g,"longitude-grade")["range_constraint"]=="NOT_SPECIFIED"
 assert field(g,"projection-type")["values"]=={"wgs84":0,"utm":1,"sgs85":2}
 assert t["IpLocation"]["type"]=="NetworkPeerInfo"
 assert len(f["cases"])==len({x["id"] for x in f["cases"]})==64
 bad=[(c["id"],c["expected"],evaluate(c,m)) for c in f["cases"] if evaluate(c,m)!=c["expected"]]
 if bad:print(*bad,sep="\n");raise SystemExit(1)
 assert not m["verification_boundary"]["critical_gap_created"] and not m["verification_boundary"]["high_gap_created"]
 print("PASS: Order 573 Locations.asn; 48 rules, 16 evidence nodes, 4 choices, 10 fields, 64 cases")
if __name__=="__main__":main()

