#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/liability/koap-13-11-procedure-limitation-routing-v1.yaml"
FIX = ROOT / "security-knowledge/liability/koap-13-11-procedure-limitation-routing-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/koap-13-11-procedure-limitation-observation-2026-08-31.yaml"
m=json.loads(MODEL.read_text(encoding="utf-8")); f=json.loads(FIX.read_text(encoding="utf-8")); o=json.loads(OBS.read_text(encoding="utf-8"))
assert m["id"] == f["model_id"] == o["model_id"]
assert m["limitation"]["personal_data_legislation_period"] == {"value":1,"unit":"year","start_for_completed_offence":"day_of_commission","basis":"article_4_5_parts_1_and_1_1"}
assert m["limitation"]["continuing_offence"]["start"] == "day_of_discovery"
assert m["initiation"]["self_report_exception"]["basis"] == "article_28_1_part_3_5_point_1"
assert m["competence"]["hearing"].startswith("judge")
assert m["protocol_and_transfer"]["clarification"].startswith("within two days")
assert m["protocol_and_transfer"]["transfer"].startswith("within three days")
assert m["hearing"]["judge_base_period"].startswith("two months")
assert m["hearing"]["parts_15_18_special_extension"].startswith("up to three months")
for key,n in f["expected_counts"].items():
    target = m.get(key, f.get("cases") if key == "regression_cases" else None)
    if key == "regression_cases": target=f["cases"]
    assert len(target) == n, (key,len(target),n)
assert [x["id"] for x in m["control_rules"]] == [f"KPR-R{i:03d}" for i in range(1,65)]
assert [x["rule_id"] for x in f["cases"]] == [f"KPR-R{i:03d}" for i in range(1,65)]
assert len(set(x["id"] for x in m["red_team_attacks"])) == 12
assert o["immutable_official_consolidated_bytes"] == "PENDING"
print("PASS koap-13-11-procedure-limitation-routing: 64/64")
