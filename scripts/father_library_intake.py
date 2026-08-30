from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = "1.0"
DEFAULT_ROOT = Path(r"G:\1\OTUS\Библиотека")
DEFAULT_OUTPUT = Path(r"G:\1\FATHER_LIBRARY_INTAKE")

BOOK_EXTENSIONS = {
    ".pdf", ".epub", ".djvu", ".djv", ".fb2", ".mobi", ".azw", ".azw3",
    ".doc", ".docx", ".odt", ".rtf", ".txt", ".md", ".html", ".htm",
}

AGENCY_PATTERNS = [
    ("FSTEC", re.compile(r"фстэк|fstec", re.I)),
    ("FSB", re.compile(r"\bфсб\b|fsb", re.I)),
    ("RKN", re.compile(r"роскомнадзор|rkn", re.I)),
    ("MINCIFRY", re.compile(r"минцифр|минкомсвяз|digital ministry", re.I)),
    ("MINZDRAV", re.compile(r"минздрав", re.I)),
    ("ROSFINS", re.compile(r"росфинмонитор", re.I)),
    ("ROSSTANDART", re.compile(r"росстандарт", re.I)),
    ("GOV_RU", re.compile(r"правительств.{0,20}(рф|российск)|government", re.I)),
]

PERSONAL_RISK_PATTERNS = [
    re.compile(r"куличенко", re.I),
    re.compile(r"для\s+виктора", re.I),
    re.compile(r"отправитель", re.I),
    re.compile(r"паспорт|снилс|инн|трудов|резюме|анкета", re.I),
    re.compile(r"ул\.|улиц|квартир|адрес", re.I),
]

INTERNAL_RISK_PATTERNS = [
    re.compile(r"положение.{0,30}отдел", re.I),
    re.compile(r"приказ.{0,30}ответствен", re.I),
    re.compile(r"первичн.{0,20}инструктаж", re.I),
]

GOST_RE = re.compile(r"(?:^|[^a-zа-я])(?:гост\s*р?|gost\s*r?|пнст|pnst)\s*[-_№\s]*\d", re.I)
LAW_RE = re.compile(r"(?:\b\d+\s*[-–]?\s*фз\b|федеральн.{0,20}закон|federal.{0,10}law|federalny.{0,15}zakon)", re.I)
GOV_DECREE_RE = re.compile(r"постановлен.{0,30}правительств|\bпп\s*(?:рф)?\s*№?\s*\d", re.I)
ORDER_RE = re.compile(r"\bприказ\b|\border\b", re.I)
REGULATORY_HINT_RE = re.compile(r"распоряжен|постановлен|приказ|федеральн.{0,10}закон|\bфз\b|норматив|регламент", re.I)

@dataclass
class FileRecord:
    source_id: str
    relative_path: str
    absolute_path: str
    filename: str
    extension: str
    size_bytes: int
    modified_utc: str
    sha256: str | None
    source_type: str
    issuer: str | None
    pipeline: str
    privacy_risk: bool
    internal_document_risk: bool
    classification_basis: list[str]
    duplicate_group: str | None = None
    duplicate_count: int = 1


def utc_iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(chunk_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def detect_issuer(text: str) -> str | None:
    for issuer, pattern in AGENCY_PATTERNS:
        if pattern.search(text):
            return issuer
    return None


def classify(path: Path, root: Path) -> tuple[str, str | None, str, bool, bool, list[str]]:
    rel = str(path.relative_to(root))
    text = f"{rel} {path.name}"
    basis: list[str] = []
    issuer = detect_issuer(text)
    privacy = any(p.search(text) for p in PERSONAL_RISK_PATTERNS)
    internal = any(p.search(text) for p in INTERNAL_RISK_PATTERNS)

    if GOST_RE.search(text):
        basis.append("filename/path matches GOST/PNST identifier")
        return "STANDARD", issuer or "ROSSTANDART", "STANDARD_PIPELINE", privacy, internal, basis
    if LAW_RE.search(text):
        basis.append("filename/path matches federal-law pattern")
        return "LAW", "FEDERAL", "LEGAL_PIPELINE", privacy, internal, basis
    if GOV_DECREE_RE.search(text):
        basis.append("filename/path matches Government decree pattern")
        return "GOVERNMENT_DECREE", "GOV_RU", "LEGAL_PIPELINE", privacy, internal, basis
    if ORDER_RE.search(text):
        basis.append("filename/path matches agency-order pattern")
        return "AGENCY_ORDER", issuer or "UNKNOWN_AGENCY", "LEGAL_PIPELINE", privacy, internal, basis
    if REGULATORY_HINT_RE.search(text):
        basis.append("filename/path has regulatory vocabulary but exact type is uncertain")
        return "REGULATORY_CANDIDATE", issuer, "LEGAL_REVIEW", privacy, internal, basis

    ext = path.suffix.lower()
    if ext in BOOK_EXTENSIONS:
        # A book/document-format file with no reliable regulatory marker is only a BOOK_CANDIDATE.
        # The second-stage content probe will distinguish books from project/internal documents.
        basis.append("book/document extension; no reliable regulatory marker")
        return "BOOK_CANDIDATE", issuer, "BOOK_PROBE", privacy, internal, basis

    basis.append("no first-pass classification rule matched")
    return "OTHER", issuer, "MANUAL_REVIEW", privacy, internal, basis


def iter_files(root: Path, output: Path) -> Iterable[Path]:
    output_resolved = output.resolve() if output.exists() else output
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        # Avoid accidental recursive scan if output is ever placed under root.
        dirnames[:] = [d for d in dirnames if not (current / d).resolve() == output_resolved]
        for name in filenames:
            path = current / name
            if path.is_file():
                yield path


def write_jsonl(path: Path, records: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="FATHER local library intake scanner")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--mode", choices=("full", "metadata"), default="full",
                        help="full=SHA256 every file; metadata=skip hashes")
    parser.add_argument("--progress-every", type=int, default=100)
    args = parser.parse_args()

    root = args.root
    output = args.output
    if not root.exists() or not root.is_dir():
        print(json.dumps({"status": "FAIL", "error": f"Library root not found: {root}"}, ensure_ascii=False))
        return 2

    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()

    records: list[FileRecord] = []
    failures: list[dict] = []
    hashes: defaultdict[str, list[int]] = defaultdict(list)

    for idx, path in enumerate(iter_files(root, output), start=1):
        try:
            stat = path.stat()
            sha = sha256_file(path) if args.mode == "full" else None
            source_type, issuer, pipeline, privacy, internal, basis = classify(path, root)
            identity_seed = sha or f"{path.relative_to(root)}:{stat.st_size}:{stat.st_mtime_ns}"
            source_id = "SRC-" + hashlib.sha256(identity_seed.encode("utf-8")).hexdigest()[:20].upper()
            record = FileRecord(
                source_id=source_id,
                relative_path=str(path.relative_to(root)),
                absolute_path=str(path),
                filename=path.name,
                extension=path.suffix.lower(),
                size_bytes=stat.st_size,
                modified_utc=utc_iso(stat.st_mtime),
                sha256=sha,
                source_type=source_type,
                issuer=issuer,
                pipeline=pipeline,
                privacy_risk=privacy,
                internal_document_risk=internal,
                classification_basis=basis,
            )
            records.append(record)
            if sha:
                hashes[sha].append(len(records) - 1)
            if args.progress_every and idx % args.progress_every == 0:
                print(f"[SCAN] files={idx} current={path.name}")
        except Exception as exc:  # per-file failure must not abort the inventory
            failures.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})

    duplicate_groups: list[dict] = []
    if args.mode == "full":
        for sha, indexes in hashes.items():
            if len(indexes) > 1:
                group = "DUP-" + sha[:16].upper()
                duplicate_groups.append({
                    "duplicate_group": group,
                    "sha256": sha,
                    "count": len(indexes),
                    "paths": [records[i].absolute_path for i in indexes],
                })
                for i in indexes:
                    records[i].duplicate_group = group
                    records[i].duplicate_count = len(indexes)

    records.sort(key=lambda r: r.relative_path.casefold())
    raw_records = [asdict(r) for r in records]

    write_jsonl(output / "library_source_registry.jsonl", raw_records)
    write_jsonl(output / "legal_queue.jsonl", [r for r in raw_records if r["pipeline"] in {"LEGAL_PIPELINE", "LEGAL_REVIEW"}])
    write_jsonl(output / "standards_queue.jsonl", [r for r in raw_records if r["pipeline"] == "STANDARD_PIPELINE"])
    write_jsonl(output / "book_queue.jsonl", [r for r in raw_records if r["pipeline"] == "BOOK_PROBE"])
    write_jsonl(output / "private_review_queue.jsonl", [r for r in raw_records if r["privacy_risk"] or r["internal_document_risk"]])
    write_jsonl(output / "other_review_queue.jsonl", [r for r in raw_records if r["pipeline"] == "MANUAL_REVIEW"])

    with (output / "library_source_registry.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        fieldnames = [
            "source_id", "relative_path", "filename", "extension", "size_bytes", "modified_utc",
            "sha256", "source_type", "issuer", "pipeline", "privacy_risk", "internal_document_risk",
            "duplicate_group", "duplicate_count",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in raw_records:
            writer.writerow({k: r.get(k) for k in fieldnames})

    (output / "duplicate_groups.json").write_text(
        json.dumps(duplicate_groups, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "scan_failures.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    type_counts = Counter(r.source_type for r in records)
    pipeline_counts = Counter(r.pipeline for r in records)
    extension_counts = Counter(r.extension or "<none>" for r in records)
    issuer_counts = Counter(r.issuer or "UNKNOWN" for r in records)
    total_bytes = sum(r.size_bytes for r in records)
    elapsed = time.perf_counter() - started

    summary = {
        "record_type": "FATHER_LIBRARY_INTAKE_RUN",
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if not failures else "PASS_WITH_FILE_ERRORS",
        "mode": args.mode,
        "root": str(root),
        "output": str(output),
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "files_total": len(records),
        "bytes_total": total_bytes,
        "gib_total": round(total_bytes / (1024 ** 3), 3),
        "source_type_counts": dict(type_counts),
        "pipeline_counts": dict(pipeline_counts),
        "extension_counts": dict(extension_counts.most_common()),
        "issuer_counts": dict(issuer_counts.most_common()),
        "duplicate_groups_total": len(duplicate_groups),
        "duplicate_file_instances_total": sum(g["count"] for g in duplicate_groups),
        "privacy_or_internal_review_total": sum(1 for r in records if r.privacy_risk or r.internal_document_risk),
        "file_errors_total": len(failures),
        "speedup_vs_1_stream_pct": None,
        "eta_seconds": None,
        "notes": [
            "First-pass classification uses filename/path metadata only; no PDF/document content is parsed.",
            "BOOK_CANDIDATE is not a verified book; second-stage content probing is required.",
            "No source file is moved, renamed, deleted, translated, uploaded or modified.",
            "No production ETA/speedup is reported without a measured one-stream baseline.",
        ],
    }
    (output / "LATEST_LIBRARY_INTAKE_REPORT.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# FATHER Library Intake — latest report",
        "",
        f"- Status: **{summary['status']}**",
        f"- Root: `{root}`",
        f"- Mode: `{args.mode}`",
        f"- Files: **{len(records)}**",
        f"- Size: **{summary['gib_total']} GiB**",
        f"- Duplicate groups: **{len(duplicate_groups)}**",
        f"- Privacy/internal review: **{summary['privacy_or_internal_review_total']}**",
        f"- File errors: **{len(failures)}**",
        f"- Elapsed: **{summary['elapsed_seconds']} s**",
        "",
        "## Source types",
        "",
        "| Type | Count |",
        "|---|---:|",
    ]
    md.extend(f"| {k} | {v} |" for k, v in type_counts.most_common())
    md += ["", "## Pipelines", "", "| Pipeline | Count |", "|---|---:|"]
    md.extend(f"| {k} | {v} |" for k, v in pipeline_counts.most_common())
    md += [
        "",
        "## Outputs",
        "",
        "- `library_source_registry.jsonl` — full local registry",
        "- `library_source_registry.csv` — human-readable registry",
        "- `legal_queue.jsonl` — laws/decrees/orders/regulatory candidates",
        "- `standards_queue.jsonl` — GOST/PNST candidates",
        "- `book_queue.jsonl` — document/book candidates for stage-2 probing",
        "- `private_review_queue.jsonl` — possible personal/internal files",
        "- `other_review_queue.jsonl` — unknown files",
        "- `duplicate_groups.json` — exact SHA-256 duplicate groups",
        "- `scan_failures.json` — per-file errors",
        "",
        "> This scan does not modify or upload originals.",
    ]
    (output / "LATEST_LIBRARY_INTAKE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report: {output / 'LATEST_LIBRARY_INTAKE_REPORT.md'}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
