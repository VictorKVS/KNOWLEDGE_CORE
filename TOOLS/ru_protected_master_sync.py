#!/usr/bin/env python3
"""Synchronize RU Protected Information / PDN master inventory telemetry.

This is deliberately a text-preserving synchronizer: it updates acquisition
state from immutable manifests without changing semantic/version-chain gates.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTOR = ROOT / "security-knowledge/corpus/ru-protected-information/master-inventory.yaml"
PDN = ROOT / "security-knowledge/corpus/ru-personal-data/master-source-inventory.yaml"
MANIFEST_DIR = ROOT / "security-corpora/RU/protected-information/manifests"

CAPTURED_IDS = {
    p.stem for p in MANIFEST_DIR.glob("*.json")
}
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).isoformat(timespec="seconds")


def mark_artifact(text: str, source_id: str) -> str:
    marker = f"  - id: {source_id}\n"
    start = text.find(marker)
    if start < 0:
        return text
    next_source = text.find("\n  - id: ", start + len(marker))
    coverage = text.find("\ncoverage:", start + len(marker))
    end_candidates = [x for x in (next_source, coverage) if x >= 0]
    end = min(end_candidates) if end_candidates else len(text)
    block = text[start:end]
    manifest_ref = f"security-corpora/RU/protected-information/manifests/{source_id}.json"
    if "artifact: {state: SOURCE_PENDING}" in block:
        block = block.replace(
            "artifact: {state: SOURCE_PENDING}",
            f'artifact: {{state: IMMUTABLE_BASELINE_CAPTURED, manifest_ref: "{manifest_ref}"}}',
            1,
        )
    elif re.search(r"\n    artifact:\n      state: SOURCE_PENDING", block):
        block = re.sub(
            r"\n    artifact:\n      state: SOURCE_PENDING",
            f'\n    artifact:\n      state: IMMUTABLE_BASELINE_CAPTURED\n      manifest_ref: "{manifest_ref}"',
            block,
            count=1,
        )
    return text[:start] + block + text[end:]


def ensure_442(text: str) -> str:
    if "SEC-SRC-RU-FZ-442-2013" in text:
        return text
    block = '''\n  - id: SEC-SRC-RU-FZ-442-2013
    sector: social_services
    regime: social_service_recipient_confidentiality
    number: "442-ФЗ"
    date: "2013-12-28"
    title: "Об основах социального обслуживания граждан в Российской Федерации"
    status: PRIMARY_PUBLICATION_VERIFIED
    official_publication_number: "0001201312300060"
    official_publication_date: "2013-12-30"
    source_url: "https://publication.pravo.gov.ru/Document/View/0001201312300060"
    primary_anchor: "статья 6 — конфиденциальность информации о получателе социальных услуг"
    overlap_candidates:
      - {target: "152-ФЗ", type: PERSONAL_DATA_PROCESSING_CONTEXT, status: CANDIDATE_PENDING_PRIMARY_CURRENT_VERSION_REVIEW}
    version_chain:
      state: VERSION_CHAIN_PARTIAL
      evidence: ["Government working text reviewed; amendment marker seen through 26.12.2024 № 476-ФЗ"]
      pending: "Полностью сверить изменения 2025-2026 по первичным публикациям до executable use."
    artifact: {state: SOURCE_PENDING}
'''
    return text.replace("\ncoverage:\n", block + "\ncoverage:\n", 1)


def replace_counter(text: str, name: str, value: int) -> str:
    # Restrict to first counters section after '\ncounters:'
    pos = text.find("\ncounters:\n")
    if pos < 0:
        return text
    tail = text[pos:]
    tail = re.sub(rf"(?m)^  {re.escape(name)}:\s*.*$", f"  {name}: {value}", tail, count=1)
    return text[:pos] + tail


def sync_sector() -> None:
    text = SECTOR.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^updated_at: ".*"$', f'updated_at: "{NOW}"', text, count=1)
    text = ensure_442(text)
    for sid in sorted(CAPTURED_IDS):
        text = mark_artifact(text, sid)
    if "  social_services:" not in text:
        text = text.replace("  civil_status_records: DISCOVERED\n", "  civil_status_records: DISCOVERED\n  social_services: PRIMARY_PUBLICATION_VERIFIED\n", 1)
    found = 16
    reused = 1
    immutable = len(CAPTURED_IDS)
    pending = max(0, found - reused - immutable)
    values = {
        "found": found,
        "new_this_pass": 1,
        "downloaded": immutable,
        "immutable": immutable,
        "pending": pending,
        "reused": reused,
        "primary_publication_verified": 6,
        "exact_binary_acquisition_attempts_this_pass": 6,
        "exact_binary_acquisition_success_this_pass": immutable,
    }
    for k, v in values.items():
        text = replace_counter(text, k, v)
    text = re.sub(r'(?m)^  checked_at: ".*"$', f'  checked_at: "{NOW}"', text, count=1)
    SECTOR.write_text(text, encoding="utf-8")


def sync_pdn() -> None:
    text = PDN.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^updated_at: ".*"$', f'updated_at: "{NOW}"', text, count=1)
    block = '''  stream_3_sector_overlays:
    status: ACTIVE
    inventory: "../ru-protected-information/master-inventory.yaml"
    overlap_graph: "../../cross-domain/pdn-sector-overlap-seed-v1.yaml"
    sources_found_total: 16
    new_sources_this_pass: 1
    reused_existing_sources: 1
    primary_publication_verified_total: 6
    immutable_artifacts: %d
    pending_immutable: %d
    exact_binary_acquisition_attempts_this_pass: 6
    exact_binary_acquisition_success_this_pass: %d
    sectors_registered: 13
    explicit_or_direct_legal_overlap_candidates:
      - "16-ФЗ article 11 -> 152-ФЗ"
      - "79-ФЗ article 42 -> personal-data legislation"
      - "143-ФЗ article 13.2(9) -> 152-ФЗ"
      - "442-ФЗ article 6 -> personal-data processing context (candidate; not executable)"
    note: >-
      Sector/special protected-information overlays remain isolated from executable PDN logic until
      authoritative current artifacts, version chains and anchored applicability edges pass review.
''' % (len(CAPTURED_IDS), max(0, 16 - 1 - len(CAPTURED_IDS)), len(CAPTURED_IDS))
    text = re.sub(
        r"(?ms)^  stream_3_sector_overlays:\n.*?(?=^quality_gates:)",
        block + "\n",
        text,
        count=1,
    )
    PDN.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    sync_sector()
    sync_pdn()
    print(f"sector manifests={len(CAPTURED_IDS)}; masters synchronized")
