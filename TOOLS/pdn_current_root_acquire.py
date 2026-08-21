#!/usr/bin/env python3
"""Capture the current consolidated 152-FZ root from its registered official IPS route.

This is deliberately separate from the general PDN acquirer because the current
consolidated root is not yet METADATA_VERIFIED: its version identity is cross-verified,
but immutable capture is itself the next proof gate. The script therefore accepts only
one explicit source ID and only when metadata_status is VERSION_IDENTITY_CROSS_VERIFIED.
It writes raw bytes + manifest and never promotes semantic/extraction status.
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
    capture_canonical_snapshot,
    top_level_section,
)

SOURCE_ID = "SEC-SRC-RU-152FZ-2026-07-26"
SOURCE_RECORD = CORPUS / "source" / f"{SOURCE_ID}.yaml"
METADATA_STATUS_RE = re.compile(r"^metadata_status:\s*([^\s#]+)\s*$", re.M)


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
    manifest["schema_version"] = "1.3"
    manifest["capture_policy"] = "current-root-version-identity-cross-verified"
    manifest["semantic_status_unchanged"] = True
    manifest["proof"]["current_root_source_id_pinned"] = True
    manifest["proof"]["metadata_status_gate"] = "VERSION_IDENTITY_CROSS_VERIFIED"

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
