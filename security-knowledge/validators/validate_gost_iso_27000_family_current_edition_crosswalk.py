#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
M=ROOT/"security-knowledge/standards/gost-iso-27000-family-current-edition-crosswalk-v1.yaml"
R=ROOT/"security-knowledge/standards/gost-iso-27000-family-current-edition-crosswalk-regression-v1.json"
O=ROOT/"security-knowledge/evidence/gost-iso-27000-family-crosswalk-observation-2026-09-01.yaml"
I=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
m=json.loads(M.read_text(encoding="utf-8"));r=json.loads(R.read_text(encoding="utf-8"));o=json.loads(O.read_text(encoding="utf-8"));inv=I.read_text(encoding="utf-8")
assert m["id"]==r["model_id"]==o["model_id"]
assert len(m["standards"])==6 and all(x["status"]=="Действует" for x in m["standards"])
assert {x["designation"] for x in m["superseded_blocklist"]}=={"ГОСТ Р ИСО/МЭК 27000-2012","ГОСТ Р ИСО/МЭК 27002-2012"}
assert next(x for x in m["standards"] if "27005" in x["designation"])["source_iso"]=="ISO/IEC 27005:2008"
assert len(m["crosswalk_edges"])==len(m["edition_gates"])==len(m["scenarios"])==8
assert {x["id"] for x in m["scenarios"]}=={x["scenario_id"] for x in r["scenario_expectations"]}
assert len(m["red_team_attacks"])==12 and all(x["blocked"] for x in m["red_team_attacks"])
assert len(m["evidence_artifacts"])==len(m["evidence_nodes"])==len(o["claims"])==18
assert len(m["control_rules"])==len(r["cases"])==64
assert {x["id"] for x in m["control_rules"]}=={x["rule_id"] for x in r["cases"]}
assert all(m["boundaries"].values()) and all(x["expect"]=="BLOCKED" for x in r["adversarial_cases"])
for k,v in r["expected_counts"].items(): assert m["counts"][k]==v
for x in ["GOST_ISO_27000_FAMILY_CURRENT_EDITION_CROSSWALK","gost-iso-27000-family-current-edition-crosswalk-v1.yaml","gost-iso-27000-family-current-edition-crosswalk-regression-v1.json"]: assert x in inv
print("PASS: GOST/ISO 27000 family; 6 current, 2 superseded, 8 edges/gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases")
