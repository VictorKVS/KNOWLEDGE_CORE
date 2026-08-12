from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

VALID_STATES = {"APPLIES", "DOES_NOT_APPLY", "CONDITIONAL", "UNKNOWN"}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    return value if isinstance(value, dict) else {}


def deep_get(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return "unknown"
        cur = cur[part]
    return cur


def is_unknown(value: Any) -> bool:
    return value is None or value == "" or str(value).lower() == "unknown"


def eval_condition(ctx: dict[str, Any], cond: dict[str, Any]) -> tuple[bool | None, str]:
    fact = str(cond.get("fact", ""))
    op = str(cond.get("op", "eq"))
    expected = cond.get("value")
    actual = deep_get(ctx, fact)
    if is_unknown(actual):
        return None, f"{fact}=unknown"
    if op == "eq":
        return actual == expected, f"{fact}={actual!r} expected {expected!r}"
    if op == "in":
        values = expected if isinstance(expected, list) else [expected]
        return actual in values, f"{fact}={actual!r} in {values!r}"
    if op == "contains":
        if not isinstance(actual, list):
            return False, f"{fact} is not a list"
        return expected in actual, f"{expected!r} in {fact}"
    if op == "not_eq":
        return actual != expected, f"{fact}={actual!r} not_eq {expected!r}"
    return None, f"unsupported operator {op}"


def evaluate(ctx: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    logic = rule.get("logic") if isinstance(rule.get("logic"), dict) else {}
    traces: list[str] = []
    unknowns: list[str] = []

    all_results = []
    for cond in logic.get("all", []) or []:
        result, trace = eval_condition(ctx, cond)
        traces.append(trace)
        if result is None:
            unknowns.append(trace)
        all_results.append(result)

    any_results = []
    for cond in logic.get("any", []) or []:
        result, trace = eval_condition(ctx, cond)
        traces.append(trace)
        if result is None:
            unknowns.append(trace)
        any_results.append(result)

    none_results = []
    for cond in logic.get("none", []) or []:
        result, trace = eval_condition(ctx, cond)
        traces.append(trace)
        if result is None:
            unknowns.append(trace)
        none_results.append(result)

    hard_false = any(r is False for r in all_results) or any(r is True for r in none_results)
    any_block = bool(any_results) and all(r is False for r in any_results if r is not None) and not any(r is True for r in any_results)

    outcomes = rule.get("outcomes") if isinstance(rule.get("outcomes"), dict) else {}
    if hard_false or any_block:
        state = str((outcomes.get("when_false") or {}).get("state", "DOES_NOT_APPLY"))
    elif unknowns or (any_results and not any(r is True for r in any_results)):
        state = str((outcomes.get("when_unknown") or {}).get("state", "UNKNOWN"))
    else:
        state = str((outcomes.get("when_true") or {}).get("state", "APPLIES"))

    if state not in VALID_STATES:
        state = "UNKNOWN"
    return {
        "rule_id": rule.get("id", ""),
        "branch": rule.get("branch", ""),
        "state": state,
        "trace": traces,
        "unknowns": unknowns,
        "normative_basis": (rule.get("normative_basis") or {}).get("source_refs", []),
        "activated_requirements": ((outcomes.get("when_true") or {}).get("activates_requirements", []) if state == "APPLIES" else []),
    }


def validate_rule(rule: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if rule.get("kind") != "security-applicability-rule":
        errors.append("kind must be security-applicability-rule")
    basis = rule.get("normative_basis") if isinstance(rule.get("normative_basis"), dict) else {}
    if not basis.get("source_refs"):
        errors.append("normative_basis.source_refs is required")
    if not basis.get("exact_locations"):
        errors.append("normative_basis.exact_locations is required")
    logic = rule.get("logic") if isinstance(rule.get("logic"), dict) else {}
    if not any(logic.get(k) for k in ("all", "any", "none")):
        errors.append("at least one applicability condition is required")
    if (rule.get("review") or {}).get("normative_review_required") is not True:
        errors.append("normative_review_required must remain true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate evidence-backed security regulatory applicability")
    parser.add_argument("context", type=Path)
    parser.add_argument("rules", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ctx = load(args.context)
    rows = []
    failed = False
    for path in args.rules:
        rule = load(path)
        errors = validate_rule(rule)
        if errors:
            failed = True
            rows.append({"rule_id": rule.get("id", path.stem), "state": "INVALID", "errors": errors})
        else:
            rows.append(evaluate(ctx, rule))

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        for row in rows:
            print(f"{row.get('state',''):16} {row.get('rule_id','')} branch={row.get('branch','')}")
            for line in row.get("trace", []):
                print(f"  - {line}")
            for error in row.get("errors", []):
                print(f"  ! {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
