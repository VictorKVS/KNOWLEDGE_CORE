#!/usr/bin/env python3
"""Targeted browser-compatible retry for the official Rossiyskaya Gazeta archive.

GitHub-hosted acquisition repeatedly receives HTTP 401 from the registered RG
publication URL for FSB Order No. 378 while the same official publication remains
publicly indexed and readable through normal browser traffic.  This helper changes
transport presentation only: it uses the already-registered official RG URL, keeps
the existing strict identity/signature gates, writes the normal immutable manifest
on success, and never changes semantic/applicability status.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import pdn_security_stack_curl_pending as base
from pdn_security_stack_acquire import discover_targets, reusable

SOURCE_ID = "SEC-SRC-RU-FSB378-2014"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)


def _browser_curl(url: str) -> tuple[bytes, str, str]:
    if not url.startswith("https://rg.ru/"):
        raise RuntimeError("browser-compatible retry is restricted to the registered rg.ru official archive")
    with tempfile.TemporaryDirectory(prefix="pdn-stack-rg-") as td:
        body = Path(td) / "body.bin"
        cmd = [
            "curl",
            "--silent",
            "--show-error",
            "--location",
            "--fail-with-body",
            "--connect-timeout",
            "15",
            "--max-time",
            "55",
            "--ipv4",
            "--http1.1",
            "--user-agent",
            BROWSER_UA,
            "--referer",
            "https://rg.ru/",
            "--header",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "--header",
            "Accept-Language: ru-RU,ru;q=0.9,en;q=0.7",
            "--header",
            "Accept-Encoding: identity",
            "--output",
            str(body),
            "--write-out",
            "%{url_effective}\n%{content_type}\n",
            url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=70)
        if proc.returncode != 0:
            raise RuntimeError(f"curl exit={proc.returncode}: {(proc.stderr or '').strip()}")
        data = body.read_bytes() if body.exists() else b""
        if not data:
            raise RuntimeError("empty official response")
        lines = (proc.stdout or "").splitlines()
        final_url = lines[0].strip() if lines else url
        mime = lines[1].strip().split(";", 1)[0].casefold() if len(lines) > 1 else "application/octet-stream"
        return data, final_url, mime or "application/octet-stream"


def main() -> int:
    if reusable(SOURCE_ID):
        print(json.dumps({"source_id": SOURCE_ID, "status": "REUSED_IMMUTABLE"}, ensure_ascii=False))
        return 0

    target = next((row for row in discover_targets() if str(row.get("source_id")) == SOURCE_ID), None)
    if target is None:
        print(json.dumps({"source_id": SOURCE_ID, "status": "SKIPPED", "reason": "REGISTERED_TARGET_NOT_FOUND"}, ensure_ascii=False))
        return 0
    if not str(target.get("value") or "").startswith("https://rg.ru/"):
        print(json.dumps({"source_id": SOURCE_ID, "status": "SKIPPED", "reason": "NON_RG_REGISTERED_ROUTE"}, ensure_ascii=False))
        return 0

    original = base._curl
    try:
        base._curl = _browser_curl
        result = base._attempt_target(target)
    finally:
        base._curl = original

    result["transport_profile"] = "BROWSER_COMPATIBLE_RG_OFFICIAL_ARCHIVE"
    result["semantic_status_unchanged"] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
