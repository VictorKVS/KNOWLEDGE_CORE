#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/legislation/RU/fstec-register-snapshot-record-schema-v1.yaml"
FIXTURES=ROOT/"security-knowledge/legislation/RU/fstec-register-snapshot-record-schema-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-register-snapshot-record-schema-observation-2026-09-01.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["status"]=="PARTIAL_VERIFIED_INDEXED_OFFICIAL_RECORDS_IMMUTABLE_FULL_EXPORT_PENDING"
assert len(model["sources"])==6 and len(model["record_families"])==3 and len(model["indexed_record_observations"])==2
assert len(model["field_groups"])==6 and len(model["snapshot_states"])==len(model["stages"])==8
assert {x["state"] for x in model["snapshot_states"]}>={"FETCHED_BYTES","HASHED","TRANSPORT_PENDING","SCHEMA_CONFLICT"}
assert all(x["evidence_state"]=="VERIFIED_OFFICIAL_SEARCH_INDEX_SNIPPET_ONLY" for x in model["indexed_record_observations"])
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["FSTEC_REGISTER_SNAPSHOT_RECORD_SCHEMA","fstec-register-snapshot-record-schema-v1.yaml","fstec-register-snapshot-record-schema-regression-v1.json"]: assert required in inventory
print("PASS: FSTEC register snapshot record schema; 3 families, 2 indexed observations, 8 states, 18 evidence nodes, 12/12 attacks blocked, 64/64 rules/cases")
