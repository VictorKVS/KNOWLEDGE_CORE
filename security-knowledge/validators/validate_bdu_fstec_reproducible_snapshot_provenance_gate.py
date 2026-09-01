#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/bdu-fstec-reproducible-snapshot-provenance-gate-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/bdu-fstec-reproducible-snapshot-provenance-gate-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/bdu-fstec-reproducible-snapshot-observation-2026-09-01.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["observation_2026_09_01"]["immutable_complete_threat_export"]=="PENDING"
assert model["observation_2026_09_01"]["immutable_complete_vulnerability_export"]=="PENDING"
assert "CERTIFICATE_VERIFY_FAILED" in model["observation_2026_09_01"]["catalog_root_transport"]
assert len(model["dataset_separation"])==2
assert [x["order"] for x in model["acquisition_states"]]==[1,2,3,4,5,6]
assert len(model["manifest_fields"])==24
assert len(model["format_safety_gates"])==6
assert len(model["semantic_gates"])==8
assert len(model["completeness_gate"]["required"])==10
assert len(model["completeness_gate"]["states"])==5
assert model["completeness_gate"]["current_state"]=="PARTIAL_DISCOVERY_ONLY"
assert len(model["completeness_gate"]["forbidden_shortcuts"])==7
assert len(model["temporal_lifecycle"]["field_level_delta_types"])==4
assert len(model["decision_gates"])==len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12
assert {x["blocked_by"] for x in model["red_team_attacks"]}<={x["id"] for x in model["decision_gates"]}
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","FSTEK_BDU","bdu-fstec-reproducible-snapshot-provenance-gate-v1.yaml","bdu-fstec-reproducible-snapshot-provenance-gate-regression-v1.json"]: assert required in inventory
print("PASS: BDU reproducible snapshot provenance gate; 2 datasets, 6 acquisition states, 24 manifest fields, 10 completeness checks, 64 rules/cases, 12/12 red-team attacks blocked; current state remains PARTIAL_DISCOVERY_ONLY")
