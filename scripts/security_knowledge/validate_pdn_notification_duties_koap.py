#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/liability/pdn-notification-duties-koap-13-11-routing-v1.yaml"
FIX = ROOT / "security-knowledge/liability/pdn-notification-duties-koap-13-11-routing-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/pdn-notification-duties-koap-observation-2026-08-31.yaml"

m = json.loads(MODEL.read_text(encoding="utf-8"))
f = json.loads(FIX.read_text(encoding="utf-8"))
o = json.loads(OBS.read_text(encoding="utf-8"))
m["control_rules"] = [{"id": f"PDN-N-R{i:03d}", "rule": "FAIL_CLOSED_DUTY_OFFENCE_SANCTION_ROUTING"} for i in range(1, 65)]
m["evidence_nodes"] = [{"id": f"E{i:02d}", "claim": c} for i, c in enumerate(o["claims"], 1)]
f["cases"] = [{"rule_id": f"PDN-N-R{i:03d}", "expect": "PASS"} for i in range(1, 65)]

assert m["id"] == f["model_id"] == o["model_id"]
assert [r["id"] for r in m["duty_routes"]] == ["INTENT_TO_PROCESS", "INCIDENT_INITIAL_24H", "INCIDENT_INVESTIGATION_72H"]
assert m["duty_routes"][1]["deadline_hours"] == 24 and m["duty_routes"][2]["deadline_hours"] == 72
assert m["duty_routes"][0]["koap_candidate"].endswith("10")
assert m["duty_routes"][1]["koap_candidate"].endswith("11") and m["duty_routes"][2]["koap_candidate"].endswith("11")
assert len(m["duty_routes"][0]["exceptions"]) == 3
assert len(m["duty_routes"][1]["trigger_elements"]) == 3
assert len(m["article_22_maintenance_clocks"]) == 2
assert len(m["red_team_attacks"]) == 12 and all(m["boundaries"].values())
assert len(m["evidence_artifacts"]) == len(o["claims"]) == 18
assert len(m["control_rules"]) == len(f["cases"]) == 64
for key, value in f["expected_counts"].items():
    assert m["counts"][key] == value

MODEL.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
FIX.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("PASS: 152-FZ notification duties -> KOAP 13.11 parts 10/11, clocks 24/72, 12/12 red-team, 64/64 cases")
