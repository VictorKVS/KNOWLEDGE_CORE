#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/liability/ru-cross-code-incident-clock-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/liability/ru-cross-code-incident-clock-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/ru-cross-code-incident-clock-routing-observation-2026-09-02.yaml"
MASTER=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); master=MASTER.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["clock_routes"])==23
clocks={x["id"]:x for x in model["clock_routes"]}
for cid,(duration,unit) in fixtures["expected_periods"].items():
    assert clocks[cid]["duration"]==duration and clocks[cid]["unit"]==unit
for cid,duration in fixtures["expected_special_routes"].items(): assert clocks[cid]["duration"]==duration
assert model["future_review"]["koap_article_4_5_change_effective"]==fixtures["future_change"]["effective"]
assert model["future_review"]["status"]==fixtures["future_change"]["snapshot_action"]
assert [x["order"] for x in model["decision_gates"]]==list(range(1,9))
assert len(model["red_team_attacks"])==12
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for path in ["security-knowledge/liability/ru-cross-code-incident-clock-routing-v1.yaml","security-knowledge/liability/ru-cross-code-incident-clock-routing-regression-v1.json"]: assert path in master
print("PASS: cross-code incident clocks; routes 23/23, rules/cases 64/64, red-team 12/12, evidence 18/18")
