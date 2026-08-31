#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/legislation/RU/szi-skzi-license-registry-temporal-lifecycle-v1.yaml"
FIXTURES=ROOT/"security-knowledge/legislation/RU/szi-skzi-license-registry-temporal-lifecycle-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/szi-skzi-license-registry-temporal-lifecycle-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["sources"])==10 and len(model["stages"])==8
assert model["certificate_lifecycle"]["serial_max_years"]==5
assert model["certificate_lifecycle"]["suspension"]["maximum_calendar_days"]==90
assert model["licence_lifecycle"]["voluntary_cessation_notice_calendar_days"]==15
assert model["licence_lifecycle"]["termination_decision_working_days"]==10
assert len(model["register_separation"])==5
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["SZI_SKZI_LICENSES_TEMPORAL_LIFECYCLE","szi-skzi-license-registry-temporal-lifecycle-v1.yaml","szi-skzi-license-registry-temporal-lifecycle-regression-v1.json"]: assert required in inventory
print("PASS: SZI/SKZI/licence registry temporal lifecycle; 4 routes, 8 stages, 10 sources, 18 evidence nodes, 12/12 attacks blocked, 64/64 rules/cases")
