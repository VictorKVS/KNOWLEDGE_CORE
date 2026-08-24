#!/usr/bin/env python3
"""Capture the current consolidated 152-FZ root from its registered official IPS route.

This is deliberately separate from the general PDN acquirer because the current
consolidated root is not yet METADATA_VERIFIED: its version identity is cross-verified,
but immutable capture is itself the next proof gate. The script therefore accepts only
one explicit source ID and only when metadata_status is VERSION_IDENTITY_CROSS_VERIFIED.
It writes raw bytes + manifest and never promotes semantic/extraction status.

Safety invariant: an official-route response is not sufficient by itself. The captured
body must contain identity markers for Federal Law No. 152-FZ on personal data and must
prove the pinned current revision. Revision proof may be either the explicit amending-law
marker No. 265-FZ or the complete Article 12 part 2 wording fingerprint introduced by
that amendment. This avoids rejecting a valid consolidated text merely because the
publisher omits the amending-law citation, while still preventing an older edition from
passing the gate. The inspection view may normalize HTML entities/tags and Unicode
variants, but the immutable stored bytes are never altered by that normalization.
"""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from pathlib import Path

from pdn_core_acquire import (
    CANONICAL_URL_RE,
    CORPUS,
    DOC_NUMBER_RE,
    MANIFEST_DIR,
    ROOT,
    capture_canonical_snapshot,
    top_level_section,
)

SOURCE_ID = "SEC-SRC-RU-152FZ-2026-07-26"
SOURCE_RECORD = CORPUS / "source" / f"{SOURCE_ID}.yaml"
METADATA_STATUS_RE = re.compile(r"^metadata_status:\s*([^\s#]+)\s*$", re.M)
IDENTITY_PATTERNS = (
    ("law_number_152_fz", re.compile(r"(?:№\s*)?152\s*-\s*фз")),
    ("personal_data", re.compile(r"персональн\w*\s+данн\w*")),
)
CURRENT_REVISION_CITATION_PATTERNS = (
    ("amendment_265_fz", re.compile(r"(?:№\s*)?265\s*-\s*фз")),
)
# Current-edition fingerprint derived from the Article 12 part 2 delta introduced by
# Federal Law No. 265-FZ on 26.07.2026. All anchors are required when the explicit
# amending-law citation is absent. They are deliberately narrower than generic Article
# 12 phrases so the pre-26.07.2026 wording cannot satisfy the gate accidentally.
CURRENT_REVISION_DELTA_PATTERNS = (
    (
        "article12_2026_country_scope",
        re.compile(
            r"государства,\s+в\s+которых\s+правовое\s+регулирование\s+"
            r"в\s+области\s+персональных\s+данных"
        ),
    ),
    (
        "article12_2026_principles",
        re.compile(r"мер\w*\s+по\s+соблюдению\s+основополагающих\s+принципов\s+защиты"),
    ),
    (
        "article12_2026_convention_conformity",
        re.compile(r"соответствуют\s+положениям\s+конвенции"),
    ),
)
CURRENT_REVISION_EFFECTIVE_FROM = "2026-07-26"
CURRENT_REVISION_TRIGGER = "265-ФЗ"


def normalize_identity_text(text: str) -> str:
    """Normalize only the inspection view; immutable raw bytes remain authoritative."""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans({
        "\xa0": " ",
        "‑": "-",
        "–": "-",
        "—": "-",
        "−": "-",
    }))
    return re.sub(r"\s+", " ", text.lower()).strip()


def decode_for_identity(data: bytes) -> str:
    """Best-effort decode only for guards; raw bytes remain authoritative."""
    candidates: list[str] = []
    for encoding in ("utf-8", "cp1251"):
        try:
            candidates.append(data.decode(encoding))
        except UnicodeDecodeError:
            candidates.append(data.decode(encoding, errors="ignore"))
    return normalize_identity_text("\n".join(candidates))


def current_root_identity_ok(data: bytes) -> tuple[bool, list[str]]:
    """Require source identity plus one independently sufficient current-revision proof."""
    text = decode_for_identity(data)
    matched: list[str] = []

    for label, pattern in IDENTITY_PATTERNS:
        hit = pattern.search(text)
        if not hit:
            return False, matched
        matched.append(f"{label}:{hit.group(0)}")

    citation_hits: list[str] = []
    citation_ok = True
    for label, pattern in CURRENT_REVISION_CITATION_PATTERNS:
        hit = pattern.search(text)
        if not hit:
            citation_ok = False
            break
        citation_hits.append(f"{label}:{hit.group(0)}")
    if citation_ok:
        matched.extend(citation_hits)
        matched.append("revision_proof:amendment_citation")
        return True, matched

    delta_hits: list[str] = []
    for label, pattern in CURRENT_REVISION_DELTA_PATTERNS:
        hit = pattern.search(text)
        if not hit:
            return False, matched
        delta_hits.append(f"{label}:{hit.group(0)}")
    matched.extend(delta_hits)
    matched.append("revision_proof:article12_2026_delta_anchor")
    return True, matched


def revision_proof_mode(markers: list[str]) -> str:
    for marker in markers:
        if marker == "revision_proof:amendment_citation":
            return "amendment_citation"
        if marker == "revision_proof:article12_2026_delta_anchor":
            return "article12_2026_delta_anchor"
    return "unknown"


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
    murl = CANONICAL_URL_RE.search(canonical)
    if not murl:
        raise RuntimeError(f"refuse current-root capture: no registered canonical_source.url for {SOURCE_ID}")

    expected_number = mnumber.group(1).strip() if mnumber else ""
    manifest = capture_canonical_snapshot(
        SOURCE_ID,
        murl.group(1),
        expected_number,
        SOURCE_RECORD,
    )

    # Validate the returned body before allowing a manifest to exist. The generic
    # canonical capture helper already wrote the raw bytes, so remove that candidate
    # if the body is not recognizably the registered law at the pinned current revision.
    artifact = ROOT / str(manifest["artifact_ref"])
    body = artifact.read_bytes()
    identity_ok, markers = current_root_identity_ok(body)
    if not identity_ok:
        artifact.unlink(missing_ok=True)
        raise RuntimeError(
            "refuse current-root capture: official-route response lacks required "
            "152-FZ/personal-data identity or pinned current-revision evidence "
            "(265-FZ citation or Article-12 2026 delta anchor)"
        )

    proof_mode = revision_proof_mode(markers)
    manifest["schema_version"] = "1.8"
    manifest["capture_policy"] = "current-root-version-identity-cross-verified-with-normalized-content-and-delta-aware-revision-proof"
    manifest["semantic_status_unchanged"] = True
    manifest["proof"]["current_root_source_id_pinned"] = True
    manifest["proof"]["metadata_status_gate"] = "VERSION_IDENTITY_CROSS_VERIFIED"
    manifest["proof"]["canonical_content_identity_markers_ok"] = True
    manifest["proof"]["canonical_content_identity_markers"] = markers
    # Preserve this legacy boolean for synchronizer compatibility; its meaning is now
    # "current revision proved", not necessarily "literal amending-law marker found".
    manifest["proof"]["current_revision_marker_ok"] = True
    manifest["proof"]["current_revision_proof_ok"] = True
    manifest["proof"]["current_revision_proof_mode"] = proof_mode
    manifest["proof"]["current_revision_trigger"] = CURRENT_REVISION_TRIGGER
    manifest["proof"]["current_revision_effective_from"] = CURRENT_REVISION_EFFECTIVE_FROM
    manifest["proof"]["identity_view_html_entities_unescaped"] = True
    manifest["proof"]["identity_view_unicode_nfkc_normalized"] = True
    manifest["proof"]["identity_view_html_tags_collapsed"] = True
    manifest["proof"]["raw_bytes_unchanged_by_identity_normalization"] = True

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    mpath = MANIFEST_DIR / f"{SOURCE_ID}.json"
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_id": SOURCE_ID,
        "status": "IMMUTABLE_CAPTURED_RAW_ONLY",
        "mime": manifest["mime"],
        "byte_length": manifest["byte_length"],
        "sha256": manifest["sha256"],
        "artifact_ref": manifest["artifact_ref"],
        "identity_and_revision_markers": markers,
        "current_revision_proof_mode": proof_mode,
        "current_revision_trigger": CURRENT_REVISION_TRIGGER,
        "current_revision_effective_from": CURRENT_REVISION_EFFECTIVE_FROM,
        "semantic_status_unchanged": True,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({
            "source_id": SOURCE_ID,
            "status": "PENDING",
            "error": str(exc),
            "semantic_status_unchanged": True,
        }, ensure_ascii=False))
        sys.exit(2)
