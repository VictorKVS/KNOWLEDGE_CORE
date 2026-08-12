from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

PREFIX_KIND = {
    "SEC-REQ-": "requirement",
    "SEC-CTRL-": "control",
    "SEC-CHECK-": "check",
    "SEC-ASSET-": "asset",
    "SEC-THREAT-": "threat",
    "SEC-FIND-": "finding",
    "SEC-REM-": "remediation",
    "SEC-RETEST-": "retest",
    "SEC-CLOSE-": "closure",
}


def load_yaml(path: Path) -> dict[str, Any] | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    return value if isinstance(value, dict) else None


def walk(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)
    else:
        yield value


def refs(record: dict[str, Any]) -> set[str]:
    return {v for v in walk(record) if isinstance(v, str) and v.startswith("SEC-")}


def classify(record_id: str) -> str | None:
    for prefix, kind in PREFIX_KIND.items():
        if record_id.startswith(prefix):
            return kind
    return None


def collect(root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for path in root.rglob("*.y*ml"):
        if "templates" in path.parts:
            continue
        data = load_yaml(path)
        if not data:
            continue
        record_id = data.get("id")
        if not isinstance(record_id, str) or not classify(record_id):
            continue
        data["__path"] = path.relative_to(root).as_posix()
        data["__refs"] = refs(data)
        records[record_id] = data
    return records


def incoming(records: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    result = {record_id: set() for record_id in records}
    for source, record in records.items():
        for target in record["__refs"]:
            if target in result:
                result[target].add(source)
    return result


def criticality(record: dict[str, Any]) -> str:
    for key in ("criticality", "severity", "business_criticality"):
        value = record.get(key)
        if isinstance(value, str):
            return value.lower()
    classification = record.get("classification")
    if isinstance(classification, dict):
        for key in ("criticality", "severity"):
            value = classification.get(key)
            if isinstance(value, str):
                return value.lower()
    return "unknown"


def report(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    inc = incoming(records)
    gaps: list[dict[str, Any]] = []

    def add(record_id: str, dimension: str, reason: str, priority: str = "medium") -> None:
        gaps.append({"id": record_id, "dimension": dimension, "reason": reason, "priority": priority})

    for rid, rec in records.items():
        kind = classify(rid)
        outgoing = rec["__refs"]
        inbound = inc.get(rid, set())

        if kind == "requirement":
            req_type = str(rec.get("requirement_type") or rec.get("type") or "").lower()
            applicable = str(rec.get("status", "")).upper() != "NOT_APPLICABLE"
            linked_controls = [x for x in inbound | outgoing if x.startswith("SEC-CTRL-")]
            if applicable and req_type in {"mandatory", "conditional", ""} and not linked_controls:
                add(rid, "requirement_to_control", "applicable requirement has no mapped control", "high")

        elif kind == "control":
            linked_checks = [x for x in inbound | outgoing if x.startswith("SEC-CHECK-") or x.startswith("SEC-RULE-")]
            if not linked_checks:
                add(rid, "control_to_check", "control has no verification check", "high")

        elif kind == "asset":
            linked_threats = [x for x in inbound | outgoing if x.startswith("SEC-THREAT-")]
            if criticality(rec) in {"critical", "high"} and not linked_threats:
                add(rid, "asset_to_threat", "critical/high asset has no linked threat analysis", "critical")

        elif kind == "threat":
            linked_controls = [x for x in inbound | outgoing if x.startswith("SEC-CTRL-")]
            risk_accept = any("RISK_ACCEPT" in str(v).upper() for v in walk(rec))
            if not linked_controls and not risk_accept:
                add(rid, "threat_to_control", "material threat has no control or explicit risk acceptance", "high")

        elif kind == "finding":
            linked_rem = [x for x in inbound | outgoing if x.startswith("SEC-REM-")]
            linked_close = [x for x in inbound | outgoing if x.startswith("SEC-CLOSE-")]
            state = str(rec.get("status", "")).upper()
            if state not in {"CLOSED", "RISK_ACCEPTED"} and not linked_rem:
                add(rid, "finding_to_remediation", "open finding has no remediation disposition", "high")
            if state == "CLOSED" and not linked_close:
                add(rid, "finding_to_closure", "finding marked CLOSED without closure record", "critical")

        elif kind == "remediation":
            linked_retest = [x for x in inbound | outgoing if x.startswith("SEC-RETEST-")]
            state = str(rec.get("status", "")).upper()
            if state in {"IMPLEMENTED", "COMPLETE", "COMPLETED"} and not linked_retest:
                add(rid, "remediation_to_retest", "implemented remediation has no retest", "high")

        elif kind == "retest":
            result = rec.get("result") if isinstance(rec.get("result"), dict) else {}
            state = str(result.get("state", "pending")).upper()
            if state == "PASS" and not result.get("evidence_refs"):
                add(rid, "retest_to_evidence", "PASS retest has no evidence refs", "critical")

    by_dimension: dict[str, int] = {}
    for gap in gaps:
        by_dimension[gap["dimension"]] = by_dimension.get(gap["dimension"], 0) + 1

    return {
        "record_count": len(records),
        "gap_count": len(gaps),
        "gaps_by_dimension": dict(sorted(by_dimension.items())),
        "gaps": sorted(gaps, key=lambda x: ({"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 9), x["id"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Security Core coverage gaps")
    parser.add_argument("--root", type=Path, default=Path("security-core"))
    parser.add_argument("--output", type=Path, default=Path("generated/security-coverage.json"))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    records = collect(args.root)
    result = report(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"records={result['record_count']} gaps={result['gap_count']}")
    for gap in result["gaps"]:
        print(f"{gap['priority'].upper():8} {gap['id']} {gap['dimension']}: {gap['reason']}")
    return 1 if args.strict and result["gap_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
