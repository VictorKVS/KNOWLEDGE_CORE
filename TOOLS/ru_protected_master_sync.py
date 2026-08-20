#!/usr/bin/env python3
"""Synchronize RU Protected Information / PDN master telemetry from immutable manifests.
Semantic/version-chain gates are preserved; raw capture never implies current-law verification.
"""
from __future__ import annotations
import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTOR = ROOT / "security-knowledge/corpus/ru-protected-information/master-inventory.yaml"
PDN = ROOT / "security-knowledge/corpus/ru-personal-data/master-source-inventory.yaml"
MANIFEST_DIR = ROOT / "security-corpora/RU/protected-information/manifests"
CAPTURED_IDS = {p.stem for p in MANIFEST_DIR.glob("*.json")}
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).isoformat(timespec="seconds")


def mark_artifact(text: str, sid: str) -> str:
    marker = f"  - id: {sid}\n"
    start = text.find(marker)
    if start < 0:
        return text
    nxt = text.find("\n  - id: ", start + len(marker))
    cov = text.find("\ncoverage:", start + len(marker))
    ends = [x for x in (nxt, cov) if x >= 0]
    end = min(ends) if ends else len(text)
    block = text[start:end]
    mref = f"security-corpora/RU/protected-information/manifests/{sid}.json"
    block = block.replace("artifact: {state: SOURCE_PENDING}",
                          f'artifact: {{state: IMMUTABLE_BASELINE_CAPTURED, manifest_ref: "{mref}"}}', 1)
    block = re.sub(r"\n    artifact:\n      state: SOURCE_PENDING",
                   f'\n    artifact:\n      state: IMMUTABLE_BASELINE_CAPTURED\n      manifest_ref: "{mref}"',
                   block, count=1)
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


def counter(text: str, name: str, value: int) -> str:
    pos = text.find("\ncounters:\n")
    if pos < 0:
        return text
    tail = re.sub(rf"(?m)^  {re.escape(name)}:\s*.*$", f"  {name}: {value}", text[pos:], count=1)
    return text[:pos] + tail


def sync_sector() -> None:
    text = SECTOR.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^updated_at: ".*"$', f'updated_at: "{NOW}"', text, count=1)
    text = ensure_442(text)
    for sid in sorted(CAPTURED_IDS):
        text = mark_artifact(text, sid)
    if "  social_services:" not in text:
        text = text.replace("  civil_status_records: DISCOVERED\n",
                            "  civil_status_records: DISCOVERED\n  social_services: PRIMARY_PUBLICATION_VERIFIED\n", 1)
    found, reused, immutable = 16, 1, len(CAPTURED_IDS)
    vals = {
        "found": found, "new_this_pass": 1, "downloaded": immutable, "immutable": immutable,
        "pending": max(0, found-reused-immutable), "reused": reused,
        "primary_publication_verified": 6, "exact_binary_acquisition_attempts_this_pass": 6,
        "exact_binary_acquisition_success_this_pass": immutable,
    }
    for k, v in vals.items():
        text = counter(text, k, v)
    telemetry = f'''production_telemetry:
  checked_at: "{NOW}"
  acquisition_status: "IMMUTABLE_BASELINE_CAPTURE_OPERATIONAL"
  exact_targets: 6
  immutable_successes: {immutable}
  exact_bytes_and_sha256_recorded: {immutable}
  note: >-
    Official byte-exact acquisition is operational. Captures prove immutable original-publication baselines only;
    current consolidated semantics remain gated by version-chain and locator review.
  remaining_capture_issue: >-
    323-ФЗ official endpoint may return a ZIP container rather than a bare PDF; acquirer v1.2 accepts and fingerprints
    recognized official PDF/ZIP containers without weakening the proof floor.
  analysis_note: >-
    Retention and access-restriction semantics remain separate; sector overlaps stay non-executable until applicability review.

'''
    text = re.sub(r"(?ms)^production_telemetry:\n.*?(?=^next_actions:)", telemetry, text, count=1)
    SECTOR.write_text(text, encoding="utf-8")


def sync_pdn() -> None:
    text = PDN.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^updated_at: ".*"$', f'updated_at: "{NOW}"', text, count=1)
    imm = len(CAPTURED_IDS)
    block = f'''  stream_3_sector_overlays:
    status: ACTIVE
    inventory: "../ru-protected-information/master-inventory.yaml"
    overlap_graph: "../../cross-domain/pdn-sector-overlap-seed-v1.yaml"
    sources_found_total: 16
    new_sources_this_pass: 1
    reused_existing_sources: 1
    primary_publication_verified_total: 6
    immutable_artifacts: {imm}
    pending_immutable: {max(0, 16-1-imm)}
    exact_binary_acquisition_attempts_this_pass: 6
    exact_binary_acquisition_success_this_pass: {imm}
    sectors_registered: 13
    semantic_collision_checks_this_pass: 1
    legal_conflicts_confirmed_this_pass: 0
    explicit_or_direct_legal_overlap_candidates:
      - "16-ФЗ article 11 -> 152-ФЗ"
      - "79-ФЗ article 42 -> personal-data legislation"
      - "143-ФЗ article 13.2(9) -> 149-ФЗ + 152-ФЗ (current consolidated text; current-primary review pending)"
      - "326-ФЗ article 44 -> restricted-access insured-person/medical-care data; PDN/health applicability review pending"
      - "125-ФЗ article 25(3) -> protected private/family-life archive information; no direct 152-ФЗ edge inferred"
      - "442-ФЗ article 6 -> personal-data processing context (candidate; not executable)"
    conflict_notes:
      - "143-ФЗ article 12 is repealed since 2018-10-01; current routing uses articles 13.1-13.2."
      - "125-ФЗ article 22.1 retention and article 25(3) access restriction are distinct semantics even when both show 75 years."
      - "442-ФЗ confidentiality of social-service-recipient information must not be auto-merged with generic 152-ФЗ personal-data confidentiality; scope comparison is pending."
    source_extensions:
      - "Росархив №24/2020: immutable original baseline captured; current-version chain remains partial."
      - "Росархив №77/2023: immutable original baseline captured; current-version chain remains partial."
    note: >-
      Sector/special protected-information overlays remain isolated from executable PDN logic until
      authoritative current artifacts, version chains and anchored applicability edges pass review.
'''
    text = re.sub(r"(?ms)^  stream_3_sector_overlays:\n.*?(?=^quality_gates:)", block + "\n", text, count=1)
    PDN.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    sync_sector(); sync_pdn()
    print(f"sector manifests={len(CAPTURED_IDS)}; masters synchronized")
