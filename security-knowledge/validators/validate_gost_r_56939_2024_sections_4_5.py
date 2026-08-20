#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/standards/gost-r-56939-2024-sections-4-5-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/standards/gost-r-56939-2024-sections-4-5-regression-v1.json")
REGISTRY = Path("security-knowledge/standards/gost-and-ru-standards-source-registry.yaml")
FSTEC117 = Path("security-knowledge/controls/gis-fstec-117-process-details-50-61-atomic-v1.yaml")


def evaluate(case, requirements, processes):
    query = case["query"]
    if query == "applicability":
        if case["binding"] == "NONE":
            return "REQUIRE_BINDING_DOCUMENT_OR_VOLUNTARY_ADOPTION"
        if case["self_developed"]:
            return "APPLY_SECTIONS_4_AND_5"
        if case["head_decision"]:
            return "INCLUDE_SELECTED_REQUIREMENTS_IN_CONTRACTOR_TECHNICAL_SPECIFICATION"
        return "NO_AUTOMATIC_SELF_DEVELOPMENT_EDGE"
    if query == "modality":
        return requirements[case["locator"]].get("modality", "REQUIRED_WHEN_APPLICABLE_SCOPE_BINDS")
    if query == "requirement_exists":
        return "PRESENT" if case["locator"] in requirements else "ABSENT"
    if query == "artifact_count":
        return len(processes[case["process"]]["artifact_locators"])
    if query == "numeric_deadline":
        if case["topic"] == "STATIC_ANALYSIS_PERIOD":
            return "NOT_STATED_DEVELOPER_DEFINES_PERIOD_OR_EVENTS"
        return "NOT_STATED_DEVELOPER_DEFINES_VALUE"
    if query == "full_conformity_required_count":
        return sum(item.get("modality") not in {"RECOMMENDED", "DISCRETIONARY"} for item in requirements.values())
    if query == "appendix_a_external_audit":
        return "NOT_MANDATORY"
    if query == "repeatable_build":
        return "PASS_PREDICTABLE_RESULT_BINARY_IDENTITY_NOT_REQUIRED"
    if query == "threat_sources":
        return "REJECT_EXAMPLES_NOT_EXHAUSTIVE" if case["only_bdu"] else "ALLOW_METHOD_JUSTIFICATION"
    if query == "artifact_proof":
        if case["artifact_present"] and case["substance_verified"]:
            return "POSSIBLE_IMPLEMENTATION_EVIDENCE"
        return "INSUFFICIENT_ARTIFACT_EXISTENCE_ALONE"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    fstec = yaml.safe_load(FSTEC117.read_text(encoding="utf-8"))

    processes = {item["locator"]: item for item in model["processes"]}
    requirements = {
        item["locator"]: item
        for process in model["processes"]
        for item in process["requirements"]
    }
    artifacts = [locator for process in model["processes"] for locator in process["artifact_locators"]]

    assert model["status"] == "VERIFIED_BOUNDED_SECTIONS_4_AND_5_PUBLIC_TEXT"
    assert len(model["section_4"]["clauses"]) == model["counts"]["section_4_clauses"] == 17
    assert len(processes) == model["counts"]["section_5_processes"] == 25
    assert len(requirements) == model["counts"]["section_5_requirement_clauses"] == 118
    assert len(artifacts) == len(set(artifacts)) == model["counts"]["artifact_clauses"] == 96
    optional = sum(item.get("modality") in {"RECOMMENDED", "DISCRETIONARY"} for item in requirements.values())
    assert optional == model["counts"]["recommended_or_discretionary_requirement_clauses"] == 8
    assert len(requirements) - optional == model["counts"]["required_when_full_conformity_applies"] == 110
    assert model["counts"]["numeric_deadlines_stated_by_standard"] == 0
    assert requirements["5.15.2.1"]["modality"] == "DISCRETIONARY"
    assert requirements["5.24.2.3"]["modality"] == "DISCRETIONARY"
    assert model["verification_boundary"]["immutable_official_normative_bytes"] == "PENDING"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False

    source = next(item for item in registry["sources"] if item["id"] == "GOST_R_56939_2024")
    assert source["status_observed"] == "Действует"
    assert source["order_number"] == "1504-ст"
    assert source["effective_date"].isoformat() == "2024-12-20"
    assert source["replaces"] == "ГОСТ Р 56939-2016"
    assert str(MODEL) in source["repo_bindings"] and str(FIXTURES) in source["repo_bindings"]

    fstec_rule = next(item for item in fstec["atomic_rules"] if item["id"] == "F117-RES-005")
    assert fstec_rule["duty"] == "IMPLEMENT_GOST_R_56939_2024_SECTIONS_4_AND_5"
    assert model["applicability"]["regulatory_binding_edge"]["locator"] == "пункт 50 абзац 2"

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, requirements, processes)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 17 section-4 clauses; 25 processes; 118 requirements (110 required, 8 optional); 96 artifact locators; 30 cases")


if __name__ == "__main__":
    main()
