from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"
DEFAULT_PROBE = Path(r"G:\1\FATHER_LIBRARY_PROBE_V2")
DEFAULT_OUTPUT = Path(r"G:\1\FATHER_LIBRARY_STAGE3")

AUTO_TYPES = {"LAW", "GOVERNMENT_DECREE", "AGENCY_ORDER", "STANDARD", "BOOK"}
LEGAL_TYPES = {"LAW", "GOVERNMENT_DECREE", "AGENCY_ORDER"}
QUARANTINE_STATUSES = {
    "REVIEW_REQUIRED",
    "OCR_REQUIRED",
    "PDF_REPAIR_REQUIRED",
    "PRIVATE_REVIEW",
    "UNRESOLVED",
    "DEPENDENCY_MISSING",
    "EXTRACT_FAILED",
}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def authority_contract(verified_type: str) -> dict:
    if verified_type == "LAW":
        return {
            "authority_class": "LEGISLATION",
            "legal_use_status": "OFFICIAL_SOURCE_AND_CURRENTNESS_VERIFICATION_REQUIRED",
            "knowledge_contract": "ATOMIC_LEGAL_NORMS",
        }
    if verified_type == "GOVERNMENT_DECREE":
        return {
            "authority_class": "GOVERNMENT_NPA",
            "legal_use_status": "OFFICIAL_SOURCE_AND_CURRENTNESS_VERIFICATION_REQUIRED",
            "knowledge_contract": "ATOMIC_LEGAL_NORMS_AND_DELEGATED_RULES",
        }
    if verified_type == "AGENCY_ORDER":
        return {
            "authority_class": "AGENCY_NPA",
            "legal_use_status": "AUTHORITY_REGISTRATION_SCOPE_AND_CURRENTNESS_REVIEW_REQUIRED",
            "knowledge_contract": "AGENCY_REQUIREMENTS_AND_MEASURES",
        }
    if verified_type == "STANDARD":
        return {
            "authority_class": "STANDARD",
            "legal_use_status": "APPLICABILITY_AND_MANDATORY_STATUS_REVIEW_REQUIRED",
            "knowledge_contract": "CLAUSES_REQUIREMENTS_PROCESSES_ARTIFACTS_VERIFICATION",
        }
    if verified_type == "BOOK":
        return {
            "authority_class": "PROFESSIONAL_SOURCE",
            "legal_use_status": "NON_NORMATIVE",
            "knowledge_contract": "CONCEPTS_PRINCIPLES_PATTERNS_ANTI_PATTERNS_TRADEOFFS",
        }
    return {
        "authority_class": "UNRESOLVED",
        "legal_use_status": "NOT_FOR_AUTOMATIC_PROMOTION",
        "knowledge_contract": "MANUAL_REVIEW",
    }


def route(row: dict) -> dict:
    verified_type = row.get("verified_type") or "UNRESOLVED"
    probe_status = row.get("probe_status") or "UNRESOLVED"

    if probe_status == "DUPLICATE_ALIAS":
        lane = "DUPLICATE_ALIAS"
        next_stage = "LINEAGE_ONLY"
    elif probe_status in QUARANTINE_STATUSES:
        lane = "QUARANTINE"
        next_stage = probe_status
    elif probe_status == "IDENTIFIED" and verified_type in LEGAL_TYPES:
        lane = "LEGAL"
        next_stage = "LEGAL_SOURCE_VERIFICATION"
    elif probe_status == "IDENTIFIED" and verified_type == "STANDARD":
        lane = "STANDARD"
        next_stage = "STANDARD_METADATA_AND_APPLICABILITY"
    elif probe_status == "IDENTIFIED" and verified_type == "BOOK":
        lane = "BOOK"
        next_stage = "BOOK_METADATA_RIGHTS_LANGUAGE"
    else:
        lane = "QUARANTINE"
        next_stage = "MANUAL_REVIEW"

    return {
        **row,
        **authority_contract(verified_type),
        "stage3_lane": lane,
        "next_stage": next_stage,
        "promotion_allowed": bool(probe_status == "IDENTIFIED" and verified_type in AUTO_TYPES),
        "kb_ready": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="FATHER Stage-3 library router")
    ap.add_argument("--probe", type=Path, default=DEFAULT_PROBE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    probe = args.probe.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    source = probe / "content_probe_registry_v2.jsonl"
    if not source.exists():
        print(f"ERROR: V2 registry not found: {source}", file=sys.stderr)
        return 2

    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()
    rows = [route(r) for r in read_jsonl(source)]

    legal = [r for r in rows if r["stage3_lane"] == "LEGAL"]
    laws = [r for r in legal if r.get("verified_type") == "LAW"]
    decrees = [r for r in legal if r.get("verified_type") == "GOVERNMENT_DECREE"]
    orders = [r for r in legal if r.get("verified_type") == "AGENCY_ORDER"]
    standards = [r for r in rows if r["stage3_lane"] == "STANDARD"]
    books = [r for r in rows if r["stage3_lane"] == "BOOK"]
    quarantine = [r for r in rows if r["stage3_lane"] == "QUARANTINE"]
    aliases = [r for r in rows if r["stage3_lane"] == "DUPLICATE_ALIAS"]

    write_jsonl(output / "stage3_processing_manifest.jsonl", rows)
    write_jsonl(output / "legal_queue.jsonl", legal)
    write_jsonl(output / "laws_queue.jsonl", laws)
    write_jsonl(output / "government_decrees_queue.jsonl", decrees)
    write_jsonl(output / "agency_orders_queue.jsonl", orders)
    write_jsonl(output / "standards_queue.jsonl", standards)
    write_jsonl(output / "books_queue.jsonl", books)
    write_jsonl(output / "quarantine_queue.jsonl", quarantine)
    write_jsonl(output / "duplicate_aliases.jsonl", aliases)

    lane_counts = Counter(r["stage3_lane"] for r in rows)
    next_counts = Counter(r["next_stage"] for r in rows)
    type_counts = Counter(r.get("verified_type") for r in rows if r.get("promotion_allowed"))
    elapsed = time.perf_counter() - started

    summary = {
        "record_type": "FATHER_LIBRARY_STAGE3_ROUTER_RUN",
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "records_total": len(rows),
        "lane_counts": dict(lane_counts),
        "promotion_type_counts": dict(type_counts),
        "next_stage_counts": dict(next_counts),
        "kb_ready_count": 0,
        "notes": [
            "Stage 3 routes only; it does not perform legal analysis, OCR, repair, translation or knowledge extraction.",
            "Legal sources require official-source/currentness checks before legal norms are promoted.",
            "Standards require applicability/mandatory-status review before use as obligations.",
            "Books are non-normative professional sources and never override binding legal sources.",
            "Duplicate aliases remain lineage-only and are not reprocessed.",
        ],
    }
    (output / "LATEST_STAGE3_ROUTER_REPORT.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# FATHER Library Stage 3 Router — latest report",
        "",
        f"- Status: **{summary['status']}**",
        f"- Records: **{len(rows)}**",
        f"- Elapsed: **{summary['elapsed_seconds']} s**",
        f"- KB_READY: **0** (routing only)",
        "",
        "## Lanes",
        "",
        "| Lane | Count |",
        "|---|---:|",
    ]
    md.extend(f"| {k} | {v} |" for k, v in lane_counts.most_common())
    md += ["", "## Auto-promotable source types (to next analysis stage only)", "", "| Type | Count |", "|---|---:|"]
    md.extend(f"| {k} | {v} |" for k, v in type_counts.most_common())
    md += [
        "",
        "## Hard gates",
        "",
        "- LEGAL -> official source + currentness + scope/applicability verification",
        "- STANDARD -> metadata + currentness + legal applicability review",
        "- BOOK -> metadata + language + rights + translation decision",
        "- QUARANTINE -> no automatic knowledge promotion",
        "- DUPLICATE_ALIAS -> lineage only",
    ]
    (output / "LATEST_STAGE3_ROUTER_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report: {output / 'LATEST_STAGE3_ROUTER_REPORT.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
