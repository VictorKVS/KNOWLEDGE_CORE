#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/standards/gost-iso-27033-6-18044-27035-incident-wireless-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/standards/gost-iso-27033-6-18044-27035-incident-wireless-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-iso-27033-6-18044-27035-incident-wireless-observation-2026-09-02.yaml"
MASTER=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); master=MASTER.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["routes"])==model["counts"]["selected_routes"]==5
assert sum(x["jurisdiction"]=="RU_NATIONAL" for x in model["routes"])==2
assert sum(x["jurisdiction"]=="INTERNATIONAL_ONLY_IN_THIS_MODEL" for x in model["routes"])==3
assert sum(x.get("national_conformity")=="IDT" for x in model["routes"])==1
assert sum(x.get("national_conformity")=="NEQ" for x in model["routes"])==1
assert [x["order"] for x in model["decision_gates"]]==list(range(1,9))
assert len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12 and all(x["result"]=="BLOCKED" for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["evidence_nodes"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
routes={x["id"]:x for x in model["routes"]}
assert routes["GOST_R_59162_2020"]["national_order"]=="1038-ст"
assert routes["GOST_R_59162_2020"]["national_conformity"]=="NEQ"
assert routes["GOST_R_ISO_IEC_TR_18044_2007"]["national_order"]=="513-ст"
assert routes["GOST_R_ISO_IEC_TR_18044_2007"]["national_conformity"]=="IDT"
assert all(routes[x]["national_status"].startswith("PENDING_") for x in ["ISO_IEC_27035_1_2023","ISO_IEC_27035_2_2023","ISO_IEC_27035_3_2020"])
actual={x["id"]:x["rule"] for x in model["control_rules"]}
for case in fixtures["cases"]: assert actual[case["rule_id"]]==case["expected"]
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
for p in (MODEL,FIXTURES,OBS): assert str(p.relative_to(ROOT)) in master
print("PASS: 27033-6/18044/27035 routing; 2 RU + 3 ISO-only; 64/64 rules/cases; red-team 12/12; evidence 18/18")

