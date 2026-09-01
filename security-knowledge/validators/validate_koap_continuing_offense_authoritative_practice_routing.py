#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/liability/koap-continuing-offense-authoritative-practice-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/liability/koap-continuing-offense-authoritative-practice-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/koap-continuing-offense-authoritative-practice-observation-2026-09-02.yaml"
MASTER=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); master=MASTER.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
routes={x["id"]:x["result"] for x in model["classification_routes"]}
assert routes==fixtures["expected_routes"]
case_nodes={x["case"]:x["holding_use"] for x in model["selected_case_nodes"]}
assert case_nodes==fixtures["expected_cases"]
assert [x["order"] for x in model["decision_gates"]]==list(range(1,9))
assert len(model["authoritative_rules"])==12
assert len(model["pdn_application_guards"])==8
assert len(model["red_team_attacks"])==12
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for path in ["security-knowledge/liability/koap-continuing-offense-authoritative-practice-routing-v1.yaml","security-knowledge/liability/koap-continuing-offense-authoritative-practice-routing-regression-v1.json"]: assert path in master
print("PASS: KoAP continuing-offence authoritative practice; routes 10/10, rules/cases 64/64, red-team 12/12, evidence 18/18")
