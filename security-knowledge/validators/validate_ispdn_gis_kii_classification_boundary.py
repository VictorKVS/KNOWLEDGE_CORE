#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
M=ROOT/"security-knowledge/classification/ispdn-gis-kii-classification-boundary-v1.yaml"
R=ROOT/"security-knowledge/classification/ispdn-gis-kii-classification-boundary-regression-v1.json"
O=ROOT/"security-knowledge/evidence/ispdn-gis-kii-classification-observation-2026-09-01.yaml"
I=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
m=json.loads(M.read_text(encoding="utf-8"));r=json.loads(R.read_text(encoding="utf-8"));o=json.loads(O.read_text(encoding="utf-8"));inv=I.read_text(encoding="utf-8")
assert m["id"]==r["model_id"]==o["model_id"]
assert len(m["regimes"]["ISPDN"]["routes"])==15
assert {x["level"] for x in m["regimes"]["ISPDN"]["routes"]}=={1,2,3,4}
assert m["regimes"]["ISPDN"]["literal_threshold_boundary"]["equality_explicitly_routed"] is False
assert len(m["regimes"]["GIS_AND_PUBLIC_BODY_IS"]["matrix"])==9
assert m["regimes"]["GIS_AND_PUBLIC_BODY_IS"]["legacy_basis"]["FSTEC17"]=="REPEALED_2026-03-01"
assert next(x for x in m["sources"] if x["id"]=="FSTEC137")["effective_general"]=="2026-09-01"
assert len(m["regimes"]["KII"]["output"])==4 and "NO_CATEGORY" in m["regimes"]["KII"]["output"]
assert len(m["decision_gates"])==len(m["scenarios"])==8
assert {x["id"] for x in m["scenarios"]}=={x["scenario_id"] for x in r["scenario_expectations"]}
assert len(m["red_team_attacks"])==12 and all(x["blocked"] for x in m["red_team_attacks"])
assert len(m["evidence_artifacts"])==len(m["evidence_nodes"])==len(o["claims"])==18
assert len(m["control_rules"])==len(r["cases"])==64
assert {x["id"] for x in m["control_rules"]}=={x["rule_id"] for x in r["cases"]}
assert all(m["boundaries"].values()) and all(x["expect"]=="BLOCKED" for x in r["adversarial_cases"])
for k,v in r["expected_counts"].items(): assert m["counts"][k]==v
for x in ["ISPDN_GIS_KII_CLASSIFICATION_BOUNDARY","ispdn-gis-kii-classification-boundary-v1.yaml","ispdn-gis-kii-classification-boundary-regression-v1.json"]: assert x in inv
print("PASS: ISPDn/GIS/KII boundary; 15 PDn routes, 9 GIS cells, 4 KII outcomes, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases")
