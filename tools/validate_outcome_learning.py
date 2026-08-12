from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTCOME_DIR = ROOT / "outcomes"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def nonempty(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, list, dict)):
        return bool(value)
    return True


def validate(path: Path, data: dict, errors: list[str]) -> None:
    rel = path.relative_to(ROOT)
    if not str(data.get("id", "")).startswith("OUT-"):
        errors.append(f"{rel}: outcome record id must start with OUT-")

    links = data.get("links") or {}
    for key in ("context", "decision_packet", "decision"):
        if not nonempty(links.get(key)):
            errors.append(f"{rel}: links.{key} is required")

    execution = data.get("execution") or {}
    if not (execution.get("test_refs") or execution.get("benchmark_refs") or execution.get("security_review_refs")):
        errors.append(f"{rel}: outcome requires at least one verification reference")

    observed = data.get("observed_outcome") or {}
    if not nonempty(observed.get("result")):
        errors.append(f"{rel}: observed_outcome.result is required")
    if observed.get("expected_behavior_met") is None:
        errors.append(f"{rel}: observed_outcome.expected_behavior_met must be explicit")

    promotion = data.get("promotion") or {}
    if promotion.get("eligible_for_decision_memory"):
        if not nonempty(promotion.get("eligibility_reason")):
            errors.append(f"{rel}: DM-eligible outcome requires eligibility_reason")
        if not nonempty(data.get("knowledge_updates", {}).get("create_or_update_decision_memory")):
            errors.append(f"{rel}: DM-eligible outcome must name create_or_update_decision_memory target")

    hypotheses = data.get("hypotheses") or {}
    classified = sum(len(hypotheses.get(k) or []) for k in ("confirmed", "rejected", "weakened", "strengthened"))
    unexpected = observed.get("unexpected_observations") or []
    if classified == 0 and not unexpected:
        errors.append(f"{rel}: outcome must capture learning via hypotheses or unexpected observations")


def main() -> int:
    errors: list[str] = []
    if not OUTCOME_DIR.exists():
        print("Outcome learning gate: no outcomes directory yet.")
        return 0

    count = 0
    for path in OUTCOME_DIR.rglob("*.yaml"):
        count += 1
        try:
            data = load_yaml(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path.relative_to(ROOT)}: record must be a mapping")
            continue
        validate(path, data, errors)

    if errors:
        print("Outcome Learning Gate FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Outcome Learning Gate PASSED. Validated {count} outcome record(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
