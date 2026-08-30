#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/fstec-2021-threat-model-lifecycle-bdu-gate-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/fstec-2021-threat-model-lifecycle-bdu-gate-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-2021-threat-model-lifecycle-bdu-observation-2026-08-31.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["approval_date"]=="2021-02-05"
assert len(model["applicability"]["covered_system_classes"])==5
assert len(model["applicability"]["excluded_topics"])==2
assert len(model["assessment_tasks"])==6 and len(model["input_classes"])==8
assert [x["order"] for x in model["assessment_stages"]]==[1,2,3]
assert len(model["model_scope_options"])==3
assert model["cloud_fail_closed_rule"]["assumption"].find("maximum capability")>=0
assert len(model["lifecycle"]["change_triggers"])==4 and model["lifecycle"]["fixed_calendar_period_prescribed"] is False
assert len(model["bdu_gate"]["roles"])==2 and len(model["bdu_gate"]["promotion_test"])==5
assert len(model["bdu_gate"]["decision_states"])==6 and len(model["bdu_gate"]["forbidden_promotions"])==4
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","FSTEK_threat_modeling_methodology","FSTEK_BDU","fstec-2021-threat-model-lifecycle-bdu-gate-v1.yaml","fstec-2021-threat-model-lifecycle-bdu-gate-regression-v1.json"]: assert required in inventory
print("PASS: FSTEC 2021 threat-model lifecycle and BDU gate; 6 tasks, 8 inputs, 3 stages, 3 scope options, 4 triggers, 4 forbidden BDU promotions, 64 rules/cases, 18 evidence nodes; no auto-relevance, fixed period, formula, scale or planned-revision invention")
