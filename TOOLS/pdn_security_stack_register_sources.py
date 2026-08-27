#!/usr/bin/env python3
"""Register explicitly declared Stream-2 source cards in the authoritative inventory.

A source card normally opts in with a top-level ``inventory_registration`` block
containing ``role`` and ``applicability``. A small explicit compatibility map is
kept for source cards that were already merged and immutably captured before that
registration field became mandatory. This keeps acquisition/accounting idempotent
without rewriting richer source-card provenance.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STACK = ROOT / "security-corpora" / "RU" / "152-FZ" / "security-stack"
SOURCE_DIR = STACK / "source"
INVENTORY = STACK / "PDN_SECURITY_STACK_SOURCE_INVENTORY.yaml"

ID_RE = re.compile(r"(?m)^id:\s*([^\s#]+)\s*$")
STATUS_RE = re.compile(r"(?m)^status:\s*([^\s#]+)\s*$")
REG_RE = re.compile(
    r"(?ms)^inventory_registration:\s*\n"
    r"(?:  .*\n)*?"
    r"  role:\s*([^\n#]+)\n"
    r"  applicability:\s*([^\n#]+)\s*$"
)

# These two cards were introduced immediately before the registration helper was
# extended to require inventory_registration. Their official PDFs were subsequently
# captured and manifested by the canonical publication-route acquirer. Registering
# them here repairs the counted-set gap without changing their legal applicability.
EXPLICIT_REGISTRATIONS: dict[str, tuple[str, str]] = {
    "SEC-SRC-RU-FSB547-2025": (
        "bounded_public_sector_incident_reporting_context",
        "PDN_INCIDENT_ONLY_WHEN_INDEPENDENT_SCOPE_IS_PROVED",
    ),
    "SEC-SRC-RU-FSB548-2025": (
        "bounded_public_sector_continuous_interaction_context",
        "PDN_INCIDENT_ONLY_WHEN_INDEPENDENT_SCOPE_IS_PROVED",
    ),
}


def clean(value: str) -> str:
    return value.strip().strip('"\'')


def main() -> int:
    text = INVENTORY.read_text(encoding="utf-8")
    existing = set(re.findall(r"(?m)^  - id:\s*([^\s#]+)\s*$", text))
    additions: list[str] = []

    for path in sorted(SOURCE_DIR.glob("*.yaml")):
        source = path.read_text(encoding="utf-8")
        mid, mst, mreg = ID_RE.search(source), STATUS_RE.search(source), REG_RE.search(source)
        if not mid or not mst or mst.group(1) != "METADATA_VERIFIED":
            continue
        sid = mid.group(1)
        if sid in existing:
            continue

        if mreg:
            role = clean(mreg.group(1))
            applicability = clean(mreg.group(2))
        elif sid in EXPLICIT_REGISTRATIONS:
            role, applicability = EXPLICIT_REGISTRATIONS[sid]
        else:
            continue

        rel = path.relative_to(STACK).as_posix()
        additions.append(
            f"  - id: {sid}\n"
            f"    role: {role}\n"
            "    metadata_status: METADATA_VERIFIED\n"
            f"    source_record: \"{rel}\"\n"
            "    raw_capture: PENDING\n"
            f"    applicability: {applicability}\n"
        )
        existing.add(sid)

    if not additions:
        print("STREAM2_SOURCE_REGISTRY_NOOP")
        return 0

    marker = "\nversion_edges:\n"
    if marker not in text:
        raise RuntimeError("version_edges anchor missing from Stream-2 inventory")
    text = text.replace(marker, "\n" + "".join(additions) + marker, 1)
    INVENTORY.write_text(text, encoding="utf-8")
    print(f"STREAM2_SOURCE_REGISTRY_ADDED={len(additions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
