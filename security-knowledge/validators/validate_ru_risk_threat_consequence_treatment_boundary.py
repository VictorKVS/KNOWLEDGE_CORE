#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/risks/ru-risk-threat-consequence-treatment-boundary-v1.yaml"
FIXTURES=ROOT/"security-knowledge/risks/ru-risk-threat-consequence-treatment-boundary-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/ru-risk-threat-consequence-treatment-boundary-observation-2026-09-01.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8"))
fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
obs=json.loads(OBS.read_text(encoding="utf-8"))
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert [x["order"] for x in model["process_stages"]]==list(range(1,8))
assert len(model["semantic_boundaries"])==8
assert len(model["fstec_crosswalk"])==5 and all(x["equivalence"] is False for x in model["fstec_crosswalk"])
assert model["treatment_options"]==["REDUCE","RETAIN","AVOID","TRANSFER"]
assert len(model["decision_gates"])==len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
assert all(x["status"]=="Действует" for x in model["sources"][:2])
assert model["counts"]["default_formulas"]==model["counts"]["default_scales"]==model["counts"]["default_thresholds"]==0
print("PASS: risk threat consequence treatment boundary; 64/64 rules and cases; red-team 12/12; evidence 18/18")
