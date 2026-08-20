#!/usr/bin/env python3
"""Synchronize immutable-capture manifests into PDN source records and inventory.

This deliberately does NOT promote a source to VERIFIED_FOR_EXTRACTION. It only
records evidence that the official raw artifact was captured byte-exactly.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "security-corpora" / "RU" / "152-FZ"
MANIFEST_DIR = CORPUS / "manifests"
INVENTORY = CORPUS / "PDN_MASTER_SOURCE_INVENTORY.yaml"


def q(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def update_source(manifest: dict) -> None:
    path = ROOT / manifest["source_record_ref"]
    text = path.read_text(encoding="utf-8")
    block = (
        "capture:\n"
        f"  raw_artifact_ref: {q(manifest['artifact_ref'])}\n"
        f"  manifest_ref: {q(str((MANIFEST_DIR / (manifest['source_id'] + '.json')).relative_to(ROOT)).replace(chr(92), '/'))}\n"
        f"  retrieved_at: {q(manifest['retrieved_at'])}\n"
        f"  mime: {q(manifest['mime'])}\n"
        f"  byte_length: {int(manifest['byte_length'])}\n"
        f"  sha256: {q(manifest['sha256'])}\n"
        "  fingerprint_status: IMMUTABLE_CAPTURED\n"
        "  semantic_status: UNCHANGED\n"
        "  note: \"Byte-exact official PDF captured; overall source status remains METADATA_VERIFIED until extraction/source-locator review gates pass.\"\n"
    )
    updated, count = re.subn(r"(?ms)^capture:\n.*?(?=^[A-Za-z_][A-Za-z0-9_]*:|\Z)", block + "\n", text, count=1)
    if count != 1:
        raise RuntimeError(f"capture block not found in {path}")
    path.write_text(updated, encoding="utf-8")


def update_inventory(manifests: list[dict]) -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    captured = {m["source_id"] for m in manifests}
    for source_id in sorted(captured):
        pat = re.compile(
            rf"(?ms)(^  - id: {re.escape(source_id)}\n.*?^    raw_capture:)\s*[^\n]+"
        )
        text, n = pat.subn(r"\1 IMMUTABLE_CAPTURED", text, count=1)
        if n != 1:
            raise RuntimeError(f"inventory source block not found for {source_id}")

    total_match = re.search(r"(?m)^  identified:\s*(\d+)\s*$", text)
    total = int(total_match.group(1)) if total_match else 0
    immutable = len(captured)
    pending = max(total - immutable, 0)

    replacements = {
        "raw_downloaded_exact": immutable,
        "immutable_sha256_verified": immutable,
        "pending_raw_capture": pending,
    }
    for key, value in replacements.items():
        text, n = re.subn(rf"(?m)^(  {re.escape(key)}:)\s*[^\n]+$", rf"\1 {value}", text, count=1)
        if n != 1:
            raise RuntimeError(f"counter not found: {key}")

    ratio = (immutable / total) if total else 0.0
    if "raw_capture_coverage_ratio:" in text:
        text = re.sub(r"(?m)^  raw_capture_coverage_ratio:\s*[^\n]+$", f"  raw_capture_coverage_ratio: {ratio:.4f}", text)
    else:
        anchor = re.search(r"(?m)^  source_registration_success_rate:.*$", text)
        if anchor:
            pos = anchor.end()
            text = text[:pos] + f"\n  raw_capture_coverage_ratio: {ratio:.4f}" + text[pos:]

    blocker = (
        "acquisition_blockers:\n"
        "  - >-\n"
        "      Byte-exact acquisition via the official publication portal is operational for source records\n"
        "      carrying an official_publication_id; each captured PDF is checked against the portal API byte\n"
        "      length, fingerprinted with SHA-256 and stored with a manifest.\n"
        "  - >-\n"
        "      Remaining raw captures are the consolidated 152-FZ text and PP RF No. 687 / No. 211. Their\n"
        "      current source records use official IPS/Government routes rather than the publication-ID path,\n"
        "      so they remain PENDING until byte-exact version-specific official artifacts are captured.\n\n"
    )
    text, n = re.subn(r"(?ms)^acquisition_blockers:\n.*?(?=^next_gate:)", blocker, text, count=1)
    if n != 1:
        raise RuntimeError("acquisition_blockers section not found")

    next_gate = (
        "next_gate:\n"
        "  - capture byte-exact version-specific official artifacts for 152-FZ, PP RF No. 687 and PP RF No. 211\n"
        "  - structural parse and legal/semantic chunking of immutable captures\n"
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
    manifests = [m for m in manifests if m.get("proof", {}).get("pdf_signature_ok") and m.get("proof", {}).get("byte_length_matches_official_api")]
    for manifest in manifests:
        update_source(manifest)
    update_inventory(manifests)
    print(json.dumps({"captured": len(manifests), "source_records_synced": len(manifests)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
