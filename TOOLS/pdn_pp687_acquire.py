#!/usr/bin/env python3
"""Guarded curl acquisition for PP RF No. 687 official canonical capture.

The primary Government portal route can time out from GitHub-hosted runners. This
helper therefore tries only routes pre-registered in the PP687 source record:
1) the Government canonical page;
2) the official pravo.gov.ru IPS route, when registered as a fallback.

No response is accepted merely because the host is official. Returned bytes must
contain strong PP-687/personal-data identity markers before an immutable artifact and
manifest are written. The helper never promotes semantic/extraction status.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "security-corpora" / "RU" / "152-FZ"
SOURCE_ID = "SEC-SRC-RU-PP687-2008"
SOURCE_RECORD = CORPUS / "source" / f"{SOURCE_ID}.yaml"
RAW_DIR = CORPUS / "raw" / SOURCE_ID
MANIFEST_DIR = CORPUS / "manifests"
RUN_FILE = CORPUS / "PDN_ACQUISITION_RUN.json"
UA = "KNOWLEDGE_CORE-pdn-pp687-curl/1.1 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"

CANONICAL_URL_RE = re.compile(r'^  url:\s*["\']([^"\']+)["\']\s*$', re.M)
OFFICIAL_IPS_URL_RE = re.compile(
    r'url:\s*["\'](https?://pravo\.gov\.ru/proxy/ips/\?[^"\']*nd=102124251[^"\']*)["\']'
)
STATUS_RE = re.compile(r"^status:\s*([^\s#]+)\s*$", re.M)
IDENTITY_GROUPS = (
    ("постановление правительства российской федерации", "правительство российской федерации"),
    ("№ 687", "№687", " 687 "),
    ("персональных данных",),
    ("без использования средств автоматизации",),
)


def top_level_section(text: str, name: str) -> str:
    start = re.search(rf"(?m)^{re.escape(name)}:\s*$", text)
    if not start:
        return ""
    tail = text[start.end():]
    nxt = re.search(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$", tail)
    end = start.end() + (nxt.start() if nxt else len(tail))
    return text[start.end():end]


def decode_identity(data: bytes) -> str:
    texts: list[str] = []
    for enc in ("utf-8", "cp1251"):
        try:
            texts.append(data.decode(enc))
        except UnicodeDecodeError:
            texts.append(data.decode(enc, errors="ignore"))
    text = "\n".join(texts).lower().replace("\xa0", " ")
    return re.sub(r"\s+", " ", text)


def identity_ok(data: bytes) -> tuple[bool, list[str]]:
    text = decode_identity(data)
    matched: list[str] = []
    for group in IDENTITY_GROUPS:
        marker = next((m for m in group if m in text), "")
        if not marker:
            return False, matched
        matched.append(marker)
    return True, matched


def curl_capture(url: str) -> tuple[bytes, str, str]:
    with tempfile.TemporaryDirectory(prefix="pdn-pp687-") as td:
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
            raise RuntimeError("empty official response")
        lines = (proc.stdout or "").splitlines()
        final_url = lines[0].strip() if lines else url
        mime = lines[1].strip().split(";", 1)[0] if len(lines) > 1 else "application/octet-stream"
        return data, final_url, mime or "application/octet-stream"


def write_immutable(data: bytes) -> tuple[Path, str]:
    sha = hashlib.sha256(data).hexdigest()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".html" if data.lstrip().lower().startswith((b"<!doctype html", b"<html")) else ".bin"
    artifact = RAW_DIR / f"official-snapshot-{sha[:16]}{ext}"
    if artifact.exists():
        existing = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if existing != sha:
            raise RuntimeError(f"immutable collision: existing={existing}, incoming={sha}")
    else:
        artifact.write_bytes(data)
    return artifact, sha


def reconcile_run(manifest: dict[str, object]) -> None:
    if not RUN_FILE.exists():
        return
    run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
    results = run.get("results", [])
    changed = False
    for row in results:
        if row.get("source_id") != SOURCE_ID:
            continue
        row.clear()
        row.update({
            "source_id": SOURCE_ID,
            "route": manifest["accepted_registered_route"],
            "source_document_number": "687",
            "status": "IMMUTABLE_CAPTURED",
            "byte_length": manifest["byte_length"],
            "sha256": manifest["sha256"],
            "mime": manifest["mime"],
            "artifact_ref": manifest["artifact_ref"],
            "manifest_ref": f"security-corpora/RU/152-FZ/manifests/{SOURCE_ID}.json",
        })
        changed = True
        break
    if not changed:
        return
    ok = sum(1 for row in results if row.get("status") == "IMMUTABLE_CAPTURED")
    run["raw_downloaded_exact"] = ok
    run["immutable_sha256_verified"] = ok
    run["pending"] = len(results) - ok
    run["postprocess_transport_fallback"] = {
        "source_id": SOURCE_ID,
        "transport": "curl_ipv4_guarded_registered_routes",
        "accepted": True,
        "accepted_registered_route": manifest["accepted_registered_route"],
        "semantic_status_unchanged": True,
    }
    RUN_FILE.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def registered_routes(source_text: str) -> list[tuple[str, str]]:
    canonical = top_level_section(source_text, "canonical_source")
    murl = CANONICAL_URL_RE.search(canonical)
    if not murl:
        raise RuntimeError("refuse PP687 capture: no registered canonical_source.url")
    routes: list[tuple[str, str]] = [("government_canonical", murl.group(1))]
    mips = OFFICIAL_IPS_URL_RE.search(canonical)
    if mips and mips.group(1) != murl.group(1):
        routes.append(("pravo_ips_registered_fallback", mips.group(1)))
    return routes


def main() -> int:
    text = SOURCE_RECORD.read_text(encoding="utf-8")
    status = STATUS_RE.search(text)
    if not status or status.group(1) != "METADATA_VERIFIED":
        raise RuntimeError(f"refuse PP687 capture: source status is not METADATA_VERIFIED for {SOURCE_ID}")

    routes = registered_routes(text)
    errors: list[str] = []
    accepted_route = ""
    accepted_source_url = ""
    data = b""
    final_url = ""
    mime = "application/octet-stream"
    markers: list[str] = []

    for route_name, route_url in routes:
        try:
            candidate, candidate_final_url, candidate_mime = curl_capture(route_url)
            ok, candidate_markers = identity_ok(candidate)
            if not ok:
                raise RuntimeError("official response lacks required PP687/personal-data identity markers")
            accepted_route = route_name
            accepted_source_url = route_url
            data = candidate
            final_url = candidate_final_url
            mime = candidate_mime
            markers = candidate_markers
            break
        except Exception as exc:
            errors.append(f"{route_name}: {exc}")

    if not data:
        raise RuntimeError("all registered official PP687 routes failed: " + " | ".join(errors))

    artifact, sha = write_immutable(data)
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    manifest: dict[str, object] = {
        "schema_version": "1.4",
        "source_id": SOURCE_ID,
        "source_document_number": "687",
        "capture_kind": "official_registered_route_snapshot",
        "accepted_registered_route": accepted_route,
        "official_file_url": final_url,
        "source_url": accepted_source_url,
        "registered_primary_source_url": routes[0][1],
        "registered_route_count": len(routes),
        "retrieved_at": retrieved,
        "mime": mime,
        "byte_length": len(data),
        "sha256": sha,
        "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
        "source_record_ref": str(SOURCE_RECORD.relative_to(ROOT)).replace("\\", "/"),
        "capture_policy": "registered-official-route-curl-with-pp687-content-identity-markers",
        "proof": {
            "official_route": True,
            "registered_route_used": True,
            "byte_exact_download": True,
            "sha256_calculated_from_downloaded_bytes": True,
            "publication_api_length_check_not_applicable": True,
            "canonical_content_identity_markers_ok": True,
            "canonical_content_identity_markers": markers,
            "semantic_status_unchanged": True,
        },
        "failed_routes_before_acceptance": errors,
        "semantic_status_unchanged": True,
        "review_note": "Capture proves exact bytes returned by a pre-registered official route and PP687 identity markers only; semantic/version-locator review remains required.",
    }
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    (MANIFEST_DIR / f"{SOURCE_ID}.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    reconcile_run(manifest)
    print(json.dumps({
        "source_id": SOURCE_ID,
        "status": "IMMUTABLE_CAPTURED_RAW_ONLY",
        "accepted_registered_route": accepted_route,
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
