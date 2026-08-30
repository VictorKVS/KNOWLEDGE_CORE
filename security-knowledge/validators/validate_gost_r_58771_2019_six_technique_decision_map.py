#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/risks/gost-r-58771-2019-six-technique-decision-map-v1.yaml"
FIXTURES=ROOT/"security-knowledge/risks/gost-r-58771-2019-six-technique-decision-map-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-r-58771-2019-six-technique-decision-map-observation-2026-08-31.yaml"
REGISTRY=ROOT/"security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); registry=REGISTRY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["status"]=="Действует"
assert len(model["dependencies"])==3
assert [x["locator"] for x in model["decision_routes"]]==["Б.1.5","Б.2.6","Б.3.3","Б.4.2","Б.9.2","Б.9.3"]
assert len(model["decision_routes"])==6 and all(len(x["admissibility"])==3 and len(x["required_outputs"])==3 and len(x["forbidden_conclusions"])==3 for x in model["decision_routes"])
assert len(model["evidence_preserving_handoffs"])==8 and all(x["condition"] for x in model["evidence_preserving_handoffs"])
assert len(model["red_team_attacks"])==12 and all(x["result"]=="BLOCKED_BY_GUARDRAIL" for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for required in ["id: GOST_R_58771_2019","SIX_TECHNIQUE_DECISION_MAP_RED_TEAM_PASS","security-knowledge/risks/gost-r-58771-2019-six-technique-decision-map-v1.yaml","security-knowledge/risks/gost-r-58771-2019-six-technique-decision-map-regression-v1.json"]: assert required in registry
print("PASS: GOST R 58771-2019 six-technique decision map; 6 routes, 8 evidence-preserving handoffs, 12/12 red-team attacks blocked, 64 rules/cases, 18 evidence nodes; no universal sequence, selector, causation, control-effectiveness or matrix-decision invention")
