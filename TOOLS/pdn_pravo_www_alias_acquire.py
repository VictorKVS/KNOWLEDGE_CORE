#!/usr/bin/env python3
"""Guarded www.pravo.gov.ru transport fallback for the two remaining PDN-core gaps.

The official source identities are already registered as pravo.gov.ru IPS routes in the
source cards. This helper does not register a new legal source: it only tries the `www`
host alias of the same official portal over HTTPS. The accepted manifest remains bound
to the pre-registered source URL, while `source_url` records the transport alias actually
used. No response is accepted without the existing PP687 or current-152-FZ content gates.
Exact returned bytes are stored unchanged and SHA-256 is calculated from those bytes.
Semantic/extraction status is never promoted here.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import pdn_pp687_acquire as pp
import pdn_current_root_curl_acquire as cr
from pdn_core_acquire import DOC_NUMBER_RE, ROOT, top_level_section
from pdn_current_root_acquire import (
    CURRENT_REVISION_EFFECTIVE_FROM,
    CURRENT_REVISION_TRIGGER,
    METADATA_STATUS_RE,
    SOURCE_ID as CURRENT_ROOT_ID,
    SOURCE_RECORD as CURRENT_ROOT_RECORD,
)


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def www_tls_alias(registered_url: str) -> str:
    parts = urlsplit(registered_url)
    host = (parts.hostname or "").lower()
    if host not in {"pravo.gov.ru", "www.pravo.gov.ru"}:
        raise RuntimeError(f"refuse transport alias for non-pravo host: {host}")
    port = f":{parts.port}" if parts.port else ""
    return urlunsplit(("https", "www.pravo.gov.ru" + port, parts.path, parts.query, parts.fragment))


def pp687_attempt() -> dict[str, object]:
    manifest_path = pp.MANIFEST_DIR / f"{pp.SOURCE_ID}.json"
    if manifest_path.exists():
        return {"source_id": pp.SOURCE_ID, "status": "ALREADY_CAPTURED"}

    text = pp.SOURCE_RECORD.read_text(encoding="utf-8")
    status = pp.STATUS_RE.search(text)
    if not status or status.group(1) != "METADATA_VERIFIED":
        raise RuntimeError("PP687 source status is not METADATA_VERIFIED")

    government_url, routes = pp.registered_sources(text)
    registered_ips = next(
        (registered for _, _, registered in routes if "pravo.gov.ru/proxy/ips/" in registered),
        "",
    )
    if not registered_ips:
        raise RuntimeError("no pre-registered PP687 pravo.gov.ru IPS route")
    alias = www_tls_alias(registered_ips)

    errors: list[str] = []
    for profile_name, profile_args in pp.NETWORK_PROFILES:
        try:
            data, final_url, mime = pp.curl_capture(alias, profile_args)
            ok, markers = pp.identity_ok(data)
            if not ok:
                raise RuntimeError("official www.pravo response lacks required PP687 identity markers")
            artifact, sha = pp.write_immutable(data)
            manifest: dict[str, object] = {
                "schema_version": "1.9",
                "source_id": pp.SOURCE_ID,
                "source_document_number": "687",
                "capture_kind": "official_registered_route_snapshot",
                "accepted_registered_route": "pravo_ips_registered_www_tls_transport_alias",
                "accepted_transport": f"www_tls_alias:{profile_name}",
                "accepted_network_profile": profile_name,
                "accepted_registered_source_url": registered_ips,
                "official_file_url": final_url,
                "source_url": alias,
                "registered_primary_source_url": government_url,
                "registered_source_urls": list(dict.fromkeys(r for _, _, r in routes)),
                "retrieved_at": utcnow(),
                "mime": mime,
                "byte_length": len(data),
                "sha256": sha,
                "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
                "source_record_ref": str(pp.SOURCE_RECORD.relative_to(ROOT)).replace("\\", "/"),
                "capture_policy": "pre-registered-pravo-source-identity-via-www-official-host-alias-with-pp687-content-gate",
                "proof": {
                    "official_route": True,
                    "registered_route_used": True,
                    "registered_source_identity_preserved_across_network_profiles": True,
                    "www_host_alias_transport_only": True,
                    "byte_exact_download": True,
                    "sha256_calculated_from_downloaded_bytes": True,
                    "publication_api_length_check_not_applicable": True,
                    "canonical_content_identity_markers_ok": True,
                    "canonical_content_identity_markers": markers,
                    "raw_bytes_unchanged_by_identity_normalization": True,
                    "semantic_status_unchanged": True,
                },
                "failed_profiles_before_acceptance": errors,
                "semantic_status_unchanged": True,
                "review_note": "The www host is a transport alias of the same official pravo.gov.ru portal; the legal source identity remains the pre-registered IPS URL. Locator review remains required before extraction promotion.",
            }
            pp.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return {
                "source_id": pp.SOURCE_ID,
                "status": "IMMUTABLE_CAPTURED_RAW_ONLY",
                "transport_alias": alias,
                "registered_source_url": registered_ips,
                "network_profile": profile_name,
                "mime": mime,
                "byte_length": len(data),
                "sha256": sha,
                "artifact_ref": manifest["artifact_ref"],
                "semantic_status_unchanged": True,
            }
        except Exception as exc:
            errors.append(f"{profile_name}: {exc}")
    return {
        "source_id": pp.SOURCE_ID,
        "status": "PENDING",
        "error": "www.pravo official-host alias failed: " + " | ".join(errors),
        "semantic_status_unchanged": True,
    }


def current_root_attempt() -> dict[str, object]:
    manifest_path = cr.MANIFEST_DIR / f"{CURRENT_ROOT_ID}.json"
    if manifest_path.exists():
        return {"source_id": CURRENT_ROOT_ID, "status": "ALREADY_CAPTURED"}

    text = CURRENT_ROOT_RECORD.read_text(encoding="utf-8")
    metadata = METADATA_STATUS_RE.search(text)
    if not metadata or metadata.group(1) != "VERSION_IDENTITY_CROSS_VERIFIED":
        raise RuntimeError("current 152-FZ metadata status is not VERSION_IDENTITY_CROSS_VERIFIED")

    document = top_level_section(text, "document")
    canonical = top_level_section(text, "canonical_source")
    registered_urls = cr.registered_urls(canonical)
    registered_ips = next((u for u in registered_urls if "pravo.gov.ru/proxy/ips/" in u), "")
    if not registered_ips:
        raise RuntimeError("no pre-registered current-root pravo.gov.ru IPS route")
    alias = www_tls_alias(registered_ips)
    number_match = DOC_NUMBER_RE.search(document)
    expected_number = number_match.group(1).strip() if number_match else "152-ФЗ"

    errors: list[str] = []
    for profile_name, profile_args in cr.NETWORK_PROFILES:
        try:
            data, final_url, mime = cr.curl_capture(alias, profile_args)
            ok, markers = cr.current_root_identity_ok(data)
            if not ok:
                raise RuntimeError("official www.pravo response lacks required 152-FZ/current-revision evidence")
            artifact, sha = cr.write_immutable(data)
            manifest: dict[str, object] = {
                "schema_version": "2.0",
                "source_id": CURRENT_ROOT_ID,
                "source_document_number": expected_number,
                "capture_kind": "official_canonical_snapshot",
                "accepted_transport": f"www_tls_alias:{profile_name}",
                "accepted_network_profile": profile_name,
                "accepted_registered_source_url": registered_ips,
                "source_url": alias,
                "official_file_url": final_url,
                "registered_source_urls": registered_urls,
                "retrieved_at": utcnow(),
                "mime": mime,
                "byte_length": len(data),
                "sha256": sha,
                "artifact_ref": str(artifact.relative_to(ROOT)).replace("\\", "/"),
                "source_record_ref": str(CURRENT_ROOT_RECORD.relative_to(ROOT)).replace("\\", "/"),
                "capture_policy": "pre-registered-pravo-current-root-via-www-official-host-alias-with-current-revision-content-gate",
                "proof": {
                    "official_route": True,
                    "official_route_pre_registered": True,
                    "www_host_alias_transport_only": True,
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
                    "network_profile_does_not_change_registered_source_identity": True,
                    "semantic_status_unchanged": True,
                },
                "failed_profiles_before_acceptance": errors,
                "semantic_status_unchanged": True,
                "review_note": "The www host is a transport alias of the same official pravo.gov.ru portal; accepted bytes still must prove the pinned 26.07.2026 revision. Locator/delta review remains required.",
            }
            cr.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return {
                "source_id": CURRENT_ROOT_ID,
                "status": "IMMUTABLE_CAPTURED_RAW_ONLY",
                "transport_alias": alias,
                "registered_source_url": registered_ips,
                "network_profile": profile_name,
                "mime": mime,
                "byte_length": len(data),
                "sha256": sha,
                "artifact_ref": manifest["artifact_ref"],
                "identity_and_revision_markers": markers,
                "semantic_status_unchanged": True,
            }
        except Exception as exc:
            errors.append(f"{profile_name}: {exc}")
    return {
        "source_id": CURRENT_ROOT_ID,
        "status": "PENDING",
        "error": "www.pravo official-host alias failed: " + " | ".join(errors),
        "semantic_status_unchanged": True,
    }


def main() -> int:
    results: list[dict[str, object]] = []
    for fn, source_id in ((pp687_attempt, pp.SOURCE_ID), (current_root_attempt, CURRENT_ROOT_ID)):
        try:
            results.append(fn())
        except Exception as exc:
            results.append({"source_id": source_id, "status": "PENDING", "error": str(exc), "semantic_status_unchanged": True})
    print(json.dumps({"kind": "pdn-pravo-www-transport-alias-attempt", "results": results}, ensure_ascii=False))
    return 0 if any(str(r.get("status", "")).startswith("IMMUTABLE_CAPTURED") for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
