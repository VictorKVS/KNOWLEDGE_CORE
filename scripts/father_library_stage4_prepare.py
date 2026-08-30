from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"
DEFAULT_STAGE3 = Path(r"G:\1\FATHER_LIBRARY_STAGE3")
DEFAULT_OUTPUT = Path(r"G:\1\FATHER_LIBRARY_STAGE4")

LAW_NO_RE = re.compile(r"\b(\d{1,4})\s*[-–]?\s*ФЗ\b", re.I)
DATE_RE = re.compile(r"\b(\d{1,2})[.\s/-]+(\d{1,2}|[А-Яа-яЁё]+)[.\s/-]+(20\d{2}|19\d{2})\b")
DECREE_NO_RE = re.compile(r"(?:постановлен\w*[^№N\d]{0,80})(?:№|N)?\s*(\d{1,6})", re.I)
ORDER_NO_RE = re.compile(r"(?:приказ\w*[^№N\d]{0,80})(?:№|N)?\s*([0-9А-ЯA-Z/-]{1,20})", re.I)
STANDARD_RE = re.compile(r"\b((?:ГОСТ(?:\s+Р)?|ПНСТ|ОСТ\s+Р)\s*[А-ЯA-Z0-9./-]*(?:\s+|-)?\d{2,6}(?:[.-]\d{1,4})*)", re.I)

P0_STANDARDS = {
    "71752-2024", "59194-2020", "57100-2025", "57193-2025", "72118-2025",
    "56939-2024", "58412-2019", "59548-2022", "59547-2021", "71207-2024",
}


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSONL {path}:{n}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def first_match(rx: re.Pattern, text: str) -> str | None:
    m = rx.search(text or "")
    return m.group(1).strip() if m else None


def standard_key(value: str | None) -> str | None:
    if not value:
        return None
    m = re.search(r"(\d{4,6}-20\d{2})", value)
    return m.group(1) if m else None


def legal_card(row: dict) -> dict:
    filename = row.get("filename") or ""
    rel = row.get("relative_path") or ""
    text = f"{filename} {rel}"
    typ = row.get("verified_type") or "UNRESOLVED"
    number = None
    if typ == "LAW":
        number = first_match(LAW_NO_RE, text)
    elif typ == "GOVERNMENT_DECREE":
        number = first_match(DECREE_NO_RE, text)
    elif typ == "AGENCY_ORDER":
        number = first_match(ORDER_NO_RE, text)
    return {
        "source_occurrence_id": row.get("source_occurrence_id"),
        "content_id": row.get("content_id"),
        "sha256": row.get("sha256"),
        "relative_path": rel,
        "filename": filename,
        "document_type": typ,
        "issuer_detected": row.get("issuer_verified") or row.get("issuer") or "UNKNOWN",
        "document_number_hint": number,
        "document_date_hint": first_match(DATE_RE, text),
        "official_source_status": "PENDING",
        "currentness_status": "PENDING",
        "scope_status": "PENDING",
        "registration_status": "PENDING" if typ == "AGENCY_ORDER" else "NOT_APPLICABLE",
        "amendment_lineage_status": "PENDING",
        "verification_result": "NOT_VERIFIED",
        "promotion_allowed": False,
        "next_action": "VERIFY_OFFICIAL_SOURCE_CURRENTNESS_SCOPE",
    }


def standard_card(row: dict) -> dict:
    filename = row.get("filename") or ""
    rel = row.get("relative_path") or ""
    text = f"{filename} {rel}"
    standard_id = first_match(STANDARD_RE, text)
    key = standard_key(standard_id)
    return {
        "source_occurrence_id": row.get("source_occurrence_id"),
        "content_id": row.get("content_id"),
        "sha256": row.get("sha256"),
        "relative_path": rel,
        "filename": filename,
        "standard_id_hint": standard_id,
        "priority": "P0" if key in P0_STANDARDS else "P1",
        "official_catalog_status": "PENDING",
        "currentness_status": "PENDING",
        "superseded_by": None,
        "legal_applicability": "PENDING_REVIEW",
        "mandatory_basis": None,
        "technical_relevance": "PENDING",
        "verification_result": "NOT_VERIFIED",
        "promotion_as_obligation_allowed": False,
        "promotion_as_guidance_allowed": False,
        "next_action": "VERIFY_CATALOG_CURRENTNESS_APPLICABILITY",
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = []
    seen = set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k); keys.append(k)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader(); w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="FATHER Stage 4 preparation: legal/standards verification manifests")
    ap.add_argument("--stage3", type=Path, default=DEFAULT_STAGE3)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    stage3 = args.stage3.resolve(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    legal_path = stage3 / "legal_queue.jsonl"
    standards_path = stage3 / "standards_queue.jsonl"
    if not legal_path.exists() or not standards_path.exists():
        print(f"ERROR: missing Stage3 queues under {stage3}", file=sys.stderr); return 2

    started = time.perf_counter(); started_at = datetime.now(timezone.utc).isoformat()
    legal = [legal_card(x) for x in read_jsonl(legal_path)]
    standards = [standard_card(x) for x in read_jsonl(standards_path)]

    write_jsonl(output / "legal_verification_manifest.jsonl", legal)
    write_jsonl(output / "standards_verification_manifest.jsonl", standards)
    write_csv(output / "legal_verification_manifest.csv", legal)
    write_csv(output / "standards_verification_manifest.csv", standards)
    write_jsonl(output / "legal_p0_queue.jsonl", [x for x in legal if x["document_type"] in {"LAW", "GOVERNMENT_DECREE", "AGENCY_ORDER"}])
    write_jsonl(output / "standards_p0_queue.jsonl", [x for x in standards if x["priority"] == "P0"])
    write_jsonl(output / "standards_p1_queue.jsonl", [x for x in standards if x["priority"] == "P1"])

    summary = {
        "record_type": "FATHER_LIBRARY_STAGE4_PREPARE_RUN",
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "legal_total": len(legal),
        "legal_type_counts": dict(Counter(x["document_type"] for x in legal)),
        "standards_total": len(standards),
        "standards_priority_counts": dict(Counter(x["priority"] for x in standards)),
        "officially_verified_count": 0,
        "kb_ready_count": 0,
        "notes": [
            "Preparation only: no legal or standards status is asserted from filenames.",
            "LEGAL requires official source, currentness, scope and amendment-lineage verification.",
            "AGENCY_ORDER also requires registration/authority review where applicable.",
            "STANDARD requires official catalog status, currentness and legal applicability review.",
            "No source file is modified or uploaded.",
        ],
    }
    (output / "LATEST_STAGE4_PREPARE_REPORT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# FATHER Stage 4 Preparation — latest report", "",
        f"- Status: **PASS**", f"- LEGAL cards: **{len(legal)}**", f"- STANDARD cards: **{len(standards)}**",
        f"- Officially verified: **0**", f"- KB_READY: **0**", "",
        "## Legal types", "", "| Type | Count |", "|---|---:|",
    ]
    for k, v in Counter(x["document_type"] for x in legal).most_common(): md.append(f"| {k} | {v} |")
    md += ["", "## Standards priority", "", "| Priority | Count |", "|---|---:|"]
    for k, v in Counter(x["priority"] for x in standards).most_common(): md.append(f"| {k} | {v} |")
    md += ["", "> Stage 4 Preparation creates verification cards only; it does not promote obligations or knowledge."]
    (output / "LATEST_STAGE4_PREPARE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report: {output / 'LATEST_STAGE4_PREPARE_REPORT.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
