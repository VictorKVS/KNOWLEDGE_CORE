#!/usr/bin/env python3
"""Guarded multi-route curl acquisition for the current consolidated 152-FZ.

All official URLs must already be registered inside the current source card. The helper
tries each registered route, including a TLS-normalized equivalent for legacy HTTP IPS
links. A response is accepted only if the existing content gate proves 152-FZ,
personal-data identity and the pinned current-revision marker No. 265-FZ.
Raw capture never promotes semantic or extraction status.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from pdn_core_acquire import CORPUS, DOC_NUMBER_RE, MANIFEST_DIR, ROOT, top_level_section
from pdn_current_root_acquire import (
    CURRENT_REVISION_EFFECTIVE_FROM,
    CURRENT_REVISION_TRIGGER,
    METADATA_STATUS_RE,
    SOURCE_ID,
    SOURCE_RECORD,
    current_root_identity_ok,
)

UA = "KNOWLEDGE_CORE-pdn-current-root-curl/1.3 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"
RAW_DIR = CORPUS / "raw" / SOURCE_ID
REGISTERED_URL_RE = re.compile(r'(?m)^\s+url:\s*["\']([^"\']+)["\']\s*$')


def curl_capture(url: str) -> tuple[bytes, str, str]:
    with tempfile.TemporaryDirectory(prefix="pdn-current-root-") as td:
        body = Path(td) / "body.bin"
        cmd = [
            "curl", "--silent", "--show-error", "--location", "--fail-with-body",
            "--retry", "3", "--retry-delay", "2", "--retry-all-errors",
            "--connect-timeout", "20", "--max-time", "120", "--ipv4", "--http1.1",
            "--header", f"User-Agent: {UA}",
            "--header", "Accept: text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
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
            raise RuntimeError("empty official-route response")
        lines = (proc.stdout or "").splitlines()
        final_url = lines[0].strip() if lines else url
        mime = lines[1].strip().split(";", 1)[0] if len(lines) > 1 else "application/octet-stream"
        return data, final_url, mime or "application/octet-stream"


def registered_urls(canonical_section: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for url in REGISTERED_URL_RE.findall(canonical_section):
        if url not in seen:
            urls.append(url)
            seen.add(url)
    return urls


def transport_variants(urls: list[str]) -> list[tuple[str, str, str]]:
    """Return (label, transport_url, registered_url) without inventing unregistered identities."""
    out: list[tuple[str, str, str]] = []
    seen_transport: set[str] = set()
    for index, registered_url in enumerate(urls, start=1):
        variants: list[tuple[str, str]] = []
        if registered_url.startswith("http://"):
            variants.append((f"registered_route_{index}_tls_equivalent", "https://" + registered_url[len("http://"):]))
        variants.append((f"registered_route_{index}_as_recorded", registered_url))
        for label, transport_url in variants:
            if transport_url in seen_transport:
                continue
            out.append((label, transport_url, registered_url))
            seen_transport.add(transport_url)
    return out


def write_immutable(data: bytes) -> tuple[Path, str]:
    sha = hashlib.sha256(data).hexdigest()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stripped = data.lstrip().lower()
    if data.startswith(b"%PDF-"):
        ext = ".pdf"
    elif stripped.startswith((b"<!doctype html", b"<html")):
        ext = ".html"
    else:
        ext = ".bin"
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
            f"refuse current-root capture: metadata_status is not VERSION_IDENTITY_CROSS_VERIFIED for {SOURCE_ID}"
        )

    document = top_level_section(text, "document")
    canonical = top_level_section(text, "canonical_source")
    mnumber = DOC_NUMBER_RE.search(document)
    expected_number = mnumber.group(1).strip() if mnumber else ""
    source_urls = registered_urls(canonical)
    if not source_urls:
        raise RuntimeError("refuse current-root capture: no registered official URLs in canonical_source")

    attempts = transport_variants(source_urls)
    errors: list[str] = []
    accepted_transport = ""
    accepted_registered_url = ""
    accepted_transport_url = ""
    data = b""
    final_url = ""
    mime = "application/octet-stream"
    markers: list[str] = []

    for label, transport_url, registered_url in attempts:
        try:
            candidate, candidate_final_url, candidate_mime = curl_capture(transport_url)
            ok, candidate_markers = current_root_identity_ok(candidate)
            if not ok:
                raise RuntimeError("official response lacks required 152-FZ/personal-data/current-revision markers")
            accepted_transport = label
            accepted_registered_url = registered_url
            accepted_transport_url = transport_url
            data = candidate
            final_url = candidate_final_url
            mime = candidate_mime
            markers = candidate_markers
            break
        except Exception as exc:
            errors.append(f"{label}: {exc}")

    if not data:
        raise RuntimeError("all registered current-root official transports failed: " + " | ".join(errors))

    artifact, sha = write_immutable(data)
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    manifest: dict[str, object] = {
        "schema_version": "1.8",
        "source_id": SOURCE_ID,
        "source_document_number": expected_number,
        "capture_kind": "official_canonical_snapshot",
        "accepted_transport": accepted_transport,
        "accepted_registered_source_url": accepted_registered_url,
        "source_url": accepted_transport_url,
        "official_file_url": final_url,
        "registered_source_urls": source_urls,
        "transport_attempt_order": [label for label, _, _ in attempts],
        "retrieved_at": retrieved,
        "mime": mime,
        "byte_length": len(data),
        "sha256": sha,
        "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
        "source_record_ref": str(SOURCE_RECORD.relative_to(ROOT)).replace("\\", "/"),
        "capture_policy": "current-root-version-identity-cross-verified-multi-official-route-with-content-and-revision-markers",
        "proof": {
            "official_route": True,
            "official_route_pre_registered": True,
            "byte_exact_download": True,
            "sha256_calculated_from_downloaded_bytes": True,
            "publication_api_length_check_not_applicable": True,
            "current_root_source_id_pinned": True,
            "metadata_status_gate": "VERSION_IDENTITY_CROSS_VERIFIED",
            "canonical_content_identity_markers_ok": True,
            "canonical_content_identity_markers": markers,
            "current_revision_marker_ok": True,
            "current_revision_trigger": CURRENT_REVISION_TRIGGER,
            "current_revision_effective_from": CURRENT_REVISION_EFFECTIVE_FROM,
            "transport_fallback_only": True,
            "semantic_status_unchanged": True,
        },
        "failed_transports_before_acceptance": errors,
        "semantic_status_unchanged": True,
        "review_note": "Capture proves exact bytes from a pre-registered official route plus source/current-revision markers only; locator/delta review remains required before extraction promotion.",
    }
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    (MANIFEST_DIR / f"{SOURCE_ID}.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "source_id": SOURCE_ID,
        "status": "IMMUTABLE_CAPTURED_RAW_ONLY",
        "accepted_transport": accepted_transport,
        "accepted_registered_source_url": accepted_registered_url,
        "mime": mime,
        "byte_length": len(data),
        "sha256": sha,
        "artifact_ref": manifest["artifact_ref"],
        "identity_and_revision_markers": markers,
        "current_revision_trigger": CURRENT_REVISION_TRIGGER,
        "current_revision_effective_from": CURRENT_REVISION_EFFECTIVE_FROM,
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
