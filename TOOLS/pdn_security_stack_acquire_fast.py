#!/usr/bin/env python3
"""Bounded Stream-2 acquisition profile for change-triggered runs.

Pushes should validate newly registered/changed official routes quickly instead of
re-spending the full scheduled-run timeout budget on every known slow endpoint.
The authoritative acquisition logic, immutable write path, manifests, counters and
proof gates remain in ``pdn_security_stack_acquire``; only transport retry budgets
are clamped here.

For publication.pravo.gov.ru publication-PDF targets, a source card may declare a
curated ``canonical_source.fallback_url`` on another official publication archive.
The fallback is attempted only after the primary publication route fails, must be a
real PDF, and is promoted only after exact downloaded bytes are hashed by the same
immutable writer as the primary path.
"""
from __future__ import annotations

import pdn_security_stack_acquire as base

_ORIGINAL_FETCH = base.fetch_bytes
_ORIGINAL_CAPTURE = base.capture


def bounded_fetch(url: str, timeout: int = 75, attempts: int = 3):
    return _ORIGINAL_FETCH(url, timeout=min(timeout, 25), attempts=1)


base.fetch_bytes = bounded_fetch


def capture_with_official_archive_fallback(target):
    if target.get("route") != "publication_pdf" or not target.get("fallback_urls"):
        return _ORIGINAL_CAPTURE(target)

    try:
        return _ORIGINAL_CAPTURE(target)
    except Exception as primary_exc:
        primary_error = repr(primary_exc)

    sid = target["source_id"]
    publication_id = target["value"]
    errors = []
    for candidate in target.get("fallback_urls", []):
        try:
            pdf, headers, final_url = base.fetch_bytes(candidate, timeout=25, attempts=1)
            if not pdf.startswith(b"%PDF-"):
                raise RuntimeError("configured official archive fallback is not a PDF")
            artifact, sha = base.write_immutable(sid, publication_id, pdf, ".pdf")
            mime = (headers.get("content-type") or "application/pdf").split(";", 1)[0].strip().lower()
            if mime in {"application/octet-stream", "binary/octet-stream"}:
                mime = "application/pdf"
            retrieved = base.dt.datetime.now(base.dt.timezone.utc).isoformat().replace("+00:00", "Z")
            return {
                "schema_version": "1.1",
                "source_id": sid,
                "capture_kind": "publication_pdf_official_archive_fallback",
                "official_publication_id": publication_id,
                "configured_primary_route_failed": True,
                "configured_primary_error": primary_error,
                "source_url": final_url,
                "retrieved_at": retrieved,
                "mime": mime,
                "byte_length": len(pdf),
                "sha256": sha,
                "artifact_ref": str(artifact.relative_to(base.ROOT)).replace("\\", "/"),
                "source_record_ref": str(target["path"].relative_to(base.ROOT)).replace("\\", "/"),
                "proof": {
                    "official_route": True,
                    "official_archive_fallback": True,
                    "pdf_signature_ok": True,
                    "sha256_calculated_from_downloaded_bytes": True,
                },
                "semantic_status_unchanged": True,
            }
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")

    raise RuntimeError(
        f"primary publication route failed: {primary_error}; official archive fallbacks failed: "
        + "; ".join(errors)
    )


base.capture = capture_with_official_archive_fallback

if __name__ == "__main__":
    raise SystemExit(base.main())
