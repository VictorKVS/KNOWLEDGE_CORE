#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/cases/RU/pdn-skzi-healthcare-deployment-synthetic-case-v1.yaml"
FIXTURES=ROOT/"security-knowledge/cases/RU/pdn-skzi-healthcare-deployment-synthetic-case-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/pdn-skzi-healthcare-deployment-synthetic-case-observation-2026-09-01.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["status"]=="VERIFIED_SYNTHETIC_CASE_LOGIC_NO_REAL_SYSTEM_ASSERTION"
assert model["case_profile"]["case_kind"]=="SYNTHETIC_ANONYMIZED_REGRESSION_FIXTURE_NOT_A_REAL_ORGANIZATION"
assert model["case_profile"]["provided_protection_level"]==2 and model["case_profile"]["provided_actual_threat_type"]==2
assert model["case_profile"]["required_minimum_class_from_fixture_inputs"]=="KV_OR_HIGHER"
assert len(model["decision_checkpoints"])==len(model["scenario_fixtures"])==len(model["stages"])==8
assert {x["id"] for x in model["scenario_fixtures"]}=={x["fixture_id"] for x in fixtures["scenario_expectations"]}
assert any(x["expect"]=="VERIFIED_SYNTHETIC_FIXTURE_ONLY" for x in model["scenario_fixtures"])
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["PDN_SKZI_HEALTHCARE_SYNTHETIC_CASE","pdn-skzi-healthcare-deployment-synthetic-case-v1.yaml","pdn-skzi-healthcare-deployment-synthetic-case-regression-v1.json"]: assert required in inventory
print("PASS: synthetic healthcare PDn/SKZI case; 8 checkpoints, 8 scenarios, 18 evidence nodes, 12/12 attacks blocked, 64/64 rules/cases")
