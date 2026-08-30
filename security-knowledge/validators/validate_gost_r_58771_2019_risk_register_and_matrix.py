#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/risks/gost-r-58771-2019-risk-register-and-matrix-v1.yaml"
FIXTURES=ROOT/"security-knowledge/risks/gost-r-58771-2019-risk-register-and-matrix-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-r-58771-2019-risk-register-and-matrix-observation-2026-08-30.yaml"
REGISTRY=ROOT/"security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); registry=REGISTRY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["status"]=="Действует"
assert [x["locator"] for x in model["techniques"]]==["Б.9.2","Б.9.3"]
register,matrix=model["techniques"]
assert len(register["usual_core_contents"])==4 and len(register["inputs"])==2 and len(register["outputs"])==1
assert len(register["strengths"])==3 and len(register["limitations"])==5
assert len(matrix["design_constraints"])==7 and len(matrix["inputs"])==4 and len(matrix["outputs"])==1
assert len(matrix["strengths"])==4 and len(matrix["limitations"])==10
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for required in ["id: GOST_R_58771_2019","REGISTER_MATRIX_B9_CLAUSE_CORE","security-knowledge/risks/gost-r-58771-2019-risk-register-and-matrix-v1.yaml","security-knowledge/risks/gost-r-58771-2019-risk-register-and-matrix-regression-v1.json"]: assert required in registry
print("PASS: GOST R 58771-2019 B.9.2/B.9.3 register and matrix; 2 techniques, 10 clause groups, 64 rules/cases, 18 evidence nodes; no universal matrix, formula, scale, threshold or automatic priority")
