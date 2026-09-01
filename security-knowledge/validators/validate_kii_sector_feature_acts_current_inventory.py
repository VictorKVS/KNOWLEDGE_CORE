#!/usr/bin/env python3
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
M = ROOT / "security-knowledge/classification/kii-sector-feature-acts-current-inventory-v1.yaml"
R = ROOT / "security-knowledge/classification/kii-sector-feature-acts-current-inventory-regression-v1.json"
O = ROOT / "security-knowledge/evidence/kii-sector-feature-acts-current-inventory-observation-2026-09-01.yaml"
I = ROOT / "security-knowledge/corpus/master-source-inventory.yaml"
m=json.loads(M.read_text(encoding="utf-8")); r=json.loads(R.read_text(encoding="utf-8")); o=json.loads(O.read_text(encoding="utf-8")); inv=I.read_text(encoding="utf-8")
assert m["id"] == r["model_id"] == o["model_id"]
assert len(m["adopted_sector_feature_acts"]) == 7
assert len(m["project_only_or_not_identified_sectors"]) == 6
assert {x["sector"] for x in m["adopted_sector_feature_acts"]} >= {"ATOMIC_ENERGY","BANKING_AND_FINANCIAL_MARKET","SCIENCE","COMMUNICATIONS","DEFENSE_INDUSTRY"}
assert all(x["state_as_of_2026_09_01"] == "ADOPTED_CURRENT" for x in m["adopted_sector_feature_acts"])
assert all(x["normative_effect"] == "NONE_FROM_PROJECT_STATUS_ALONE" for x in m["project_only_or_not_identified_sectors"])
assert next(x for x in m["adopted_sector_feature_acts"] if x["sector"]=="COMMUNICATIONS")["valid_from"] == "2026-09-01"
assert len(m["decision_gates"]) == len(m["scenarios"]) == 8
assert len(m["red_team_attacks"]) == 12 and all(x["blocked"] for x in m["red_team_attacks"])
assert len(m["evidence_nodes"]) == len(o["claims"]) == 18
assert len(m["control_rules"]) == len(r["cases"]) == 64
assert {x["id"] for x in m["control_rules"]} == {x["rule_id"] for x in r["cases"]}
assert all(x["expected"] == "BLOCKED" for x in r["adversarial_cases"])
assert all(m["boundaries"].values())
for k,v in r["expected_counts"].items(): assert m["counts"][k] == v
for marker in ["KII_SECTOR_FEATURE_ACTS_CURRENT_INVENTORY","kii-sector-feature-acts-current-inventory-v1.yaml","kii-sector-feature-acts-current-inventory-regression-v1.json"]: assert marker in inv
print("PASS: 7 adopted sector acts, 6 project/pending sectors, 8 gates/scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases")
