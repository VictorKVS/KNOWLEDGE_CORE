#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/liability/uk-137-privacy-qualification-limitation-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/liability/uk-137-privacy-qualification-limitation-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/uk-137-privacy-qualification-limitation-observation-2026-09-02.yaml"
MASTER=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); master=MASTER.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert [x["part"] for x in model["offense_parts"]]==["137.1","137.2","137.3"]
for part in model["offense_parts"]:
    expected=fixtures["expected_parts"][part["part"]]
    assert part["initial_category"]==expected["category"]
    assert part["article78_limitation_years"]==expected["limitation_years"]
assert model["sources"][5]["effective_from"]==fixtures["expected_effective_dates"]["421_fz"]
assert model["sources"][6]["effective_from"]==fixtures["expected_effective_dates"]["251_fz"]
assert len(model["temporal_rules"])==8
assert [x["order"] for x in model["decision_gates"]]==list(range(1,9))
assert len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for path in ["security-knowledge/liability/uk-137-privacy-qualification-limitation-routing-v1.yaml","security-knowledge/liability/uk-137-privacy-qualification-limitation-routing-regression-v1.json"]: assert path in master
print("PASS: UK 137 qualification/limitation routing; parts 3/3, rules/cases 64/64, red-team 12/12, evidence 18/18")

