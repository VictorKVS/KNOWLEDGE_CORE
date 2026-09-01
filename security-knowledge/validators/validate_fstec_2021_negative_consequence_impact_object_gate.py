#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/threats/fstec-2021-negative-consequence-impact-object-gate-v1.yaml"
FIXTURES=ROOT/"security-knowledge/threats/fstec-2021-negative-consequence-impact-object-gate-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fstec-2021-negative-consequence-impact-object-observation-2026-09-01.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"

model=json.loads(MODEL.read_text(encoding="utf-8"))
fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
obs=json.loads(OBS.read_text(encoding="utf-8"))
inventory=INVENTORY.read_text(encoding="utf-8")

assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["source"]["approval_date"]=="2021-02-05"
assert "not" in model["revision_boundary"]["current_effect"].lower() or "не является" in model["revision_boundary"]["current_effect"]
assert len(model["negative_consequence_stage"]["inputs"])==5
assert len(model["negative_consequence_stage"]["event_outcome_classes"])==3
assert len(model["appendix4_risk_types"]["types"])==3
assert [len(x["typical_consequences"]) for x in model["appendix4_risk_types"]["types"]]==[11,25,30]
assert model["appendix4_risk_types"]["typical_not_exhaustive"] is True
assert model["appendix4_risk_types"]["must_be_concretized"] is True
assert len(model["impact_object_stage"]["inputs"])==5
assert len(model["impact_object_stage"]["object_groups"])==8
assert len(model["impact_object_stage"]["impact_types"])==6
assert len(model["impact_object_stage"]["architecture_levels"])==5
assert len(model["impact_object_stage"]["lifecycle_contexts"])==2
assert len(model["appendix5_example_bindings"])==18
assert len(model["decision_gates"])==len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12
assert {x["blocked_by"] for x in model["red_team_attacks"]}<={x["id"] for x in model["decision_gates"]}
assert len(model["evidence_artifacts"])==18
assert len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items():
    assert model["counts"][key]==value
for required in ["THREAT_MODELING_AND_THREAT_CATALOGS","fstec-2021-negative-consequence-impact-object-gate-v1.yaml","fstec-2021-negative-consequence-impact-object-gate-regression-v1.json"]:
    assert required in inventory
print("PASS: FSTEC 2021 clauses 3.1-4.9 and appendices 4-5; 3 risk types, 66 typical consequences, 8 object groups, 6 impact types, 18 example bindings, 64 rules/cases, 12/12 red-team attacks blocked")
