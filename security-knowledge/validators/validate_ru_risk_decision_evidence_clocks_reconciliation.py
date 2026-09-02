#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/risks/ru-risk-decision-evidence-clocks-reconciliation-v1.yaml"
FIXTURES = ROOT / "security-knowledge/risks/ru-risk-decision-evidence-clocks-reconciliation-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/ru-risk-decision-evidence-clocks-reconciliation-observation-2026-09-02.yaml"

model = json.loads(MODEL.read_text(encoding="utf-8"))
fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
obs = json.loads(OBS.read_text(encoding="utf-8"))
assert model["id"] == fixtures["model_id"] == obs["model_id"]
for key, value in fixtures["expected_counts"].items():
    assert model["counts"][key] == value, (key, model["counts"][key], value)
assert [x["order"] for x in model["layer_boundaries"]] == [1, 2, 3, 4]
assert [x["order"] for x in model["lifecycle_stages"]] == list(range(1, 11))
assert len({x["id"] for x in model["evidence_clocks"]}) == 10
assert len(model["evidence_nodes"]) == len(obs["claims"]) == 18
assert [x["id"] for x in model["evidence_nodes"]] == [f"E-{i:02d}" for i in range(1, 19)]
assert all(model["boundaries"].values())
assert model["counts"]["invented_universal_intervals"] == 0
assert model["counts"]["automatic_edition_substitutions"] == 0
national = {x["id"]: x for x in model["sources"][:4]}
assert all(x["status"] == "Действует" for x in national.values())
assert model["sources"][5]["id"] == "ISO_IEC_27005_2022"
assert model["sources"][5]["automatic_substitution_for_gost_2010"] is False
assert len(model["red_team_attacks"]) == 12 and fixtures["red_team_expectation"] == "12_OF_12_BLOCKED"
rules = {x["id"] for x in model["control_rules"]}
cases = {x["rule_id"] for x in fixtures["cases"]}
assert rules == cases == {f"RDC-{i:03d}" for i in range(1, 65)}
assert all(x["expected"] == "BLOCK_OR_REVIEW" for x in fixtures["cases"])
print("PASS: risk decision evidence clocks reconciliation; 64/64 cases; red-team 12/12; evidence 18/18")
