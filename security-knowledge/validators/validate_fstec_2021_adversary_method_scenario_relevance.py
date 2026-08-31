#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/fstec-2021-adversary-method-scenario-relevance-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/fstec-2021-adversary-method-scenario-relevance-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-2021-adversary-method-scenario-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["approval_date"]=="2021-02-05"
assert len(model["anthropogenic_source"]["violator_types"])==13
assert len(model["anthropogenic_source"]["capability_dimensions"])==3
assert [x["id"] for x in model["anthropogenic_source"]["capability_levels"]]==["N1","N2","N3","N4"]
assert [x["id"] for x in model["anthropogenic_source"]["access_categories"]]==["EXTERNAL","INTERNAL"]
assert sum(len(x["modes"]) for x in model["anthropogenic_source"]["intent_rules"])==3
assert len(model["technogenic_source_boundary"]["factors"])==3
assert len(model["realization_assessment"]["methods"])==9
assert len(model["realization_assessment"]["interface_types"])==6
assert len(model["scenario_relevance_gate"]["possible_threat_tuple"])==4
assert [x["order"] for x in model["scenario_relevance_gate"]["operation_stage"]["steps"]]==list(range(1,9))
assert len(model["scenario_relevance_gate"]["decision_states"])==6
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","FSTEK_threat_modeling_methodology","FSTEK_BDU","violator_models","attack_scenarios","threat_applicability_rules","fstec-2021-adversary-method-scenario-relevance-v1.yaml","fstec-2021-adversary-method-scenario-relevance-regression-v1.json"]: assert required in inventory
print("PASS: FSTEC 2021 clauses 5.1-5.3; 13 violator types, N1-N4, 2 access categories, 9 methods, 6 interfaces, 4-part threat tuple, 8 operational scenario steps, 12/12 red-team attacks blocked, 64 rules/cases, 18 evidence nodes")
