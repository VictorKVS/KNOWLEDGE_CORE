#!/usr/bin/env python3
"""Guarded acquisition for the current PP RF No. 687 consolidated text.

Only official routes pre-registered in the PP687 source card are eligible. A transport
response is not accepted merely because it contains PP687: it must prove both document
identity and the current revision effective 26.01.2025. PP RF No. 12 changed clause 3 by
adding the validity limit through 01.09.2030, so that phrase is used as a revision-specific
content fingerprint. This prevents an old 2008 IPS rendering from being captured as the
current consolidated text.

Returned bytes are stored unchanged and SHA-256 is calculated from those exact bytes.
Transport/profile fallback never promotes semantic or extraction status.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "security-corpora" / "RU" / "152-FZ"
SOURCE_ID = "SEC-SRC-RU-PP687-2008"
SOURCE_RECORD = CORPUS / "source" / f"{SOURCE_ID}.yaml"
RAW_DIR = CORPUS / "raw" / SOURCE_ID
MANIFEST_DIR = CORPUS / "manifests"
RUN_FILE = CORPUS / "PDN_ACQUISITION_RUN.json"
UA = "KNOWLEDGE_CORE-pdn-pp687-curl/1.6 (+https://github.com/VictorKVS/KNOWLEDGE_CORE)"
CURRENT_REVISION_SOURCE = "PP RF No. 12 of 18.01.2025"
CURRENT_REVISION_EFFECTIVE_FROM = "2025-01-26"
CURRENT_VALID_UNTIL = "2030-09-01"

CANONICAL_URL_RE = re.compile(r'^  url:\s*["\']([^"\']+)["\']\s*$', re.M)
OFFICIAL_IPS_URL_RE = re.compile(
    r'url:\s*["\'](https?://(?:www\.)?pravo\.gov\.ru/proxy/ips/\?[^"\']*nd=102124251[^"\']*)["\']',
    re.I,
)
STATUS_RE = re.compile(r"^status:\s*([^\s#]+)\s*$", re.M)
IDENTITY_PATTERNS = (
    ("government_issuer", re.compile(r"(?:постановление\s+)?правительства\s+российской\s+федерации")),
    ("document_number_687", re.compile(r"(?:№|n|no\.?|номер)?\s*687(?:\D|$)")),
    ("personal_data", re.compile(r"персональн\w*\s+данн\w*")),
    ("non_automated_processing", re.compile(r"без\s+использования\s+средств\s+автоматизац\w*")),
)
CURRENT_REVISION_PATTERNS = (
    (
        "valid_until_2030_09_01",
        re.compile(r"действует\s+до\s+1\s+сентября\s+2030\s*(?:г\.?|года)?"),
    ),
)
NETWORK_PROFILES = (
    ("ipv4_http11", ("--ipv4", "--http1.1")),
    ("default_stack", ()),
)


def top_level_section(text: str, name: str) -> str:
    start = re.search(rf"(?m)^{re.escape(name)}:\s*$", text)
    if not start:
        return ""
    tail = text[start.end():]
    nxt = re.search(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$", tail)
    end = start.end() + (nxt.start() if nxt else len(tail))
    return text[start.end():end]


def normalize_identity_text(text: str) -> str:
    """Normalize inspection text only; immutable raw bytes remain untouched."""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans({"\xa0": " ", "‑": "-", "–": "-", "—": "-", "−": "-"}))
    return re.sub(r"\s+", " ", text.lower()).strip()


def decode_identity(data: bytes) -> str:
    texts: list[str] = []
    for enc in ("utf-8", "cp1251"):
        try:
            texts.append(data.decode(enc))
        except UnicodeDecodeError:
            texts.append(data.decode(enc, errors="ignore"))
    return normalize_identity_text("\n".join(texts))


def identity_ok(data: bytes) -> tuple[bool, list[str]]:
    """Require PP687 identity plus the PP12 current-revision fingerprint."""
    text = decode_identity(data)
    matched: list[str] = []
    for label, pattern in IDENTITY_PATTERNS:
        hit = pattern.search(text)
        if not hit:
            return False, matched
        matched.append(f"{label}:{hit.group(0)}")
    for label, pattern in CURRENT_REVISION_PATTERNS:
        hit = pattern.search(text)
        if not hit:
            return False, matched
        matched.append(f"current_revision_{label}:{hit.group(0)}")
    return True, matched


def curl_capture(url: str, network_args: tuple[str, ...]) -> tuple[bytes, str, str]:
    with tempfile.TemporaryDirectory(prefix="pdn-pp687-") as td:
        body = Path(td) / "body.bin"
        cmd = [
            "curl", "--silent", "--show-error", "--location", "--fail-with-body",
            "--retry", "2", "--retry-delay", "2", "--retry-all-errors",
            "--connect-timeout", "20", "--max-time", "120",
            *network_args,
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


def registered_sources(source_text: str) -> tuple[str, list[tuple[str, str, str]]]:
    """Enumerate every pre-registered PP687 IPS route plus the canonical Government page."""
    canonical = top_level_section(source_text, "canonical_source")
    murl = CANONICAL_URL_RE.search(canonical)
    if not murl:
        raise RuntimeError("refuse PP687 capture: no registered canonical_source.url")
    government_url = murl.group(1)
    routes: list[tuple[str, str, str]] = []
    ips_urls: list[str] = []
    for match in OFFICIAL_IPS_URL_RE.finditer(canonical):
        url = match.group(1)
        if url not in ips_urls:
            ips_urls.append(url)
    for index, ips in enumerate(ips_urls, start=1):
        if ips.startswith("http://"):
            routes.append((f"pravo_ips_registered_{index}_tls_equivalent", "https://" + ips[len("http://"):], ips))
        routes.append((f"pravo_ips_registered_{index}", ips, ips))
    routes.append(("government_canonical", government_url, government_url))

    out: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for name, transport_url, registered_url in routes:
        key = (transport_url, registered_url)
        if key not in seen:
            out.append((name, transport_url, registered_url))
            seen.add(key)
    return government_url, out


def transport_attempts(routes: list[tuple[str, str, str]]) -> list[tuple[str, str, str, str, str, tuple[str, ...]]]:
    attempts: list[tuple[str, str, str, str, str, tuple[str, ...]]] = []
    for route_name, transport_url, registered_url in routes:
        for profile_name, profile_args in NETWORK_PROFILES:
            attempts.append((f"{route_name}:{profile_name}", route_name, transport_url, registered_url, profile_name, profile_args))
    return attempts


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
            "network_profile": manifest["accepted_network_profile"],
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
    if changed:
        ok = sum(1 for row in results if row.get("status") == "IMMUTABLE_CAPTURED")
        run["raw_downloaded_exact"] = ok
        run["immutable_sha256_verified"] = ok
        run["pending"] = len(results) - ok
        run["postprocess_transport_fallback"] = {
            "source_id": SOURCE_ID,
            "transport": "curl_registered_routes_multi_network_profile_current_revision_guarded",
            "accepted": True,
            "accepted_registered_route": manifest["accepted_registered_route"],
            "accepted_network_profile": manifest["accepted_network_profile"],
            "semantic_status_unchanged": True,
        }
        RUN_FILE.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    text = SOURCE_RECORD.read_text(encoding="utf-8")
    status = STATUS_RE.search(text)
    if not status or status.group(1) != "METADATA_VERIFIED":
        raise RuntimeError(f"refuse PP687 capture: source status is not METADATA_VERIFIED for {SOURCE_ID}")

    government_url, routes = registered_sources(text)
    attempts = transport_attempts(routes)
    errors: list[str] = []
    accepted_route = accepted_transport = accepted_registered_url = accepted_transport_url = ""
    accepted_network_profile = final_url = ""
    data = b""
    mime = "application/octet-stream"
    markers: list[str] = []

    for attempt_label, route_name, transport_url, registered_url, profile_name, profile_args in attempts:
        try:
            candidate, candidate_final_url, candidate_mime = curl_capture(transport_url, profile_args)
            ok, candidate_markers = identity_ok(candidate)
            if not ok:
                raise RuntimeError("official response lacks required PP687 identity/current-revision markers")
            accepted_route = route_name
            accepted_transport = attempt_label
            accepted_registered_url = registered_url
            accepted_transport_url = transport_url
            accepted_network_profile = profile_name
            data = candidate
            final_url = candidate_final_url
            mime = candidate_mime
            markers = candidate_markers
            break
        except Exception as exc:
            errors.append(f"{attempt_label}: {exc}")

    if not data:
        raise RuntimeError("all registered official PP687 transports failed: " + " | ".join(errors))

    artifact, sha = write_immutable(data)
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    registered_urls = list(dict.fromkeys(registered_url for _, _, registered_url in routes))
    manifest: dict[str, object] = {
        "schema_version": "1.9",
        "source_id": SOURCE_ID,
        "source_document_number": "687",
        "capture_kind": "official_registered_route_snapshot",
        "accepted_registered_route": accepted_route,
        "accepted_transport": accepted_transport,
        "accepted_network_profile": accepted_network_profile,
        "accepted_registered_source_url": accepted_registered_url,
        "official_file_url": final_url,
        "source_url": accepted_transport_url,
        "registered_primary_source_url": government_url,
        "registered_source_urls": registered_urls,
        "registered_route_count": len(registered_urls),
        "transport_attempt_order": [label for label, *_ in attempts],
        "network_profiles": [name for name, _ in NETWORK_PROFILES],
        "retrieved_at": retrieved,
        "mime": mime,
        "byte_length": len(data),
        "sha256": sha,
        "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
        "source_record_ref": str(SOURCE_RECORD.relative_to(ROOT)).replace("\\", "/"),
        "capture_policy": "registered-official-route-curl-with-pp687-identity-and-pp12-current-revision-fingerprint",
        "proof": {
            "official_route": True,
            "registered_route_used": True,
            "registered_source_identity_preserved_across_network_profiles": True,
            "byte_exact_download": True,
            "sha256_calculated_from_downloaded_bytes": True,
            "publication_api_length_check_not_applicable": True,
            "canonical_content_identity_markers_ok": True,
            "canonical_content_identity_markers": markers,
            "current_revision_marker_ok": True,
            "current_revision_source": CURRENT_REVISION_SOURCE,
            "current_revision_effective_from": CURRENT_REVISION_EFFECTIVE_FROM,
            "current_valid_until": CURRENT_VALID_UNTIL,
            "identity_view_html_entities_unescaped": True,
            "identity_view_unicode_nfkc_normalized": True,
            "identity_view_html_tags_collapsed": True,
            "raw_bytes_unchanged_by_identity_normalization": True,
            "semantic_status_unchanged": True,
        },
        "failed_routes_before_acceptance": errors,
        "semantic_status_unchanged": True,
        "review_note": "Capture proves exact bytes from a registered official PP687 route plus the PP12 current-revision fingerprint (valid through 01.09.2030). Locator review remains required before extraction promotion.",
    }
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    (MANIFEST_DIR / f"{SOURCE_ID}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reconcile_run(manifest)
    print(json.dumps({
        "source_id": SOURCE_ID,
        "status": "IMMUTABLE_CAPTURED_RAW_ONLY",
        "accepted_registered_route": accepted_route,
        "accepted_network_profile": accepted_network_profile,
        "accepted_registered_source_url": accepted_registered_url,
        "mime": mime,
        "byte_length": len(data),
        "sha256": sha,
        "artifact_ref": manifest["artifact_ref"],
        "identity_and_current_revision_markers": markers,
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
