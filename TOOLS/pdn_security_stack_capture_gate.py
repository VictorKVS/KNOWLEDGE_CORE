#!/usr/bin/env python3
"""Fail-closed identity gate for exact PDN security-stack captures.

The acquisition runner proves bytes/hash/route. This gate prevents a generic
portal/error page from being accepted as the requested legal document when the
route is an HTML/text snapshot rather than a publication-PDF endpoint.
"""
from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STACK = ROOT / "security-corpora" / "RU" / "152-FZ" / "security-stack"
MANIFEST_DIR = STACK / "manifests"

ALLOWED_HOST_SUFFIXES = (
    "pravo.gov.ru",
    "publication.pravo.gov.ru",
    "government.ru",
    "fstec.ru",
    "minzdrav.gov.ru",
    "fsb.ru",
    "rg.ru",
)

# These are identity markers, not semantic extraction rules.
STRICT_TEXT_IDENTITIES: dict[str, tuple[tuple[str, ...], ...]] = {
    "SEC-SRC-RU-PP1119-2012": (
        ("1119",),
        ("персональн",),
        ("информационн", "систем"),
    ),
    "SEC-SRC-RU-PP313-2012": (
        ("313",),
        ("лицензирован",),
        ("шифровальн", "криптограф"),
    ),
    "SEC-SRC-RU-PP79-2012": (
        ("79",),
        ("лицензирован",),
        ("техническ", "конфиденциальн"),
    ),
    "SEC-SRC-RU-FAPSI152-2001": (
        ("152",),
        ("фапси",),
        ("криптограф", "шифровальн"),
    ),
    "SEC-SRC-RU-FSB66-2005": (
        ("66",),
        ("фсб",),
        ("пкз-2005", "шифровальн", "криптограф"),
    ),
}


def _decode(data: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            return data.decode(enc).casefold()
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="ignore").casefold()


def _host_ok(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").casefold()
    return any(host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_HOST_SUFFIXES)


def _looks_textual(manifest: dict, artifact: Path) -> bool:
    mime = str(manifest.get("mime", "")).casefold()
    return "html" in mime or mime.startswith("text/") or artifact.suffix.casefold() in {".html", ".htm", ".txt"}


def main() -> int:
    failures: list[str] = []
    checked = 0
    for source_id, groups in STRICT_TEXT_IDENTITIES.items():
        mp = MANIFEST_DIR / f"{source_id}.json"
        if not mp.exists():
            continue
        manifest = json.loads(mp.read_text(encoding="utf-8"))
        source_url = str(manifest.get("source_url", ""))
        if not _host_ok(source_url):
            failures.append(f"{source_id}: non-official final host: {source_url}")
            continue
        artifact = ROOT / str(manifest.get("artifact_ref", ""))
        if not artifact.is_file():
            failures.append(f"{source_id}: artifact missing: {artifact}")
            continue
        if not _looks_textual(manifest, artifact):
            # PDF/DOCX identity is guarded by signature/route-specific acquisition
            # checks; this gate only addresses generic HTML/text portal responses.
            continue
        checked += 1
        text = re.sub(r"\s+", " ", _decode(artifact.read_bytes()))
        for alternatives in groups:
            if not any(marker.casefold() in text for marker in alternatives):
                failures.append(f"{source_id}: identity marker group missing: {alternatives}")
    if failures:
        print("PDN_SECURITY_STACK_CAPTURE_IDENTITY_FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 2
    print(f"PDN_SECURITY_STACK_CAPTURE_IDENTITY_PASS textual_checked={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
