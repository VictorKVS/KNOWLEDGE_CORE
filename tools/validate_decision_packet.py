from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKETS = ROOT / "decision-packets"
MATURE = {"reviewed", "verified", "approved", "reusable"}


def load(path: Path) -> dict[str, Any]:
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


def validate(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status = str(data.get("status", "draft")).lower()
    if status not in MATURE:
        return errors

    for key in ("request", "candidate_search", "candidates", "selection", "result", "traceability", "reproducibility"):
        if not nonempty(data.get(key)):
            errors.append(f"{path.name}: mature packet requires {key}")

    selection = data.get("selection") or {}
    route = str(selection.get("route", "")).upper()
    if route not in {"FAST", "ADAPT", "RESEARCH"}:
        errors.append(f"{path.name}: invalid selection.route {route!r}")

    candidates = data.get("candidates") or []
    if not isinstance(candidates, list) or not candidates:
        errors.append(f"{path.name}: mature packet requires at least one candidate")
        candidates = []

    for idx, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"{path.name}: candidates[{idx}] must be an object")
            continue
        for key in ("id", "health", "route", "context_match", "supporting_reasons", "blocking_reasons"):
            if key not in candidate:
                errors.append(f"{path.name}: candidates[{idx}] missing {key}")

    selected_id = selection.get("selected_candidate")
    if route == "FAST":
        if not selected_id:
            errors.append(f"{path.name}: FAST requires selected_candidate")
        selected = next((c for c in candidates if isinstance(c, dict) and c.get("id") == selected_id), None)
        if selected is None:
            errors.append(f"{path.name}: FAST selected_candidate must exist in candidates")
        else:
            if str(selected.get("health", "")).upper() != "GREEN":
                errors.append(f"{path.name}: FAST selected candidate must be GREEN")
            mismatched = ((selected.get("context_match") or {}).get("mismatched") or [])
            if mismatched:
                errors.append(f"{path.name}: FAST candidate cannot contain context mismatches")

    if route == "ADAPT" and not selection.get("required_revalidation"):
        errors.append(f"{path.name}: ADAPT requires explicit required_revalidation actions")

    if route == "RESEARCH" and not selection.get("rationale"):
        errors.append(f"{path.name}: RESEARCH requires escalation rationale")

    result = data.get("result") or {}
    if route in {"FAST", "ADAPT"} and not result.get("decision_record"):
        errors.append(f"{path.name}: {route} packet requires result.decision_record")

    repro = data.get("reproducibility") or {}
    if not repro.get("policy_versions"):
        errors.append(f"{path.name}: mature packet requires policy_versions")

    return errors


def main() -> int:
    if not PACKETS.exists():
        print("Decision packet gate PASSED: no decision-packets directory yet.")
        return 0

    errors: list[str] = []
    checked = 0
    for path in sorted(PACKETS.glob("*.yaml")):
        checked += 1
        errors.extend(validate(path, load(path)))

    if errors:
        print("Decision packet gate FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Decision packet gate PASSED. Validated {checked} packet(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
