#!/usr/bin/env python3
"""Capture the current consolidated 152-FZ root from its registered official IPS route.

This is deliberately separate from the general PDN acquirer because the current
consolidated root is not yet METADATA_VERIFIED: its version identity is cross-verified,
but immutable capture is itself the next proof gate. The script therefore accepts only
one explicit source ID and only when metadata_status is VERSION_IDENTITY_CROSS_VERIFIED.
It writes raw bytes + manifest and never promotes semantic/extraction status.

Safety invariant (v1.4): an official-route response is not sufficient by itself. The
captured body must also contain identity markers for Federal Law No. 152-FZ on personal
data. This prevents a generic error, anti-bot, redirect or portal landing page from being
accepted as an immutable consolidated-law artifact merely because it came from pravo.gov.ru.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pdn_core_acquire import (
    CANONICAL_URL_RE,
    CORPUS,
    DOC_NUMBER_RE,
    MANIFEST_DIR,
    ROOT,
    capture_canonical_snapshot,
    top_level_section,
)

SOURCE_ID = "SEC-SRC-RU-152FZ-2026-07-26"
SOURCE_RECORD = CORPUS / "source" / f"{SOURCE_ID}.yaml"
METADATA_STATUS_RE = re.compile(r"^metadata_status:\s*([^\s#]+)\s*$", re.M)
IDENTITY_MARKER_GROUPS = (
    ("152-фз", "№ 152-фз", "№152-фз", "152 фз"),
    ("персональных данных", "персональные данные"),
)


def decode_for_identity(data: bytes) -> str:
    """Best-effort decode only for an identity guard; raw bytes remain authoritative."""
    candidates: list[str] = []
    for encoding in ("utf-8", "cp1251"):
        try:
            candidates.append(data.decode(encoding))
        except UnicodeDecodeError:
            candidates.append(data.decode(encoding, errors="ignore"))
    return "\n".join(candidates).lower().replace("\xa0", " ")


def current_root_identity_ok(data: bytes) -> tuple[bool, list[str]]:
    text = decode_for_identity(data)
    matched: list[str] = []
    for group in IDENTITY_MARKER_GROUPS:
        marker = next((m for m in group if m in text), "")
        if not marker:
            return False, matched
        matched.append(marker)
    return True, matched


def main() -> int:
    text = SOURCE_RECORD.read_text(encoding="utf-8")
    metadata = METADATA_STATUS_RE.search(text)
    if not metadata or metadata.group(1) != "VERSION_IDENTITY_CROSS_VERIFIED":
        raise RuntimeError(
            f"refuse current-root capture: metadata_status is not VERSION_IDENTITY_CROSS_VERIFIED for {SOURCE_ID}"
        )

    document = top_level_section(text, "document")
    canonical = top_level_section(text, "canonical_source")
    mnumber = DOC_NUMBER_RE.search(document)
    murl = CANONICAL_URL_RE.search(canonical)
    if not murl:
        raise RuntimeError(f"refuse current-root capture: no registered canonical_source.url for {SOURCE_ID}")

    expected_number = mnumber.group(1).strip() if mnumber else ""
    manifest = capture_canonical_snapshot(
        SOURCE_ID,
        murl.group(1),
        expected_number,
        SOURCE_RECORD,
    )

    # Validate the returned body before allowing a manifest to exist. The generic
    # canonical capture helper already wrote the raw bytes, so remove that candidate
    # if the body is not recognizably the registered law.
    artifact = ROOT / str(manifest["artifact_ref"])
    body = artifact.read_bytes()
    identity_ok, markers = current_root_identity_ok(body)
    if not identity_ok:
        artifact.unlink(missing_ok=True)
        raise RuntimeError(
            "refuse current-root capture: official-route response lacks required "
            "152-FZ/personal-data identity markers"
        )

    manifest["schema_version"] = "1.4"
    manifest["capture_policy"] = "current-root-version-identity-cross-verified-with-content-markers"
    manifest["semantic_status_unchanged"] = True
    manifest["proof"]["current_root_source_id_pinned"] = True
    manifest["proof"]["metadata_status_gate"] = "VERSION_IDENTITY_CROSS_VERIFIED"
    manifest["proof"]["canonical_content_identity_markers_ok"] = True
    manifest["proof"]["canonical_content_identity_markers"] = markers

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    mpath = MANIFEST_DIR / f"{SOURCE_ID}.json"
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_id": SOURCE_ID,
        "status": "IMMUTABLE_CAPTURED_RAW_ONLY",
        "mime": manifest["mime"],
        "byte_length": manifest["byte_length"],
        "sha256": manifest["sha256"],
        "artifact_ref": manifest["artifact_ref"],
        "identity_markers": markers,
        "semantic_status_unchanged": True,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({
            "source_id": SOURCE_ID,
            "status": "PENDING",
            "error": str(exc),
            "semantic_status_unchanged": True,
        }, ensure_ascii=False))
        sys.exit(2)
