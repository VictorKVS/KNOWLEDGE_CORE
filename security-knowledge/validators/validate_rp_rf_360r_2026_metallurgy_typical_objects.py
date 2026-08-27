#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import yaml
MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-metallurgy-rows308-361-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-metallurgy-rows308-361-regression-v1.json")
EXPECTED_ROWS_SHA256 = "bb6c7d9d7ff9dcb31ebf1fe99ff5ab2a95b286bea025bf154a9a8dc1a4f49b0a"
def main():
    model=yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures=json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows=model["rows"];shared=model["shared_activity_code_domain"];overlay=model["sector_overlay_dependency"]
    rules={x["id"]:x["rule"] for x in model["control_rules"]}
    assert model["status"]=="VERIFIED_CURRENT_METALLURGY_ROWS308_361_SECTOR_OVERLAY_PROJECT_ONLY_FAIL_CLOSED"
    assert [x["row"] for x in rows]==list(range(308,362)) and len(rows)==54
    assert all(x["object_text_ru"] and x["processes_ru"] for x in rows)
    assert sum(len(x["processes_ru"]) for x in rows)==188
    assert shared["applies_to_rows"]==list(range(308,362))
    assert shared["codes"]==["24","25.11","25.29","28.99.6","32.12"]
    assert all(x["activity_code_scope"]=="METALLURGY_COMMON_CODES_308_361" for x in rows)
    canonical=[{"row":x["row"],"object_text_ru":x["object_text_ru"],"processes_ru":x["processes_ru"]} for x in rows]
    digest=hashlib.sha256(json.dumps(canonical,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    assert digest==model["verification_boundary"]["canonical_rows_sha256"]==EXPECTED_ROWS_SHA256
    assert overlay["status"]=="PROJECT_ONLY_NOT_EXECUTABLE" and overlay["project_id"]=="02/07/06-25/00157757"
    assert overlay["adopted_current_act_identified_in_bounded_search"] is False
    assert model["verification_boundary"]["next_section_first_row"]==362 and model["verification_boundary"]["next_section"]=="CHEMICAL_INDUSTRY"
    assert len(rules)==64 and list(rules)==[f"RP360R-ME-{i:03d}" for i in range(1,65)] and len(fixtures["cases"])==64
    failures=[]
    for case in fixtures["cases"]:
        actual=rules[case["rule_id"]]
        if actual!=case["expected"]:failures.append((case["id"],case["expected"],actual))
    if failures:
        for failure in failures:print("FAIL",failure)
        raise SystemExit(1)
    assert model["verification_boundary"]["critical_gap_created"]==0 and model["verification_boundary"]["high_gap_created"]==0
    print("PASS: RP RF 360-r metallurgy rows 308-361; 54 rows, 188 process groups, 5 activity codes, project-only sector overlay blocked, canonical source-text digest, 64 rules/cases")
if __name__=="__main__":main()

