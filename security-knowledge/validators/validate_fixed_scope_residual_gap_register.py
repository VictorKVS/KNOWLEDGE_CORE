#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/audits/fixed-scope-residual-gap-register-2026-09-02-v1.yaml"
FIX=ROOT/"security-knowledge/audits/fixed-scope-residual-gap-register-2026-09-02-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fixed-scope-residual-gap-register-observation-2026-09-02.yaml"
INV=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
SCORE=ROOT/"security-knowledge/coverage/coverage-scorecard-2026-09-02-run379.json"
m=json.loads(MODEL.read_text(encoding="utf-8")); f=json.loads(FIX.read_text(encoding="utf-8")); o=json.loads(OBS.read_text(encoding="utf-8")); s=json.loads(SCORE.read_text(encoding="utf-8")); inv=INV.read_text(encoding="utf-8")
assert m["id"]==f["model_id"]==o["model_id"]
for k,v in f["expected_counts"].items(): assert m["counts"][k]==v,(k,m["counts"][k],v)
assert [x["id"] for x in m["gap_families"]]==[f"M{i:02d}" for i in range(1,10)]
assert all(x["status"].startswith("PENDING") for x in m["gap_families"])
assert len({x["blocked_claim"] for x in m["gap_families"]})==9
assert len(m["evidence_nodes"])==len(o["claims"])==18
assert len(m["red_team_attacks"])==12 and all(m["boundaries"].values())
assert {x["id"] for x in m["control_rules"]}=={x["rule_id"] for x in f["cases"]}=={f"FGR-{i:03d}" for i in range(1,65)}
assert all(x["expect"]=="PASS_OR_EXPLICIT_PENDING" for x in f["cases"])
assert s["inventory"]=={"verified":293,"pending":31} and s["gaps"]=={"critical":0,"high":0,"medium":9}
for token in ["FIXED_SCOPE_RESIDUAL_GAP_REGISTER","fixed-scope-residual-gap-register-2026-09-02-v1.yaml","validate_fixed_scope_residual_gap_register.py"]: assert token in inv
print("PASS: fixed-scope residual gap register; 9 Medium families, 0 Critical, 0 High; 64/64 cases; red-team 12/12")
