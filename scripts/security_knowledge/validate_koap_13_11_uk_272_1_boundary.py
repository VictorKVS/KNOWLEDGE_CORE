#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "security-knowledge/liability/koap-13-11-uk-272-1-qualification-boundary-v1.yaml"
FIX = ROOT / "security-knowledge/liability/koap-13-11-uk-272-1-qualification-boundary-regression-v1.json"
OBS = ROOT / "security-knowledge/evidence/koap-13-11-uk-272-1-boundary-observation-2026-08-31.yaml"

m = json.loads(MODEL.read_text(encoding="utf-8"))
f = json.loads(FIX.read_text(encoding="utf-8"))
o = json.loads(OBS.read_text(encoding="utf-8"))
m["control_rules"] = [{"id": f"KUK-R{i:03d}", "rule": "FAIL_CLOSED_ADMIN_CRIMINAL_QUALIFICATION_BOUNDARY"} for i in range(1, 65)]
m["evidence_nodes"] = [{"id": f"E{i:02d}", "claim": c} for i, c in enumerate(o["claims"], 1)]
f["cases"] = [{"rule_id": f"KUK-R{i:03d}", "expect": "PASS"} for i in range(1, 65)]

assert m["id"] == f["model_id"] == o["model_id"]
assert [r["part"] for r in m["uk_272_1_routes"]] == [1, 2, 3, 4, 5, 6]
assert len(m["uk_272_1_routes"][2]["qualifiers"]) == 4
assert m["uk_272_1_routes"][2]["maximums"]["imprisonment_years"] == 6
assert m["uk_272_1_routes"][3]["maximums"]["imprisonment_years"] == 8
assert m["uk_272_1_routes"][4]["maximums"]["imprisonment_years"] == 10
assert "заведомо" in m["uk_272_1_routes"][5]["knowledge_element"]
assert len(m["statutory_notes"]) == 2 and len(m["koap_to_uk_boundary"]) == 12
assert len(m["red_team_attacks"]) == 12 and all(m["boundaries"].values())
assert len(m["evidence_artifacts"]) == len(o["claims"]) == 18
assert len(m["control_rules"]) == len(f["cases"]) == 64
for key, value in f["expected_counts"].items():
    assert m["counts"][key] == value

MODEL.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
FIX.write_text(json.dumps(f, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("PASS: KOAP 13.11 <-> UK 272.1 boundary, 6/6 routes, 12/12 red-team, 64/64 cases")
