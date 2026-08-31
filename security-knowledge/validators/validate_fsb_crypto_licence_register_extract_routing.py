#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/"security-knowledge/legislation/RU/fsb-crypto-licence-register-extract-routing-v1.yaml"
FIXTURES=ROOT/"security-knowledge/legislation/RU/fsb-crypto-licence-register-extract-routing-regression-v1.json"
OBS=ROOT/"security-knowledge/evidence/fsb-crypto-licence-register-extract-routing-observation-2026-09-01.yaml"
INVENTORY=ROOT/"security-knowledge/corpus/master-source-inventory.yaml"
model=json.loads(MODEL.read_text(encoding="utf-8")); fixtures=json.loads(FIXTURES.read_text(encoding="utf-8")); obs=json.loads(OBS.read_text(encoding="utf-8")); inventory=INVENTORY.read_text(encoding="utf-8")
assert model["id"]==fixtures["model_id"]==obs["model_id"]
assert model["status"]=="VERIFIED_NORMATIVE_AND_OFFICIAL_ROUTE_LIVE_REGISTER_BYTES_PENDING"
assert len(model["sources"])==7 and len(model["route_separation"])==5
assert len(model["article_21_register_fields"])==15
assert [x["work_id"] for x in model["pp_313_licensed_works"]]==list(range(1,29))
assert sum(len(v) for v in model["pp_313_work_families"].values())==28
assert model["extract_route"]["maximum_working_days"]==3 and model["extract_route"]["daily_application_limit"]==10
assert model["extract_content"]["formation_date_required"] and model["extract_content"]["two_dimensional_barcode_required"]
assert len(model["verification_states"])==len(model["stages"])==8
assert len(model["red_team_attacks"])==12 and all(x["blocked"] for x in model["red_team_attacks"])
assert len(model["evidence_artifacts"])==len(model["evidence_nodes"])==len(obs["claims"])==18
assert len(model["control_rules"])==len(fixtures["cases"])==64
assert {x["id"] for x in model["control_rules"]}=={x["rule_id"] for x in fixtures["cases"]}
assert len(fixtures["adversarial_cases"])==12 and all(x["expect"]=="BLOCKED" for x in fixtures["adversarial_cases"])
assert all(model["boundaries"].values())
for key,value in fixtures["expected_counts"].items(): assert model["counts"][key]==value
for required in ["FSB_CRYPTO_LICENCE_REGISTER_EXTRACT_ROUTING","fsb-crypto-licence-register-extract-routing-v1.yaml","fsb-crypto-licence-register-extract-routing-regression-v1.json"]: assert required in inventory
print("PASS: FSB crypto-licence register/extract route; 15 register fields, 28 works, 3-day extract gate, 18 evidence nodes, 12/12 attacks blocked, 64/64 rules/cases")
