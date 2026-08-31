#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/fstec-2021-appendix11-tactics-technique-identifiers-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/fstec-2021-appendix11-tactics-technique-identifiers-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-2021-appendix11-tactics-technique-identifiers-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["approval_date"]=="2021-02-05"
assert [x["id"] for x in model["tactics"]]==[f"T{i}" for i in range(1,11)]
expected=[20,14,16,7,13,9,29,8,14,15]
assert [x["technique_count"] for x in model["tactics"]]==expected
all_ids=[]
for index,tactic in enumerate(model["tactics"],1):
    ids=tactic["technique_ids"]
    assert ids==[f"T{index}.{n}" for n in range(1,tactic["technique_count"]+1)]
    assert tactic["first"]==ids[0] and tactic["last"]==ids[-1]
    all_ids.extend(ids)
assert len(all_ids)==len(set(all_ids))==145
assert model["atomization_boundary"]["technique_wording_atomized"]==0
assert model["atomization_boundary"]["notes_and_examples_atomized"]==0
assert len(model["scenario_gate"]["required_inputs"])==8
assert len(model["scenario_gate"]["states"])==7
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","FSTEK_threat_modeling_methodology","attack_scenarios","fstec-2021-appendix11-tactics-technique-identifiers-v1.yaml","fstec-2021-appendix11-tactics-technique-identifiers-regression-v1.json"]: assert required in inventory
print("PASS: FSTEC 2021 appendix 11 identifier structure; 10 tactics, 145 unique contiguous technique IDs, 12/12 red-team attacks blocked, 64 rules/cases, 18 evidence nodes; technique wording, notes, examples and primary bytes remain pending")
