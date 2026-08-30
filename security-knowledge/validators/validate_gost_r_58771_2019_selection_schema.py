#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/risks/gost-r-58771-2019-selection-schema-v1.yaml"
FIXTURES = ROOT / "security-knowledge/risks/gost-r-58771-2019-selection-schema-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/gost-r-58771-2019-selection-schema-observation-2026-08-30.yaml"
REGISTRY = ROOT / "security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model = json.loads(MODEL.read_text(encoding="utf-8"))
fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
observation = json.loads(OBS.read_text(encoding="utf-8"))
registry = REGISTRY.read_text(encoding="utf-8")

assert model["id"] == fixtures["model_id"]
assert model["source"]["status"] == "Действует"
assert model["source"]["section"] == "7"
assert model["source"]["table"] == "А.1"
assert model["source"]["appendix_status"] == "INFORMATIVE"
assert len(model["section_nodes"]) == 4
assert [x["id"] for x in model["decision_factors"]] == fixtures["required_factor_ids"]
assert len(model["selection_constraints"]) == 6
assert [x["id"] for x in model["table_a1_characteristics"]] == fixtures["required_characteristic_ids"]
assert len(model["table_a2_schema"]["columns"]) == 11
assert model["table_a2_schema"]["normalization_performed"] is False
decision = next(x for x in model["table_a1_characteristics"] if x["id"] == "DECISION_LEVEL")
data = next(x for x in model["table_a1_characteristics"] if x["id"] == "INITIAL_INFORMATION_OR_DATA")
assert [(x["code"], x["id"]) for x in decision["values"]] == [(1,"STRATEGIC"),(2,"OPERATIONAL"),(3,"TACTICAL")]
assert [(x["code"], x["id"]) for x in data["values"]] == [(1,"HIGH"),(2,"MEDIUM"),(3,"LOW")]
assert len(model["selection_record_evidence"]) == 14
assert len(model["evidence_nodes"]) == 18
assert len(observation["claims"]) == 18
assert len(model["control_rules"]) == 64
assert len(fixtures["cases"]) == 64
assert len({x["id"] for x in model["control_rules"]}) == 64
assert {x["rule_id"] for x in fixtures["cases"]} == {x["id"] for x in model["control_rules"]}
assert all(v is True for v in model["boundaries"].values())
for key in ["default_formulas","default_scales","default_weights","default_thresholds","automatic_selections"]:
    assert model["counts"][key] == 0
for key, value in fixtures["expected_counts"].items():
    assert model["counts"][key] == value
for required in [
    "id: GOST_R_58771_2019",
    "REGRESSION_PROTECTED_FOUNDATION_SELECTION_SCHEMA_FAMILY_CROSSWALK_AND_42_TECHNIQUE_CATALOG",
    "security-knowledge/risks/gost-r-58771-2019-selection-schema-v1.yaml",
    "security-knowledge/risks/gost-r-58771-2019-selection-schema-regression-v1.json",
]:
    assert required in registry
print("PASS: GOST R 58771-2019 section 7/Table A.1; 6 decision factors, 6 selection constraints, 8 characteristics, 11 Table A.2 columns, 2 rendered anomalies preserved, 18 evidence nodes, 64 rules/cases; 0 defaults or automatic selections")
