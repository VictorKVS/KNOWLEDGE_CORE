from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from pypdf import PdfReader  # type: ignore
except Exception:
    PdfReader = None

DEFAULT_OUTPUT = Path(r"G:\1\FATHER_LIBRARY_REBASELINE_20260830")
DEFAULT_ROOTS = [
    Path(r"G:\1\OTUS\Библиотека"),
    Path(r"G:\1\KNOWLEDGE_CORE_IMPORT_20260827-162116\sources"),
]
DEFAULT_BASELINE = (
    Path(__file__).resolve().parents[1]
    / "father"
    / "agent-factory"
    / "knowledge"
    / "library"
    / "ru_regulatory_rebaseline_p0_20260830.json"
)
SUPPORTED = {".pdf", ".odt", ".docx", ".rtf", ".txt", ".md", ".html", ".htm"}
MAX_TEXT = 18000
PDF_PAGES = 4


def norm(value: str) -> str:
    s = (value or "").upper().replace("Ё", "Е").replace("№", " N ")
    s = s.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            b = fh.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


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
        t, e = read_pdf(path)
        return t, "pypdf", e
    if ext == ".odt":
        t, e = read_zip_xml(path, "content.xml")
        return t, "odt:zipxml", e
    if ext == ".docx":
        t, e = read_zip_xml(path, "word/document.xml")
        return t, "docx:zipxml", e
    if ext in {".rtf", ".txt", ".md", ".html", ".htm"}:
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


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def date_variants(value: str | None) -> list[str]:
    if not value:
        return []
    if re.fullmatch(r"\d{4}", value):
        return [value]
    m = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{4})", value)
    if not m:
        return [norm(value)]
    dd, mm, yyyy = m.groups()
    return [f"{dd}.{mm}.{yyyy}", f"{dd}-{mm}-{yyyy}", f"{dd}/{mm}/{yyyy}", yyyy]


def number_patterns(number: str) -> list[re.Pattern]:
    n = norm(number)
    if "ФЗ" in n:
        digits = re.search(r"\d+", n)
        if digits:
            d = re.escape(digits.group(0))
            return [re.compile(rf"(?<!\d){d}\s*-?\s*ФЗ(?!\w)", re.I)]
    escaped = re.escape(number.replace("№", "").strip())
    return [
        re.compile(rf"(?:№|\bN\b)?\s*{escaped}(?!\d)", re.I),
    ]


def has_number(blob: str, number: str) -> bool:
    return any(rx.search(blob) for rx in number_patterns(number))


def match_baseline(item: dict, blob: str, authority_aliases: dict[str, list[str]]) -> tuple[bool, int, dict]:
    score = 0
    evidence: dict[str, object] = {}
    number = item.get("number") or ""
    if number and has_number(blob, number):
        score += 3
        evidence["number"] = True
    else:
        evidence["number"] = False

    aliases = authority_aliases.get(item.get("authority") or "", [])
    authority_hit = any(norm(a) in blob for a in aliases)
    if authority_hit:
        score += 3
    evidence["authority"] = authority_hit

    date_hit = any(norm(v) in blob for v in date_variants(item.get("date")))
    if date_hit:
        score += 2
    evidence["date"] = date_hit

    kw_hits = []
    for kw in item.get("title_keywords") or []:
        hit = norm(kw) in blob
        kw_hits.append({"keyword": kw, "hit": hit})
        if hit:
            score += 1
    evidence["keywords"] = kw_hits

    # Number is mandatory. Then require either authority, date, or at least two title-keyword hits.
    keyword_count = sum(1 for x in kw_hits if x["hit"])
    matched = bool(evidence["number"] and (authority_hit or date_hit or keyword_count >= 2) and score >= 5)
    return matched, score, evidence


def inventory_file(root: Path, path: Path) -> dict:
    text, extractor, err = extract(path)
    rel = str(path.relative_to(root))
    blob = norm(f"{path.name}\n{rel}\n{text[:MAX_TEXT]}")
    try:
        digest = sha256(path)
        hash_error = None
    except Exception as exc:
        digest = None
        hash_error = f"{type(exc).__name__}: {exc}"
    return {
        "root": str(root),
        "relative_path": rel,
        "full_path": str(path),
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": digest,
        "hash_error": hash_error,
        "extractor": extractor,
        "extractor_error": err,
        "search_blob": blob,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="FATHER regulatory rebaseline: physical inventory + critical coverage")
    ap.add_argument("--root", action="append", dest="roots", help="Source root; repeat for multiple roots")
    ap.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    roots = [Path(x) for x in args.roots] if args.roots else DEFAULT_ROOTS
    roots = [r for r in roots if r.exists()]
    if not roots:
        print("ERROR: none of the source roots exists", file=sys.stderr)
        return 2
    if not args.baseline.exists():
        print(f"ERROR: baseline missing: {args.baseline}", file=sys.stderr)
        return 2

    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    docs = baseline.get("documents") or []
    aliases = baseline.get("authority_aliases") or {}

    files: list[dict] = []
    seen_paths: set[str] = set()
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED:
                continue
            key = str(path.resolve()).lower()
            if key in seen_paths:
                continue
            seen_paths.add(key)
            rec = inventory_file(root, path)
            print(f"[INVENTORY] {rec['full_path']}")
            files.append(rec)

    coverage = []
    for item in docs:
        matches = []
        for f in files:
            matched, score, evidence = match_baseline(item, f["search_blob"], aliases)
            if matched:
                matches.append({
                    "full_path": f["full_path"],
                    "filename": f["filename"],
                    "sha256": f["sha256"],
                    "score": score,
                    "evidence": evidence,
                })
        matches.sort(key=lambda x: (-x["score"], x["full_path"].lower()))
        coverage.append({
            **item,
            "presence_status": "FOUND" if matches else "MISSING",
            "match_count": len(matches),
            "matches": matches,
            "official_source_status": "PENDING",
            "currentness_status": "PENDING",
            "applicability_status": "PENDING",
            "kb_ready": False,
        })

    # Physical duplicates are defined strictly by SHA-256, not by filename or guessed legal identity.
    hash_map: dict[str, list[dict]] = defaultdict(list)
    for f in files:
        if f.get("sha256"):
            hash_map[f["sha256"]].append(f)
    duplicate_hashes = []
    for digest, group in hash_map.items():
        if len(group) > 1:
            duplicate_hashes.append({
                "sha256": digest,
                "count": len(group),
                "files": [x["full_path"] for x in group],
            })

    public_inventory = [{k: v for k, v in f.items() if k != "search_blob"} for f in files]
    write_jsonl(output / "all_source_files.jsonl", public_inventory)
    write_jsonl(output / "critical_coverage.jsonl", coverage)
    write_jsonl(output / "missing_critical_documents.jsonl", [x for x in coverage if x["presence_status"] == "MISSING"])
    write_jsonl(output / "duplicate_hashes.jsonl", duplicate_hashes)

    ext_counts = Counter(f["extension"] for f in files)
    root_counts = Counter(f["root"] for f in files)
    domain_total: Counter[str] = Counter()
    domain_found: Counter[str] = Counter()
    for row in coverage:
        for domain in row.get("domain") or []:
            domain_total[domain] += 1
            if row["presence_status"] == "FOUND":
                domain_found[domain] += 1

    found = sum(1 for x in coverage if x["presence_status"] == "FOUND")
    missing = len(coverage) - found
    summary = {
        "record_type": "FATHER_REGULATORY_REBASELINE",
        "status": "PASS",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "roots": [str(r) for r in roots],
        "physical_files": len(files),
        "files_by_root": dict(root_counts),
        "files_by_extension": dict(ext_counts),
        "duplicate_hash_groups": len(duplicate_hashes),
        "critical_baseline_total": len(coverage),
        "critical_found": found,
        "critical_missing": missing,
        "officially_verified": 0,
        "kb_ready": 0,
        "notes": [
            "This pass re-establishes physical coverage. It does not assert legal currentness or applicability.",
            "Stage 6/7 outputs must not be treated as completeness proof.",
            "Official verification follows only after missing-source intake is closed for the selected domain.",
            "Source files are read-only; no source file is modified."
        ],
    }
    (output / "LATEST_REBASELINE_REPORT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# FATHER — Regulatory Rebaseline", "",
        f"- Status: **PASS**",
        f"- Physical source files: **{len(files)}**",
        f"- Critical baseline: **{len(coverage)}**",
        f"- Found: **{found}**",
        f"- Missing: **{missing}**",
        f"- Duplicate SHA-256 groups: **{len(duplicate_hashes)}**",
        "- Officially verified: **0**",
        "- KB_READY: **0**", "",
        "## Coverage by domain", "", "| Domain | Found | Baseline |", "|---|---:|---:|",
    ]
    for domain in sorted(domain_total):
        md.append(f"| {domain} | {domain_found[domain]} | {domain_total[domain]} |")
    md += ["", "## Missing critical documents", ""]
    for row in coverage:
        if row["presence_status"] == "MISSING":
            md.append(f"- `{row['id']}` — {row['type']} {row['number']} ({row['date']}); domains: {', '.join(row.get('domain') or [])}")
    md += [
        "", "## Important", "",
        "> Presence is not validity. After coverage is closed, every legal act still requires official-source, currentness, amendment-lineage and applicability gates.",
    ]
    (output / "LATEST_REBASELINE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Report: {output / 'LATEST_REBASELINE_REPORT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
