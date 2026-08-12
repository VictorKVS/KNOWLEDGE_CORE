from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            value = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError):
        return {}
    return value if isinstance(value, dict) else {}


def collect(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in root.rglob("*.y*ml"):
        if ".git" in path.parts or ".github" in path.parts or "templates" in path.parts:
            continue
        record = load_yaml(path)
        if isinstance(record.get("id"), str) and str(record["id"]).startswith("SEC-"):
            record["_path"] = path.relative_to(root).as_posix()
            records.append(record)
    return records


def status(record: dict[str, Any]) -> str:
    return str(record.get("status", "UNKNOWN")).upper()


def kind(record: dict[str, Any]) -> str:
    return str(record.get("kind", "unknown"))


def dashboard(records: list[dict[str, Any]]) -> dict[str, Any]:
    kinds = Counter(kind(r) for r in records)
    statuses = Counter(status(r) for r in records)

    findings = [r for r in records if kind(r) == "security-finding"]
    remediations = [r for r in records if kind(r) == "security-remediation"]
    retests = [r for r in records if kind(r) == "security-retest"]
    risks = [r for r in records if kind(r) == "security-risk"]
    priorities = [r for r in records if kind(r) == "security-priority-item"]
    roadmap = [r for r in records if kind(r) == "security-roadmap-item"]

    open_findings = [r for r in findings if status(r) not in {"CLOSED", "RISK_ACCEPTED"}]
    unknown_risks = [r for r in risks if str((r.get("assessment") or {}).get("level", "UNKNOWN")).upper() == "UNKNOWN"]
    p0 = [r for r in priorities if str((r.get("priority") or {}).get("class", "")).upper() == "P0"]
    p1 = [r for r in priorities if str((r.get("priority") or {}).get("class", "")).upper() == "P1"]
    now = [r for r in roadmap if str((r.get("plan") or {}).get("horizon", "")).upper() == "NOW"]
    blocked = [r for r in roadmap if (r.get("plan") or {}).get("blockers")]

    return {
        "schema_version": "1.0",
        "record_count": len(records),
        "records_by_kind": dict(sorted(kinds.items())),
        "records_by_status": dict(sorted(statuses.items())),
        "headline": {
            "open_findings": len(open_findings),
            "unknown_risks": len(unknown_risks),
            "P0_items": len(p0),
            "P1_items": len(p1),
            "NOW_roadmap_items": len(now),
            "blocked_roadmap_items": len(blocked),
            "remediation_records": len(remediations),
            "retest_records": len(retests),
        },
        "critical_drilldown": {
            "open_findings": [{"id": r.get("id"), "path": r.get("_path")} for r in open_findings],
            "unknown_risks": [{"id": r.get("id"), "path": r.get("_path")} for r in unknown_risks],
            "P0_items": [{"id": r.get("id"), "path": r.get("_path")} for r in p0],
            "blocked_roadmap_items": [{"id": r.get("id"), "path": r.get("_path")} for r in blocked],
        },
        "warning": "Aggregate counts are navigation aids, not proof of compliance or security.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build evidence-linked security dashboard data")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("generated/security-dashboard.json"))
    args = parser.parse_args()
    result = dashboard(collect(args.root.resolve()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["headline"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
