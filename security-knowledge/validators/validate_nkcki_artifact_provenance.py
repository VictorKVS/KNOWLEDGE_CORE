from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "provenance" / "nkcki-2026-artifact-provenance-regression-v1.yaml"
MANIFEST = ROOT / "security-knowledge" / "provenance" / "nkcki-2026-artifact-acquisition-manifest-v1.yaml"
RECEIPT = ROOT / "security-knowledge" / "evidence" / "nkcki-2026-official-origin-acquisition-receipt.json"
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def evaluate(case_input: dict) -> str:
    requested_status = case_input.get("requested_status")
    requested_assertion = case_input.get("requested_assertion")
    source_kind = case_input.get("source_kind")

    if requested_assertion == "FIELD_LEVEL_SCHEMA_COMPLETE":
        if not case_input.get("bytes_preserved"):
            return "BLOCK_FIELD_LEVEL_COMPLETENESS"

    if requested_status == "PRIMARY_WEB_OPERATIONAL_GUIDANCE":
        if source_kind == "DYNAMIC_OFFICIAL_WEB_FORM":
            return (
                "ALLOW_TIME_BOUNDED_WEB_OBSERVATION"
                if case_input.get("observed_at")
                else "REQUIRE_OBSERVATION_TIME"
            )

    if requested_status == "IMMUTABLE_PRIMARY":
        if source_kind in {
            "SEARCH_ENGINE_EXCERPT",
            "THIRD_PARTY_MIRROR",
            "DOCUMENT_VIEWER_DERIVATIVE",
        }:
            return "BLOCK_IMMUTABLE_PRIMARY"
        if not case_input.get("bytes_preserved"):
            return "BLOCK_IMMUTABLE_PRIMARY"
        sha = case_input.get("sha256")
        if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
            return "BLOCK_IMMUTABLE_PRIMARY"
        if not case_input.get("retrieved_at"):
            return "BLOCK_IMMUTABLE_PRIMARY"
        return "ALLOW_IMMUTABLE_PRIMARY"

    return "UNHANDLED"


def main() -> int:
    data = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    failures = []
    for case in data.get("cases", []):
        actual = evaluate(case.get("input", {}))
        expected = case.get("expected")
        if actual != expected:
            failures.append((case.get("id"), expected, actual))

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "PRIMARY_ARTIFACTS_IMMUTABLE":
        failures.append(("MANIFEST-STATUS", "PRIMARY_ARTIFACTS_IMMUTABLE", manifest.get("status")))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    receipt_by_id = {item.get("logical_id"): item for item in receipt.get("artifacts", [])}
    logical_ids = {
        "NKTSKI-2026-ORDER-2": "NKTSKI-ORDER-2-2026-07-14",
        "NKTSKI-2026-ATTACK-TYPE-INITIAL-DATA": "NKTSKI-ATTACK-TYPE-INITIAL-DATA-2026-07-08",
    }
    for artifact in manifest.get("artifacts", [])[:2]:
        artifact_id = artifact.get("artifact_id")
        for key in ("authoritative_download_url", "authoritative_gossopka_download_url"):
            value = artifact.get(key)
            if not isinstance(value, str) or not value.startswith("https://") or not value.endswith(".pdf"):
                failures.append((f"{artifact_id}-{key}", "exact official PDF URL", value))
        if artifact.get("exact_download_target_resolved") is not True:
            failures.append((f"{artifact_id}-href", True, artifact.get("exact_download_target_resolved")))
        if artifact.get("bytes_preserved") is not True or artifact.get("immutable_status") != "IMMUTABLE_PRIMARY":
            failures.append((f"{artifact_id}-immutable", "bytes=true/status=IMMUTABLE_PRIMARY", artifact))
        path_value = artifact.get("repository_path")
        path = ROOT / path_value if isinstance(path_value, str) else None
        if path is None or not path.is_file():
            failures.append((f"{artifact_id}-path", "existing repository artifact", path_value))
        else:
            payload = path.read_bytes()
            observed_sha = hashlib.sha256(payload).hexdigest()
            observed_bytes = len(payload)
            if payload[:5] != b"%PDF-":
                failures.append((f"{artifact_id}-magic", "%PDF-", payload[:5]))
            if observed_sha != artifact.get("sha256"):
                failures.append((f"{artifact_id}-sha", artifact.get("sha256"), observed_sha))
            if observed_bytes != artifact.get("bytes"):
                failures.append((f"{artifact_id}-bytes", artifact.get("bytes"), observed_bytes))
            receipt_item = receipt_by_id.get(logical_ids.get(artifact_id))
            if not receipt_item:
                failures.append((f"{artifact_id}-receipt", "matching receipt entry", None))
            else:
                if receipt_item.get("sha256") != observed_sha:
                    failures.append((f"{artifact_id}-receipt-sha", observed_sha, receipt_item.get("sha256")))
                if receipt_item.get("bytes") != observed_bytes:
                    failures.append((f"{artifact_id}-receipt-bytes", observed_bytes, receipt_item.get("bytes")))
                allowed_urls = {
                    artifact.get("authoritative_download_url"),
                    artifact.get("authoritative_gossopka_download_url"),
                }
                if receipt_item.get("effective_url") not in allowed_urls:
                    failures.append((f"{artifact_id}-receipt-url", sorted(allowed_urls), receipt_item.get("effective_url")))
                if receipt_item.get("content_type") != "application/pdf":
                    failures.append((f"{artifact_id}-receipt-mime", "application/pdf", receipt_item.get("content_type")))
                if receipt_item.get("tls", {}).get("verification") != "OPENSSL_CA_CHAIN_AND_HOSTNAME":
                    failures.append((f"{artifact_id}-receipt-tls", "OPENSSL_CA_CHAIN_AND_HOSTNAME", receipt_item.get("tls")))
        if not artifact.get("retrieved_at"):
            failures.append((f"{artifact_id}-retrieved-at", "non-empty retrieval timestamp", artifact.get("retrieved_at")))
        render = artifact.get("non_primary_render_observation", {})
        render_sha = render.get("sha256") or render.get("sha256_from_each_origin")
        if not isinstance(render_sha, str) or not SHA256_RE.fullmatch(render_sha):
            failures.append((f"{artifact_id}-render-sha", "valid derivative SHA-256", render_sha))
        if render.get("byte_fidelity_to_official_origin") != "UNPROVEN":
            failures.append((f"{artifact_id}-render-fidelity", "UNPROVEN", render.get("byte_fidelity_to_official_origin")))
        if render.get("immutable_primary_effect") != "NONE":
            failures.append((f"{artifact_id}-render-effect", "NONE", render.get("immutable_primary_effect")))

    if failures:
        for case_id, expected, actual in failures:
            print(f"FAIL {case_id}: expected={expected} actual={actual}")
        return 1

    print(f"PASS: {len(data.get('cases', []))} NKTsKI provenance cases plus two immutable official-origin artifacts and receipt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
