#!/usr/bin/env python3
"""Guarded curl fallback for the current consolidated 152-FZ official IPS route.

This is a transport fallback only. It uses the same registered official IPS URL and
the same current-root metadata gate as pdn_current_root_acquire.py. A response is
accepted only if it contains the 152-FZ and personal-data identity markers. Raw capture
never promotes semantic/extraction status.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from pdn_core_acquire import (
    CANONICAL_URL_RE,
    CORPUS,
    DOC_NUMBER_RE,
    MANIFEST_DIR,
    ROOT,
    top_level_section,
)
from pdn_current_root_acquire import (
    METADATA_STATUS_RE,
    SOURCE_ID,
    SOURCE_RECORD,
    current_root_identity_ok,
)

UA = "KNOWLEDGE_CORE-pdn-current-root-curl/1.0 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"
RAW_DIR = CORPUS / "raw" / SOURCE_ID


def curl_capture(url: str) -> tuple[bytes, str, str]:
    with tempfile.TemporaryDirectory(prefix="pdn-current-root-") as td:
        body = Path(td) / "body.bin"
        cmd = [
            "curl", "--silent", "--show-error", "--location", "--fail-with-body",
            "--retry", "4", "--retry-delay", "2", "--retry-all-errors",
            "--connect-timeout", "20", "--max-time", "120", "--ipv4",
            "--header", f"User-Agent: {UA}",
            "--header", "Accept: text/html,application/xhtml+xml,*/*;q=0.8",
            "--header", "Accept-Encoding: identity",
            "--output", str(body),
            "--write-out", "%{url_effective}\n%{content_type}\n",
            url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=150)
        if proc.returncode != 0:
            raise RuntimeError(f"curl exit={proc.returncode}: {(proc.stderr or '').strip()}")
        data = body.read_bytes() if body.exists() else b""
        if not data:
            raise RuntimeError("empty official IPS response")
        lines = (proc.stdout or "").splitlines()
        final_url = lines[0].strip() if lines else url
        mime = lines[1].strip().split(";", 1)[0] if len(lines) > 1 else "application/octet-stream"
        return data, final_url, mime or "application/octet-stream"


def write_immutable(data: bytes) -> tuple[Path, str]:
    sha = hashlib.sha256(data).hexdigest()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".html" if data.lstrip().lower().startswith((b"<!doctype html", b"<html")) else ".bin"
    artifact = RAW_DIR / f"official-current-snapshot-{sha[:16]}{ext}"
    if artifact.exists():
        old = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if old != sha:
            raise RuntimeError(f"immutable collision: existing={old}, incoming={sha}")
    else:
        artifact.write_bytes(data)
    return artifact, sha


def main() -> int:
    text = SOURCE_RECORD.read_text(encoding="utf-8")
    metadata = METADATA_STATUS_RE.search(text)
    if not metadata or metadata.group(1) != "VERSION_IDENTITY_CROSS_VERIFIED":
        raise RuntimeError(
            f"refuse current-root curl capture: metadata_status is not VERSION_IDENTITY_CROSS_VERIFIED for {SOURCE_ID}"
        )

    document = top_level_section(text, "document")
    canonical = top_level_section(text, "canonical_source")
    mnumber = DOC_NUMBER_RE.search(document)
    murl = CANONICAL_URL_RE.search(canonical)
    if not murl:
        raise RuntimeError("refuse current-root curl capture: no registered canonical_source.url")

    source_url = murl.group(1)
    expected_number = mnumber.group(1).strip() if mnumber else ""
    data, final_url, mime = curl_capture(source_url)
    identity_ok, markers = current_root_identity_ok(data)
    if not identity_ok:
        raise RuntimeError(
            "refuse current-root curl capture: official response lacks required 152-FZ/personal-data identity markers"
        )

    artifact, sha = write_immutable(data)
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    manifest: dict[str, object] = {
        "schema_version": "1.5",
        "source_id": SOURCE_ID,
        "source_document_number": expected_number,
        "capture_kind": "official_canonical_snapshot",
        "official_file_url": final_url,
        "source_url": source_url,
        "retrieved_at": retrieved,
        "mime": mime,
        "byte_length": len(data),
        "sha256": sha,
        "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
        "source_record_ref": str(SOURCE_RECORD.relative_to(ROOT)).replace("\\", "/"),
        "capture_policy": "current-root-version-identity-cross-verified-curl-fallback-with-content-markers",
        "proof": {
            "official_route": True,
            "publication_id_scoped_to_source_document_section": True,
            "byte_exact_download": True,
            "sha256_calculated_from_downloaded_bytes": True,
            "publication_api_length_check_not_applicable": True,
            "current_root_source_id_pinned": True,
            "metadata_status_gate": "VERSION_IDENTITY_CROSS_VERIFIED",
            "canonical_content_identity_markers_ok": True,
            "canonical_content_identity_markers": markers,
            "transport_fallback_only": True,
        },
        "semantic_status_unchanged": True,
        "review_note": "Capture proves exact bytes from the registered official IPS route and source identity markers only; current-version locator/delta review remains required before extraction promotion.",
    }
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    (MANIFEST_DIR / f"{SOURCE_ID}.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "source_id": SOURCE_ID,
        "status": "IMMUTABLE_CAPTURED_RAW_ONLY",
        "mime": mime,
        "byte_length": len(data),
        "sha256": sha,
        "artifact_ref": manifest["artifact_ref"],
        "identity_markers": markers,
        "semantic_status_unchanged": True,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({
            "source_id": SOURCE_ID,
            "status": "PENDING",
            "error": str(exc),
            "semantic_status_unchanged": True,
        }, ensure_ascii=False))
        raise SystemExit(2)
