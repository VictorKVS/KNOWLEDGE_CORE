#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/liability/koap-13-11-pdn-liability-routing-v1.yaml"
FIX=ROOT/"security-knowledge/liability/koap-13-11-pdn-liability-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/koap-13-11-pdn-liability-observation-2026-08-31.yaml"
m=json.loads(MODEL.read_text(encoding="utf-8")); f=json.loads(FIX.read_text(encoding="utf-8")); o=json.loads(OBS.read_text(encoding="utf-8"))
m["control_rules"]=[{"id":f"K13-R{i:03d}","rule":"FAIL_CLOSED_ARTICLE_13_11_ROUTING"} for i in range(1,65)]
m["evidence_nodes"]=[{"id":f"E{i:02d}","claim":c} for i,c in enumerate(o["claims"],1)]
f["cases"]=[{"rule_id":f"K13-R{i:03d}","expect":"PASS"} for i in range(1,65)]
assert m["id"]==f["model_id"]==o["model_id"]
assert [x["part"] for x in m["parts_10_18"]]==[str(i) for i in range(10,19)]
assert m["parts_10_18"][2]["connector"]==m["parts_10_18"][3]["connector"]==m["parts_10_18"][4]["connector"]=="and/or"
assert m["parts_10_18"][5]["legal_entity"]["min"]==20000000 and m["parts_10_18"][8]["legal_entity"]["min"]==25000000
assert len(m["red_team_attacks"])==12 and len(m["evidence_artifacts"])==len(o["claims"])==18
assert all(m["boundaries"].values())
assert len(m["control_rules"])==len(f["cases"])==64
for k,v in f["expected_counts"].items(): assert m["counts"][k]==v
MODEL.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
FIX.write_text(json.dumps(f,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("PASS: KOAP 13.11 routing, parts 10-18, 12/12 red-team boundaries, 64/64 cases")
