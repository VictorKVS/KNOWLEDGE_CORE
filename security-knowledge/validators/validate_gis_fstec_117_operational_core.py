#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

import yaml

MODEL = Path("security-knowledge/classification/gis-fstec-117-operational-core-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/classification/gis-fstec-117-operational-core-regression-v1.json")
TEMPORAL = Path("security-knowledge/classification/gis-fstec-117-137-temporal-amendment-atomic-v1.yaml")


def evaluate(case, model):
    q = case["query"]
    if q == "version":
        when = date.fromisoformat(case["as_of"])
        if when < date(2026, 3, 1):
            return "HISTORICAL_ORDER17_ROUTE"
        if when < date(2026, 9, 1):
            return "ORDER117_ORIGINAL"
        if when < date(2027, 3, 1):
            return "ORDER117_WITH_ORDER137_GENERAL"
        return "ORDER117_WITH_ORDER137_FULL"
    if q == "vulnerability_deadline":
        return {"CRITICAL":"24_HOURS", "HIGH":"7_CALENDAR_DAYS"}.get(case["severity"], "INTERNAL_REGULATION")
    if q == "bdu_notice":
        return "NO_CLAUSE38_NEW_VULNERABILITY_NOTICE" if case["in_bdu"] else "5_WORKING_DAYS_FROM_DETECTION"
    if q == "recovery":
        return {"K1":"24_HOURS", "K2":"7_CALENDAR_DAYS", "K3":"4_WEEKS"}[case["class"]]
    if q == "backup_drill":
        return "AT_LEAST_ONCE_EVERY_2_YEARS"
    if q == "knowledge_assessment":
        return "AFTER_INCIDENT" if case["incident"] else "AT_LEAST_ONCE_EVERY_3_YEARS"
    if q == "protection_control":
        return "AFTER_INCIDENT" if case["incident"] else "AT_LEAST_ONCE_EVERY_3_YEARS"
    if q == "control_report":
        return {"LEADERSHIP":"3_WORKING_DAYS_FROM_COMPLETION", "FSTEC":"5_WORKING_DAYS_FROM_COMPLETION"}[case["target"]]
    if q == "adversary":
        return model["class_routes"]["adversary_capability_clause_64"][case["class"]]
    if q == "szi":
        return {"K1":"MIN_CLASS_AND_TRUST_4", "K2":"MIN_CLASS_AND_TRUST_5", "K3":"CLASS_AND_TRUST_6"}[case["class"]]
    if q == "attestation":
        return "MANDATORY_BEFORE_PROCESSING_OR_STORAGE" if case["system"] == "GIS" else "HEAD_OR_RESPONSIBLE_PERSON_DECISION"
    if q == "selection_step":
        return {1:"IMPLEMENT_BASELINE", 2:"ADAPT_TO_SYSTEM", 3:"VERIFY_SUPPLEMENT_OR_STRENGTHEN"}[case["step"]]
    if q == "compensating":
        return "IMPLEMENT_REQUIRED_MEASURE" if case["required_measure_possible"] else "DESIGN_DEPLOY_JUSTIFY_AND_PROVE_EFFECTIVENESS"
    if q == "lifecycle":
        return "ROUTE_PP676" if case["system"] == "GIS" else "ROUTE_GOST_R_51583_2014_SECTION_5"
    if q == "completeness":
        return "BOUNDED_SLICE_NOT_ALL_73_CLAUSES"
    if q == "crypto":
        return "ROUTE_SEPARATE_FSB_REQUIREMENTS"
    if q == "count":
        return str(len(model["process_directions_clause_34"] if case["family"] == "CLAUSE34" else model["base_measure_families_clause_63"]))
    raise AssertionError(f"Unhandled query: {q}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    temporal = yaml.safe_load(TEMPORAL.read_text(encoding="utf-8"))
    assert model["status"] == "VERIFIED_CURRENT_BOUNDED_SLICE"
    assert len(model["process_directions_clause_34"]) == 21
    assert len(model["base_measure_families_clause_63"]) == 17
    assert len(model["measure_selection_pipeline_clause_62"]) == 3
    assert len(model["numeric_and_triggered_rules"]) == 12
    assert len(model["protection_control_clause_66"]["methods"]) == 4
    assert model["verification_boundary"]["complete_clauses_1_to_73_atomization"] == "PENDING"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False
    assert temporal["id"] == "RU-FSTEC117-137-GIS-TEMPORAL-AMENDMENT-ATOMIC-V1"
    assert len(fixtures["cases"]) == 40
    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 21 process directions; 17 base families; 12 numeric/trigger rules; 40 cases")


if __name__ == "__main__":
    main()
