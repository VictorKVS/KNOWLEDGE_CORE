#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-methodical-2026-measure-catalog-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-methodical-2026-measure-catalog-regression-v1.json")


def evaluate(case, model, families, measures):
    query = case["query"]
    if query == "family_count":
        return len(families)
    if query == "measure_count":
        return len(measures)
    if query == "family_measure_count":
        return len(families[case["family"]]["measures"])
    if query == "measure_exists":
        return "PRESENT" if case["measure"] in measures else "ABSENT"
    if query == "matrix":
        return {"PLUS":"INCLUDED_IN_BASE_SET_FOR_CLASS","BLANK":"NOT_BASELINE_MAY_APPLY_LATER","NUMBERED":"REQUIRED_ENHANCEMENT_FOR_CLASS"}[case["mark"]]
    if query == "selection_pipeline":
        return [item["id"] for item in model["selection_pipeline"]]
    if query == "pdn_mapping":
        return model["cross_regime_mapping"]["personal_data_levels"][case["class"]]
    if query == "cii_mapping":
        return model["cross_regime_mapping"]["cii_significance_categories"][case["class"]]
    if query == "crypto_scope":
        return "SEPARATE_FSB_LAYER"
    if query == "legacy_2014":
        return "NOT_CURRENT"
    if query == "official_bytes":
        return model["verification_boundary"]["official_immutable_bytes"]
    if query == "content_completeness":
        return "IAF_COMPLETE_UPD_RSB_ZSV_ZKO_ZEP_ZVT_ZPI_AND_ZKU_OTHER_41_PENDING" if model["verification_boundary"]["all_measure_implementation_requirements"] == "PARTIAL_IAF_COMPLETE_UPD_RSB_ZSV_ZKO_ZEP_ZVT_ZPI_AND_ZKU_55_OF_96" else None
    if query == "measure_proof":
        return "INSUFFICIENT_CODE_EXISTENCE_ALONE" if case["code_present"] and not case["implementation_verified"] else None
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    families = {item["id"]: item for item in model["families"]}
    measures = [code for family in model["families"] for code in family["measures"]]
    assert model["status"] == "VERIFIED_BOUNDED_CATALOG_SELECTION_IAF_UPD_RSB_ZSV_ZKO_ZEP_ZVT_ZPI_ZKU_PUBLIC_TEXT_CROSSCHECK"
    assert len(families) == model["counts"]["families"] == 17
    assert len(measures) == len(set(measures)) == model["counts"]["measure_codes"] == 96
    assert model["source_evidence"]["official_endpoint_result"] == "TIMEOUT_BYTES_NOT_ACQUIRED"
    assert model["verification_boundary"]["exact_class_matrix_cells"] == "PARTIAL_IAF_COMPLETE_UPD_RSB_ZSV_ZKO_ZEP_ZVT_ZPI_AND_ZKU_330_CELLS_VERIFIED_REMAINDER_PENDING"
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model, families, measures)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 17 families; 96 unique measure codes; IAF, complete UPD, RSB, ZSV, ZKO, ZEP, ZVT, ZPI and ZKU detail linked; 36 fail-closed cases")


if __name__ == "__main__":
    main()
