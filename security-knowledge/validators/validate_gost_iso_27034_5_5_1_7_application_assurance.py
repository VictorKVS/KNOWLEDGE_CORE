#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/standards/gost-iso-27034-5-5-1-7-application-assurance-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/standards/gost-iso-27034-5-5-1-7-application-assurance-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-iso-27034-5-5-1-7-application-assurance-observation-2026-09-02.yaml"
MASTER=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); master=MASTER.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["routes"])==model["counts"]["selected_routes"]==3
assert sum(x["jurisdiction"]=="RU_NATIONAL" for x in model["routes"])==2
assert sum(x["jurisdiction"]=="INTERNATIONAL_ONLY_IN_THIS_MODEL" for x in model["routes"])==1
assert sum(x.get("national_conformity")=="IDT" for x in model["routes"])==2
assert [x["order"] for x in model["decision_gates"]]==list(range(1,9))
assert len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12 and all(x["result"]=="BLOCKED" for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["evidence_nodes"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
routes={x["id"]:x for x in model["routes"]}
assert routes["GOST_R_ISO_IEC_27034_5_2020"]["national_order"]=="1043-ст"
assert routes["GOST_R_ISO_IEC_27034_5_2020"]["national_effective"]=="2021-06-01"
assert routes["ISO_IEC_TS_27034_5_1_2018"]["publication_type"]=="TECHNICAL_SPECIFICATION"
assert routes["ISO_IEC_TS_27034_5_1_2018"]["national_status"].startswith("PENDING_")
assert routes["GOST_R_ISO_IEC_27034_7_2020"]["national_order"]=="1170-ст"
assert routes["GOST_R_ISO_IEC_27034_7_2020"]["national_effective"]=="2021-06-01"
actual={x["id"]:x["rule"] for x in model["control_rules"]}
for case in fixtures["cases"]: assert actual[case["rule_id"]]==case["expected"]
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
for p in (MODEL,FIXTURES,OBS): assert str(p.relative_to(ROOT)) in master
print("PASS: 27034-5/5-1/7; 2 Russian IDT + 1 ISO-only TS; 64/64 rules/cases; red-team 12/12; evidence 18/18")

