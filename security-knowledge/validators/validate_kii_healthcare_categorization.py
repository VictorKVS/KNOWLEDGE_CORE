#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "security-knowledge/classification/kii-healthcare-categorization-pp127-2025-v1.yaml"
R = ROOT / "security-knowledge/classification/kii-healthcare-categorization-pp127-2025-regression-v1.json"
O = ROOT / "security-knowledge/evidence/kii-healthcare-categorization-observation-2026-09-01.yaml"
I = ROOT / "security-knowledge/corpus/master-source-inventory.yaml"

m = json.loads(M.read_text(encoding="utf-8"))
r = json.loads(R.read_text(encoding="utf-8"))
o = json.loads(O.read_text(encoding="utf-8"))
inv = I.read_text(encoding="utf-8")

assert m["id"] == r["model_id"] == o["model_id"]
assert next(x for x in m["sources"] if x["id"] == "PP127")["current_edition"] == "2025-11-07"
assert next(x for x in m["sources"] if x["id"] == "RP360")["current_edition"] == "2026-05-27"
assert len(m["healthcare_typical_objects"]) == 12
assert [x["row"] for x in m["healthcare_typical_objects"]] == list(range(1, 13))
assert len({x["id"] for x in m["healthcare_typical_objects"]}) == 12
bands = m["verified_healthcare_indicator"]["bands"]
assert bands == [
    {"category": "III", "min_inclusive": 1, "max_inclusive": 50},
    {"category": "II", "min_exclusive": 50, "max_inclusive": 500},
    {"category": "I", "min_exclusive": 500, "max": None},
]
assert m["current_route"]["no_category_rule"].startswith("NO_CATEGORY")
assert m["sector_feature_state"]["binding_healthcare_sector_feature_npa"].startswith("NOT_IDENTIFIED")
assert m["sector_feature_state"]["minzdrav_2021"].startswith("REFERENCE_ONLY")
assert len(m["decision_gates"]) == len(m["scenarios"]) == 8
assert {x["id"] for x in m["scenarios"]} == {x["scenario_id"] for x in r["scenario_expectations"]}
assert len(m["red_team_attacks"]) == 12 and all(x["blocked"] for x in m["red_team_attacks"])
assert len(m["evidence_artifacts"]) == len(m["evidence_nodes"]) == len(o["claims"]) == 18
assert len(m["control_rules"]) == len(r["cases"]) == 64
assert {x["id"] for x in m["control_rules"]} == {x["rule_id"] for x in r["cases"]}
assert all(m["boundaries"].values())
assert all(x["expected"] == "BLOCKED" for x in r["adversarial_cases"])
for key, value in r["expected_counts"].items():
    assert m["counts"][key] == value
for marker in [
    "KII_HEALTHCARE_CATEGORIZATION_CURRENT",
    "kii-healthcare-categorization-pp127-2025-v1.yaml",
    "kii-healthcare-categorization-pp127-2025-regression-v1.json",
]:
    assert marker in inv

print("PASS: healthcare KII current route; 12 typical objects, 3 exact harm bands, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases")
