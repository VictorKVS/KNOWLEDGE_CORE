from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CRITICAL_DIMENSIONS = {
    "workload",
    "scale",
    "data_semantics",
    "trust_boundary",
    "failure_model",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def flatten_known(section: Any) -> dict[str, Any]:
    if not isinstance(section, dict):
        return {}
    return {str(k): v for k, v in section.items() if nonempty(v)}


def compare_section(current: dict[str, Any], candidate: dict[str, Any]) -> tuple[str, list[str]]:
    if not current:
        return "UNKNOWN", ["current context missing"]
    if not candidate:
        return "UNKNOWN", ["candidate applicability missing"]

    compared = 0
    mismatches: list[str] = []
    for key, cur in current.items():
        if key not in candidate or not nonempty(candidate[key]):
            continue
        compared += 1
        if candidate[key] != cur:
            mismatches.append(f"{key}: current={cur!r}, candidate={candidate[key]!r}")

    if mismatches:
        return "MISMATCH", mismatches
    if compared == 0:
        return "UNKNOWN", ["no comparable declared fields"]
    if len(compared_fields := [k for k in current if k in candidate and nonempty(candidate[k])]) == len(current):
        return "EXACT", [f"matched fields: {', '.join(compared_fields)}"]
    return "COMPATIBLE", [f"matched {compared} declared field(s); remaining fields not constrained by candidate"]


def candidate_context(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    context = record.get("context") if isinstance(record.get("context"), dict) else {}
    applicability = record.get("applicability") if isinstance(record.get("applicability"), dict) else {}
    constraints = record.get("constraints") if isinstance(record.get("constraints"), dict) else {}

    return {
        "workload": flatten_known(context.get("workload")),
        "scale": flatten_known(context.get("scale")),
        "runtime": flatten_known({
            "language": context.get("language"),
            "version": context.get("runtime_version"),
        }),
        "environment": flatten_known({
            "environment": context.get("environment"),
        }),
        "data_semantics": flatten_known(applicability.get("data_semantics")),
        "trust_boundary": flatten_known({
            "trust_boundary": context.get("trust_boundary"),
        }),
        "failure_model": flatten_known(applicability.get("failure_model")),
        "compatibility": flatten_known(applicability.get("compatibility")),
        "operational_constraints": flatten_known(constraints.get("operational")),
    }


def route(current: dict[str, Any], candidate: dict[str, Any], health: str) -> dict[str, Any]:
    health = str(health or "UNKNOWN").upper()
    details: dict[str, Any] = {}
    hard_mismatch = False
    critical_unknown = False
    soft_difference = False

    candidate_ctx = candidate_context(candidate)
    for dimension in (
        "workload",
        "scale",
        "runtime",
        "environment",
        "data_semantics",
        "trust_boundary",
        "failure_model",
        "compatibility",
        "operational_constraints",
    ):
        cur = flatten_known(current.get(dimension))
        state, notes = compare_section(cur, candidate_ctx.get(dimension, {}))
        details[dimension] = {"state": state, "notes": notes}
        if dimension in CRITICAL_DIMENSIONS and state == "MISMATCH":
            hard_mismatch = True
        elif dimension in CRITICAL_DIMENSIONS and state == "UNKNOWN":
            critical_unknown = True
        elif state in {"MISMATCH", "UNKNOWN", "COMPATIBLE"}:
            soft_difference = True

    if health == "RED" or hard_mismatch:
        selected = "RESEARCH"
        next_action = "revalidate evidence or hand off to Analyst/Specialist before reuse"
    elif health != "GREEN" or critical_unknown or soft_difference:
        selected = "ADAPT"
        next_action = "reuse only the verified structure; revalidate changed or unknown assumptions"
    else:
        selected = "FAST"
        next_action = "reuse verified decision within the declared applicability envelope"

    return {
        "route": selected,
        "health_state": health,
        "hard_context_mismatch": hard_mismatch,
        "critical_context_unknown": critical_unknown,
        "context_match": details,
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a task to FAST, ADAPT or RESEARCH.")
    parser.add_argument("context", type=Path, help="Task context YAML")
    parser.add_argument("candidate", type=Path, help="Decision-memory or decision YAML")
    parser.add_argument("--health", default="UNKNOWN", help="Evidence health: GREEN/YELLOW/RED")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = route(load_yaml(args.context), load_yaml(args.candidate), args.health)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"ROUTE: {result['route']}")
        print(f"HEALTH: {result['health_state']}")
        for name, item in result["context_match"].items():
            print(f"- {name}: {item['state']} ({'; '.join(item['notes'])})")
        print(f"NEXT: {result['next_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
