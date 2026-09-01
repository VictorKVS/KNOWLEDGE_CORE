#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/liability/tk-worker-pdn-disciplinary-material-liability-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/liability/tk-worker-pdn-disciplinary-material-liability-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/tk-worker-pdn-disciplinary-material-liability-observation-2026-09-01.yaml"
MASTER=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); master=MASTER.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["provisions"])==16
assert [x["order"] for x in model["stages"]]==list(range(1,9))
assert len(model["clock_rules"])==8
assert {x["id"] for x in model["clock_rules"]}==set(fixtures["expected_clock_ids"])
assert model["disciplinary_sanctions"]==["REMARK","REPRIMAND","DISMISSAL_ON_APPLICABLE_GROUND"]
assert len(model["full_liability_grounds"])==8 and len(model["article239_exclusions"])==5
assert len(model["decision_gates"])==len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for k,v in fixtures["expected_counts"].items(): assert model["counts"][k]==v
for path in ["security-knowledge/liability/tk-worker-pdn-disciplinary-material-liability-routing-v1.yaml","security-knowledge/liability/tk-worker-pdn-disciplinary-material-liability-routing-regression-v1.json"]: assert path in master
print("PASS: TK worker PDn disciplinary/material liability; 16 provisions, 8 clocks, 64/64 rules/cases, red-team 12/12, evidence 18/18")
