#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/liability/gk-privacy-damages-moral-harm-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/liability/gk-privacy-damages-moral-harm-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gk-privacy-damages-moral-harm-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["sources"])==13 and len(model["stages"])==8
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
assert model["monetary_heads"]["article_15_losses"]["components"]==["actual_loss","lost_profit"]
assert model["limitation_routing"]["general_years"]==3 and model["limitation_routing"]["objective_cap_years"]==10
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["CODES_KOAP_UK_GK_TK","gk-privacy-damages-moral-harm-routing-v1.yaml","gk-privacy-damages-moral-harm-routing-regression-v1.json"]: assert required in inventory
print("PASS: GK privacy/damages/moral-harm routing; 8 stages, 13 source groups, 18 evidence nodes, 12/12 attacks blocked, 64/64 rules/cases")
