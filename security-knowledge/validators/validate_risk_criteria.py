#!/usr/bin/env python3
from __future__ import annotations

import ast
from datetime import date
from pathlib import Path
import operator
import sys

import yaml

FIXTURE = Path(__file__).parents[1] / "risk-methods" / "risk-criteria-regression-v1.yaml"


def present(value):
    return value is not None and value != "" and value != [] and value != {}


def parse_date(value):
    if not present(value):
        return None
    return date.fromisoformat(value)


_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_numeric_expression(expression: str, values: dict[str, float]) -> float:
    """Evaluate only numeric literals, declared variable names, + - * / and parentheses."""
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name) and node.id in values:
            return float(values[node.id])
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            return _ALLOWED_BINOPS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
            return _ALLOWED_UNARY[type(node.op)](visit(node.operand))
        raise ValueError(f"unsupported expression element: {ast.dump(node)}")

    return visit(tree)


def qualitative(i):
    dimensions = i.get("dimensions") or {}
    values = i.get("values") or {}
    for dimension, allowed in dimensions.items():
        if dimension not in values or values[dimension] not in allowed:
            return "VALUE_OUT_OF_SCALE"
    if "likelihood" not in values or "impact" not in values:
        return "NEEDS_ASSESSMENT_METHOD"
    key = f"{values['likelihood']}|{values['impact']}"
    mapping = i.get("mapping_table") or {}
    if key not in mapping:
        return "NEEDS_MAPPING_CELL"
    result = mapping[key]
    if result not in (i.get("decision_bands") or []):
        return "NEEDS_RISK_CRITERIA"
    return f"ASSESSED_{result}"


def band_for_score(score, bands):
    for band in bands or []:
        low = band.get("min")
        if low is not None and score < low:
            continue
        if "max_exclusive" in band and not score < band["max_exclusive"]:
            continue
        if "max_inclusive" in band and not score <= band["max_inclusive"]:
            continue
        return band.get("label")
    return None


def semi_quantitative(i):
    definition = i.get("calculation_definition")
    if not present(definition):
        return "NEEDS_CALCULATION_DEFINITION"
    if definition.get("type") != "WEIGHTED_SUM":
        return "NEEDS_ASSESSMENT_METHOD"
    expression = definition.get("expression")
    variables = definition.get("variables") or []
    values = i.get("values") or {}
    dimensions = i.get("dimensions") or {}
    if not present(expression) or not present(definition.get("source_reference")) or not present(definition.get("units")):
        return "NEEDS_CALCULATION_DEFINITION"
    for variable in variables:
        if variable not in values or variable not in dimensions:
            return "VALUE_OUT_OF_SCALE"
        bounds = dimensions[variable]
        if values[variable] < bounds.get("min", values[variable]) or values[variable] > bounds.get("max", values[variable]):
            return "VALUE_OUT_OF_SCALE"
    try:
        score = safe_numeric_expression(expression, {k: values[k] for k in variables})
    except (ValueError, ZeroDivisionError, SyntaxError):
        return "NEEDS_CALCULATION_DEFINITION"
    label = band_for_score(score, i.get("decision_bands"))
    if not present(label):
        return "NEEDS_RISK_CRITERIA"
    return f"ASSESSED_{label}"


def route(i):
    if not present(i.get("criteria_id")) or not present(i.get("version")):
        return "NEEDS_RISK_CRITERIA"
    if i.get("status") != "APPROVED" or not present(i.get("approval_evidence")) or not present(i.get("approved_by_role")):
        return "NEEDS_CRITERIA_APPROVAL"
    for key in ("source_reference", "source_provenance", "observed_at"):
        if not present(i.get(key)):
            return "NEEDS_CRITERIA_PROVENANCE"
    if i.get("concurrent_conflicting_current_criteria"):
        return "CONFLICT"
    assessment_date = parse_date(i.get("assessment_date"))
    effective_from = parse_date(i.get("effective_from"))
    effective_to = parse_date(i.get("effective_to"))
    if assessment_date is None and i.get("multiple_temporal_versions"):
        return "NEEDS_TEMPORAL_RESOLUTION"
    if assessment_date is not None and effective_from is not None and assessment_date < effective_from:
        return "CRITERIA_NOT_YET_EFFECTIVE"
    if assessment_date is not None and effective_to is not None and assessment_date > effective_to:
        return "STALE_CRITERIA"
    if present(i.get("requested_scope")) and i.get("scope") != i.get("requested_scope"):
        return "CRITERIA_SCOPE_MISMATCH"

    mode = i.get("assessment_mode")
    if mode == "QUALITATIVE":
        return qualitative(i)
    if mode == "SEMI_QUANTITATIVE":
        return semi_quantitative(i)
    return "NEEDS_ASSESSMENT_METHOD"


def main():
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    failures = []
    for case in data["cases"]:
        actual = route(case["input"])
        if actual != case["expected_status"]:
            failures.append((case["id"], case["expected_status"], actual))
    if failures:
        for failure in failures:
            print("FAIL", failure)
        return 1
    print(f"PASS {len(data['cases'])} risk-criteria cases; qualitative and semi-quantitative adapters executable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
