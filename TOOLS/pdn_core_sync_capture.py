#!/usr/bin/env python3
"""Synchronize immutable-capture manifests into PDN source records and inventory.

This deliberately does NOT promote a source to VERIFIED_FOR_EXTRACTION. It only
records evidence that bytes from the registered official route were captured
byte-exactly and fingerprinted.

For publication-ID manifests, source-identity proof is mandatory: publication IDs
must have been taken from the source document section, and the official API number
must match a registered federal-law source number when that check applies.

Registered canonical-route captures that do not use a publication ID are validated
by their own route/content proof instead. The current consolidated 152-FZ additionally
requires proof that the returned bytes contain the amendment marker of the pinned
current revision (No. 265-FZ, effective 26.07.2026), and that the accepted route was
pre-registered in the current source card.

Production telemetry is synchronized from PDN_ACQUISITION_RUN.json into the master
inventory on every pass so reuse, network work, pending counts and dedicated-route
failure classes do not remain stale after a successful workflow run.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "security-corpora" / "RU" / "152-FZ"
MANIFEST_DIR = CORPUS / "manifests"
INVENTORY = CORPUS / "PDN_MASTER_SOURCE_INVENTORY.yaml"
RUN_FILE = CORPUS / "PDN_ACQUISITION_RUN.json"
FEDERAL_LAW_NUMBER_RE = re.compile(r"^\d+-ФЗ$")
CURRENT_ROOT_SOURCE_ID = "SEC-SRC-RU-152FZ-2026-07-26"
PP687_SOURCE_ID = "SEC-SRC-RU-PP687-2008"
PRODUCTION_COUNTERS_RE = re.compile(
    r"(?ms)^production_counters:\n.*?(?=^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$|\Z)"
)
ACQUISITION_ACTIVITY_RE = re.compile(
    r"(?ms)^acquisition_activity:\n.*?(?=^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$|\Z)"
)


def q(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def manifest_is_raw_verified(manifest: dict) -> bool:
    proof = manifest.get("proof", {})
    schema_version = str(manifest.get("schema_version") or "")
    capture_kind = str(manifest.get("capture_kind") or "")
    source_id = str(manifest.get("source_id") or "")

    if schema_version == "1.0":
        return bool(
            proof.get("pdf_signature_ok")
            and proof.get("byte_length_matches_official_api")
            and proof.get("sha256_calculated_from_downloaded_bytes")
        )

    if not (
        proof.get("official_route")
        and proof.get("byte_exact_download")
        and proof.get("sha256_calculated_from_downloaded_bytes")
    ):
        return False

    if capture_kind == "official_registered_route_snapshot":
        return bool(
            source_id == PP687_SOURCE_ID
            and proof.get("registered_route_used")
            and proof.get("publication_api_length_check_not_applicable")
            and proof.get("canonical_content_identity_markers_ok")
            and manifest.get("semantic_status_unchanged")
        )

    # The current consolidated 152-FZ has no publication-ID PDF for the consolidated
    # 26.07.2026 form. Accept only a byte-exact snapshot from an official URL that was
    # already registered in the source card and whose body proves both source identity
    # and the pinned No. 265-FZ revision marker. This branch intentionally does NOT fake
    # a publication-ID-scoping proof that is inapplicable to consolidated snapshots.
    if capture_kind == "official_canonical_snapshot" and source_id == CURRENT_ROOT_SOURCE_ID:
        registered_urls = manifest.get("registered_source_urls") or []
        accepted_registered_url = str(manifest.get("accepted_registered_source_url") or "")
        route_binding_ok = bool(
            isinstance(registered_urls, list)
            and accepted_registered_url
            and accepted_registered_url in registered_urls
        )
        return bool(
            proof.get("official_route_pre_registered")
            and route_binding_ok
            and proof.get("publication_api_length_check_not_applicable")
            and proof.get("canonical_content_identity_markers_ok")
            and proof.get("current_revision_marker_ok")
            and proof.get("current_revision_trigger") == "265-ФЗ"
            and proof.get("current_revision_effective_from") == "2026-07-26"
            and manifest.get("semantic_status_unchanged")
        )

    if schema_version >= "1.2":
        if not proof.get("publication_id_scoped_to_source_document_section"):
            return False
        source_number = str(manifest.get("source_document_number") or "").strip()
        if FEDERAL_LAW_NUMBER_RE.fullmatch(source_number):
            if not proof.get("official_api_number_matches_source_document_when_checkable"):
                if capture_kind != "official_canonical_snapshot":
                    return False

    if capture_kind == "official_publication_pdf":
        return bool(proof.get("pdf_signature_ok") and proof.get("byte_length_matches_official_api"))

    if capture_kind == "official_canonical_snapshot":
        if not proof.get("publication_api_length_check_not_applicable"):
            return False
        return True

    return False


def update_source(manifest: dict) -> None:
    path = ROOT / manifest["source_record_ref"]
    text = path.read_text(encoding="utf-8")
    kind = manifest.get("capture_kind", "official_publication_pdf")
    note = (
        "Byte-exact official PDF captured; overall source status remains METADATA_VERIFIED until extraction/source-locator review gates pass."
        if kind == "official_publication_pdf"
        else "Byte-exact snapshot from a registered official canonical URL captured; overall source status remains unchanged until semantic/version-locator review gates pass."
    )
    block = (
        "capture:\n"
        f"  raw_artifact_ref: {q(manifest['artifact_ref'])}\n"
        f"  manifest_ref: {q(str((MANIFEST_DIR / (manifest['source_id'] + '.json')).relative_to(ROOT)).replace(chr(92), '/'))}\n"
        f"  capture_kind: {q(kind)}\n"
        f"  source_url: {q(manifest.get('source_url') or manifest.get('official_file_url'))}\n"
        f"  retrieved_at: {q(manifest['retrieved_at'])}\n"
        f"  mime: {q(manifest['mime'])}\n"
        f"  byte_length: {int(manifest['byte_length'])}\n"
        f"  sha256: {q(manifest['sha256'])}\n"
        "  fingerprint_status: IMMUTABLE_CAPTURED\n"
        "  semantic_status: UNCHANGED\n"
        f"  note: {q(note)}\n"
    )
    updated, count = re.subn(
        r"(?ms)^capture:\n.*?(?=^[A-Za-z_][A-Za-z0-9_]*:|\Z)", block + "\n", text, count=1
    )
    if count != 1:
        raise RuntimeError(f"capture block not found in {path}")
    path.write_text(updated, encoding="utf-8")


def inventory_source_ids(text: str) -> list[str]:
    return re.findall(r"(?m)^  - id:\s*([^\s#]+)\s*$", text)


def update_production_counters(text: str, immutable: int, pending: int, total: int) -> str:
    match = PRODUCTION_COUNTERS_RE.search(text)
    if not match:
        raise RuntimeError("production_counters block missing")
    block = match.group(0)
    replacements = {
        "raw_downloaded_exact": immutable,
        "immutable_sha256_verified": immutable,
        "pending_raw_capture": pending,
    }
    for key, value in replacements.items():
        block, n = re.subn(
            rf"(?m)^(  {re.escape(key)}:)\s*[^\n]+$",
            rf"\1 {value}",
            block,
            count=1,
        )
        if n != 1:
            raise RuntimeError(f"production counter not found: {key}")

    ratio = (immutable / total) if total else 0.0
    if "raw_capture_coverage_ratio:" in block:
        block = re.sub(
            r"(?m)^  raw_capture_coverage_ratio:\s*[^\n]+$",
            f"  raw_capture_coverage_ratio: {ratio:.4f}",
            block,
            count=1,
        )
    else:
        anchor = re.search(r"(?m)^  source_registration_success_rate:.*$", block)
        if anchor:
            pos = anchor.end()
            block = block[:pos] + f"\n  raw_capture_coverage_ratio: {ratio:.4f}" + block[pos:]

    return text[: match.start()] + block + text[match.end() :]


def update_version_chain_resolution_statuses(text: str, captured: set[str]) -> str:
    section = re.search(
        r"(?ms)^version_chain_identity_resolutions:\n.*?(?=^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$|\Z)",
        text,
    )
    if not section:
        return text
    block = section.group(0)
    for source_id in sorted(captured):
        pat = re.compile(
            rf"(?ms)(^  - chain: .*?\n    source_id: {re.escape(source_id)}\n.*?^    status:)\s*[^\n]+"
        )
        block = pat.sub(r"\1 IMMUTABLE_CAPTURED", block, count=1)
    return text[: section.start()] + block + text[section.end() :]


def update_pending_priority(text: str, pending_ids: list[str]) -> str:
    section = ACQUISITION_ACTIVITY_RE.search(text)
    if not section:
        return text
    block = section.group(0)
    replacement = "  pending_priority:\n" + "".join(f"    - {sid}\n" for sid in pending_ids)
    block, n = re.subn(
        r"(?m)^  pending_priority:\n(?:    - [^\n]+\n)*",
        replacement,
        block,
        count=1,
    )
    if n == 0:
        block = block.rstrip("\n") + "\n" + replacement
    return text[: section.start()] + block + text[section.end() :]


def attempt_summary(attempt: object) -> str:
    if not isinstance(attempt, dict):
        return "NOT_RUN"
    status = str(attempt.get("status") or "UNKNOWN")
    if status.startswith("IMMUTABLE_CAPTURED"):
        return "IMMUTABLE_CAPTURED"
    classes = attempt.get("failure_classes") or []
    if isinstance(classes, list) and classes:
        return "PENDING_" + "_AND_".join(str(item) for item in classes)
    return status


def combined_current_root_summary(telemetry: dict) -> str:
    attempts = [telemetry.get("current_root_curl"), telemetry.get("current_root_urllib")]
    if any(isinstance(a, dict) and str(a.get("status") or "").startswith("IMMUTABLE_CAPTURED") for a in attempts):
        return "IMMUTABLE_CAPTURED"
    classes: list[str] = []
    for attempt in attempts:
        if not isinstance(attempt, dict):
            continue
        for item in attempt.get("failure_classes") or []:
            item = str(item)
            if item not in classes:
                classes.append(item)
    return "PENDING_" + "_AND_".join(classes) if classes else "PENDING"


def update_acquisition_activity(text: str) -> str:
    if not RUN_FILE.exists():
        return text
    try:
        run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
    except Exception:
        return text

    section = ACQUISITION_ACTIVITY_RE.search(text)
    if not section:
        return text
    block = section.group(0)

    new_immutable = int(run.get("new_immutable_captured") or 0)
    block = re.sub(
        r"(?m)^  accepted_manifest_delta_at_inventory_write:\s*[^\n]+$",
        f"  accepted_manifest_delta_at_inventory_write: {new_immutable}",
        block,
        count=1,
    )

    started_at = str(run.get("started_at") or "")
    finished_at = str(run.get("finished_at") or "")
    targets = int(run.get("targets_total") or 0)
    reused = int(run.get("reused_immutable") or 0)
    network = int(run.get("network_targets_attempted") or 0)
    pending_generic = int(run.get("pending_after_run") or 0)
    reuse_ratio = float(run.get("reuse_ratio") or 0.0)
    last_run_block = (
        "  last_proven_acquisition_run:\n"
        f"    started_at: {q(started_at)}\n"
        f"    finished_at: {q(finished_at)}\n"
        f"    targets: {targets}\n"
        f"    reused_immutable: {reused}\n"
        f"    network_targets_attempted: {network}\n"
        f"    new_immutable_captured: {new_immutable}\n"
        f"    pending_generic: {pending_generic}\n"
        f"    reuse_ratio: {reuse_ratio:.10f}\n"
        "    note: >-\n"
        "      Synchronized automatically from PDN_ACQUISITION_RUN.json; dedicated guarded routes are reported separately below.\n"
    )
    block, n = re.subn(
        r"(?ms)^  last_proven_acquisition_run:\n.*?(?=^  latest_proven_dedicated_attempt:)",
        last_run_block,
        block,
        count=1,
    )
    if n == 0:
        anchor = re.search(r"(?m)^  latest_proven_dedicated_attempt:", block)
        if anchor:
            block = block[:anchor.start()] + last_run_block + block[anchor.start():]

    telemetry = run.get("dedicated_route_attempt_telemetry")
    if isinstance(telemetry, dict):
        observed_at = str(telemetry.get("observed_at") or "")
        pp687 = attempt_summary(telemetry.get("pp687"))
        current_root = combined_current_root_summary(telemetry)
        proof_held = all(
            not isinstance(telemetry.get(key), dict) or bool(telemetry[key].get("proof_floor_held", True))
            for key in ("pp687", "current_root_curl", "current_root_urllib")
        )
        dedicated_block = (
            "  latest_proven_dedicated_attempt:\n"
            f"    observed_at: {q(observed_at)}\n"
            f"    pp687: {pp687}\n"
            f"    current_152fz: {current_root}\n"
            "    semantic_promotions: 0\n"
            f"    proof_floor_held: {'true' if proof_held else 'false'}\n"
        )
        block, n = re.subn(
            r"(?ms)^  latest_proven_dedicated_attempt:\n.*?(?=^  pending_priority:)",
            dedicated_block,
            block,
            count=1,
        )
        if n == 0:
            anchor = re.search(r"(?m)^  pending_priority:", block)
            if anchor:
                block = block[:anchor.start()] + dedicated_block + block[anchor.start():]

    return text[: section.start()] + block + text[section.end() :]


def update_inventory(manifests: list[dict]) -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    captured = {m["source_id"] for m in manifests}
    all_ids = inventory_source_ids(text)
    for source_id in sorted(captured):
        pat = re.compile(rf"(?ms)(^  - id: {re.escape(source_id)}\n.*?^    raw_capture:)\s*[^\n]+")
        text, n = pat.subn(r"\1 IMMUTABLE_CAPTURED", text, count=1)
        if n != 1:
            raise RuntimeError(f"inventory source block not found for {source_id}")

    for source_id in all_ids:
        if source_id in captured:
            continue
        pat = re.compile(rf"(?ms)(^  - id: {re.escape(source_id)}\n.*?^    raw_capture:)\s*[^\n]+")
        text, _ = pat.subn(r"\1 PENDING", text, count=1)

    total = len(all_ids)
    immutable = len(captured.intersection(all_ids))
    pending_ids = [sid for sid in all_ids if sid not in captured]
    text = update_production_counters(text, immutable, len(pending_ids), total)
    text = update_version_chain_resolution_statuses(text, captured)
    text = update_pending_priority(text, pending_ids)
    text = update_acquisition_activity(text)

    if pending_ids:
        blocker = (
            "acquisition_blockers:\n"
            "  - >-\n"
            "      Official byte-exact acquisition is operational through publication-ID PDFs and registered canonical official URLs.\n"
            "      Remaining source IDs without an accepted immutable manifest: " + ", ".join(pending_ids) + ".\n\n"
        )
        first_gate = "  - capture and fingerprint the remaining official raw artifacts\n"
    else:
        blocker = (
            "acquisition_blockers:\n"
            "  - >-\n"
            "      None at the raw-acquisition layer for the registered PDN core: every inventory source has an accepted immutable manifest.\n"
            "      Semantic extraction and source-locator review remain separate gates.\n\n"
        )
        first_gate = ""

    text, n = re.subn(r"(?ms)^acquisition_blockers:\n.*?(?=^next_gate:)", blocker, text, count=1)
    if n != 1:
        raise RuntimeError("acquisition_blockers section not found")

    next_gate = (
        "next_gate:\n"
        + first_gate
        + "  - structural parse and legal/semantic chunking of immutable captures\n"
        "  - concept/definition reconciliation and conflict detection\n"
        "  - atomic requirement extraction with source locators\n"
        "  - typed inter-document relations, regression fixtures and review gates\n"
    )
    text, n = re.subn(r"(?ms)^next_gate:\n.*\Z", next_gate, text, count=1)
    if n != 1:
        raise RuntimeError("next_gate section not found")

    INVENTORY.write_text(text, encoding="utf-8")


def main() -> None:
    manifests = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(MANIFEST_DIR.glob("*.json"))]
    manifests = [m for m in manifests if manifest_is_raw_verified(m)]
    for manifest in manifests:
        update_source(manifest)
    update_inventory(manifests)
    print(json.dumps({"captured": len(manifests), "source_records_synced": len(manifests)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
