#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/liability/uk-272-1-criminal-procedure-evidence-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/liability/uk-272-1-criminal-procedure-evidence-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/uk-272-1-criminal-procedure-evidence-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["sources"])==14 and len(model["stages"])==8
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
assert {tuple(x["parts"]) for x in model["offence_part_working_categories"]}=={(1,2,6),(3,4,5)}
assert model["report_check"]["base_decision_days"]==3 and model["report_check"]["motivated_extension_days"]==10 and model["report_check"]["maximum_extension_days"]==30
assert model["preliminary_investigation_clock"]["base_months"]==2 and model["preliminary_investigation_clock"]["extension_to_months"]==3 and model["preliminary_investigation_clock"]["special_complexity_to_months"]==12
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["CODES_KOAP_UK_GK_TK","uk-272-1-criminal-procedure-evidence-routing-v1.yaml","uk-272-1-criminal-procedure-evidence-routing-regression-v1.json"]: assert required in inventory
print("PASS: UK 272.1 criminal-procedure/evidence routing; 8 stages, 14 source groups, 18 evidence nodes, 12/12 attacks blocked, 64/64 rules/cases")
