#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/liability/tk-90-cross-regime-liability-red-team-v1.yaml"
FIXTURES=ROOT/"security-knowledge/liability/tk-90-cross-regime-liability-red-team-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/tk-90-cross-regime-liability-red-team-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["sources"])==11 and len(model["stages"])==8 and len(model["linked_models"])==6
assert model["article_90_role"]["function"]=="ROUTING_NOT_SELF_EXECUTING_OFFENCE"
assert set(model["article_90_role"]["regimes"])=={"disciplinary","material","civil","administrative","criminal"}
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["CODES_KOAP_UK_GK_TK","tk-90-cross-regime-liability-red-team-v1.yaml","tk-90-cross-regime-liability-red-team-regression-v1.json"]: assert required in inventory
print("PASS: TK Article 90 cross-regime red-team routing; 5 regimes, 8 stages, 11 sources, 18 evidence nodes, 12/12 attacks blocked, 64/64 rules/cases")
