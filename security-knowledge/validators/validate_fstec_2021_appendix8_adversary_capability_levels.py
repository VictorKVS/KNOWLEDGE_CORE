#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/fstec-2021-appendix8-adversary-capability-levels-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/fstec-2021-appendix8-adversary-capability-levels-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-2021-appendix8-adversary-capability-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["approval_date"]=="2021-02-05"
assert model["dimension_basis"]==["competence","resources and equipment","motivation"]
assert [x["id"] for x in model["levels"]]==["N1","N2","N3","N4"]
assert [x["inherits"] for x in model["levels"]]==[None,"N1","N2","N3"]
assert [len(x["characteristics"]) for x in model["levels"]]==[5,7,10,9]
assert sum(len(x["characteristics"]) for x in model["levels"])==31
assert sum(len(x["table_type_rows"]) for x in model["levels"])==13
assert len(model["inheritance_edges"])==3
assert len(model["assignment_gate"]["required_inputs"])==6
assert len(model["assignment_gate"]["characteristic_states"])==4
assert len(model["assignment_gate"]["decision_states"])==6
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","FSTEK_threat_modeling_methodology","violator_models","fstec-2021-appendix8-adversary-capability-levels-v1.yaml","fstec-2021-appendix8-adversary-capability-levels-regression-v1.json"]: assert required in inventory
print("PASS: FSTEC 2021 appendix 8; N1-N4, 31 characteristics, 3 inheritance edges, 13 table type rows, 12/12 red-team attacks blocked, 64 rules/cases, 18 evidence nodes; no score, weight, threshold or type-only assignment")
