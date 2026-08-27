#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/legislation/RU/government-decrees/719/section-ix-storage-systems-requirements-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/legislation/RU/government-decrees/719/section-ix-storage-systems-requirements-regression-v1.json")


def threshold(as_of):
    d = date.fromisoformat(as_of)
    if d < date(2022, 10, 15):
        return "BLOCK_PRE_EFFECTIVE_MODEL"
    if d <= date(2022, 12, 31):
        return 110
    if d <= date(2023, 12, 31):
        return 120
    return 150


def evaluate(case):
    q = case["query"]
    if q == "threshold":
        return threshold(case["as_of"])
    if q == "scope":
        if case["code"] in {"26.20.21", "26.20.22"}:
            return "BLOCK_EXCLUDED_CODE"
        if case["code"] != "26.20.2":
            return "BLOCK_WRONG_CODE"
        if not case["storage_system"]:
            return "BLOCK_NOT_STORAGE_SYSTEM"
        if case.get("model_match") is False:
            return "BLOCK_PRODUCT_MODEL_MISMATCH"
        return "IN_SCOPE"
    if q == "ratio":
        russian, total = case["russian"], case["total"]
        if total == 0:
            return "BLOCK_ZERO_DENOMINATOR"
        if total < 0 or russian < 0 or russian > total:
            return "BLOCK_INVALID_COUNTS"
        return case["btop"] * russian / total
    if q == "module_score":
        if case["board_points"] < 50:
            return "BLOCK_SYSTEM_BOARD_BELOW_50"
        if not case["modules"]:
            return "BLOCK_NO_MODULES"
        if any(m["ki"] == 0 for m in case["modules"]):
            return "BLOCK_ZERO_KI"
        return sum(m["bi"] / m["ki"] for m in case["modules"])
    if q == "module_bi":
        if case["confirmation"] == "LEGACY_WITHOUT_SCORE":
            return 50
        if case["confirmation"] == "NONE" and case["actual_points"] < case["minimum"]:
            return "BLOCK_MODULE_MINIMUM_NOT_MET"
        return case["actual_points"]
    if q == "qualification":
        if not case["scope"]:
            return "BLOCK_SCOPE"
        if not case["mandatory_block"]:
            return "BLOCK_MANDATORY_BLOCK"
        if not case["firmware_write"]:
            return "BLOCK_FIRMWARE_WRITE"
        if not case["assembly_test"]:
            return "BLOCK_ASSEMBLY_TEST"
        needed = threshold(case["as_of"])
        if not isinstance(needed, int):
            return needed
        return "PASS" if case["score"] >= needed else f"BLOCK_SCORE_BELOW_{needed}"
    if q == "claim":
        return {
            "SCORE_ALONE_PROVES_ACTIVE_REGISTRY": "REJECT_LIVE_RECORD_REQUIRED",
            "USE_120_POINTS_IN_2026": "REJECT_CURRENT_THRESHOLD_150",
            "K1_MULTIPLIER_1_7": "REJECT_OTHER_ROW_RULE",
            "DOUBLE_COUNT_MODULE_COMPONENTS": "REJECT_FOOTNOTE_32",
            "POINTS_ARE_RETENTION_DAYS": "REJECT_CATEGORY_ERROR",
            "ZERO_DENOMINATOR_MEANS_ZERO_POINTS": "REJECT_UNREGULATED_DENOMINATOR",
        }[case["claim"]]
    raise AssertionError(f"Unhandled query: {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    assert len(model["atomic_rules"]) == len({r["id"] for r in model["atomic_rules"]}) == 40
    assert len(model["temporal_thresholds"]) == 3
    assert len(model["evidence_model"]) == len({r["id"] for r in model["evidence_model"]}) == 18
    assert len(model["operations"]) == 10
    assert model["formula_model"]["electronic_modules"]["exact_glyph"] == "B = Σ_(i = 1, 2 … K) (B_i / K_i)"
    assert model["formula_model"]["proportional_operations"]["exact_glyph"] == "B = B_top × K"
    assert model["temporal_thresholds"][2]["minimum_points"] == 150
    assert model["operations"][6]["mandatory"] is True
    assert model["operations"][7]["mandatory"] is True
    assert model["verification_boundary"]["formula_glyphs_and_image_hashes"] == "VERIFIED"
    assert model["verification_boundary"]["live_registry_snapshot_for_installed_product"].startswith("PENDING")
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert len(fixtures["cases"]) == 56
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 40 rules; 3 threshold routes; 10 operations; 18 evidence nodes; 56 cases; PP719 Section IX storage-system model")


if __name__ == "__main__":
    main()
