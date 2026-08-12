from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECORD_ROOTS = [
    "sources", "claims", "tests", "benchmarks", "experiments",
    "decisions", "decision-memory",
]


def load_records() -> dict[str, tuple[Path, dict]]:
    records: dict[str, tuple[Path, dict]] = {}
    for root_name in RECORD_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.yaml"):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            rid = data.get("id") or data.get("record_id")
            if rid:
                records[str(rid)] = (path, data)
    return records


def flatten_refs(value) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for item in value.values():
            refs |= flatten_refs(item)
    elif isinstance(value, list):
        for item in value:
            refs |= flatten_refs(item)
    elif isinstance(value, str):
        if value.startswith(("SRC-", "CLM-", "TEST-", "BENCH-", "EXP-", "ADR-", "DM-", "SEC-")):
            refs.add(value)
    return refs


def direct_health(rid: str, data: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    state = "GREEN"

    verification = data.get("verification") or {}
    verification_status = str(verification.get("status", "")).lower()
    status = str(data.get("status", "")).lower()
    review = data.get("review") or {}
    review_status = str(review.get("status", "")).lower()
    applicability = data.get("applicability") or {}

    if verification_status in {"withdrawn", "failed"}:
        return "RED", [f"verification status is {verification_status}"]
    if verification_status == "superseded" and not data.get("relationships", {}).get("superseded_by_sources"):
        return "RED", ["superseded without recorded replacement"]
    if review_status == "disputed":
        return "RED", ["claim/review is disputed"]
    if status in {"failed", "withdrawn"}:
        return "RED", [f"record status is {status}"]

    if verification_status in {"stale", "superseded"}:
        state = "YELLOW"
        reasons.append(f"verification status is {verification_status}")
    if review_status in {"stale", "unreviewed"}:
        state = "YELLOW"
        reasons.append(f"review status is {review_status}")
    if applicability.get("deprecated") is True:
        state = "YELLOW"
        reasons.append("applicability is deprecated")

    traceability = data.get("traceability") or {}
    gaps = traceability.get("unresolved_evidence_gaps") or []
    if gaps:
        state = "YELLOW"
        reasons.append(f"{len(gaps)} unresolved evidence gap(s)")

    confidence = data.get("confidence")
    if isinstance(confidence, dict):
        level = str(confidence.get("level", "")).upper()
        if level in {"UNKNOWN", "LOW", "MEDIUM"}:
            state = "YELLOW"
            reasons.append(f"confidence is {level}")

    return state, reasons


def worse(a: str, b: str) -> str:
    order = {"GREEN": 0, "YELLOW": 1, "RED": 2}
    return a if order[a] >= order[b] else b


def main() -> int:
    records = load_records()
    health: dict[str, str] = {}
    reasons: dict[str, list[str]] = {}
    deps: dict[str, set[str]] = {}

    for rid, (_, data) in records.items():
        health[rid], reasons[rid] = direct_health(rid, data)
        deps[rid] = {ref for ref in flatten_refs(data) if ref != rid and ref in records}

    changed = True
    while changed:
        changed = False
        for rid in records:
            current = health[rid]
            for dep in deps[rid]:
                dep_health = health[dep]
                promoted = worse(current, dep_health)
                if promoted != current:
                    health[rid] = promoted
                    reasons[rid].append(f"dependency {dep} is {dep_health}")
                    current = promoted
                    changed = True

    summary = {"GREEN": 0, "YELLOW": 0, "RED": 0}
    for state in health.values():
        summary[state] += 1

    report = {
        "summary": summary,
        "records": {
            rid: {
                "health": health[rid],
                "reasons": sorted(set(reasons[rid])),
                "dependencies": sorted(deps[rid]),
                "path": str(records[rid][0].relative_to(ROOT)),
            }
            for rid in sorted(records)
        },
    }

    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "evidence-health.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Evidence health:", summary)
    for rid in sorted(records):
        if health[rid] != "GREEN":
            print(f"- {health[rid]} {rid}: {'; '.join(sorted(set(reasons[rid])))}")

    # This report is diagnostic. Hard repository-integrity failures are handled by validate_knowledge.py.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
