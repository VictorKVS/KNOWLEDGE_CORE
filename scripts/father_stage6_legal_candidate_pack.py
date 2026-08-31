from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from pypdf import PdfReader  # type: ignore
except Exception:
    PdfReader = None

SCHEMA_VERSION = "1.0"
DEFAULT_STAGE4 = Path(r"G:\1\FATHER_LIBRARY_STAGE4")
DEFAULT_OUTPUT = Path(r"G:\1\FATHER_LIBRARY_STAGE6_LEGAL")
LIBRARY_ROOT = Path(r"G:\1\OTUS\Библиотека")
MAX_TEXT = 18000
PDF_PAGES = 3

DATE_PATTERNS = [
    re.compile(r"(?:от\s*)?(\d{1,2}\s+[А-Яа-яЁё]+\s+(?:19|20)\d{2}\s*г\.?)", re.I),
    re.compile(r"(?:от\s*)?(\d{1,2}[./-]\d{1,2}[./-](?:19|20)\d{2})", re.I),
]
LAW_NO = re.compile(r"(?:№|N)?\s*(\d{1,4})\s*[-–]?\s*ФЗ\b", re.I)
DECREE_NO = re.compile(r"(?:постановлен\w*[^\n]{0,180}?)(?:№|N)\s*(\d{1,6})", re.I)
ORDER_NO = re.compile(r"(?:приказ\w*[^\n]{0,180}?)(?:№|N)\s*([0-9А-ЯA-Z./-]{1,24})", re.I)
REG_NO = re.compile(r"зарегистрирован\w*[^\n]{0,120}?(?:№|N)\s*(\d{3,8})", re.I)

ISSUERS = [
    ("FSTEC", re.compile(r"ФСТЭК|Федеральн\w*\s+служб\w*\s+по\s+техническ\w*\s+и\s+экспортн\w*\s+контрол", re.I)),
    ("FSB", re.compile(r"\bФСБ\b|Федеральн\w*\s+служб\w*\s+безопасност", re.I)),
    ("RKN", re.compile(r"Роскомнадзор|Федеральн\w*\s+служб\w*\s+по\s+надзор", re.I)),
    ("MINCIFRY", re.compile(r"Минцифр|Министерств\w*\s+цифрового\s+развит", re.I)),
    ("MINZDRAV", re.compile(r"Минздрав|Министерств\w*\s+здравоохран", re.I)),
    ("GOV_RU", re.compile(r"Правительств\w*\s+Российск\w*\s+Федерац", re.I)),
    ("FEDERAL", re.compile(r"ФЕДЕРАЛЬНЫЙ\s+ЗАКОН|Федеральный\s+закон", re.I)),
]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\x00", " ")).strip()


def read_pdf(path: Path) -> tuple[str, str | None]:
    if PdfReader is None:
        return "", "pypdf_missing"
    try:
        r = PdfReader(str(path), strict=False)
        chunks = []
        for p in r.pages[:PDF_PAGES]:
            try:
                chunks.append(p.extract_text() or "")
            except Exception:
                chunks.append("")
        return "\n".join(chunks), None
    except Exception as exc:
        return "", f"{type(exc).__name__}: {exc}"


def read_zip_xml(path: Path, member: str) -> tuple[str, str | None]:
    try:
        with zipfile.ZipFile(path) as zf:
            data = zf.read(member)
        root = ET.fromstring(data)
        return " ".join(n.text or "" for n in root.iter() if n.text), None
    except Exception as exc:
        return "", f"{type(exc).__name__}: {exc}"


def extract(path: Path) -> tuple[str, str, str | None]:
    ext = path.suffix.lower()
    if ext == ".pdf":
        t, e = read_pdf(path); return t, "pypdf", e
    if ext == ".odt":
        t, e = read_zip_xml(path, "content.xml"); return t, "odt:zipxml", e
    if ext == ".docx":
        t, e = read_zip_xml(path, "word/document.xml"); return t, "docx:zipxml", e
    if ext in {".txt", ".rtf", ".md", ".html", ".htm"}:
        try:
            raw = path.read_bytes()
            for enc in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
                try:
                    return raw.decode(enc), f"text:{enc}", None
                except UnicodeDecodeError:
                    pass
            return raw.decode("utf-8", errors="replace"), "text:utf8-replace", None
        except Exception as exc:
            return "", "text", f"{type(exc).__name__}: {exc}"
    return "", "unsupported", "unsupported_format"


def first(rx: re.Pattern, s: str) -> str | None:
    m = rx.search(s or "")
    return m.group(1).strip() if m else None


def detect_date(s: str) -> str | None:
    for rx in DATE_PATTERNS:
        v = first(rx, s)
        if v:
            return v
    return None


def detect_issuer(s: str, fallback: str | None) -> str:
    for name, rx in ISSUERS:
        if rx.search(s[:9000]):
            return name
    return fallback or "UNKNOWN"


def detect_number(doc_type: str, s: str) -> str | None:
    if doc_type == "LAW":
        return first(LAW_NO, s)
    if doc_type == "GOVERNMENT_DECREE":
        return first(DECREE_NO, s)
    if doc_type == "AGENCY_ORDER":
        return first(ORDER_NO, s)
    return None


def title_hint(text: str, filename: str) -> str:
    t = norm(text[:5000])
    # Prefer a bounded title-like prefix around regulatory marker; fallback to filename.
    markers = ["ФЕДЕРАЛЬНЫЙ ЗАКОН", "ПОСТАНОВЛЕНИЕ", "ПРИКАЗ"]
    upper = t.upper()
    starts = [upper.find(m) for m in markers if upper.find(m) >= 0]
    if starts:
        start = min(starts)
        return t[start:start+700]
    return Path(filename).stem[:700]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Invalid JSONL {path}:{n}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="FATHER Stage 6 legal candidate pack")
    ap.add_argument("--stage4", type=Path, default=DEFAULT_STAGE4)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    stage4 = args.stage4.resolve(); output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    src = stage4 / "legal_verification_manifest.jsonl"
    if not src.exists():
        print(f"ERROR: missing {src}", file=sys.stderr); return 2

    started = time.perf_counter(); started_at = datetime.now(timezone.utc).isoformat()
    out = []
    for idx, row in enumerate(read_jsonl(src), 1):
        rel = row.get("relative_path") or ""
        path = LIBRARY_ROOT / rel
        text, extractor, err = extract(path)
        text = norm(text)[:MAX_TEXT]
        joined = f"{row.get('filename') or ''}\n{text}"
        doc_type = row.get("document_type") or "UNRESOLVED"
        number = detect_number(doc_type, joined) or row.get("document_number_hint")
        date = detect_date(joined) or row.get("document_date_hint")
        issuer = detect_issuer(joined, row.get("issuer_detected"))
        registration = first(REG_NO, joined) if doc_type == "AGENCY_ORDER" else None
        key_bits = [doc_type, number or "", date or "", issuer or ""]
        search_key = " | ".join(x for x in key_bits if x)
        completeness = sum(bool(x) for x in (number, date, issuer))
        status = "READY_FOR_OFFICIAL_SEARCH" if completeness >= 2 and not err else "METADATA_REVIEW_REQUIRED"
        out.append({
            "source_occurrence_id": row.get("source_occurrence_id"),
            "content_id": row.get("content_id"),
            "sha256": row.get("sha256"),
            "relative_path": rel,
            "filename": row.get("filename"),
            "document_type": doc_type,
            "issuer_candidate": issuer,
            "document_number_candidate": number,
            "document_date_candidate": date,
            "registration_number_candidate": registration,
            "title_hint": title_hint(text, row.get("filename") or ""),
            "search_key": search_key,
            "extractor": extractor,
            "extractor_error": err,
            "candidate_status": status,
            "official_source_status": "PENDING",
            "currentness_status": "PENDING",
            "amendment_lineage_status": "PENDING",
            "scope_status": "PENDING",
            "verification_result": "NOT_VERIFIED",
        })
        if idx % 20 == 0:
            print(f"[LEGAL-PACK] records={idx} current={path.name}")

    write_jsonl(output / "legal_candidates.jsonl", out)
    write_csv(output / "legal_candidates.csv", out)
    ready = [r for r in out if r["candidate_status"] == "READY_FOR_OFFICIAL_SEARCH"]
    review = [r for r in out if r["candidate_status"] != "READY_FOR_OFFICIAL_SEARCH"]
    write_jsonl(output / "legal_ready_for_official_search.jsonl", ready)
    write_jsonl(output / "legal_metadata_review_required.jsonl", review)

    counts = Counter(r["document_type"] for r in out)
    status_counts = Counter(r["candidate_status"] for r in out)
    summary = {
        "record_type": "FATHER_STAGE6_LEGAL_CANDIDATE_PACK",
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "legal_total": len(out),
        "document_type_counts": dict(counts),
        "candidate_status_counts": dict(status_counts),
        "officially_verified_count": 0,
        "kb_ready_count": 0,
        "notes": [
            "This step extracts candidate metadata only; it does not assert legal validity or currentness.",
            "Official verification must use publication.pravo.gov.ru / official regulator sources as primary evidence.",
            "No source file is modified or uploaded.",
        ],
    }
    (output / "LATEST_STAGE6_LEGAL_CANDIDATE_REPORT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# FATHER Stage 6 — LEGAL candidate pack", "",
        f"- Status: **PASS**", f"- LEGAL total: **{len(out)}**",
        f"- Ready for official search: **{len(ready)}**", f"- Metadata review required: **{len(review)}**",
        "- Officially verified: **0**", "- KB_READY: **0**", "",
        "## Types", "", "| Type | Count |", "|---|---:|",
    ]
    md += [f"| {k} | {v} |" for k, v in counts.most_common()]
    md += ["", "## Outputs", "", "- `legal_candidates.csv`", "- `legal_candidates.jsonl`", "- `legal_ready_for_official_search.jsonl`", "- `legal_metadata_review_required.jsonl`", "", "> Candidate metadata only. No legal status asserted."]
    (output / "LATEST_STAGE6_LEGAL_CANDIDATE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report: {output / 'LATEST_STAGE6_LEGAL_CANDIDATE_REPORT.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
