#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import yaml

MODEL = Path("security-knowledge/classification/rp-rf-360r-2026-rocket-space-rows196-268-pp356-crosswalk-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/rp-rf-360r-2026-rocket-space-rows196-268-pp356-crosswalk-regression-v1.json")
EXPECTED_ROWS_SHA256 = "0ca655c576490238526f8003197cbc57e272543a3af469e4a9296a3c15f87367"

def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    rows = model["rows"]
    shared = model["shared_activity_code_domain"]
    overlay = model["pp356_overlay_dependency"]
    rules = {item["id"]: item["rule"] for item in model["control_rules"]}
    assert model["status"] == "VERIFIED_CURRENT_ROCKET_SPACE_ROWS196_268_PP356_TEXT_FORMULA_IMAGES_FAIL_CLOSED"
    assert [row["row"] for row in rows] == list(range(196, 269))
    assert len(rows) == 73
    assert all(row["object_text_ru"] and row["processes_ru"] for row in rows)
    assert sum(len(row["processes_ru"]) for row in rows) == 151
    assert shared["applies_to_rows"] == list(range(196, 269))
    assert len(shared["codes"]) == len(set(shared["codes"])) == 15
    assert all(row["activity_code_scope"] == "ROCKET_SPACE_COMMON_CODES_196_268" for row in rows)
    canonical = [
        {"row": row["row"], "object_text_ru": row["object_text_ru"], "processes_ru": row["processes_ru"]}
        for row in rows
    ]
    digest = hashlib.sha256(
        json.dumps(canonical, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == model["verification_boundary"]["canonical_rows_sha256"] == EXPECTED_ROWS_SHA256
    assert overlay["effective_from"] == "2026-04-09"
    assert overlay["indicator_applicability_routes"] == 5
    assert overlay["formula_images_blocked"] == 4
    assert overlay["variable_glyph_images_blocked"] == 2
    assert overlay["positions13_and13_1_dependency"] == "CURRENT_PP796_TEXT_MODEL_NUMERIC_IMAGES_FAIL_CLOSED"
    assert len(rules) == 64
    assert list(rules) == [f"RP360R-RS-{i:03d}" for i in range(1, 65)]
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
    print("PASS: RP RF 360-r rocket-space rows 196-268 plus PP RF 356; 73 rows, 151 process groups, 15 codes, canonical source-text digest, 6 image fragments blocked, 64 rules/cases")

if __name__ == "__main__":
    main()
