#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-mining-industry-rows269-307-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-mining-industry-rows269-307-regression-v1.json")
EXPECTED_ROWS_SHA256 = "083924a54a0e32e79f1842c9216cbf0e841a0deab51c50a5b1dffc7abe2efe9e"

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows = model["rows"]
    shared = model["shared_activity_code_domain"]
    overlay = model["sector_overlay_dependency"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_MINING_ROWS269_307_SECTOR_OVERLAY_PROJECT_ONLY_FAIL_CLOSED"
    assert [row["row"] for row in rows] == list(range(269, 308))
    assert len(rows) == 39
    assert all(row["object_text_ru"] and row["processes_ru"] for row in rows)
    assert sum(len(row["processes_ru"]) for row in rows) == 115
    assert shared["applies_to_rows"] == list(range(269, 308))
    assert shared["codes"] == ["07", "08", "23.5", "23.99.4", "32.12"]
    assert shared["entries"][1]["exclusion"]["code"] == "08.92"
    assert all(row["activity_code_scope"] == "MINING_COMMON_CODES_269_307" for row in rows)
    canonical = [
        {"row": row["row"], "object_text_ru": row["object_text_ru"], "processes_ru": row["processes_ru"]}
        for row in rows
    ]
    digest = hashlib.sha256(
        json.dumps(canonical, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == model["verification_boundary"]["canonical_rows_sha256"] == EXPECTED_ROWS_SHA256
    assert overlay["status"] == "PROJECT_ONLY_NOT_EXECUTABLE"
    assert overlay["project_id"] == "02/07/06-25/00157758"
    assert overlay["adopted_current_act_identified_in_bounded_search"] is False
    assert model["verification_boundary"]["next_section_first_row"] == 308
    assert model["verification_boundary"]["next_section"] == "METALLURGICAL_INDUSTRY"
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-MI-{i:03d}" for i in range(1, 65)]
    assert len(fixtures["cases"]) == 64
    failures = []
    for case in fixtures["cases"]:
        actual = rules[case["rule_id"]]
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    assert model["verification_boundary"]["critical_gap_created"] == 0
    assert model["verification_boundary"]["high_gap_created"] == 0
    print("PASS: RP RF 360-r mining rows 269-307; 39 rows, 115 process groups, 5 activity codes with 08.92 exclusion, project-only sector overlay blocked, canonical source-text digest, 64 rules/cases")

if __name__ == "__main__":
    main()

