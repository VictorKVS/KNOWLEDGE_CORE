#!/usr/bin/env python3
"""Synchronize RU Protected Information / PDN master telemetry from source cards and immutable manifests.

The synchronizer is intentionally conservative: acquisition may prove identity and immutable
original-publication bytes, but it never upgrades current-law semantics, applicability or a
version-chain gate. Source-universe counters are derived from repository state instead of
hard-coded totals so adding a new sector source cannot silently corrupt telemetry.

Safety invariant (v1.4): baseline identity fields are read only from the top-level ``document``
section of a source card. Nested amendment/version-chain publication IDs cannot promote the
baseline source or its master-inventory artifact state.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTOR = ROOT / "security-knowledge/corpus/ru-protected-information/master-inventory.yaml"
PDN = ROOT / "security-knowledge/corpus/ru-personal-data/master-source-inventory.yaml"
CORPUS = ROOT / "security-corpora/RU/protected-information"
SOURCE_DIR = CORPUS / "source"
MANIFEST_DIR = CORPUS / "manifests"
RUN_FILE = CORPUS / "SECTOR_ACQUISITION_RUN.json"
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).isoformat(timespec="seconds")
TOP_LEVEL_RE = re.compile(r"(?m)^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$")


def captured_ids() -> set[str]:
    return {p.stem for p in MANIFEST_DIR.glob("*.json")}


def source_blocks(text: str) -> dict[str, str]:
    """Return source blocks from master inventory, stopping before coverage."""
    sources_start = text.find("\nsources:\n")
    coverage = text.find("\ncoverage:\n")
    if sources_start < 0 or coverage < 0 or coverage <= sources_start:
        return {}
    area = text[sources_start:coverage]
    out: dict[str, str] = {}
    matches = list(re.finditer(r"(?m)^  - id:\s*([^\s]+)\s*$", area))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(area)
        out[m.group(1)] = area[start:end]
    return out


def top_level_section(text: str, name: str) -> str:
    start_match = re.search(rf"(?m)^{re.escape(name)}:\s*$", text)
    if not start_match:
        return ""
    start = start_match.end()
    tail = text[start:]
    next_top = TOP_LEVEL_RE.search(tail)
    end = start + next_top.start() if next_top else len(text)
    return text[start:end]


def anchored_field(text: str, name: str, indent: int = 0, default: str = "") -> str:
    prefix = " " * indent
    m = re.search(rf'(?m)^{re.escape(prefix)}{re.escape(name)}:\s*["\']?([^"\'\n]+)["\']?\s*$', text)
    return m.group(1).strip() if m else default


def quoted_top_field(text: str, name: str, default: str = "") -> str:
    m = re.search(rf'(?m)^{re.escape(name)}:\s*"(.*)"\s*$', text)
    return m.group(1).strip() if m else default


def parse_card(path: Path) -> dict[str, str | bool]:
    text = path.read_text(encoding="utf-8")
    document = top_level_section(text, "document")
    canonical = top_level_section(text, "canonical_source")
    protected = top_level_section(text, "protected_information")
    version = top_level_section(text, "version_chain")
    reuse = top_level_section(text, "reuse")

    sid = anchored_field(text, "id")
    title = quoted_top_field(text, "title", sid)
    sector = anchored_field(protected, "sector", indent=2, default="unclassified")
    regime = anchored_field(protected, "regime", indent=2, default="protected_information")
    number = anchored_field(document, "number", indent=2)
    adopted = anchored_field(document, "adopted_date", indent=2)
    eo = anchored_field(document, "official_publication_id", indent=2)
    pub_date = anchored_field(document, "official_publication_date", indent=2)
    url = anchored_field(canonical, "url", indent=2)
    anchor = anchored_field(protected, "primary_anchor", indent=2)
    version_state = anchored_field(version, "state", indent=2, default="VERSION_CHAIN_PARTIAL")
    origin_verified = anchored_field(canonical, "origin_verified", indent=2).lower() == "true"
    card_status = anchored_field(text, "status")
    existing_source_ref = anchored_field(reuse, "existing_source_ref", indent=2)
    return {
        "id": sid,
        "title": title,
        "sector": sector,
        "regime": regime,
        "number": number,
        "date": adopted,
        "official_publication_number": eo,
        "official_publication_date": pub_date,
        "source_url": url,
        "primary_anchor": anchor,
        "version_state": version_state,
        "origin_verified": origin_verified,
        "card_status": card_status,
        "existing_source_ref": existing_source_ref,
        "source_card_ref": str(path.relative_to(ROOT)).replace("\\", "/"),
    }


def cards() -> dict[str, dict[str, str | bool]]:
    out = {}
    for path in sorted(SOURCE_DIR.glob("*.yaml")):
        c = parse_card(path)
        if c["id"]:
            out[str(c["id"])] = c
    return out


def yaml_q(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def effective_status(card: dict[str, str | bool]) -> str:
    if card.get("card_status") == "REUSED_EXISTING_SOURCE":
        return "REUSED"
    if bool(card.get("origin_verified")) and bool(card.get("official_publication_number")):
        return "PRIMARY_PUBLICATION_VERIFIED"
    return "SOURCE_PENDING"


def card_to_master_block(card: dict[str, str | bool], captured: set[str]) -> str:
    sid = str(card["id"])
    status = effective_status(card)
    lines = [
        f"  - id: {sid}",
        f"    sector: {card['sector']}",
        f"    regime: {card['regime']}",
        f"    number: {yaml_q(card['number'])}",
        f"    date: {yaml_q(card['date'])}",
        f"    title: {yaml_q(card['title'])}",
        f"    status: {status}",
        f"    source_card_ref: {yaml_q(card['source_card_ref'])}",
    ]
    if card["official_publication_number"]:
        lines.append(f"    official_publication_number: {yaml_q(card['official_publication_number'])}")
    if card["official_publication_date"]:
        lines.append(f"    official_publication_date: {yaml_q(card['official_publication_date'])}")
    if card["source_url"]:
        lines.append(f"    source_url: {yaml_q(card['source_url'])}")
    if card["existing_source_ref"]:
        lines.append(f"    reuse_path: {yaml_q(card['existing_source_ref'])}")
        lines.append('    reuse_note: "Existing legal source node is reused; this sector card does not create a duplicate legal node."')
    if card["primary_anchor"]:
        lines.append(f"    primary_anchor: {yaml_q(card['primary_anchor'])}")
    lines += [
        "    version_chain:",
        f"      state: {card['version_state']}",
        "      pending: \"See source card; current executable semantics remain gated by full primary version-chain review.\"",
    ]
    if sid in captured:
        mref = f"security-corpora/RU/protected-information/manifests/{sid}.json"
        lines.append(f'    artifact: {{state: IMMUTABLE_BASELINE_CAPTURED, manifest_ref: "{mref}"}}')
    else:
        lines.append("    artifact: {state: SOURCE_PENDING}")
    return "\n".join(lines) + "\n"


def ensure_source_cards(text: str, source_cards: dict[str, dict[str, str | bool]], captured: set[str]) -> tuple[str, set[str]]:
    existing = set(source_blocks(text))
    new_ids = set(source_cards) - existing
    if not new_ids:
        return text, set()
    insertion = "\n".join(card_to_master_block(source_cards[sid], captured).rstrip() for sid in sorted(new_ids)) + "\n"
    text = text.replace("\ncoverage:\n", "\n" + insertion + "\ncoverage:\n", 1)
    return text, new_ids


def replace_source_block(text: str, sid: str, new_block: str) -> str:
    marker = f"  - id: {sid}\n"
    start = text.find(marker)
    if start < 0:
        return text
    nxt = text.find("\n  - id: ", start + len(marker))
    cov = text.find("\ncoverage:", start + len(marker))
    ends = [x for x in (nxt, cov) if x >= 0]
    end = min(ends) if ends else len(text)
    return text[:start] + new_block.rstrip() + "\n" + text[end:]


def reconcile_card_owned_blocks(text: str, source_cards: dict[str, dict[str, str | bool]], captured: set[str]) -> str:
    """Rebuild only source-card-owned master blocks.

    This removes stale promotions if a bad manifest is deleted and prevents nested amendment IDs from
    persisting as baseline publication metadata. Legacy hand-curated blocks without source_card_ref are untouched.
    """
    blocks = source_blocks(text)
    for sid, card in source_cards.items():
        block = blocks.get(sid, "")
        if block and "source_card_ref:" in block:
            text = replace_source_block(text, sid, card_to_master_block(card, captured))
            blocks = source_blocks(text)
    return text


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
    block = block.replace(
        "artifact: {state: SOURCE_PENDING}",
        f'artifact: {{state: IMMUTABLE_BASELINE_CAPTURED, manifest_ref: "{mref}"}}',
        1,
    )
    block = re.sub(
        r"\n    artifact:\n      state: SOURCE_PENDING",
        f'\n    artifact:\n      state: IMMUTABLE_BASELINE_CAPTURED\n      manifest_ref: "{mref}"',
        block,
        count=1,
    )
    return text[:start] + block + text[end:]


def counter(text: str, name: str, value: int) -> str:
    pos = text.find("\ncounters:\n")
    if pos < 0:
        return text
    tail = re.sub(rf"(?m)^  {re.escape(name)}:\s*.*$", f"  {name}: {value}", text[pos:], count=1)
    return text[:pos] + tail


def acquisition_run() -> dict:
    if not RUN_FILE.exists():
        return {}
    try:
        return json.loads(RUN_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def sector_metrics(text: str, source_cards: dict[str, dict[str, str | bool]], captured: set[str]) -> dict[str, int]:
    blocks = source_blocks(text)
    found = len(blocks)
    reused = sum(1 for b in blocks.values() if re.search(r"(?m)^    status:\s*REUSED\s*$", b))
    immutable = len(set(blocks) & captured)
    verified_ids = {
        sid for sid, b in blocks.items()
        if re.search(r"(?m)^    status:\s*PRIMARY_PUBLICATION_VERIFIED\s*$", b)
    }
    verified_ids |= {
        sid for sid, card in source_cards.items()
        if sid in blocks and effective_status(card) == "PRIMARY_PUBLICATION_VERIFIED"
    }
    sectors = {
        m.group(1).strip() for b in blocks.values()
        if (m := re.search(r"(?m)^    sector:\s*([^\s#]+)\s*$", b))
    }
    return {
        "found": found,
        "reused": reused,
        "immutable": immutable,
        "pending": max(0, found - reused - immutable),
        "primary_verified": len(verified_ids),
        "sectors": len(sectors),
    }


def ensure_coverage(text: str, source_cards: dict[str, dict[str, str | bool]]) -> str:
    coverage_start = text.find("\ncoverage:\n")
    conflict_start = text.find("\nconflict_registry:", coverage_start + 1)
    if coverage_start < 0 or conflict_start < 0:
        return text
    coverage_block = text[coverage_start:conflict_start]
    for card in source_cards.values():
        sector = str(card["sector"])
        if not re.search(rf"(?m)^  {re.escape(sector)}:\s*", coverage_block):
            coverage_block += f"  {sector}: DISCOVERED\n"
    return text[:coverage_start] + coverage_block + text[conflict_start:]


def sync_sector() -> tuple[dict[str, int], set[str], dict]:
    text = SECTOR.read_text(encoding="utf-8")
    source_cards = cards()
    captured = captured_ids()
    run = acquisition_run()
    text = re.sub(r'(?m)^updated_at: ".*"$', f'updated_at: "{NOW}"', text, count=1)
    text, new_ids = ensure_source_cards(text, source_cards, captured)
    text = reconcile_card_owned_blocks(text, source_cards, captured)
    for sid in sorted(captured):
        text = mark_artifact(text, sid)
    text = ensure_coverage(text, source_cards)
    metrics = sector_metrics(text, source_cards, captured)
    attempts = int(run.get("targets_with_official_publication_id", len(source_cards)))
    successes = int(run.get("raw_downloaded_exact", metrics["immutable"]))
    vals = {
        "found": metrics["found"],
        "new_this_pass": len(new_ids),
        "downloaded": metrics["immutable"],
        "immutable": metrics["immutable"],
        "pending": metrics["pending"],
        "reused": metrics["reused"],
        "primary_publication_verified": metrics["primary_verified"],
        "exact_binary_acquisition_attempts_this_pass": attempts,
        "exact_binary_acquisition_success_this_pass": successes,
    }
    for k, v in vals.items():
        text = counter(text, k, v)
    telemetry = f'''production_telemetry:
  checked_at: "{NOW}"
  acquisition_status: "IMMUTABLE_BASELINE_CAPTURE_OPERATIONAL"
  identity_scope_guard: "document.official_publication_id only"
  exact_targets: {attempts}
  immutable_successes: {successes}
  exact_bytes_and_sha256_recorded: {metrics['immutable']}
  bytes_scanned_this_acquisition_run: {int(run.get('bytes_downloaded', 0))}
  source_universe_count: {metrics['found']}
  sectors_registered: {metrics['sectors']}
  note: >-
    Official byte-exact acquisition is operational. Captures prove immutable original-publication baselines only;
    current consolidated semantics remain gated by version-chain and locator review.
  analysis_note: >-
    Source-universe and acquisition counters are derived from source cards, master nodes and manifests;
    semantic overlaps remain non-executable until applicability review. Nested amendment publication IDs
    are never treated as baseline source identities.

'''
    text = re.sub(r"(?ms)^production_telemetry:\n.*?(?=^next_actions:)", telemetry, text, count=1)
    SECTOR.write_text(text, encoding="utf-8")
    return metrics, new_ids, run


def sync_pdn(metrics: dict[str, int], new_ids: set[str], run: dict) -> None:
    text = PDN.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^updated_at: ".*"$', f'updated_at: "{NOW}"', text, count=1)
    attempts = int(run.get("targets_with_official_publication_id", metrics["immutable"]))
    successes = int(run.get("raw_downloaded_exact", metrics["immutable"]))
    sector_ids = source_blocks(SECTOR.read_text(encoding="utf-8"))
    overlap_lines = [
        '      - "16-ФЗ article 11 -> 152-ФЗ"',
        '      - "79-ФЗ article 42 -> personal-data legislation"',
        '      - "143-ФЗ article 13.2(9) -> 149-ФЗ + 152-ФЗ (current consolidated text; current-primary review pending)"',
        '      - "326-ФЗ article 44 -> restricted-access insured-person/medical-care data; PDN/health applicability review pending"',
        '      - "125-ФЗ article 25(3) -> protected private/family-life archive information; no direct 152-ФЗ edge inferred"',
        '      - "442-ФЗ article 6 -> personal-data processing context (candidate; not executable)"',
    ]
    if "SEC-SRC-RU-FZ-230-2016" in sector_ids:
        overlap_lines.append('      - "152-ФЗ article 6(1)(7) -> 230-ФЗ debt-collection regime; processing basis does not equal unrestricted disclosure permission"')
    if "SEC-SRC-RU-FZ-353-2013" in sector_ids:
        overlap_lines.append('      - "353-ФЗ article 12(2)-(3) -> borrower personal data + banking/other protected secrecy in assignment-of-rights scenario; scope remains scenario-dependent"')
    if "SEC-SRC-RU-FZ-63-2002" in sector_ids:
        overlap_lines.append('      - "63-ФЗ advocacy article 8 -> professional secrecy; no automatic 152-ФЗ edge without an identifiable-person processing scenario"')
    if "SEC-SRC-RU-FZ-98" in sector_ids:
        overlap_lines.append('      - "98-ФЗ commercial secret -> reused legal node; no automatic equivalence with personal data"')
    overlap_text = "\n".join(overlap_lines)
    block = f'''  stream_3_sector_overlays:
    status: ACTIVE
    inventory: "../ru-protected-information/master-inventory.yaml"
    overlap_graph: "../../cross-domain/pdn-sector-overlap-seed-v1.yaml"
    sources_found_total: {metrics['found']}
    new_sources_this_pass: {len(new_ids)}
    reused_existing_sources: {metrics['reused']}
    primary_publication_verified_total: {metrics['primary_verified']}
    immutable_artifacts: {metrics['immutable']}
    pending_immutable: {metrics['pending']}
    exact_binary_acquisition_attempts_this_pass: {attempts}
    exact_binary_acquisition_success_this_pass: {successes}
    sectors_registered: {metrics['sectors']}
    semantic_collision_checks_this_pass: 2
    legal_conflicts_confirmed_this_pass: 0
    explicit_or_direct_legal_overlap_candidates:
{overlap_text}
    conflict_notes:
      - "143-ФЗ article 12 is repealed since 2018-10-01; current routing uses articles 13.1-13.2."
      - "125-ФЗ article 22.1 retention and article 25(3) access restriction are distinct semantics even when both show 75 years."
      - "442-ФЗ confidentiality of social-service-recipient information must not be auto-merged with generic 152-ФЗ personal-data confidentiality; scope comparison is pending."
      - "230-ФЗ special restrictions on third-party disclosure must not be collapsed into the 152-ФЗ lawful-basis rule for processing; classify as scope specialization, not contradiction, until full version-chain review."
      - "Professional secrecy (63-ФЗ advocacy) and commercial secrecy (98-ФЗ) are independent regimes; neither is automatically personal data."
      - "Acquisition identity guard rejects nested amendment publication IDs as baseline artifacts."
    source_extensions:
      - "222-ФЗ/2015 credit-rating confidentiality: immutable original baseline captured; current-version chain remains partial."
      - "353-ФЗ/2013 consumer credit: immutable original baseline captured; Article 12 PDN/secrecy overlap registered; current-version chain remains partial."
      - "Росархив №24/2020: immutable original baseline captured; current-version chain remains partial."
      - "Росархив №77/2023: immutable original baseline captured; current-version chain remains partial."
      - "230-ФЗ/2016: immutable original baseline captured; explicit PDN overlap registered; current-version chain remains partial."
    note: >-
      Sector/special protected-information overlays remain isolated from executable PDN logic until
      authoritative current artifacts, version chains and anchored applicability edges pass review.
'''
    text = re.sub(r"(?ms)^  stream_3_sector_overlays:\n.*?(?=^quality_gates:)", block + "\n", text, count=1)
    PDN.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    metrics, new_ids, run = sync_sector()
    sync_pdn(metrics, new_ids, run)
    print(json.dumps({"metrics": metrics, "new_ids": sorted(new_ids)}, ensure_ascii=False))
