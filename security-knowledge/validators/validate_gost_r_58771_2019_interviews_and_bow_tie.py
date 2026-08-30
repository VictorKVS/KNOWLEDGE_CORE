#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/risks/gost-r-58771-2019-interviews-and-bow-tie-v1.yaml"
FIXTURES=ROOT/"security-knowledge/risks/gost-r-58771-2019-interviews-and-bow-tie-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-r-58771-2019-interviews-and-bow-tie-observation-2026-08-30.yaml"
REGISTRY=ROOT/"security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); registry=REGISTRY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["status"]=="Действует"
assert [x["locator"] for x in model["techniques"]]==["Б.1.5","Б.4.2"]
interview,bow=model["techniques"]
assert len(interview["variants"])==2 and len(interview["question_design_constraints"])==7
assert len(interview["inputs"])==3 and len(interview["outputs"])==1
assert len(interview["strengths"])==3 and len(interview["limitations"])==5
assert len(bow["diagram_components"])==9 and len(bow["quantification_preconditions"])==3
assert len(bow["inputs"])==3 and len(bow["outputs"])==4
assert len(bow["strengths"])==4 and len(bow["limitations"])==2
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for required in ["id: GOST_R_58771_2019","INTERVIEWS_BOW_TIE_CLAUSE_CORE","security-knowledge/risks/gost-r-58771-2019-interviews-and-bow-tie-v1.yaml","security-knowledge/risks/gost-r-58771-2019-interviews-and-bow-tie-regression-v1.json"]: assert required in registry
print("PASS: GOST R 58771-2019 B.1.5/B.4.2 interviews and bow-tie; 2 techniques, 10 clause groups, 64 rules/cases, 18 evidence nodes; no questionnaire, probabilities or automatic control-effectiveness claims")
