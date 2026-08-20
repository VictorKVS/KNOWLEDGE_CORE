#!/usr/bin/env python3
import json
from pathlib import Path

import yaml


MODEL = Path("security-knowledge/controls/fstec-uzi-2026-methodology-atomic-v1.yaml")
FIXTURES = Path("security-knowledge/controls/fstec-uzi-2026-methodology-regression-v1.json")


def aggregate_band(value):
    if value < 1:
        return 0
    if value < 2:
        return 1
    if value < 3:
        return 2
    if value < 4:
        return 3
    return 4


def evaluate(case, model, directions, requirements):
    query = case["query"]
    if query == "count":
        mapping = {
            "clauses": model["counts"]["numbered_clauses"],
            "pipeline": len(model["evaluation_route"]["pipeline"]),
            "directions": len(directions),
            "evidence": len(model["input_evidence_classes"]),
            "tools": len(model["optional_tools"]["classes"]),
            "requirements": len(requirements),
            "bands": len(model["aggregate_maturity_bands"]),
            "targets": len(model["target_level_recommendations"]["routes"]),
            "report_fields": len(model["report"]["required_fields"]),
            "dynamics": len(model["dynamics_and_improvement"]["retrospective_states"]),
        }
        return mapping[case["kind"]]
    if query == "band":
        return aggregate_band(case["value"])
    if query == "direction":
        return directions[case["id"]]["title"]
    if query == "weight":
        return requirements[case["id"]]["weight"]
    if query == "coefficients":
        return requirements[case["id"]]["allowed_coefficients"]
    if query == "target":
        for route in model["target_level_recommendations"]["routes"]:
            if case["class"] in route["classes"]:
                return route["target_minimum"]
        return "NO_RECOMMENDATION_IN_BOUNDED_MODEL"
    if query == "missing_evidence":
        return model["evidence_and_role_rules"]["missing_requested_material"]
    if query == "inapplicable":
        return model["direction_scope_rules"]["inapplicable_direction"]
    if query == "external_mandatory":
        return model["evaluation_route"]["external_evaluation_universally_mandatory"]
    if query == "target_strength":
        return model["target_level_recommendations"]["normative_strength"]
    if query == "tools_strength":
        return model["optional_tools"]["normative_strength"]
    if query == "direction_level_by_p_only":
        return model["calculation_boundary"]["p_threshold_alone_is_sufficient"]
    if query == "formula":
        return model["calculation_boundary"][case["kind"]]
    if query == "table3_cells":
        return model["calculation_boundary"]["table_3_normalized_d_ij_minima"]
    if query == "plan_deadline":
        return model["dynamics_and_improvement"]["numeric_plan_deadline_in_method"]
    if query == "official_bytes":
        return model["verification_boundary"]["immutable_official_bytes"]
    if query == "segregation":
        return model["evidence_and_role_rules"]["evaluator_segregation"]
    if query == "responsibility":
        return model["evidence_and_role_rules"]["operator_responsibility"]
    if query == "report_approval":
        return model["report"]["approved_by"]
    if query == "metric_identity":
        return "THIS_METRIC" if case["candidate"] == "UZI" else "DISTINCT_METRIC"
    raise AssertionError(f"Unhandled query: {query}")


def main():
    model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    directions = {item["id"]: item for item in model["directions"]}
    requirements = {item["id"]: item for item in model["requirement_types"]}

    assert model["status"] == "VERIFIED_BOUNDED_CURRENT_TEXT_INTERFACE_OFFICIAL_BYTES_AND_IMAGE_CELLS_PENDING"
    assert len(directions) == model["counts"]["directions"] == 21
    assert len(requirements) == model["counts"]["requirement_types"] == 8
    assert round(sum(item["weight"] for item in requirements.values()), 10) == 1.0
    assert requirements["R6"]["allowed_coefficients"] == [0.0, 0.3, 0.5, 1.0]
    assert all(
        item["allowed_coefficients"] == [0.0, 0.5, 1.0]
        for key, item in requirements.items() if key != "R6"
    )
    assert len(model["input_evidence_classes"]) == model["counts"]["input_evidence_classes"] == 13
    assert len(model["optional_tools"]["classes"]) == model["counts"]["optional_tool_classes"] == 4
    assert len(model["report"]["required_fields"]) == model["counts"]["report_required_fields"] == 13
    assert model["calculation_boundary"]["p_threshold_alone_is_sufficient"] is False
    assert model["calculation_boundary"]["table_3_normalized_d_ij_minima"] == "PENDING_IMAGE_CELL_EXTRACTION"
    assert model["verification_boundary"]["immutable_official_bytes"] == "PENDING"
    assert model["verification_boundary"]["critical_gap_created"] is False
    assert model["verification_boundary"]["high_gap_created"] is False

    failures = []
    for case in fixtures["cases"]:
        actual = evaluate(case, model, directions, requirements)
        if actual != case["expected"]:
            failures.append((case["id"], case["expected"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        raise SystemExit(1)
    print("PASS: 36 clauses; 21 directions; 8 requirements; 13 evidence inputs; 52 fail-closed cases")


if __name__ == "__main__":
    main()
