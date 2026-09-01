#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/standards/gost-r-iso-iec-27001-2021-applicability-conformity-v1.yaml"
REG=ROOT/"security-knowledge/standards/gost-r-iso-iec-27001-2021-applicability-conformity-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/gost-r-iso-iec-27001-2021-applicability-observation-2026-09-01.yaml"
INV=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
m=json.loads(MODEL.read_text(encoding="utf-8"));r=json.loads(REG.read_text(encoding="utf-8"));o=json.loads(OBS.read_text(encoding="utf-8"));inv=INV.read_text(encoding="utf-8")
assert m["id"]==r["model_id"]==o["model_id"]
assert m["identity"]=={"designation":"ГОСТ Р ИСО/МЭК 27001-2021","status":"Действует","order":"1653-ст","order_date":"2021-11-30","effective_from":"2022-01-01","replaces":"ГОСТ Р ИСО/МЭК 27001-2006","replaced_by":None,"official_check_date":"2026-09-01"}
assert [x["clause"] for x in m["clause_groups"]]==["4","5","6","7","8","9","10"]
assert len(m["applicability_routes"])==6 and len(m["scenarios"])==8
assert {x["id"] for x in m["scenarios"]}=={x["scenario_id"] for x in r["scenario_expectations"]}
assert len(m["red_team_attacks"])==12 and all(x["blocked"] for x in m["red_team_attacks"])
assert len(m["evidence_artifacts"])==len(m["evidence_nodes"])==len(o["claims"])==18
assert len(m["control_rules"])==len(r["cases"])==64
assert {x["id"] for x in m["control_rules"]}=={x["rule_id"] for x in r["cases"]}
assert len(r["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in r["adversarial_cases"])
assert all(m["boundaries"].values())
for k,v in r["expected_counts"].items(): assert m["counts"][k]==v
for x in ["GOST_ISO_STANDARDS_APPLICABILITY","gost-r-iso-iec-27001-2021-applicability-conformity-v1.yaml","gost-r-iso-iec-27001-2021-applicability-conformity-regression-v1.json"]: assert x in inv
print("PASS: GOST 27001 applicability/conformity; 7 clauses, 6 routes, 8 scenarios, 18 evidence nodes, 12/12 attacks, 64/64 rules/cases")
