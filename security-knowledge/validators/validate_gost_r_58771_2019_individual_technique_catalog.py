#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/risks/gost-r-58771-2019-individual-technique-catalog-v1.yaml"
FIXTURES = ROOT / "security-knowledge/risks/gost-r-58771-2019-individual-technique-catalog-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/gost-r-58771-2019-individual-technique-catalog-observation-2026-08-30.yaml"
REGISTRY = ROOT / "security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model = json.loads(MODEL.read_text(encoding="utf-8"))
fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
observation = json.loads(OBS.read_text(encoding="utf-8"))
registry = REGISTRY.read_text(encoding="utf-8")

assert model["id"] == fixtures["model_id"]
assert model["source"]["status"] == "Действует"
assert model["source"]["table"] == "А.2"
assert model["source"]["appendices_status"] == "INFORMATIVE"
assert len(model["techniques"]) == 42
assert len({x["id"] for x in model["techniques"]}) == 42
assert len({x["locator"] for x in model["techniques"]}) == 42
assert {x["locator"] for x in model["techniques"]} == set(fixtures["required_locators"])
assert dict(Counter(x["family"] for x in model["techniques"])) == fixtures["expected_family_counts"]
assert model["family_counts"] == fixtures["expected_family_counts"]
assert len(model["table_a1_characteristics"]) == 8
assert len(model["evidence_nodes"]) == 18
assert len(observation["claims"]) == 18
assert len(model["control_rules"]) == 64
assert len(fixtures["cases"]) == 64
assert len({x["id"] for x in model["control_rules"]}) == 64
assert {x["rule_id"] for x in fixtures["cases"]} == {x["id"] for x in model["control_rules"]}
assert all(v is True for v in model["boundaries"].values())
assert model["catalog_semantics"]["list_is_exhaustive"] is False
assert model["catalog_semantics"]["alphabetical_order_implies_priority"] is False
for key in ["default_formulas","default_scales","default_weights","default_thresholds","automatic_selections"]:
    assert model["counts"][key] == 0
for required in [
    "id: GOST_R_58771_2019",
    "REGRESSION_PROTECTED_FOUNDATION_FAMILY_CROSSWALK_AND_42_TECHNIQUE_CATALOG",
    "security-knowledge/risks/gost-r-58771-2019-individual-technique-catalog-v1.yaml",
    "security-knowledge/risks/gost-r-58771-2019-individual-technique-catalog-regression-v1.json",
]:
    assert required in registry
print("PASS: GOST R 58771-2019 Table A.2 catalog; 42 unique techniques, 9 families with 5/5/2/3/13/2/4/5/3 rows, 8 Table A.1 characteristics, 18 evidence nodes, 64 rules/cases; 0 defaults or automatic selections")
