# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GLOSSARY_PATH = REPO_ROOT / "father" / "agent-factory" / "translation" / "glossary" / "core_en_ru.tsv"
DEFAULT_INVENTORY = Path(r"C:\Users\1\Documents\Codex\2026-08-26\new-chat\outputs\library_inventory.csv")
DEFAULT_OUTPUT = Path(r"G:\1\FATHER_TRANSLATION_FACTORY")

DOMAIN_RULES = [
    ("architecture", 100, ["architecture", "architect", "system design", "solution architecture", "enterprise architecture", "distributed systems", "designing data", "ddd", "domain-driven", "c4", "patterns"]),
    ("software-engineering", 95, ["programming", "software engineering", "clean code", "refactoring", "algorithm", "data structure", "python", "java", "golang", "rust", "c++", "testing", "design pattern", "api design"]),
    ("information-security", 90, ["security", "cybersecurity", "information security", "appsec", "devsecops", "threat modeling", "zero trust", "cryptography", "privacy", "pentest", "secure coding", "soc", "siem"]),
    ("cloud-devops-sre", 80, ["cloud", "kubernetes", "docker", "devops", "sre", "reliability", "terraform", "gitops", "observability", "microservice"]),
    ("ai-data", 70, ["machine learning", "artificial intelligence", " llm", "rag", "data engineering", "database", "distributed data"]),
]

SUPPORTED_EXT = {".txt", ".md", ".html", ".htm", ".pdf", ".docx", ".epub"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def safe_name(value: str, limit: int = 96) -> str:
    value = re.sub(r'[<>:"/\\|?*]+', "_", value)
    value = re.sub(r"\s+", " ", value).strip().rstrip(".")
    return (value or "book")[:limit]


def read_csv_auto(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = raw.splitlines()
    if not lines:
        return []
    first = lines[0]
    candidates = {";": first.count(";"), ",": first.count(","), "\t": first.count("\t")}
    delimiter = max(candidates, key=candidates.get)
    return list(csv.DictReader(lines, delimiter=delimiter))


def row_value(row: dict, names: list[str]) -> str:
    lowered = {str(k).lower(): v for k, v in row.items()}
    for name in names:
        if name in row and row[name] is not None:
            return str(row[name])
        value = lowered.get(name.lower())
        if value is not None:
            return str(value)
    return ""


def classify_domain(text: str) -> tuple[str, int, list[str]]:
    low = text.lower()
    best_domain = "other"
    best_score = 0
    best_hits: list[str] = []
    for domain, priority, keywords in DOMAIN_RULES:
        hits = [kw for kw in keywords if kw in low]
        if hits:
            score = priority + min(len(hits) * 3, 24)
            if score > best_score:
                best_domain = domain
                best_score = score
                best_hits = hits
    return best_domain, best_score, best_hits


def discover_from_inventory(inventory: Path) -> list[dict]:
    rows = read_csv_auto(inventory)
    found: list[dict] = []
    seen_paths: set[str] = set()
    for row in rows:
        raw_path = row_value(row, ["full_path", "path", "fullname", "FullName"])
        if not raw_path:
            continue
        path = Path(raw_path)
        ext = path.suffix.lower()
        if ext not in SUPPORTED_EXT:
            continue
        key = str(path).lower()
        if key in seen_paths:
            continue
        seen_paths.add(key)
        filename = row_value(row, ["filename", "name", "Name"]) or path.name
        category = row_value(row, ["category", "Category", "domain", "Domain", "classification"])
        meta = f"{filename} {raw_path} {category}"
        domain, score, hits = classify_domain(meta)
        if score <= 0:
            continue
        found.append({
            "path": raw_path,
            "filename": filename,
            "extension": ext,
            "category": category,
            "domain": domain,
            "priority_score": score,
            "keyword_hits": hits,
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        })
    found.sort(key=lambda x: (-x["priority_score"], -x["size_bytes"], x["filename"].lower()))
    return found


def strip_html(raw: str) -> str:
    raw = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style.*?>.*?</style>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", "\n", raw)
    return html.unescape(raw)


def extract_text(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    if ext in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace"), "stdlib-text"
    if ext in {".html", ".htm"}:
        return strip_html(path.read_text(encoding="utf-8", errors="replace")), "stdlib-html"
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception as exc:
            raise RuntimeError("PDF extractor missing: run INSTALL_FATHER_TRANSLATION_DEPS.cmd") from exc
        reader = PdfReader(str(path))
        parts = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            parts.append(f"\n\n[[PAGE {i + 1}]]\n\n{text}")
        return "".join(parts), "pypdf"
    if ext == ".docx":
        try:
            from docx import Document
        except Exception as exc:
            raise RuntimeError("DOCX extractor missing: run INSTALL_FATHER_TRANSLATION_DEPS.cmd") from exc
        doc = Document(str(path))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip()), "python-docx"
    if ext == ".epub":
        try:
            from ebooklib import ITEM_DOCUMENT, epub
            from bs4 import BeautifulSoup
        except Exception as exc:
            raise RuntimeError("EPUB extractor missing: run INSTALL_FATHER_TRANSLATION_DEPS.cmd") from exc
        book = epub.read_epub(str(path))
        parts = []
        for item in book.get_items_of_type(ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            parts.append(soup.get_text("\n"))
        return "\n\n".join(parts), "ebooklib+bs4"
    raise RuntimeError(f"Unsupported extension: {ext}")


def detect_language(text: str) -> tuple[str, float]:
    sample = text[:30000]
    latin = len(re.findall(r"[A-Za-z]", sample))
    cyr = len(re.findall(r"[А-Яа-яЁё]", sample))
    total = latin + cyr
    if total == 0:
        return "unknown", 0.0
    ratio = latin / total
    if latin >= 300 and ratio >= 0.72:
        return "en", ratio
    if cyr >= 300 and ratio <= 0.28:
        return "ru", 1.0 - ratio
    return "mixed", max(ratio, 1.0 - ratio)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_chars: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for p in paragraphs:
        if len(p) > chunk_chars * 2:
            sentences = re.split(r"(?<=[.!?])\s+", p)
        else:
            sentences = [p]
        for unit in sentences:
            add = len(unit) + 2
            if current and current_len + add > chunk_chars:
                chunks.append("\n\n".join(current).strip())
                current = []
                current_len = 0
            if len(unit) > chunk_chars:
                for start in range(0, len(unit), chunk_chars):
                    piece = unit[start:start + chunk_chars].strip()
                    if piece:
                        if current:
                            chunks.append("\n\n".join(current).strip())
                            current = []
                            current_len = 0
                        chunks.append(piece)
            else:
                current.append(unit)
                current_len += add
    if current:
        chunks.append("\n\n".join(current).strip())
    return chunks


def load_glossary(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    version = sha256_bytes(raw)[:16]
    text = raw.decode("utf-8-sig", errors="replace")
    rows = list(csv.DictReader(text.splitlines(), delimiter="\t"))
    return rows, version


def relevant_glossary(rows: list[dict], source: str, limit: int = 24) -> str:
    low = source.lower()
    hits = []
    for row in rows:
        en = (row.get("english") or "").strip()
        if en and en.lower() in low:
            hits.append(f"{en} => {row.get('russian','').strip()} | {row.get('note','').strip()}")
    return "\n".join(hits[:limit]) or "No glossary entries matched this chunk."


def llm_call(endpoint: str, model: str, system_prompt: str, user_prompt: str, timeout: int = 600) -> str:
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Local LLM endpoint unavailable: {endpoint}: {exc}") from exc
    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except Exception as exc:
        raise RuntimeError(f"Unexpected local LLM response: {str(data)[:500]}") from exc


def translate_chunk(source: str, glossary_text: str, endpoint: str, model: str) -> str:
    system_prompt = (
        "You are FATHER Technical Translator EN->RU. Translate faithfully, not creatively. "
        "Preserve meaning, modality, numbers, URLs, formulas, code blocks, identifiers, API names, class/function names, "
        "configuration keys and commands. Do not add facts, explanations or corrections. "
        "Use professional Russian terminology. If a term is ambiguous, preserve the English term in parentheses on first use. "
        "Return only the Russian translation, preserving paragraph structure."
    )
    user_prompt = f"SHARED GLOSSARY FOR THIS CHUNK:\n{glossary_text}\n\nSOURCE ENGLISH:\n{source}"
    return llm_call(endpoint, model, system_prompt, user_prompt)


def parse_json_loose(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)


def review_chunk(source: str, draft: str, glossary_text: str, endpoint: str, model: str) -> dict:
    system_prompt = (
        "You are FATHER Translation Reviewer. Compare English source and Russian draft for omissions, additions, mistranslations, "
        "terminology drift, changed modality, lost negation, changed numbers/URLs/code and broken technical meaning. "
        "Do not rewrite stylistically unless needed for correctness. Return strict JSON only with keys: "
        "verdict (PASS|CORRECTED|FAIL), issues (array of short strings), corrected_translation (string)."
    )
    user_prompt = (
        f"GLOSSARY:\n{glossary_text}\n\nSOURCE:\n{source}\n\nDRAFT TRANSLATION:\n{draft}\n\n"
        "If PASS, corrected_translation must equal the draft. If CORRECTED, return the corrected full translation."
    )
    raw = llm_call(endpoint, model, system_prompt, user_prompt)
    try:
        result = parse_json_loose(raw)
    except Exception:
        return {"verdict": "FAIL", "issues": ["reviewer_output_not_valid_json"], "corrected_translation": draft}
    verdict = str(result.get("verdict", "FAIL")).upper()
    if verdict not in {"PASS", "CORRECTED", "FAIL"}:
        verdict = "FAIL"
    corrected = str(result.get("corrected_translation") or draft)
    issues = result.get("issues")
    if not isinstance(issues, list):
        issues = [str(issues)] if issues else []
    return {"verdict": verdict, "issues": [str(x) for x in issues], "corrected_translation": corrected}


def extract_numbers(text: str) -> set[str]:
    values = set()
    for x in re.findall(r"(?<!\w)\d+(?:[.,]\d+)*(?!\w)", text):
        values.add(x.replace(",", "."))
    return values


def extract_urls(text: str) -> set[str]:
    return set(re.findall(r"https?://[^\s)\]>]+", text))


def deterministic_qa(source: str, target: str) -> dict:
    source_numbers = extract_numbers(source)
    target_numbers = extract_numbers(target)
    source_urls = extract_urls(source)
    target_urls = extract_urls(target)
    return {
        "numbers_preserved": source_numbers.issubset(target_numbers),
        "urls_preserved": source_urls.issubset(target_urls),
        "code_fences_preserved": source.count("```") == target.count("```"),
        "non_empty": bool(target.strip()),
    }


def load_tm(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
            key = row.get("source_chunk_sha256")
            if key:
                result[str(key)] = row
        except Exception:
            continue
    return result


def append_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def process_one_chunk(index: int, source: str, book: dict, glossary_rows: list[dict], glossary_version: str,
                      endpoint: str, translator_model: str, reviewer_model: str, qa_enabled: bool,
                      tm: dict[str, dict]) -> dict:
    chunk_sha = sha256_bytes(source.encode("utf-8"))
    cached = tm.get(chunk_sha)
    if cached and cached.get("glossary_version") == glossary_version and cached.get("status") == "READY_FOR_KNOWLEDGE_EXTRACTION":
        out = dict(cached)
        out["chunk_index"] = index
        out["reused_from_translation_memory"] = True
        return out

    glossary_text = relevant_glossary(glossary_rows, source)
    draft = translate_chunk(source, glossary_text, endpoint, translator_model)
    review = {"verdict": "PASS", "issues": [], "corrected_translation": draft}
    if qa_enabled:
        review = review_chunk(source, draft, glossary_text, endpoint, reviewer_model)
    final_translation = review.get("corrected_translation") or draft
    qa = deterministic_qa(source, final_translation)
    qa["reviewer_verdict"] = review.get("verdict", "FAIL")
    qa["issues"] = review.get("issues", [])
    deterministic_pass = all(qa[k] for k in ["numbers_preserved", "urls_preserved", "code_fences_preserved", "non_empty"])
    reviewer_pass = qa["reviewer_verdict"] in {"PASS", "CORRECTED"}
    status = "READY_FOR_KNOWLEDGE_EXTRACTION" if deterministic_pass and reviewer_pass else "QA_REVIEW_REQUIRED"
    return {
        "book_id": book["book_id"],
        "source_sha256": book["source_sha256"],
        "chunk_index": index,
        "source_chunk_sha256": chunk_sha,
        "source_language": "en",
        "target_language": "ru",
        "domain": book["domain"],
        "translator_model": translator_model,
        "reviewer_model": reviewer_model,
        "glossary_version": glossary_version,
        "source_text": source,
        "draft_translation": draft,
        "final_translation": final_translation,
        "qa": qa,
        "status": status,
        "reused_from_translation_memory": False,
        "created_at": now_iso(),
    }


def render_bilingual(book: dict, records: list[dict]) -> str:
    lines = [
        f"# {book['filename']}",
        "",
        f"- Book ID: `{book['book_id']}`",
        f"- Source SHA-256: `{book['source_sha256']}`",
        f"- Domain: `{book['domain']}`",
        f"- Source path: `{book['path']}`",
        "",
        "> Local working translation. Original, translation and downstream knowledge are separate layers.",
        "",
    ]
    for record in sorted(records, key=lambda x: x["chunk_index"]):
        lines.extend([
            f"## Chunk {record['chunk_index'] + 1}",
            "",
            f"Status: `{record['status']}` | source chunk SHA-256: `{record['source_chunk_sha256']}`",
            "",
            "### EN original",
            "",
            record["source_text"],
            "",
            "### RU translation",
            "",
            record["final_translation"],
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="FATHER Technical Book Translation Factory M1")
    parser.add_argument("--mode", choices=["plan", "pilot", "run"], default="pilot")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--workers", type=int, default=int(os.getenv("FATHER_TRANSLATION_WORKERS", "4")))
    parser.add_argument("--max-books", type=int, default=0)
    parser.add_argument("--max-chunks", type=int, default=0)
    args = parser.parse_args()

    inventory = Path(args.inventory)
    output = Path(args.output)
    endpoint = os.getenv("FATHER_LLM_BASE_URL", "http://127.0.0.1:8080/v1/chat/completions")
    translator_model = os.getenv("FATHER_TRANSLATOR_MODEL", "local-model")
    reviewer_model = os.getenv("FATHER_REVIEWER_MODEL", translator_model)
    qa_enabled = os.getenv("FATHER_TRANSLATION_QA", "1").lower() not in {"0", "false", "no"}
    chunk_chars = int(os.getenv("FATHER_TRANSLATION_CHUNK_CHARS", "4500"))

    print("=" * 72)
    print("FATHER AGENT FACTORY — LAYER 1 TECHNICAL TRANSLATOR")
    print("=" * 72)
    print(f"Mode: {args.mode}")
    print(f"Inventory: {inventory}")
    print(f"Output: {output}")
    print(f"Workers: {args.workers}")

    if not inventory.exists():
        raise FileNotFoundError(f"Inventory not found: {inventory}")
    if not GLOSSARY_PATH.exists():
        raise FileNotFoundError(f"Glossary not found: {GLOSSARY_PATH}")

    output.mkdir(parents=True, exist_ok=True)
    candidates = discover_from_inventory(inventory)
    inventory_dir = output / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(inventory_dir / "candidate_books.jsonl", candidates)
    print(f"Priority technical book candidates: {len(candidates)}")

    if args.mode == "plan":
        for item in candidates[:30]:
            print(f"{item['priority_score']:3d} | {item['domain']:<22} | {item['filename']}")
        print("PLAN complete. No LLM calls were made.")
        return 0

    glossary_rows, glossary_version = load_glossary(GLOSSARY_PATH)
    tm_path = output / "translation_memory" / "en_ru_tm.jsonl"
    tm = load_tm(tm_path)

    max_books = args.max_books
    max_chunks = args.max_chunks
    if args.mode == "pilot":
        max_books = 1
        max_chunks = max_chunks or 8

    processed_books = 0
    summary: list[dict] = []

    for candidate in candidates:
        if max_books and processed_books >= max_books:
            break
        path = Path(candidate["path"])
        if not path.exists() or path.stat().st_size == 0:
            continue
        print("\n" + "-" * 72)
        print(f"BOOK: {candidate['filename']}")
        print(f"Domain: {candidate['domain']} | priority={candidate['priority_score']}")
        try:
            text, extractor = extract_text(path)
        except Exception as exc:
            print(f"SKIP extractor error: {exc}")
            summary.append({**candidate, "status": "BLOCKED_EXTRACTOR", "error": str(exc)})
            continue
        text = normalize_text(text)
        language, confidence = detect_language(text)
        if language != "en":
            print(f"SKIP language={language} confidence={confidence:.3f}")
            summary.append({**candidate, "status": "SKIPPED_NOT_ENGLISH", "language": language})
            continue

        source_sha = sha256_file(path)
        book_id = source_sha[:16]
        book = {**candidate, "book_id": book_id, "source_sha256": source_sha, "language": language,
                "language_confidence": confidence, "extractor": extractor}
        book_dir = output / "translated" / book_id
        book_dir.mkdir(parents=True, exist_ok=True)
        original_text_path = output / "original_text" / f"{book_id}.txt"
        original_text_path.parent.mkdir(parents=True, exist_ok=True)
        original_text_path.write_text(text, encoding="utf-8")
        (book_dir / "book_manifest.json").write_text(json.dumps(book, ensure_ascii=False, indent=2), encoding="utf-8")

        chunks = chunk_text(text, chunk_chars)
        if max_chunks:
            chunks = chunks[:max_chunks]
        print(f"English detected confidence={confidence:.3f}; chunks queued={len(chunks)}; extractor={extractor}")
        if not chunks:
            summary.append({**book, "status": "BLOCKED_EMPTY_EXTRACTION"})
            continue

        records: list[dict] = []
        errors: list[str] = []
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {
                pool.submit(process_one_chunk, i, chunk, book, glossary_rows, glossary_version, endpoint,
                            translator_model, reviewer_model, qa_enabled, tm): i
                for i, chunk in enumerate(chunks)
            }
            for future in as_completed(futures):
                i = futures[future]
                try:
                    record = future.result()
                    records.append(record)
                    print(f"chunk {i + 1}/{len(chunks)} -> {record['status']}")
                except Exception as exc:
                    errors.append(f"chunk {i + 1}: {exc}")
                    print(f"chunk {i + 1}/{len(chunks)} -> ERROR: {exc}")

        records.sort(key=lambda x: x["chunk_index"])
        write_jsonl(book_dir / "translation_records.jsonl", records)
        (book_dir / "bilingual.md").write_text(render_bilingual(book, records), encoding="utf-8")
        new_tm = [r for r in records if not r.get("reused_from_translation_memory")]
        if new_tm:
            append_jsonl(tm_path, new_tm)
            for r in new_tm:
                tm[r["source_chunk_sha256"]] = r

        ready = sum(1 for r in records if r["status"] == "READY_FOR_KNOWLEDGE_EXTRACTION")
        review_required = sum(1 for r in records if r["status"] == "QA_REVIEW_REQUIRED")
        status = "READY_FOR_KNOWLEDGE_EXTRACTION" if records and ready == len(records) and not errors else "QA_REVIEW_REQUIRED"
        report = {
            "book_id": book_id,
            "filename": candidate["filename"],
            "source_sha256": source_sha,
            "domain": candidate["domain"],
            "chunks_processed": len(records),
            "chunks_ready": ready,
            "chunks_review_required": review_required,
            "errors": errors,
            "status": status,
        }
        summary.append(report)
        (book_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        processed_books += 1

    reports = output / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    report_path = reports / f"run_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 72)
    print("FINISHED")
    print("=" * 72)
    print(f"Books processed: {processed_books}")
    print(f"Report: {report_path}")
    print("Source files deleted: 0")
    print("Source files moved:   0")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted by user.")
        raise SystemExit(130)
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
        raise
