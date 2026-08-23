#!/usr/bin/env python3
"""Register explicitly declared Stream-2 source cards in the authoritative inventory.

A source card opts in with a top-level ``inventory_registration`` block containing
``role`` and ``applicability``. This keeps discovery metadata next to the source
while preserving the inventory as the authoritative counted set used by acquisition.
The helper is idempotent and never promotes capture state.
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


def clean(value: str) -> str:
    return value.strip().strip('"\'')


def main() -> int:
    text = INVENTORY.read_text(encoding="utf-8")
    existing = set(re.findall(r"(?m)^  - id:\s*([^\s#]+)\s*$", text))
    additions: list[str] = []

    for path in sorted(SOURCE_DIR.glob("*.yaml")):
        source = path.read_text(encoding="utf-8")
        mid, mst, mreg = ID_RE.search(source), STATUS_RE.search(source), REG_RE.search(source)
        if not mid or not mst or not mreg or mst.group(1) != "METADATA_VERIFIED":
            continue
        sid = mid.group(1)
        if sid in existing:
            continue
        role = clean(mreg.group(1))
        applicability = clean(mreg.group(2))
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
