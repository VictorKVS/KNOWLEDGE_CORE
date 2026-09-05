#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/classification/gis-fstec-117-137-temporal-amendment-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/gis-fstec-117-137-temporal-amendment-regression-v1.json")
CURRENT_SLICE = Path("security-knowledge/classification/gis-fstec-117-transition-and-classification-verified.yaml")
FSTEC_DOC = Path("security-knowledge/legislation/RU/regulators/FSTEK/117-2025/document.yaml")
FSB_DOC = Path("security-knowledge/legislation/RU/regulators/FSB/117-2025/document.yaml")
CHANGE_GRAPH = Path("security-knowledge/legislation/RU/regulators/FSTEK/change-graph.yaml")


def d(value):
    return date.fromisoformat(value)


def version(as_of):
    value = d(as_of)
    if value < d("2026-03-01"):
        return "GIS-V1-ORDER17-HISTORICAL"
    if value < d("2026-09-01"):
        return "GIS-V2-ORDER117-ORIGINAL"
    if value < d("2027-03-01"):
        return "GIS-V3-ORDER117-WITH-137-GENERAL"
    return "GIS-V4-ORDER117-WITH-137-FULL"


def current_date_status(as_of):
    value = d(as_of)
    if value < d("2026-09-01"):
        return "ORDER117_ORIGINAL_CURRENT_ORDER137_REGISTERED_FUTURE"
    if value < d("2027-03-01"):
        return "ORDER117_WITH_137_GENERAL_CURRENT_ITEM7_FUTURE"
    return "ORDER117_WITH_137_FULL_CURRENT"


def evaluate(case):
    q = case["query"]
    as_of = case.get("as_of")
    if q == "version": return version(as_of)
    if q == "order17_current": return "HISTORICAL_VERSION_APPLIES_BY_EVENT_DATE" if d(as_of) < d("2026-03-01") else "REJECT_REPEALED_CURRENT_BASELINE"
    if q == "order137_general": return "NOT_YET_EFFECTIVE" if d(as_of) < d("2026-09-01") else "EFFECTIVE_ITEMS_1_TO_6_AND_8_TO_18"
    if q == "order137_item7": return "NOT_YET_EFFECTIVE" if d(as_of) < d("2027-03-01") else "EFFECTIVE_POINT32_REPLACED"
    if q == "point32_kzi_interval": return "6_MONTH_MAXIMUM" if d(as_of) < d("2027-03-01") else "6_MONTH_MAXIMUM_OPERATOR_OR_HOLDER"
    if q == "point32_maturity_indicator":
        return "UZI_CONTRACTOR_BEFORE_ACCESS_AND_2_YEAR_MAXIMUM" if d(as_of) >= d("2027-03-01") else ("PZI_2_YEAR_MAXIMUM_POINT32_NOT_YET_REPLACED" if d(as_of) >= d("2026-09-01") else "PZI_2_YEAR_MAXIMUM")
    if q in {"head_notice", "fstec_submission"}:
        if d(as_of) >= d("2027-03-01") and case["indicator"] == "PZI": return "NOT_IN_REPLACED_POINT32"
        return "3_CALENDAR_DAYS" if q == "head_notice" else "5_WORKING_DAYS"
    if q == "point31_label": return "UZI" if d(as_of) >= d("2026-09-01") else "PZI"
    if q == "authentication_option": return "STRICT_OR_ENHANCED_MULTIFACTOR" if d(as_of) >= d("2026-09-01") else "ORIGINAL_STRICT_ROUTE"
    if q == "contractor_uzi_training": return "IN_SCOPE_OF_POINT58_TRAINING" if d(as_of) >= d("2026-09-01") else "AMENDMENT_NOT_YET_EFFECTIVE"
    fixed = {
        "publication_id_137": "VERIFIED_0001202608110006",
        "fstec117_vs_fsb117": "DISTINCT_PARALLEL_NONCRYPTO_AND_CRYPTO_ACTS",
        "gis_is_also_ispdn": "CUMULATIVE_APPLICABILITY_REVIEW_NO_SILENT_REPLACEMENT",
        "class_equivalence": "REJECT_K_CLASS_IS_NOT_PP1119_LEVEL",
        "delete_constant_effect": "DO_NOT_INFER_MONITORING_DUTY_REPEALED",
        "item_count": 18,
        "item7_target": "FULL_POINT32_REPLACEMENT",
        "general_item_set": "1_TO_6_AND_8_TO_18",
        "fsb378_repealed_by_fsb117": "NOT_PROVEN_DO_NOT_INFER",
        "crypto_scope": "ROUTE_TO_SEPARATE_FSB117_AND_IF_ISPDN_FSB378_REVIEW",
        "red_team": "PASS_TEMPORAL_ROUTER_FAIL_GLOBAL_SCOPE_INCOMPLETE",
    }
    if q in fixed: return fixed[q]
    if q == "legacy_attestation": return "NOT_AUTOMATICALLY_INVALIDATED" if d(case["issued"]) < d("2026-03-01") else "ROUTE_TO_CURRENT_ATTESTATION_RULES"
    if q == "apply_all_137": return "ALLOW_ALL_ITEMS" if d(as_of) >= d("2027-03-01") else "BLOCK_ITEM7_PREMATURE"
    if q == "current_date_status": return current_date_status(as_of)
    raise AssertionError(f"Unhandled query {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    current = yaml.safe_load(CURRENT_SLICE.read_text(encoding="utf-8"))
    fstec = yaml.safe_load(FSTEC_DOC.read_text(encoding="utf-8"))
    fsb = yaml.safe_load(FSB_DOC.read_text(encoding="utf-8"))
    graph = yaml.safe_load(CHANGE_GRAPH.read_text(encoding="utf-8"))
    rules = model["amendment_rules"]
    assert len(rules) == len({r["id"] for r in rules}) == 18
    assert {r["item"] for r in rules} == set(range(1, 19))
    assert next(r for r in rules if r["item"] == 7)["effective_from"] == "2027-03-01"
    assert all(r["effective_from"] == "2026-09-01" for r in rules if r["item"] != 7)
    assert len(model["version_router"]) == 4
    assert len(model["integration_boundaries"]) == 10
    assert len(model["evidence_model"]) == 10
    amending = model["sources"]["amending_order"]
    assert amending["official_publication_identity"] == "VERIFIED"
    assert amending["official_publication_number"] == "0001202608110006"
    assert amending["official_publication_date"] == "2026-08-11"
    assert amending["general_effective_from"] == "2026-09-01"
    assert amending["amendment_item_7_effective_from"] == "2027-03-01"
    assert amending["immutable_official_publication_bytes"] == "PENDING"
    assert current["source"]["future_amendment"]["number"] == "137"
    assert fstec["future_amendments"][0]["id"] == "FSTEK-137-2026"
    assert fsb["id"] == "FSB-117-2025" and fstec["id"] == "FSTEK-117-2025"
    assert "FSTEK-137-2026" in graph["nodes"]
    assert any(e["from"] == "FSTEK-137-2026" and e["to"] == "FSTEK-117-2025" for e in graph["edges"])
    assert len(fixtures["cases"]) == 48
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case)
        if actual != case["expected"]: failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures: print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: publication 0001202608110006 verified; 4 temporal versions; 18 amendment items; 10 boundaries; 10 evidence nodes; 48 cases")


if __name__ == "__main__":
    main()
