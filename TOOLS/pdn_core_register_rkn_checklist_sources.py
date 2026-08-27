#!/usr/bin/env python3
"""Register missing general-core Roskomnadzor checklist sources in the PDN master inventory.

This is a narrow, deterministic repair for Stream 1. It does not promote raw or
semantic status. Exact-byte acquisition remains the responsibility of the normal
PDN acquisition/sync pipeline.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "security-corpora" / "RU" / "152-FZ" / "PDN_MASTER_SOURCE_INVENTORY.yaml"

BLOCKS = {
    "SEC-SRC-RU-RKN253-2021": '''  - id: SEC-SRC-RU-RKN253-2021
    document: "Приказ Роскомнадзора от 24.12.2021 № 253"
    role: federal_state_control_supervision_checklist_personal_data
    metadata_status: METADATA_VERIFIED
    source_record: "source/SEC-SRC-RU-RKN253-2021.yaml"
    raw_capture: PENDING
    current_revision_anchor: SEC-SRC-RU-RKN1-2023
''',
    "SEC-SRC-RU-RKN1-2023": '''  - id: SEC-SRC-RU-RKN1-2023
    document: "Приказ Роскомнадзора от 10.01.2023 № 1"
    role: rkn253_current_revision_amendment
    metadata_status: METADATA_VERIFIED
    source_record: "source/SEC-SRC-RU-RKN1-2023.yaml"
    raw_capture: PENDING
    applicability: VERSION_CHAIN_AND_CONTROL_CHECKLIST_SCOPE
    amends: SEC-SRC-RU-RKN253-2021
''',
}


def source_ids(text: str) -> list[str]:
    return re.findall(r"(?m)^  - id:\s*([^\s#]+)\s*$", text)


def replace_counter(text: str, key: str, value: object) -> str:
    pattern = rf"(?m)^(  {re.escape(key)}:)\s*[^\n]+$"
    updated, n = re.subn(pattern, rf"\1 {value}", text, count=1)
    if n != 1:
        raise RuntimeError(f"production counter not found: {key}")
    return updated


def main() -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    existing = set(source_ids(text))
    missing = [sid for sid in BLOCKS if sid not in existing]

    if missing:
        section = re.search(
            r"(?ms)^sources:\n(?P<body>.*?)(?=^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$|\Z)",
            text,
        )
        if not section:
            raise RuntimeError("sources block not found")
        insertion = "\n" + "\n".join(BLOCKS[sid].rstrip() for sid in missing) + "\n"
        pos = section.end("body")
        text = text[:pos].rstrip() + insertion + "\n" + text[pos:]

    ids = source_ids(text)
    sources_section = re.search(
        r"(?ms)^sources:\n(?P<body>.*?)(?=^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$|\Z)",
        text,
    )
    if not sources_section:
        raise RuntimeError("sources block not found after registration")
    metadata_verified = len(
        re.findall(r"(?m)^    metadata_status:\s*METADATA_VERIFIED\s*$", sources_section.group("body"))
    )
    immutable = len(re.findall(r"(?m)^    raw_capture:\s*IMMUTABLE_CAPTURED\s*$", sources_section.group("body")))
    pending = len(ids) - immutable

    text = replace_counter(text, "identified", len(ids))
    text = replace_counter(text, "metadata_verified", metadata_verified)
    text = replace_counter(text, "raw_downloaded_exact", immutable)
    text = replace_counter(text, "immutable_sha256_verified", immutable)
    text = replace_counter(text, "pending_raw_capture", pending)
    ratio = immutable / len(ids) if ids else 0.0
    text = replace_counter(text, "raw_capture_coverage_ratio", f"{ratio:.4f}")
    text = re.sub(r'(?m)^checked_at:\s*"[^"]+"$', 'checked_at: "2026-08-27"', text, count=1)

    INVENTORY.write_text(text, encoding="utf-8")
    print({
        "registered": missing,
        "identified": len(ids),
        "metadata_verified": metadata_verified,
        "immutable_before_acquisition": immutable,
        "pending_before_acquisition": pending,
        "raw_capture_coverage_ratio": round(ratio, 4),
    })


if __name__ == "__main__":
    main()
