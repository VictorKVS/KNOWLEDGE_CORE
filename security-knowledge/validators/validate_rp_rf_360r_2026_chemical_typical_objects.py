#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
import yaml
MODEL=Path("security-knowledge/classification/rp-rf-360r-2026-chemical-rows362-397-atomic-v1.yaml")
FIXTURES=Path("security-knowledge/classification/rp-rf-360r-2026-chemical-rows362-397-regression-v1.json")
EXPECTED_ROWS_SHA256="9a3123d8a00bf999f4c2e7399ef082c836e38d1ff7ea94e24aeac6b677fe5959"
EXPECTED_CODES=["10.89.4", "10.91.3", "13.20.6", "20.11", "20.12", "20.13", "20.14", "20.15", "20.16", "20.2", "20.3", "20.41", "20.42", "20.52", "20.59.1", "20.59.3", "20.59.4", "20.6", "22.1", "22.21", "22.23", "38.21", "38.22", "39"]
def main():
 model=yaml.safe_load(MODEL.read_text(encoding="utf-8"));fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
 rows=model["rows"];shared=model["shared_activity_code_domain"];overlay=model["sector_overlay_dependency"];rules={x["id"]:x["rule"] for x in model["control_rules"]}
 assert model["status"]=="VERIFIED_CURRENT_CHEMICAL_ROWS362_397_SECTOR_OVERLAY_PROJECT_ONLY_FAIL_CLOSED"
 assert [x["row"] for x in rows]==list(range(362,398)) and len(rows)==36 and sum(len(x["processes_ru"]) for x in rows)==65
 assert all(x["object_text_ru"] and x["processes_ru"] for x in rows)
 assert shared["applies_to_rows"]==list(range(362,398)) and shared["codes"]==EXPECTED_CODES and len(shared["entries"])==24
 assert shared["entries"][14]["code"]=="20.59.1" and shared["entries"][14]["title_ru"].count(";")==2
 assert all(x["activity_code_scope"]=="CHEMICAL_COMMON_CODES_362_397" for x in rows)
 canonical=[{"row":x["row"],"object_text_ru":x["object_text_ru"],"processes_ru":x["processes_ru"]} for x in rows]
 digest=hashlib.sha256(json.dumps(canonical,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
 assert digest==model["verification_boundary"]["canonical_rows_sha256"]==EXPECTED_ROWS_SHA256
 assert overlay["status"]=="PROJECT_ONLY_NOT_EXECUTABLE" and overlay["project_id"]=="02/07/06-25/00157760" and overlay["adopted_current_act_identified_in_bounded_search"] is False
 assert model["verification_boundary"]["list_last_row"]==397 and model["verification_boundary"]["synthetic_row398_prohibited"] is True
 assert model["verification_boundary"]["current_rp360r_rows1_397_coverage_with_previous_models"]=="COMPLETE_CURRENT_TEXTUAL_ROW_GATE"
 assert len(rules)==64 and list(rules)==[f"RP360R-CH-{i:03d}" for i in range(1,65)] and len(fixtures["cases"])==64
 fail=[]
 for case in fixtures["cases"]:
  actual=rules[case["rule_id"]]
  if actual!=case["expected"]:fail.append((case["id"],case["expected"],actual))
 if fail:
  for x in fail:print("FAIL",x)
  raise SystemExit(1)
 assert model["verification_boundary"]["critical_gap_created"]==0 and model["verification_boundary"]["high_gap_created"]==0
 print("PASS: RP RF 360-r chemical rows 362-397 and list termination; 36 rows, 65 process groups, 24 activity codes, project-only sector overlay blocked, canonical source-text digest, 64 rules/cases")
if __name__=="__main__":main()

