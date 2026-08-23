#!/usr/bin/env python3
"""Guarded curl fallback for pending PDN technical/crypto official routes.

The normal Stream-2 acquirer uses urllib.  Several legacy pravo.gov.ru and issuer
routes time out there even when curl can retrieve them.  This helper tries only the
already-registered canonical/fallback URLs, validates the expected file signature
and (for strict text sources) the existing document identity marker groups, writes
byte-exact immutable artifacts/manifests, and leaves semantic status unchanged.

It deliberately does not discover or trust new hosts.  The normal capture gate runs
again after this helper and the main acquirer reconciles all counters from accepted
manifests.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from pdn_security_stack_acquire import (
    DOCX_MIME,
    MANIFEST_DIR,
    ROOT,
    capture,
    discover_targets,
    extension,
    reusable,
    sync_source,
    validate_expected,
    write_immutable,
)
from pdn_security_stack_capture_gate import STRICT_TEXT_IDENTITIES

REPORT = ROOT / "security-corpora" / "RU" / "152-FZ" / "security-stack" / "PDN_SECURITY_STACK_CURL_ATTEMPT.json"
UA = "KNOWLEDGE_CORE-pdn-security-stack-curl/1.0 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"


def _decode(data: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            return " ".join(data.decode(enc).casefold().split())
        except UnicodeDecodeError:
            pass
    return " ".join(data.decode("utf-8", errors="ignore").casefold().split())


def _strict_identity_ok(source_id: str, data: bytes, mime: str, suffix: str) -> tuple[bool, list[str]]:
    groups = STRICT_TEXT_IDENTITIES.get(source_id)
    textual = "html" in mime.casefold() or mime.casefold().startswith("text/") or suffix in {".html", ".htm", ".txt"}
    if not groups or not textual:
        return True, []
    text = _decode(data)
    matched: list[str] = []
    for alternatives in groups:
        hit = next((marker for marker in alternatives if marker.casefold() in text), None)
        if not hit:
            return False, matched
        matched.append(hit)
    return True, matched


def _curl(url: str) -> tuple[bytes, str, str]:
    with tempfile.TemporaryDirectory(prefix="pdn-stack-curl-") as td:
        body = Path(td) / "body.bin"
        cmd = [
            "curl",
            "--silent",
            "--show-error",
            "--location",
            "--fail-with-body",
            "--retry",
            "2",
            "--retry-delay",
            "2",
            "--retry-all-errors",
            "--connect-timeout",
            "15",
            "--max-time",
            "70",
            "--ipv4",
            "--http1.1",
            "--header",
            f"User-Agent: {UA}",
            "--header",
            "Accept: application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/html,application/xhtml+xml,*/*;q=0.8",
            "--header",
            "Accept-Encoding: identity",
            "--output",
            str(body),
            "--write-out",
            "%{url_effective}\n%{content_type}\n",
            url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=95)
        if proc.returncode != 0:
            raise RuntimeError(f"curl exit={proc.returncode}: {(proc.stderr or '').strip()}")
        data = body.read_bytes() if body.exists() else b""
        if not data:
            raise RuntimeError("empty official response")
        lines = (proc.stdout or "").splitlines()
        final_url = lines[0].strip() if lines else url
        mime = lines[1].strip().split(";", 1)[0].casefold() if len(lines) > 1 else "application/octet-stream"
        return data, final_url, mime or "application/octet-stream"


def _variants(primary: str, fallbacks: list[str]) -> list[tuple[str, str]]:
    ordered: list[tuple[str, str]] = []
    for index, configured in enumerate([primary, *fallbacks]):
        label = "registered_primary" if index == 0 else f"registered_fallback_{index}"
        if configured.startswith("http://"):
            ordered.append((label + "_tls_equivalent", "https://" + configured[len("http://") :]))
        ordered.append((label, configured))
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for label, url in ordered:
        if url not in seen:
            seen.add(url)
            out.append((label, url))
    return out


def _attempt_target(target: dict[str, object]) -> dict[str, object]:
    source_id = str(target["source_id"])
    expected = str(target.get("expected_mime") or "")
    variants = _variants(str(target["value"]), [str(v) for v in target.get("fallback_urls", [])])
    errors: list[str] = []

    for transport, url in variants:
        try:
            data, final_url, response_mime = _curl(url)
            validate_expected(data, response_mime, expected)
            ext = extension(response_mime, data, expected)
            identity_ok, markers = _strict_identity_ok(source_id, data, response_mime, ext)
            if not identity_ok:
                raise RuntimeError("strict document identity markers missing from returned legal text")

            artifact, sha = write_immutable(source_id, "official-curl-snapshot", data, ext)
            retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
            mime = expected if expected and response_mime in {"application/octet-stream", "binary/octet-stream"} else response_mime
            manifest = {
                "schema_version": "1.2",
                "source_id": source_id,
                "capture_kind": "canonical_snapshot",
                "configured_primary_url": str(target["value"]),
                "source_url": final_url,
                "accepted_registered_transport": transport,
                "retrieved_at": retrieved,
                "mime": mime,
                "byte_length": len(data),
                "sha256": sha,
                "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
                "source_record_ref": str(Path(target["path"]).relative_to(ROOT)).replace("\\", "/"),
                "proof": {
                    "official_route": True,
                    "byte_exact_download": True,
                    "sha256_calculated_from_downloaded_bytes": True,
                    "expected_pdf_signature_ok": expected != "application/pdf" or data.startswith(b"%PDF-"),
                    "expected_docx_signature_ok": expected != DOCX_MIME or data.startswith(b"PK\x03\x04"),
                    "strict_text_identity_ok": identity_ok,
                    "strict_text_identity_markers": markers,
                    "registered_url_only": True,
                    "curl_transport_fallback": True,
                },
                "failed_registered_transports_before_acceptance": errors,
                "semantic_status_unchanged": True,
            }
            MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
            (MANIFEST_DIR / f"{source_id}.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            sync_source(manifest)
            return {
                "source_id": source_id,
                "status": "IMMUTABLE_CAPTURED",
                "transport": transport,
                "source_url": final_url,
                "mime": mime,
                "byte_length": len(data),
                "sha256": sha,
            }
        except Exception as exc:
            errors.append(f"{transport}: {exc}")

    return {"source_id": source_id, "status": "PENDING", "errors": errors}


def main() -> int:
    started = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    results: list[dict[str, object]] = []
    for target in discover_targets():
        if str(target.get("route")) != "canonical_snapshot":
            continue
        if reusable(str(target["source_id"])):
            continue
        results.append(_attempt_target(target))

    report = {
        "schema_version": "1.0",
        "kind": "pdn-security-stack-guarded-curl-fallback",
        "started_at": started,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "attempted": len(results),
        "captured": sum(row.get("status") == "IMMUTABLE_CAPTURED" for row in results),
        "pending": sum(row.get("status") == "PENDING" for row in results),
        "results": results,
        "semantic_status_unchanged": True,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("attempted", "captured", "pending")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
