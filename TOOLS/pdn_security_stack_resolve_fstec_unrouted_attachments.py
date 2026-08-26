#!/usr/bin/env python3
"""Resolve remaining exact official FSTEC attachment routes for Stream 2.

This resolver is deliberately conservative:
- only pre-registered official fstec.ru landing pages are fetched;
- only same-host /files/... PDF/DOC attachments are candidates;
- exactly one candidate is required before a source card is updated;
- ambiguous, missing, off-site, or transport-failed cases remain unresolved;
- this step never stores immutable evidence and never invents fingerprints.

The normal Stream-2 acquisition pipeline downloads accepted routes and computes
MIME, byte length and SHA-256 from actual bytes afterwards.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
STACK = ROOT / "security-corpora/RU/152-FZ/security-stack"
SOURCE_DIR = STACK / "source"
REPORT = STACK / "PDN_FSTEC_UNROUTED_ATTACHMENT_RESOLUTION.json"
UA = "KNOWLEDGE_CORE-pdn-fstec-unrouted-resolver/1.0 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"

TARGETS = (
    "SEC-SRC-RU-FSTEC-INFO-240-13-5521-2026",
    "SEC-SRC-RU-FSTEC-TZI-EQUIPMENT-LIST-2026",
    "SEC-SRC-RU-FSTEC-TZI-LIST-2024",
    "SEC-SRC-RU-FSTEC-INFO-240-13-5331-2026",
    "SEC-SRC-RU-FSTEC-INFO-240-24-3693-2026",
    "SEC-SRC-RU-FSTEC-INFO-240-24-4974-2026",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.casefold() != "a":
            return
        for key, value in attrs:
            if key.casefold() == "href" and value:
                self.hrefs.append(str(value))


def candidate_attachment_links(html: str, landing: str) -> list[str]:
    """Return unique same-host official /files/ PDF/DOC candidates only."""
    parser = LinkParser()
    parser.feed(html)
    base_host = (urlparse(landing).hostname or "").casefold()
    if base_host not in {"fstec.ru", "www.fstec.ru"}:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for href in parser.hrefs:
        url = urljoin(landing, href)
        parsed = urlparse(url)
        host = (parsed.hostname or "").casefold()
        path = parsed.path.casefold()
        if host != base_host or host not in {"fstec.ru", "www.fstec.ru"}:
            continue
        if not path.startswith("/files/"):
            continue
        if not path.endswith((".pdf", ".doc", ".docx")):
            continue
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def extract_landing(text: str) -> str | None:
    match = re.search(r'^  landing_page:\s*"([^"]+)"\s*$', text, re.M)
    return match.group(1) if match else None


def curl_text(url: str) -> str:
    with tempfile.TemporaryDirectory(prefix="pdn-fstec-unrouted-") as td:
        body = Path(td) / "landing.html"
        cmd = [
            "curl", "--silent", "--show-error", "--location", "--fail-with-body",
            "--connect-timeout", "12", "--max-time", "35", "--ipv4", "--http1.1",
            "--header", f"User-Agent: {UA}",
            "--header", "Accept: text/html,application/xhtml+xml",
            "--output", str(body), url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if proc.returncode != 0:
            raise RuntimeError(f"curl exit={proc.returncode}: {(proc.stderr or '').strip()}")
        data = body.read_bytes()
        if not data:
            raise RuntimeError("empty official landing response")
        for enc in ("utf-8", "utf-8-sig", "cp1251"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                pass
        return data.decode("utf-8", errors="replace")


def mime_for(url: str) -> str:
    path = urlparse(url).path.casefold()
    if path.endswith(".pdf"):
        return "application/pdf"
    if path.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if path.endswith(".doc"):
        return "application/msword"
    raise ValueError("unsupported attachment type")


def update_source(text: str, direct: str, checked_at: str) -> str:
    """Expose a resolved route to the normal acquirer without promotion."""
    canonical_match = re.search(r"(?ms)^canonical_source:\n.*?(?=^[A-Za-z_][A-Za-z0-9_-]*:|\Z)", text)
    if not canonical_match:
        raise RuntimeError("canonical_source block missing")
    block = canonical_match.group(0)
    expected_mime = mime_for(direct)
    if re.search(r'^  url:\s*', block, re.M):
        block = re.sub(r'^  url:\s*.*$', f'  url: "{direct}"', block, flags=re.M)
    elif re.search(r'^  landing_page:.*$', block, re.M):
        block = re.sub(r'(^  landing_page:.*$)', rf'\1\n  url: "{direct}"', block, count=1, flags=re.M)
    else:
        raise RuntimeError("canonical_source landing_page missing")
    if re.search(r'^  expected_mime:\s*', block, re.M):
        block = re.sub(r'^  expected_mime:\s*.*$', f'  expected_mime: "{expected_mime}"', block, flags=re.M)
    else:
        block = re.sub(r'(^  url:.*$)', rf'\1\n  expected_mime: "{expected_mime}"', block, count=1, flags=re.M)
    if re.search(r'^  direct_file_url:\s*', block, re.M):
        block = re.sub(r'^  direct_file_url:\s*.*$', f'  direct_file_url: "{direct}"', block, flags=re.M)
    else:
        block = re.sub(r'(^  expected_mime:.*$)', rf'\1\n  direct_file_url: "{direct}"', block, count=1, flags=re.M)
    block = re.sub(
        r'^  exact_file_route_status:\s*.*$',
        '  exact_file_route_status: EXACT_OFFICIAL_FILE_ROUTE_RESOLVED_CAPTURE_PENDING',
        block,
        flags=re.M,
    )
    block = re.sub(
        r'(^  freshness_check:\n\s+checked_at:)\s*"[^"]+"',
        rf'\1 "{checked_at}"', block, count=1, flags=re.M,
    )
    updated = text[:canonical_match.start()] + block + text[canonical_match.end():]
    if re.search(r'(^  source_url:)\s*"[^"]+"', updated, re.M):
        updated = re.sub(r'(^  source_url:)\s*"[^"]+"', rf'\1 "{direct}"', updated, count=1, flags=re.M)
    updated = re.sub(
        r'(^  exact_official_file_route_verified:)\s*(true|false)',
        r'\1 true', updated, count=1, flags=re.M,
    )
    return updated


def resolve_one(source_id: str, observed: str) -> dict[str, object]:
    source = SOURCE_DIR / f"{source_id}.yaml"
    result: dict[str, object] = {
        "source_id": source_id,
        "semantic_status_unchanged": True,
        "immutable_promotion": False,
    }
    if not source.is_file():
        result.update(status="PENDING_SOURCE_CARD_MISSING")
        return result
    text = source.read_text(encoding="utf-8")
    landing = extract_landing(text)
    if not landing:
        result.update(status="PENDING_OFFICIAL_LANDING_UNRESOLVED", reason="registered landing_page missing")
        return result
    result["landing_page"] = landing
    try:
        html = curl_text(landing)
        links = candidate_attachment_links(html, landing)
        result["candidate_attachment_links"] = links
        if len(links) != 1:
            result["status"] = "PENDING_AMBIGUOUS_OR_MISSING_ATTACHMENT"
            result["reason"] = f"expected exactly one same-host /files/ PDF/DOC attachment, got {len(links)}"
            return result
        direct = links[0]
        source.write_text(update_source(text, direct, observed[:10]), encoding="utf-8")
        result["status"] = "EXACT_OFFICIAL_FILE_ROUTE_RESOLVED_CAPTURE_PENDING"
        result["resolved_url"] = direct
        return result
    except Exception as exc:
        result["status"] = "PENDING_TRANSPORT"
        result["reason"] = f"{type(exc).__name__}: {exc}"
        return result


def main() -> int:
    observed = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    rows = [resolve_one(source_id, observed) for source_id in TARGETS]
    payload = {
        "schema_version": "1.0",
        "record_type": "PDN_FSTEC_UNROUTED_ATTACHMENT_RESOLUTION",
        "observed_at": observed,
        "targets_total": len(rows),
        "resolved_total": sum(row.get("status") == "EXACT_OFFICIAL_FILE_ROUTE_RESOLVED_CAPTURE_PENDING" for row in rows),
        "immutable_promotion": False,
        "results": rows,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
