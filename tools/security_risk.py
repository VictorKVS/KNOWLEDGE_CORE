from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

LEVEL = {"unknown": None, "low": 1, "medium": 2, "high": 3, "critical": 4}
LIKELIHOOD = {"unknown": None, "low": 1, "medium": 2, "high": 3}
CONTROL = {"unknown": None, "weak": 0, "partial": 1, "strong": 2}
HEALTH = {"RED": 0, "YELLOW": 1, "GREEN": 2, "unknown": None}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    return value if isinstance(value, dict) else {}


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def norm(value: Any) -> str:
    return str(value if value is not None else "unknown").strip()


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != "security-risk":
        errors.append("kind must be security-risk")

    scope = as_dict(record.get("scope"))
    if not as_list(scope.get("asset_refs")):
        errors.append("scope.asset_refs is required")

    assessment = as_dict(record.get("assessment"))
    required = (
        "asset_criticality",
        "threat_likelihood",
        "weakness_exposure",
        "control_effectiveness",
        "evidence_health",
    )
    for key in required:
        if key not in assessment:
            errors.append(f"assessment.{key} is required")

    result = as_dict(record.get("result"))
    state = norm(result.get("risk_state")).upper()
    if state not in {"LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"}:
        errors.append("result.risk_state is invalid")
    if state != "UNKNOWN" and not result.get("rationale"):
        errors.append("non-UNKNOWN risk requires result.rationale")
    if state != "UNKNOWN" and not as_list(result.get("major_contributors")):
        errors.append("non-UNKNOWN risk requires major_contributors")

    acceptance = as_dict(record.get("risk_acceptance"))
    if acceptance.get("accepted") is True:
        for field in ("owner", "rationale", "valid_until", "review_date"):
            if not acceptance.get(field):
                errors.append(f"accepted risk requires risk_acceptance.{field}")
    return errors


def derive(record: dict[str, Any]) -> dict[str, Any]:
    a = as_dict(record.get("assessment"))
    criticality = LEVEL.get(norm(a.get("asset_criticality")).lower())
    likelihood = LIKELIHOOD.get(norm(a.get("threat_likelihood")).lower())
    exposure = LEVEL.get(norm(a.get("weakness_exposure")).lower())
    control = CONTROL.get(norm(a.get("control_effectiveness")).lower())
    health_key = norm(a.get("evidence_health"))
    health = HEALTH.get(health_key.upper(), HEALTH.get(health_key.lower()))

    impact = as_dict(a.get("impact"))
    impact_values = [LEVEL.get(norm(v).lower()) for v in impact.values()]
    known_impacts = [v for v in impact_values if isinstance(v, int)]
    max_impact = max(known_impacts) if known_impacts else None

    missing = [
        name
        for name, value in (
            ("asset_criticality", criticality),
            ("threat_likelihood", likelihood),
            ("weakness_exposure", exposure),
            ("control_effectiveness", control),
            ("evidence_health", health),
            ("impact", max_impact),
        )
        if value is None
    ]
    if missing:
        return {"derived_state": "UNKNOWN", "score": None, "uncertainty_drivers": missing}

    # Sortable implementation aid only; policy remains authoritative.
    raw = criticality * 3 + likelihood * 2 + exposure * 3 + max_impact * 3
    raw -= control * 2
    if health == 0:
        raw += 2
    elif health == 1:
        raw += 1

    if criticality == 4 and exposure >= 3 and control == 0:
        state = "CRITICAL"
    elif raw >= 34:
        state = "CRITICAL"
    elif raw >= 25:
        state = "HIGH"
    elif raw >= 16:
        state = "MEDIUM"
    else:
        state = "LOW"

    return {"derived_state": state, "score": raw, "uncertainty_drivers": []}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and derive explainable security risk records")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failed = False
    rows = []
    for path in args.paths:
        record = load(path)
        errors = validate(record)
        derived = derive(record)
        failed = failed or bool(errors)
        rows.append({
            "id": record.get("id", path.stem),
            "path": str(path),
            "declared_state": as_dict(record.get("result")).get("risk_state", "UNKNOWN"),
            **derived,
            "errors": errors,
        })

    rows.sort(key=lambda row: (row["score"] is None, -(row["score"] or 0), row["id"]))
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        for row in rows:
            marker = "FAIL" if row["errors"] else "OK"
            print(f"{marker:4} {row['id']} derived={row['derived_state']} score={row['score']}")
            for error in row["errors"]:
                print(f"     - {error}")
            if row["uncertainty_drivers"]:
                print(f"     unknown: {', '.join(row['uncertainty_drivers'])}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
