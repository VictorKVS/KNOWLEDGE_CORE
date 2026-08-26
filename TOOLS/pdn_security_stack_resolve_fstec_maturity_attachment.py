#!/usr/bin/env python3
"""Resolve the exact official FSTEC PDF attachment for the 07.08.2026 maturity method.

Fail-closed rules:
- only the pre-registered fstec.ru landing page is fetched;
- only same-host /files/...pdf links are candidates;
- exactly one candidate must be present;
- this step resolves a route only; it never creates immutable evidence or promotes semantics.
The normal Stream-2 acquirer subsequently downloads and fingerprints the PDF.
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
SOURCE = ROOT / "security-corpora/RU/152-FZ/security-stack/source/SEC-SRC-RU-FSTEC-MATURITY-METHOD-2026.yaml"
REPORT = ROOT / "security-corpora/RU/152-FZ/security-stack/PDN_FSTEC_MATURITY_ATTACHMENT_RESOLUTION.json"
UA = "KNOWLEDGE_CORE-pdn-fstec-maturity-resolver/1.0 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"
LANDING_RE = re.compile(r'^  landing_page:\s*"([^"]+)"\s*$', re.M)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.casefold() != "a":
            return
        for key, value in attrs:
            if key.casefold() == "href" and value:
                self.hrefs.append(str(value))


def candidate_pdf_links(html: str, landing: str) -> list[str]:
    parser = LinkParser()
    parser.feed(html)
    base_host = (urlparse(landing).hostname or "").casefold()
    out: list[str] = []
    seen: set[str] = set()
    for href in parser.hrefs:
        url = urljoin(landing, href)
        parsed = urlparse(url)
        host = (parsed.hostname or "").casefold()
        if host != base_host or host not in {"fstec.ru", "www.fstec.ru"}:
            continue
        if not parsed.path.startswith("/files/") or not parsed.path.casefold().endswith(".pdf"):
            continue
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def curl_text(url: str) -> str:
    with tempfile.TemporaryDirectory(prefix="pdn-fstec-maturity-") as td:
        body = Path(td) / "landing.html"
        cmd = [
            "curl", "--silent", "--show-error", "--location", "--fail-with-body",
            "--connect-timeout", "12", "--max-time", "35", "--ipv4", "--http1.1",
            "--header", f"User-Agent: {UA}", "--header", "Accept: text/html,application/xhtml+xml",
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


def update_source(text: str, direct: str, checked_at: str) -> str:
    canonical_match = re.search(r"(?ms)^canonical_source:\n.*?(?=^[A-Za-z_][A-Za-z0-9_-]*:|\Z)", text)
    if not canonical_match:
        raise RuntimeError("canonical_source block missing")
    block = canonical_match.group(0)
    if re.search(r'^  url:\s*', block, re.M):
        block = re.sub(r'^  url:\s*.*$', f'  url: "{direct}"', block, flags=re.M)
    else:
        block = re.sub(r'(^  landing_page:.*$)', rf'\1\n  url: "{direct}"', block, count=1, flags=re.M)
    if re.search(r'^  expected_mime:\s*', block, re.M):
        block = re.sub(r'^  expected_mime:\s*.*$', '  expected_mime: "application/pdf"', block, flags=re.M)
    else:
        block = re.sub(r'(^  url:.*$)', r'\1\n  expected_mime: "application/pdf"', block, count=1, flags=re.M)
    if re.search(r'^  direct_pdf_url:\s*', block, re.M):
        block = re.sub(r'^  direct_pdf_url:\s*.*$', f'  direct_pdf_url: "{direct}"', block, flags=re.M)
    else:
        block = re.sub(r'(^  expected_mime:.*$)', rf'\1\n  direct_pdf_url: "{direct}"', block, count=1, flags=re.M)
    block = re.sub(r'^  exact_file_route_status:\s*.*$', '  exact_file_route_status: EXACT_OFFICIAL_PDF_ROUTE_RESOLVED_CAPTURE_PENDING', block, flags=re.M)
    block = re.sub(r'(^  freshness_check:\n\s+checked_at:)\s*"[^"]+"', rf'\1 "{checked_at}"', block, count=1, flags=re.M)
    updated = text[:canonical_match.start()] + block + text[canonical_match.end():]
    updated = re.sub(r'(^  source_url:)\s*"[^"]+"', rf'\1 "{direct}"', updated, count=1, flags=re.M)
    updated = re.sub(r'(^  exact_official_file_route_verified:)\s*(true|false)', r'\1 true', updated, count=1, flags=re.M)
    return updated


def main() -> int:
    observed = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    text = SOURCE.read_text(encoding="utf-8")
    match = LANDING_RE.search(text)
    if not match:
        raise SystemExit("registered FSTEC landing_page missing")
    landing = match.group(1)
    result: dict[str, object] = {
        "schema_version": "1.0", "source_id": "SEC-SRC-RU-FSTEC-MATURITY-METHOD-2026",
        "landing_page": landing, "observed_at": observed, "semantic_status_unchanged": True,
        "immutable_promotion": False,
    }
    try:
        html = curl_text(landing)
        links = candidate_pdf_links(html, landing)
        result["candidate_pdf_links"] = links
        if len(links) != 1:
            result["status"] = "PENDING_AMBIGUOUS_OR_MISSING_ATTACHMENT"
            result["reason"] = f"expected exactly one same-host /files/*.pdf link, got {len(links)}"
        else:
            direct = links[0]
            SOURCE.write_text(update_source(text, direct, observed[:10]), encoding="utf-8")
            result["status"] = "EXACT_OFFICIAL_PDF_ROUTE_RESOLVED_CAPTURE_PENDING"
            result["resolved_url"] = direct
    except Exception as exc:
        result["status"] = "PENDING_TRANSPORT"
        result["reason"] = f"{type(exc).__name__}: {exc}"
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
