from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

SCHEMA_VERSION = "1.0"
DEFAULT_INTAKE = Path(r"G:\1\FATHER_LIBRARY_INTAKE")
DEFAULT_OUTPUT = Path(r"G:\1\FATHER_LIBRARY_PROBE")
MAX_TEXT_CHARS = 24000
PDF_PAGES = 4

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

ISSUER_PATTERNS = [
    ("FSTEC", re.compile(r"ФСТЭК|Федеральн\w*\s+служб\w*\s+по\s+техническ\w*\s+и\s+экспортн\w*\s+контрол", re.I)),
    ("FSB", re.compile(r"\bФСБ\b|Федеральн\w*\s+служб\w*\s+безопасност", re.I)),
    ("RKN", re.compile(r"Роскомнадзор|Федеральн\w*\s+служб\w*\s+по\s+надзор\w*\s+в\s+сфер\w*\s+связ", re.I)),
    ("MINCIFRY", re.compile(r"Минцифр|Министерств\w*\s+цифрового\s+развит", re.I)),
    ("MINZDRAV", re.compile(r"Минздрав|Министерств\w*\s+здравоохран", re.I)),
    ("ROSSTANDART", re.compile(r"Росстандарт|Федеральн\w*\s+агентств\w*\s+по\s+техническому\s+регулирован", re.I)),
    ("GOV_RU", re.compile(r"Правительств\w*\s+Российск\w*\s+Федерац", re.I)),
]

PRIVATE_PATTERNS = [
    re.compile(r"паспорт", re.I), re.compile(r"снилс", re.I), re.compile(r"инн\b", re.I),
    re.compile(r"дата\s+рождения", re.I), re.compile(r"место\s+жительства", re.I),
    re.compile(r"личн\w*\s+дел", re.I), re.compile(r"трудов\w*\s+договор", re.I),
]


def normalize_text(value: str) -> str:
    value = html.unescape(value or "")
    value = value.replace("\x00", " ")
    return WS_RE.sub(" ", value).strip()


def read_text_file(path: Path) -> tuple[str, dict]:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
        try:
            return raw.decode(enc), {"extractor": f"text:{enc}"}
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), {"extractor": "text:utf-8-replace"}


def read_pdf(path: Path) -> tuple[str, dict]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:
        return "", {"extractor": "pdf:pypdf", "dependency_missing": True, "error": str(exc)}
    try:
        reader = PdfReader(str(path))
        page_count = len(reader.pages)
        chunks: list[str] = []
        for page in reader.pages[:PDF_PAGES]:
            try:
                chunks.append(page.extract_text() or "")
            except Exception:
                chunks.append("")
        text = "\n".join(chunks)
        return text, {"extractor": "pdf:pypdf", "page_count": page_count, "pages_probed": min(page_count, PDF_PAGES)}
    except Exception as exc:
        return "", {"extractor": "pdf:pypdf", "error": f"{type(exc).__name__}: {exc}"}


def read_docx(path: Path) -> tuple[str, dict]:
    try:
        with zipfile.ZipFile(path) as zf:
            data = zf.read("word/document.xml")
        root = ET.fromstring(data)
        text = " ".join(node.text or "" for node in root.iter() if node.text)
        return text, {"extractor": "docx:zipxml"}
    except Exception as exc:
        return "", {"extractor": "docx:zipxml", "error": f"{type(exc).__name__}: {exc}"}


def read_odt(path: Path) -> tuple[str, dict]:
    try:
        with zipfile.ZipFile(path) as zf:
            data = zf.read("content.xml")
        root = ET.fromstring(data)
        text = " ".join(node.text or "" for node in root.iter() if node.text)
        return text, {"extractor": "odt:zipxml"}
    except Exception as exc:
        return "", {"extractor": "odt:zipxml", "error": f"{type(exc).__name__}: {exc}"}


def read_epub(path: Path) -> tuple[str, dict]:
    try:
        chunks: list[str] = []
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith((".xhtml", ".html", ".htm"))]
            for name in names[:12]:
                data = zf.read(name).decode("utf-8", errors="ignore")
                chunks.append(TAG_RE.sub(" ", data))
                if sum(map(len, chunks)) >= MAX_TEXT_CHARS:
                    break
        return "\n".join(chunks), {"extractor": "epub:ziphtml", "members_probed": min(len(names), 12)}
    except Exception as exc:
        return "", {"extractor": "epub:ziphtml", "error": f"{type(exc).__name__}: {exc}"}


def extract_probe(path: Path) -> tuple[str, dict]:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return read_pdf(path)
    if ext == ".docx":
        return read_docx(path)
    if ext == ".odt":
        return read_odt(path)
    if ext == ".epub":
        return read_epub(path)
    if ext in {".txt", ".md", ".rtf", ".html", ".htm", ".csv"}:
        return read_text_file(path)
    return "", {"extractor": "unsupported", "unsupported": True}


def detect_issuer(text: str, fallback: str) -> str:
    for issuer, rx in ISSUER_PATTERNS:
        if rx.search(text):
            return issuer
    return fallback or "UNKNOWN"


def detect_language(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "UNKNOWN"
    cyr = sum("а" <= c.lower() <= "я" or c.lower() == "ё" for c in letters)
    lat = sum("a" <= c.lower() <= "z" for c in letters)
    if cyr > lat * 1.5:
        return "RU"
    if lat > cyr * 1.5:
        return "EN"
    return "MIXED"


def classify(text: str, filename: str, fallback_type: str) -> tuple[str, float, list[str]]:
    hay = f"{filename}\n{text[:MAX_TEXT_CHARS]}"
    reasons: list[str] = []
    scores = defaultdict(float)

    if re.search(r"\b(ГОСТ(?:\s+Р)?|ПНСТ|ОСТ\s+Р|ISO/IEC|ISO\s+\d)", hay, re.I):
        scores["STANDARD"] += 5; reasons.append("standard_identifier")
    if re.search(r"ФЕДЕРАЛЬНЫЙ\s+ЗАКОН|Федеральный\s+закон\s+от|\b\d+[-–]?ФЗ\b", hay, re.I):
        scores["LAW"] += 6; reasons.append("federal_law_marker")
    if re.search(r"ПОСТАНОВЛЕНИЕ\s+ПРАВИТЕЛЬСТВА\s+РОССИЙСКОЙ\s+ФЕДЕРАЦИИ", hay, re.I):
        scores["GOVERNMENT_DECREE"] += 7; reasons.append("government_decree_marker")
    if re.search(r"\bПРИКАЗ\b", hay, re.I) and any(rx.search(hay) for _, rx in ISSUER_PATTERNS):
        scores["AGENCY_ORDER"] += 6; reasons.append("agency_order_marker")
    if re.search(r"ISBN(?:-1[03])?\s*[: ]?\s*97[89]|©|Copyright|Издательств|O'Reilly|Packt|Manning|Apress", hay, re.I):
        scores["BOOK"] += 4; reasons.append("book_metadata_marker")
    if re.search(r"Содержание|Оглавление|Table of Contents", hay, re.I):
        scores["BOOK"] += 1.5; reasons.append("toc_marker")

    fallback_map = {
        "STANDARD": "STANDARD", "LAW": "LAW", "GOVERNMENT_DECREE": "GOVERNMENT_DECREE",
        "AGENCY_ORDER": "AGENCY_ORDER", "BOOK_CANDIDATE": "BOOK",
    }
    if fallback_type in fallback_map:
        scores[fallback_map[fallback_type]] += 0.5

    if not scores:
        return "UNRESOLVED", 0.0, ["no_semantic_marker"]
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_type, best_score = ordered[0]
    second = ordered[1][1] if len(ordered) > 1 else 0.0
    confidence = max(0.0, min(1.0, (best_score - second + 1.0) / 7.0))
    return best_type, round(confidence, 3), reasons


def load_registry(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="FATHER stage-2 content identification probe")
    ap.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--progress-every", type=int, default=50)
    args = ap.parse_args()

    intake = args.intake.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    registry_path = intake / "library_source_registry.csv"
    if not registry_path.exists():
        print(f"ERROR: registry not found: {registry_path}", file=sys.stderr)
        return 2

    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()
    records = load_registry(registry_path)

    # One content-processing representative per exact SHA; preserve every alias.
    canonical_by_group: dict[str, str] = {}
    for r in records:
        group = (r.get("duplicate_group") or "").strip()
        if group and group not in canonical_by_group:
            canonical_by_group[group] = r["source_id"]

    out: list[dict] = []
    failures: list[dict] = []
    for idx, r in enumerate(records, start=1):
        group = (r.get("duplicate_group") or "").strip()
        if group and canonical_by_group.get(group) != r["source_id"]:
            out.append({
                **r,
                "probe_status": "DUPLICATE_ALIAS",
                "canonical_source_id": canonical_by_group[group],
                "verified_type": "DUPLICATE_ALIAS",
                "content_confidence": None,
            })
            continue

        path = Path(r.get("absolute_path") or "") if r.get("absolute_path") else None
        if path is None or not path.exists():
            # CSV intentionally omits absolute_path; reconstruct from Scan-01 root + relative_path.
            root = Path(r"G:\1\OTUS\Библиотека")
            path = root / (r.get("relative_path") or "")

        try:
            raw_text, meta = extract_probe(path)
            text = normalize_text(raw_text)[:MAX_TEXT_CHARS]
            ext = path.suffix.lower()
            page_count = meta.get("page_count")
            ocr_required = bool(ext == ".pdf" and page_count and len(text) < 180 and not meta.get("dependency_missing"))
            dependency_missing = bool(meta.get("dependency_missing"))
            private_hit = any(rx.search(text[:12000]) for rx in PRIVATE_PATTERNS)

            if dependency_missing:
                status = "DEPENDENCY_MISSING"
                verified_type = "UNRESOLVED"
                confidence = 0.0
                reasons = ["pdf_dependency_missing"]
            elif ocr_required:
                status = "OCR_REQUIRED"
                verified_type = "UNRESOLVED"
                confidence = 0.0
                reasons = ["insufficient_extractable_pdf_text"]
            elif meta.get("unsupported"):
                status = "UNRESOLVED"
                verified_type = "UNRESOLVED"
                confidence = 0.0
                reasons = ["unsupported_format"]
            else:
                verified_type, confidence, reasons = classify(text, path.name, r.get("source_type") or "")
                status = "PRIVATE_REVIEW" if private_hit else ("IDENTIFIED" if verified_type != "UNRESOLVED" else "UNRESOLVED")

            title_hint = text[:500] if text else path.stem
            content_sha = hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None
            out.append({
                **r,
                "probe_status": status,
                "verified_type": verified_type,
                "content_confidence": confidence,
                "issuer_verified": detect_issuer(text, r.get("issuer") or "UNKNOWN"),
                "language": detect_language(text),
                "extractor": meta.get("extractor"),
                "page_count": page_count,
                "probe_text_chars": len(text),
                "probe_text_sha256": content_sha,
                "title_hint": title_hint,
                "classification_reasons": reasons,
                "canonical_source_id": r["source_id"],
                "private_content_flag": private_hit,
                "extractor_error": meta.get("error"),
            })
        except Exception as exc:
            failures.append({"source_id": r.get("source_id"), "path": str(path), "error": f"{type(exc).__name__}: {exc}"})
            out.append({**r, "probe_status": "UNRESOLVED", "verified_type": "UNRESOLVED", "probe_error": str(exc)})

        if args.progress_every and idx % args.progress_every == 0:
            print(f"[PROBE] records={idx} current={path.name}")

    write_jsonl(output / "content_probe_registry.jsonl", out)
    write_jsonl(output / "identified_legal_queue.jsonl", [x for x in out if x.get("verified_type") in {"LAW", "GOVERNMENT_DECREE", "AGENCY_ORDER"} and x.get("probe_status") == "IDENTIFIED"])
    write_jsonl(output / "identified_standards_queue.jsonl", [x for x in out if x.get("verified_type") == "STANDARD" and x.get("probe_status") == "IDENTIFIED"])
    write_jsonl(output / "identified_books_queue.jsonl", [x for x in out if x.get("verified_type") == "BOOK" and x.get("probe_status") == "IDENTIFIED"])
    write_jsonl(output / "ocr_required_queue.jsonl", [x for x in out if x.get("probe_status") == "OCR_REQUIRED"])
    write_jsonl(output / "private_review_queue_stage2.jsonl", [x for x in out if x.get("probe_status") == "PRIVATE_REVIEW"])
    write_jsonl(output / "unresolved_queue.jsonl", [x for x in out if x.get("probe_status") in {"UNRESOLVED", "DEPENDENCY_MISSING"}])
    write_jsonl(output / "duplicate_aliases.jsonl", [x for x in out if x.get("probe_status") == "DUPLICATE_ALIAS"])

    status_counts = Counter(x.get("probe_status") for x in out)
    type_counts = Counter(x.get("verified_type") for x in out)
    elapsed = time.perf_counter() - started
    summary = {
        "record_type": "FATHER_LIBRARY_CONTENT_PROBE_RUN",
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if not failures else "PASS_WITH_FILE_ERRORS",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "records_total": len(out),
        "status_counts": dict(status_counts),
        "verified_type_counts": dict(type_counts),
        "file_errors_total": len(failures),
        "speedup_vs_1_stream_pct": None,
        "eta_seconds": None,
        "notes": [
            "Stage-2 is bounded content identification, not legal analysis or knowledge extraction.",
            "Exact SHA duplicate aliases are not re-read; one canonical source per group is probed.",
            "PDFs with insufficient extractable text are routed to OCR_REQUIRED; OCR is not performed here.",
            "No original is moved, renamed, deleted, uploaded or modified.",
        ],
    }
    (output / "LATEST_LIBRARY_PROBE_REPORT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "probe_failures.json").write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# FATHER Library Content Probe — latest report", "",
        f"- Status: **{summary['status']}**",
        f"- Records: **{len(out)}**",
        f"- File errors: **{len(failures)}**",
        f"- Elapsed: **{summary['elapsed_seconds']} s**", "",
        "## Probe statuses", "", "| Status | Count |", "|---|---:|",
    ]
    md.extend(f"| {k} | {v} |" for k, v in status_counts.most_common())
    md += ["", "## Verified types", "", "| Type | Count |", "|---|---:|"]
    md.extend(f"| {k} | {v} |" for k, v in type_counts.most_common())
    md += ["", "> Identification only. No source files were modified."]
    (output / "LATEST_LIBRARY_PROBE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report: {output / 'LATEST_LIBRARY_PROBE_REPORT.md'}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
