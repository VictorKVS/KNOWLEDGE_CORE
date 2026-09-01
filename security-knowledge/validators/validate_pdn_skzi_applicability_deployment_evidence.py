#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/legislation/RU/pdn-skzi-applicability-deployment-evidence-v1.yaml"
FIXTURES=ROOT/"security-knowledge/legislation/RU/pdn-skzi-applicability-deployment-evidence-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/pdn-skzi-applicability-deployment-evidence-observation-2026-09-01.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["status"]=="VERIFIED_NORMATIVE_APPLICABILITY_AND_DEPLOYMENT_EVIDENCE_MODEL"
assert len(model["sources"])==7 and len(model["regime_separation"])==6
assert len(model["applicability_gates"])==8 and len(model["order_378_class_mapping"])==8
assert {x["protection_level"] for x in model["order_378_class_mapping"]}=={1,2,3,4}
assert model["order_378_level_measures"]["UZ2"][-1].endswith("six months")
assert "once every month" in model["order_378_level_measures"]["UZ1"][3]
assert len(model["deployment_joins"])==6 and len(model["stages"])==8
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["PDN_SKZI_APPLICABILITY_DEPLOYMENT","pdn-skzi-applicability-deployment-evidence-v1.yaml","pdn-skzi-applicability-deployment-evidence-regression-v1.json"]: assert required in inventory
print("PASS: PDn/SKZI applicability and deployment evidence; 8 gates, 8 class rows, 4 levels, 18 evidence nodes, 12/12 attacks blocked, 64/64 rules/cases")
