from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "security-knowledge" / "provenance" / "nkcki-2026-artifact-provenance-regression-v1.yaml"
MANIFEST = ROOT / "security-knowledge" / "provenance" / "nkcki-2026-artifact-acquisition-manifest-v1.yaml"
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
    if manifest.get("status") != "PRIMARY_DOWNLOAD_TARGETS_RESOLVED_ORIGIN_BYTES_PENDING":
        failures.append(("MANIFEST-STATUS", "resolved targets with origin bytes pending", manifest.get("status")))
    for artifact in manifest.get("artifacts", [])[:2]:
        artifact_id = artifact.get("artifact_id")
        for key in ("authoritative_download_url", "authoritative_gossopka_download_url"):
            value = artifact.get(key)
            if not isinstance(value, str) or not value.startswith("https://") or not value.endswith(".pdf"):
                failures.append((f"{artifact_id}-{key}", "exact official PDF URL", value))
        if artifact.get("exact_download_target_resolved") is not True:
            failures.append((f"{artifact_id}-href", True, artifact.get("exact_download_target_resolved")))
        if artifact.get("bytes_preserved") is not False or artifact.get("immutable_status") != "PENDING":
            failures.append((f"{artifact_id}-fail-closed", "bytes=false/status=PENDING", artifact))
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

    print(f"PASS: {len(data.get('cases', []))} NKTsKI provenance regression cases and resolved-target fail-closed manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
