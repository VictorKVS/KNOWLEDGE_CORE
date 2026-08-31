#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/fstec-2021-appendix11-t8-t10-semantic-atoms-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/fstec-2021-appendix11-t8-t10-semantic-atoms-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-2021-appendix11-t8-t10-semantic-observation-2026-08-31.yaml"
IDENTIFIERS=ROOT/"security-knowledge/threats/fstec-2021-appendix11-tactics-technique-identifiers-v1.yaml"
T1_T3=ROOT/"security-knowledge/threats/fstec-2021-appendix11-t1-t3-semantic-atoms-v1.yaml"
T4_T7=ROOT/"security-knowledge/threats/fstec-2021-appendix11-t4-t7-semantic-atoms-v1.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); identifiers=json.loads(IDENTIFIERS.read_text(encoding="utf-8")); t1_t3=json.loads(T1_T3.read_text(encoding="utf-8")); t4_t7=json.loads(T4_T7.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["depends_on"]==[identifiers["id"],t1_t3["id"],t4_t7["id"]]
assert [x["id"] for x in model["tactics"]]==["T8","T9","T10"]
assert [len(x["technique_atoms"]) for x in model["tactics"]]==[8,14,15]
all_atoms=[]; all_family_members=[]
for tactic in model["tactics"]:
    source_ids=next(x["technique_ids"] for x in identifiers["tactics"] if x["id"]==tactic["id"])
    atom_ids=[x["id"] for x in tactic["technique_atoms"]]
    assert atom_ids==source_ids
    assert all(x["tag"] and len(x["tag"].split())<=5 for x in tactic["technique_atoms"])
    family_members=[item for family in tactic["semantic_families"] for item in family["techniques"]]
    assert sorted(family_members)==sorted(atom_ids) and len(family_members)==len(set(family_members))
    all_atoms.extend(atom_ids); all_family_members.extend(family_members)
assert len(all_atoms)==len(set(all_atoms))==37 and len(all_family_members)==37
assert len(model["context_records"]["note_labels"])==3
assert model["context_records"]["combination_edges"]==[]
assert model["context_records"]["examples_atomized"]==0 and model["context_records"]["literal_note_text_atomized"]==0
assert len(model["applicability_gate"]["required_inputs"])==8 and len(model["applicability_gate"]["states"])==7
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==18 and len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
assert sum(len(x["technique_atoms"]) for x in t1_t3["tactics"])+sum(len(x["technique_atoms"]) for x in t4_t7["tactics"])+len(all_atoms)==145
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","attack_scenarios","fstec-2021-appendix11-t8-t10-semantic-atoms-v1.yaml","fstec-2021-appendix11-t8-t10-semantic-atoms-regression-v1.json"]: assert required in inventory
print("PASS: FSTEC 2021 appendix 11 T8-T10 semantic layer; 37 atoms, 14 exclusive families, 3 note boundaries, 145/145 identifiers semantically covered, 12/12 red-team attacks blocked, 64 rules/cases, 18 evidence nodes")
