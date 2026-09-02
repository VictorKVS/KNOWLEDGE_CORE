#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/standards/gost-iso-27000-digital-investigation-method-analysis-process-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/standards/gost-iso-27000-digital-investigation-method-analysis-process-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-iso-27000-digital-investigation-method-analysis-process-observation-2026-09-02.yaml"
MASTER=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); master=MASTER.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert len(model["routes"])==model["counts"]["selected_routes"]==3
assert all(x["jurisdiction"]=="INTERNATIONAL_ONLY_IN_THIS_MODEL" for x in model["routes"])
assert all(x["national_status"].startswith("PENDING_") for x in model["routes"])
assert sum("90.20" in x["international_status"] for x in model["routes"])==model["counts"]["under_systematic_review"]==2
assert sum("90.60" in x["international_status"] for x in model["routes"])==model["counts"]["close_of_review"]==1
assert [x["order"] for x in model["decision_gates"]]==list(range(1,9))
assert len(model["scenarios"])==8
assert len(model["red_team_attacks"])==12 and all(x["result"]=="BLOCKED" for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["evidence_nodes"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
routes={x["id"]:x for x in model["routes"]}
assert "METHOD_SUITABILITY" in routes["ISO_IEC_27041_2015"]["role"]
assert "ANALYSIS_AND_INTERPRETATION" in routes["ISO_IEC_27042_2015"]["role"]
assert "IDEALIZED_COMMON_PROCESS" in routes["ISO_IEC_27043_2015"]["scope_boundary"]
actual={x["id"]:x["rule"] for x in model["control_rules"]}
for case in fixtures["cases"]: assert actual[case["rule_id"]]==case["expected"]
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
for path in (MODEL,FIXTURES,OBS): assert str(path.relative_to(ROOT)) in master
print("PASS: ISO 27041/27042/27043; 3 ISO-only PENDING-RU routes; 2 review + 1 close-of-review; 64/64 rules/cases; red-team 12/12; evidence 18/18")

