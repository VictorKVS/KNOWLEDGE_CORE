#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/risks/gost-r-58771-2019-table-a2-literal-cells-v1.yaml"
FIXTURES = ROOT / "security-knowledge/risks/gost-r-58771-2019-table-a2-literal-cells-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/gost-r-58771-2019-table-a2-literal-cells-observation-2026-08-30.yaml"
CATALOG = ROOT / "security-knowledge/risks/gost-r-58771-2019-individual-technique-catalog-v1.yaml"
REGISTRY = ROOT / "security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model = json.loads(MODEL.read_text(encoding="utf-8"))
fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
observation = json.loads(OBS.read_text(encoding="utf-8"))
catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
registry = REGISTRY.read_text(encoding="utf-8")

assert model["id"] == fixtures["model_id"]
assert model["source"]["status"] == "Действует"
assert model["source"]["table"] == "А.2"
assert model["source"]["appendix_status"] == "INFORMATIVE"
assert model["columns"] == fixtures["required_columns"]
assert len(model["literal_rows"]) == 42
assert len({x["id"] for x in model["literal_rows"]}) == 42
assert len({x["locator"] for x in model["literal_rows"]}) == 42
assert {(x["id"],x["locator"]) for x in model["literal_rows"]} == {(x["id"],x["locator"]) for x in catalog["techniques"]}
assert all(set(row) == {"id","locator",*model["columns"]} for row in model["literal_rows"])
assert sum(len(model["columns"]) for _ in model["literal_rows"]) == 336
all_values = {row[col] for row in model["literal_rows"] for col in model["columns"]}
assert set(fixtures["required_pending_literals"]).issubset(all_values)
assert model["literal_semantics"]["normalization_layer_present"] is False
assert model["literal_semantics"]["cell_values_are_verbatim_tokens_from_public_rendering"] is True
assert model["literal_semantics"]["descriptions_reproduced"] is False
assert len(model["rendered_anomaly_classes"]) == 10
assert len(model["evidence_nodes"]) == 18
assert len(observation["claims"]) == 18
assert len(model["control_rules"]) == 64
assert len(fixtures["cases"]) == 64
assert {x["rule_id"] for x in fixtures["cases"]} == {x["id"] for x in model["control_rules"]}
assert all(v is True for v in model["boundaries"].values())
for key, value in fixtures["expected_counts"].items():
    assert model["counts"][key] == value
for required in [
    "id: GOST_R_58771_2019",
    "REGRESSION_PROTECTED_FOUNDATION_SELECTION_SCHEMA_FAMILY_CROSSWALK_42_TECHNIQUE_CATALOG_AND_336_LITERAL_A2_CELLS",
    "security-knowledge/risks/gost-r-58771-2019-table-a2-literal-cells-v1.yaml",
    "security-knowledge/risks/gost-r-58771-2019-table-a2-literal-cells-regression-v1.json",
]:
    assert required in registry
print("PASS: GOST R 58771-2019 Table A.2 literal layer; 42 rows x 8 characteristics = 336 cells, 10 anomaly classes, 18 evidence nodes, 64 rules/cases; 0 normalized cells, defaults or automatic selections")
