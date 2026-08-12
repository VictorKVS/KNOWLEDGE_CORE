from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

LEVELS = {
    "risk": {"low": 1, "medium": 2, "high": 4, "critical": 7, "unknown": 0},
    "obligation": {"informative": 0, "recommended": 1, "conditional": 3, "mandatory": 6, "unknown": 0},
    "exposure": {"low": 1, "medium": 2, "high": 4, "critical": 6, "unknown": 0},
    "asset_criticality": {"low": 1, "medium": 2, "high": 4, "critical": 6, "unknown": 0},
    "evidence_confidence": {"low": 1, "medium": 2, "high": 3, "unknown": 0},
    "remediation_efficiency": {"low": 1, "medium": 2, "high": 4, "unknown": 0},
    "deadline_pressure": {"low": 1, "medium": 2, "high": 4, "critical": 6, "unknown": 0},
}
WEIGHTS = {
    "risk": 30,
    "obligation": 20,
    "exposure": 15,
    "asset_criticality": 15,
    "evidence_confidence": 5,
    "remediation_efficiency": 10,
    "deadline_pressure": 5,
}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    return value if isinstance(value, dict) else {}


def score(record: dict[str, Any]) -> tuple[float, list[str]]:
    priority = record.get("priority") if isinstance(record.get("priority"), dict) else {}
    if priority.get("hard_override") is True:
        return 100.0, [f"hard override: {priority.get('override_reason', '')}".strip()]

    factors = record.get("factors") if isinstance(record.get("factors"), dict) else {}
    total = 0.0
    reasons: list[str] = []
    unknown_material = []
    for name, weight in WEIGHTS.items():
        raw = str(factors.get(name, "unknown")).lower()
        mapping = LEVELS[name]
        value = mapping.get(raw, 0)
        max_value = max(mapping.values()) or 1
        contribution = weight * value / max_value
        total += contribution
        reasons.append(f"{name}={raw} (+{contribution:.1f})")
        if raw == "unknown" and name in {"risk", "obligation", "exposure", "asset_criticality"}:
            unknown_material.append(name)

    uncertainty = record.get("uncertainty") if isinstance(record.get("uncertainty"), dict) else {}
    material_gaps = uncertainty.get("material_gaps") if isinstance(uncertainty.get("material_gaps"), list) else []
    if unknown_material or material_gaps:
        reasons.append("material uncertainty present")
    return round(total, 2), reasons


def classify(record: dict[str, Any], numeric: float) -> str:
    priority = record.get("priority") if isinstance(record.get("priority"), dict) else {}
    if priority.get("hard_override") is True:
        return "P0"
    uncertainty = record.get("uncertainty") if isinstance(record.get("uncertainty"), dict) else {}
    material_gaps = uncertainty.get("material_gaps") if isinstance(uncertainty.get("material_gaps"), list) else []
    factors = record.get("factors") if isinstance(record.get("factors"), dict) else {}
    if material_gaps or any(str(factors.get(k, "unknown")).lower() == "unknown" for k in ("risk", "obligation", "asset_criticality")):
        return "RESEARCH"
    if numeric >= 75:
        return "P1"
    if numeric >= 50:
        return "P2"
    return "P3"


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != "security-priority-item":
        errors.append("kind must be security-priority-item")
    subject = record.get("subject") if isinstance(record.get("subject"), dict) else {}
    if not any(isinstance(subject.get(key), list) and subject.get(key) for key in (
        "finding_refs", "risk_refs", "coverage_gap_refs", "requirement_refs", "asset_refs"
    )):
        errors.append("subject must reference at least one security object")
    priority = record.get("priority") if isinstance(record.get("priority"), dict) else {}
    if priority.get("hard_override") is True and not priority.get("override_reason"):
        errors.append("hard override requires override_reason")
    ordering = record.get("ordering") if isinstance(record.get("ordering"), dict) else {}
    if str(record.get("status", "OPEN")).upper() not in {"DRAFT", "OPEN"} and not ordering.get("rationale"):
        errors.append("mature priority item requires ordering.rationale")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and rank security remediation priority items")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = []
    failed = False
    for path in args.paths:
        record = load(path)
        errors = validate(record)
        failed = failed or bool(errors)
        numeric, reasons = score(record)
        rows.append({
            "id": record.get("id", path.stem),
            "title": record.get("title", ""),
            "class": classify(record, numeric),
            "score": numeric,
            "reasons": reasons,
            "errors": errors,
            "path": str(path),
        })

    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "RESEARCH": 4}
    rows.sort(key=lambda row: (order.get(row["class"], 9), -row["score"], row["id"]))
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            marker = "FAIL" if row["errors"] else "OK"
            print(f"{marker:4} {row['class']:8} score={row['score']:>5} {row['id']} {row['title']}")
            for reason in row["reasons"]:
                print(f"     - {reason}")
            for error in row["errors"]:
                print(f"     ! {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
