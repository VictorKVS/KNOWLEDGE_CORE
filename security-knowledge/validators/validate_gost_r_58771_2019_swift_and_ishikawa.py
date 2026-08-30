#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/risks/gost-r-58771-2019-swift-and-ishikawa-v1.yaml"
FIXTURES=ROOT/"security-knowledge/risks/gost-r-58771-2019-swift-and-ishikawa-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-r-58771-2019-swift-and-ishikawa-observation-2026-08-30.yaml"
REGISTRY=ROOT/"security-knowledge/standards/gost-and-ru-standards-source-registry.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); registry=REGISTRY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["status"]=="Действует"
assert [x["locator"] for x in model["techniques"]]==["Б.2.6","Б.3.3"]
swift,ishikawa=model["techniques"]
assert len(swift["workflow"])==8 and len(swift["prompt_topic_classes"])==5
assert len(swift["inputs"])==4 and len(swift["outputs"])==2
assert len(swift["strengths"])==7 and len(swift["limitations"])==3
assert len(ishikawa["workflow"])==5 and sum(map(len,ishikawa["example_category_sets"]))==11
assert len(ishikawa["inputs"])==3 and len(ishikawa["outputs"])==2
assert len(ishikawa["strengths"])==6 and len(ishikawa["limitations"])==2
assert len(model["rendered_anomalies"])==2 and all(x["status"]=="PENDING_PRIMARY_BYTES" and x["normalization"] is None for x in model["rendered_anomalies"])
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for required in ["id: GOST_R_58771_2019","SWIFT_ISHIKAWA_CLAUSE_CORE","security-knowledge/risks/gost-r-58771-2019-swift-and-ishikawa-v1.yaml","security-knowledge/risks/gost-r-58771-2019-swift-and-ishikawa-regression-v1.json"]: assert required in registry
print("PASS: GOST R 58771-2019 B.2.6/B.3.3 SWIFT and Ishikawa; 2 techniques, 2 rendered anomalies pending, 64 rules/cases, 18 evidence nodes; no completeness, causation, ranking or control-effectiveness invention")
