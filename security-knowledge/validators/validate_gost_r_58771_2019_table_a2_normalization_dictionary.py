#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/risks/gost-r-58771-2019-table-a2-normalization-dictionary-v1.yaml"
FIXTURES=ROOT/"security-knowledge/risks/gost-r-58771-2019-table-a2-normalization-dictionary-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-r-58771-2019-table-a2-normalization-dictionary-observation-2026-08-30.yaml"
LITERAL=ROOT/"security-knowledge/risks/gost-r-58771-2019-table-a2-literal-cells-v1.yaml"
REGISTRY=ROOT/"security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); literal=json.loads(LITERAL.read_text(encoding="utf-8")); registry=REGISTRY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]
assert model["source"]["status"]=="Действует"
assert model["input_model"]==literal["id"]
assert model["normalization_policy"]["retain_literal_value"] is True
assert model["normalization_policy"]["mode"]=="DIRECT_ONE_LITERAL_TOKEN_TO_ONE_VISIBLE_A1_CATEGORY_ONLY"
assert all(v is False for k,v in model["normalization_policy"].items() if k.startswith("allow_"))
mappings=model["safe_mappings"]
assert sum(len(v) for v in mappings.values())==18
column_pairs={(col,row[col]) for row in literal["literal_rows"] for col in literal["columns"]}
assert len(column_pairs)==82
mapped=Counter()
for row in literal["literal_rows"]:
    for col in literal["columns"]:
        if row[col] in mappings.get(col,{}): mapped[col]+=1
mapped={col:mapped.get(col,0) for col in literal["columns"]}
assert mapped==fixtures["expected_mapped_cell_counts"]==model["mapped_cell_counts"]
assert sum(mapped.values())==125
assert 336-sum(mapped.values())==211
assert len(model["pending_classes"])==12
assert len(model["explicit_non_mappings"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for required in ["id: GOST_R_58771_2019","REGRESSION_PROTECTED_FOUNDATION_SELECTION_SCHEMA_FAMILY_CROSSWALK_42_TECHNIQUE_CATALOG_336_LITERAL_A2_CELLS_AND_125_SAFE_NORMALIZED_CELLS","security-knowledge/risks/gost-r-58771-2019-table-a2-normalization-dictionary-v1.yaml","security-knowledge/risks/gost-r-58771-2019-table-a2-normalization-dictionary-regression-v1.json"]: assert required in registry
print("PASS: GOST R 58771-2019 Table A.2 normalization; 82 distinct column/token pairs, 18 direct mappings, 125/336 normalized and 211 pending; literal retained; 64 rules/cases, 18 evidence nodes, 0 automatic selections/defaults")
