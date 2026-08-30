from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import logging
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

SCHEMA_VERSION = "2.0"
DEFAULT_INTAKE = Path(r"G:\1\FATHER_LIBRARY_INTAKE")
DEFAULT_OUTPUT = Path(r"G:\1\FATHER_LIBRARY_PROBE_V2")
LIBRARY_ROOT = Path(r"G:\1\OTUS\Библиотека")
MAX_TEXT_CHARS = 24000
HEADER_CHARS = 4500
PDF_PAGES = 4

logging.getLogger("pypdf").setLevel(logging.ERROR)
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

STRONG_PRIVATE = [
    re.compile(r"паспорт\w*\s+(?:серия|№|номер)", re.I),
    re.compile(r"СНИЛС\s*[:№]?\s*\d", re.I),
    re.compile(r"дата\s+рождения\s*[:]?\s*\d", re.I),
    re.compile(r"место\s+жительства\s*:", re.I),
    re.compile(r"личн\w*\s+дел\w*\s*№", re.I),
    re.compile(r"трудов\w*\s+договор\w*\s*№", re.I),
]


def normalize_text(value: str) -> str:
    value = html.unescape(value or "").replace("\x00", " ")
    return WS_RE.sub(" ", value).strip()


def read_text_file(path: Path) -> tuple[str, dict]:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
        try:
            return raw.decode(enc), {"extractor": f"text:{enc}"}
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace"), {"extractor": "text:utf-8-replace"}


def read_pdf(path: Path) -> tuple[str, dict]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:
        return "", {"extractor": "pdf:pypdf", "dependency_missing": True, "error": str(exc)}
    try:
        reader = PdfReader(str(path), strict=False)
        page_count = len(reader.pages)
        chunks = []
        for page in reader.pages[:PDF_PAGES]:
            try:
                chunks.append(page.extract_text() or "")
            except Exception:
                chunks.append("")
        return "\n".join(chunks), {
            "extractor": "pdf:pypdf",
            "page_count": page_count,
            "pages_probed": min(page_count, PDF_PAGES),
        }
    except Exception as exc:
        return "", {"extractor": "pdf:pypdf", "error": f"{type(exc).__name__}: {exc}"}


def read_zip_xml(path: Path, member: str, label: str) -> tuple[str, dict]:
    try:
        with zipfile.ZipFile(path) as zf:
            data = zf.read(member)
        root = ET.fromstring(data)
        return " ".join(n.text or "" for n in root.iter() if n.text), {"extractor": label}
    except Exception as exc:
        return "", {"extractor": label, "error": f"{type(exc).__name__}: {exc}"}


def read_epub(path: Path) -> tuple[str, dict]:
    try:
        chunks = []
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith((".xhtml", ".html", ".htm"))]
            for name in names[:12]:
                chunks.append(TAG_RE.sub(" ", zf.read(name).decode("utf-8", errors="ignore")))
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
        return read_zip_xml(path, "word/document.xml", "docx:zipxml")
    if ext == ".odt":
        return read_zip_xml(path, "content.xml", "odt:zipxml")
    if ext == ".epub":
        return read_epub(path)
    if ext in {".txt", ".md", ".rtf", ".html", ".htm", ".csv"}:
        return read_text_file(path)
    return "", {"extractor": "unsupported", "unsupported": True}


def occurrence_id(relative_path: str) -> str:
    return "OCC-" + hashlib.sha256(relative_path.casefold().encode("utf-8")).hexdigest()[:20].upper()


def content_id(sha256: str) -> str | None:
    sha = (sha256 or "").strip().lower()
    return "CNT-" + sha[:20].upper() if sha else None


def detect_issuer(text: str, fallback: str) -> str:
    for issuer, rx in ISSUER_PATTERNS:
        if rx.search(text[:12000]):
            return issuer
    return fallback or "UNKNOWN"


def detect_language(text: str) -> str:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "UNKNOWN"
    cyr = sum(("а" <= c.lower() <= "я") or c.lower() == "ё" for c in letters)
    lat = sum("a" <= c.lower() <= "z" for c in letters)
    if cyr > lat * 1.5:
        return "RU"
    if lat > cyr * 1.5:
        return "EN"
    return "MIXED"


def classify(text: str, filename: str, fallback_type: str) -> tuple[str, float, list[str], dict[str, float]]:
    header = f"{filename}\n{text[:HEADER_CHARS]}"
    body = text[:MAX_TEXT_CHARS]
    reasons: list[str] = []
    scores: dict[str, float] = defaultdict(float)

    # Standards: strong only in filename/header. A citation deep inside a book is weak evidence.
    std_rx = re.compile(r"\b(?:ГОСТ(?:\s+Р)?|ПНСТ|ОСТ\s+Р)\s*[А-ЯA-Z0-9./-]*\s*\d|\bISO(?:/IEC)?\s*\d{3,}", re.I)
    if std_rx.search(filename):
        scores["STANDARD"] += 12; reasons.append("standard_id_filename")
    elif std_rx.search(text[:1800]):
        scores["STANDARD"] += 9; reasons.append("standard_id_header")
    elif std_rx.search(body):
        scores["STANDARD"] += 1; reasons.append("standard_reference_only")

    # Laws: references such as 152-ФЗ inside books are not sufficient.
    law_title = re.search(r"ФЕДЕРАЛЬНЫЙ\s+ЗАКОН(?:\s+ОТ\s+\d|\s*\n|\s+[«\"])", header, re.I)
    law_filename = re.search(r"федеральн\w*[_\s-]*закон|\b\d+[-–]?ФЗ\b", filename, re.I)
    law_official = re.search(r"Принят\w*\s+Государственн\w*\s+Дум|Одобрен\w*\s+Совет\w*\s+Федерац|Президент\w*\s+Российск\w*\s+Федерац", text[:12000], re.I)
    if law_filename:
        scores["LAW"] += 10; reasons.append("law_filename")
    if law_title:
        scores["LAW"] += 8; reasons.append("federal_law_header")
    if law_official and (law_title or law_filename):
        scores["LAW"] += 3; reasons.append("law_official_form")
    if not (law_title or law_filename) and re.search(r"\b\d+[-–]?ФЗ\b", body, re.I):
        scores["LAW"] += 0.5; reasons.append("law_reference_only")

    gov_header = re.search(r"ПОСТАНОВЛЕНИЕ\s+ПРАВИТЕЛЬСТВА\s+РОССИЙСКОЙ\s+ФЕДЕРАЦИИ", header, re.I)
    gov_filename = re.search(r"постановлен\w*\s+правительств\w*", filename, re.I)
    if gov_filename:
        scores["GOVERNMENT_DECREE"] += 11; reasons.append("government_decree_filename")
    if gov_header:
        scores["GOVERNMENT_DECREE"] += 9; reasons.append("government_decree_header")
        if re.search(r"\bПОСТАНОВЛЯЕТ\b", text[:8000], re.I):
            scores["GOVERNMENT_DECREE"] += 2; reasons.append("government_decree_form")

    issuer_present = any(rx.search(text[:6000]) for _, rx in ISSUER_PATTERNS)
    order_header = re.search(r"(?:^|\s)ПРИКАЗ(?:\s|$)", text[:2200], re.I)
    order_filename = re.search(r"(?:^|[_\s-])приказ(?:[_\s-]|$)", filename, re.I)
    if order_filename and (issuer_present or fallback_type == "AGENCY_ORDER"):
        scores["AGENCY_ORDER"] += 10; reasons.append("agency_order_filename")
    if order_header and issuer_present:
        scores["AGENCY_ORDER"] += 9; reasons.append("agency_order_header")
        if re.search(r"\bПРИКАЗЫВАЮ\b", text[:6000], re.I):
            scores["AGENCY_ORDER"] += 3; reasons.append("agency_order_form")

    book_meta = re.search(r"ISBN(?:-1[03])?\s*[: ]?\s*(?:97[89])|Copyright|©\s*\d{4}|O'Reilly|Packt|Manning|Apress|Pearson|Springer", text[:9000], re.I)
    ru_publisher = re.search(r"Издательств\w*|БХВ|Питер|Диалектика|Вильямс", text[:6000], re.I)
    toc = re.search(r"Оглавление|Table of Contents|Contents", text[:10000], re.I)
    if book_meta:
        scores["BOOK"] += 9; reasons.append("book_metadata")
    if ru_publisher:
        scores["BOOK"] += 4; reasons.append("book_publisher")
    if toc:
        scores["BOOK"] += 2; reasons.append("book_toc")
    if fallback_type == "BOOK_CANDIDATE" and len(text) >= 1200:
        scores["BOOK"] += 3; reasons.append("book_candidate_with_text")

    # Stage-1 is supporting evidence only, never enough to override strong semantic evidence.
    fallback_map = {
        "STANDARD": "STANDARD", "LAW": "LAW", "GOVERNMENT_DECREE": "GOVERNMENT_DECREE",
        "AGENCY_ORDER": "AGENCY_ORDER",
    }
    if fallback_type in fallback_map:
        scores[fallback_map[fallback_type]] += 2; reasons.append("stage1_support")

    if not scores:
        return "UNRESOLVED", 0.0, ["no_semantic_marker"], {}
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_type, best_score = ordered[0]
    second_score = ordered[1][1] if len(ordered) > 1 else 0.0
    gap = best_score - second_score
    if best_score < 5:
        return "UNRESOLVED", round(min(0.49, best_score / 12), 3), reasons, dict(scores)
    confidence = min(1.0, (best_score / 12.0) * min(1.0, (gap + 2.0) / 6.0))
    return best_type, round(confidence, 3), reasons, dict(scores)


def load_registry(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="FATHER stage-2 content probe v2: precision-first legal classification")
    ap.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--progress-every", type=int, default=50)
    args = ap.parse_args()

    intake = args.intake.resolve(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    registry_path = intake / "library_source_registry.csv"
    if not registry_path.exists():
        print(f"ERROR: registry not found: {registry_path}", file=sys.stderr); return 2

    started = time.perf_counter(); started_at = datetime.now(timezone.utc).isoformat()
    records = load_registry(registry_path)

    # Canonical duplicate is selected by concrete path, not source_id (legacy source_id is SHA-derived).
    canonical_path_by_group: dict[str, str] = {}
    for r in records:
        group = (r.get("duplicate_group") or "").strip()
        rel = (r.get("relative_path") or "").strip()
        if group and group not in canonical_path_by_group:
            canonical_path_by_group[group] = rel

    out: list[dict] = []; failures: list[dict] = []
    for idx, r in enumerate(records, start=1):
        rel = (r.get("relative_path") or "").strip()
        group = (r.get("duplicate_group") or "").strip()
        base = {
            **r,
            "source_occurrence_id": occurrence_id(rel),
            "content_id": content_id(r.get("sha256") or ""),
        }
        if group and canonical_path_by_group.get(group) != rel:
            out.append({
                **base,
                "probe_status": "DUPLICATE_ALIAS",
                "canonical_relative_path": canonical_path_by_group[group],
                "verified_type": "DUPLICATE_ALIAS",
                "content_confidence": None,
            })
            continue

        path = LIBRARY_ROOT / rel
        try:
            raw_text, meta = extract_probe(path)
            text = normalize_text(raw_text)[:MAX_TEXT_CHARS]
            ext = path.suffix.lower(); page_count = meta.get("page_count")
            stage1_private = str(r.get("privacy_risk") or "").lower() in {"true", "1", "yes"}
            stage1_internal = str(r.get("internal_document_risk") or "").lower() in {"true", "1", "yes"}
            private_hits = sum(bool(rx.search(text[:12000])) for rx in STRONG_PRIVATE)

            if meta.get("dependency_missing"):
                status = "DEPENDENCY_MISSING"; verified_type = "UNRESOLVED"; confidence = 0.0
                reasons = ["pdf_dependency_missing"]; scores = {}
            elif meta.get("error"):
                status = "PDF_REPAIR_REQUIRED" if ext == ".pdf" else "EXTRACT_FAILED"
                verified_type = "UNRESOLVED"; confidence = 0.0; reasons = ["extractor_error"]; scores = {}
            elif ext == ".pdf" and page_count and len(text) < 180:
                status = "OCR_REQUIRED"; verified_type = "UNRESOLVED"; confidence = 0.0
                reasons = ["insufficient_extractable_pdf_text"]; scores = {}
            elif meta.get("unsupported"):
                status = "UNRESOLVED"; verified_type = "UNRESOLVED"; confidence = 0.0
                reasons = ["unsupported_format"]; scores = {}
            else:
                verified_type, confidence, reasons, scores = classify(text, path.name, r.get("source_type") or "")
                ordered = sorted(scores.values(), reverse=True)
                ambiguous = len(ordered) > 1 and (ordered[0] - ordered[1] < 2.0)
                if stage1_private or stage1_internal or private_hits >= 1:
                    status = "PRIVATE_REVIEW"
                elif verified_type == "UNRESOLVED":
                    status = "UNRESOLVED"
                elif ambiguous or confidence < 0.60:
                    status = "REVIEW_REQUIRED"
                else:
                    status = "IDENTIFIED"

            out.append({
                **base,
                "probe_status": status,
                "verified_type": verified_type,
                "content_confidence": confidence,
                "issuer_verified": detect_issuer(text, r.get("issuer") or "UNKNOWN"),
                "language": detect_language(text),
                "extractor": meta.get("extractor"),
                "page_count": page_count,
                "probe_text_chars": len(text),
                "probe_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None,
                "classification_reasons": reasons,
                "classification_scores": scores,
                "private_content_hits": private_hits,
                "extractor_error": meta.get("error"),
            })
        except Exception as exc:
            failures.append({"relative_path": rel, "error": f"{type(exc).__name__}: {exc}"})
            out.append({**base, "probe_status": "UNRESOLVED", "verified_type": "UNRESOLVED", "probe_error": str(exc)})

        if args.progress_every and idx % args.progress_every == 0:
            print(f"[PROBE-V2] records={idx} current={path.name}")

    write_jsonl(output / "content_probe_registry_v2.jsonl", out)
    write_jsonl(output / "identified_legal_queue.jsonl", [x for x in out if x.get("verified_type") in {"LAW", "GOVERNMENT_DECREE", "AGENCY_ORDER"} and x.get("probe_status") == "IDENTIFIED"])
    write_jsonl(output / "identified_standards_queue.jsonl", [x for x in out if x.get("verified_type") == "STANDARD" and x.get("probe_status") == "IDENTIFIED"])
    write_jsonl(output / "identified_books_queue.jsonl", [x for x in out if x.get("verified_type") == "BOOK" and x.get("probe_status") == "IDENTIFIED"])
    write_jsonl(output / "review_required_queue.jsonl", [x for x in out if x.get("probe_status") == "REVIEW_REQUIRED"])
    write_jsonl(output / "ocr_required_queue.jsonl", [x for x in out if x.get("probe_status") == "OCR_REQUIRED"])
    write_jsonl(output / "pdf_repair_required_queue.jsonl", [x for x in out if x.get("probe_status") == "PDF_REPAIR_REQUIRED"])
    write_jsonl(output / "private_review_queue.jsonl", [x for x in out if x.get("probe_status") == "PRIVATE_REVIEW"])
    write_jsonl(output / "unresolved_queue.jsonl", [x for x in out if x.get("probe_status") in {"UNRESOLVED", "DEPENDENCY_MISSING", "EXTRACT_FAILED"}])
    write_jsonl(output / "duplicate_aliases.jsonl", [x for x in out if x.get("probe_status") == "DUPLICATE_ALIAS"])

    status_counts = Counter(x.get("probe_status") for x in out)
    type_counts = Counter(x.get("verified_type") for x in out)
    stage1_stage2 = Counter((x.get("source_type"), x.get("verified_type")) for x in out if x.get("probe_status") != "DUPLICATE_ALIAS")
    elapsed = time.perf_counter() - started
    summary = {
        "record_type": "FATHER_LIBRARY_CONTENT_PROBE_RUN",
        "schema_version": SCHEMA_VERSION,
        "status": "PASS" if not failures else "PASS_WITH_FILE_ERRORS",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "records_total": len(out),
        "canonical_records_probed": sum(1 for x in out if x.get("probe_status") != "DUPLICATE_ALIAS"),
        "duplicate_aliases_skipped": status_counts.get("DUPLICATE_ALIAS", 0),
        "status_counts": dict(status_counts),
        "verified_type_counts": dict(type_counts),
        "file_errors_total": len(failures),
        "speedup_vs_1_stream_pct": None,
        "eta_seconds": None,
        "notes": [
            "V2 uses precision-first regulatory classification: a citation to a law/GOST inside a book is not sufficient to classify the whole source as regulatory.",
            "Duplicate aliases are skipped by relative path within SHA duplicate groups.",
            "SOURCE_OCCURRENCE_ID identifies a concrete file path; CONTENT_ID identifies byte content by SHA-256.",
            "Broken PDFs route to PDF_REPAIR_REQUIRED; image-only PDFs route to OCR_REQUIRED.",
            "No original is moved, renamed, deleted, uploaded or modified.",
        ],
    }
    (output / "LATEST_LIBRARY_PROBE_V2_REPORT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "stage1_stage2_crosswalk.json").write_text(json.dumps([
        {"stage1": a, "stage2": b, "count": n} for (a, b), n in stage1_stage2.most_common()
    ], ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "probe_failures.json").write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# FATHER Library Content Probe V2 — latest report", "",
        f"- Status: **{summary['status']}**",
        f"- Records: **{len(out)}**",
        f"- Canonical records actually probed: **{summary['canonical_records_probed']}**",
        f"- Duplicate aliases skipped: **{summary['duplicate_aliases_skipped']}**",
        f"- File errors: **{len(failures)}**",
        f"- Elapsed: **{summary['elapsed_seconds']} s**", "",
        "## Probe statuses", "", "| Status | Count |", "|---|---:|",
    ]
    md.extend(f"| {k} | {v} |" for k, v in status_counts.most_common())
    md += ["", "## Verified types", "", "| Type | Count |", "|---|---:|"]
    md.extend(f"| {k} | {v} |" for k, v in type_counts.most_common())
    md += ["", "> V2 is identification/QA only. No knowledge extraction yet."]
    (output / "LATEST_LIBRARY_PROBE_V2_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report: {output / 'LATEST_LIBRARY_PROBE_V2_REPORT.md'}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
