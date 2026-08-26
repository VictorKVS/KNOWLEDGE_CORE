#!/usr/bin/env python3
"""Restore authoritative Stream-2 counters in the PDN master inventory.

The PDN core and the technical/crypto security-stack have independent acquisition
manifests and counters. This guard reads only the accepted Stream-2 acquisition
run and rewrites only the `security_stack:` block in the shared master inventory.
It prevents the core synchronizer from accidentally writing its own immutable /
pending counts into Stream-2 when identically named scalar keys exist later in the
same YAML file.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDN = ROOT / "security-corpora" / "RU" / "152-FZ"
MASTER = PDN / "PDN_MASTER_SOURCE_INVENTORY.yaml"
STACK_RUN = PDN / "security-stack" / "PDN_SECURITY_STACK_ACQUISITION_RUN.json"

SECTION_RE = re.compile(
    r"(?ms)^security_stack:\n.*?(?=^[A-Za-z_][A-Za-z0-9_-]*:\s*(?:.*)?$|\Z)"
)


def replace_scalar(block: str, key: str, value: object) -> str:
    rendered = json.dumps(value, ensure_ascii=False) if isinstance(value, str) else str(value)
    updated, count = re.subn(
        rf"(?m)^(  {re.escape(key)}:)\s*[^\n]+$",
        rf"\1 {rendered}",
        block,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"security_stack scalar missing: {key}")
    return updated


def main() -> int:
    if not MASTER.is_file() or not STACK_RUN.is_file():
        print("PDN_SECURITY_STACK_MASTER_RECONCILIATION_INPUT_MISSING")
        return 2

    run = json.loads(STACK_RUN.read_text(encoding="utf-8"))
    identified = int(run["sources_registered"])
    immutable = int(run["immutable_total"])
    pending = int(run["pending_after_run"])
    unrouted = run.get("unrouted_source_ids", [])
    if not isinstance(unrouted, list):
        raise RuntimeError("invalid Stream-2 unrouted_source_ids: expected list")
    unresolved_routes = len(unrouted)
    if immutable < 0 or pending < 0 or immutable + pending != identified:
        raise RuntimeError(
            f"invalid Stream-2 counters: identified={identified}, immutable={immutable}, pending={pending}"
        )
    if unresolved_routes < 0 or unresolved_routes > pending:
        raise RuntimeError(
            f"invalid Stream-2 unresolved route count: unresolved={unresolved_routes}, pending={pending}"
        )

    text = MASTER.read_text(encoding="utf-8")
    match = SECTION_RE.search(text)
    if not match:
        raise RuntimeError("security_stack block missing from PDN master inventory")

    block = match.group(0)
    block = replace_scalar(block, "identified", identified)
    block = replace_scalar(block, "immutable_sha256_verified", immutable)
    block = replace_scalar(block, "pending_raw_capture", pending)
    block = replace_scalar(block, "exact_official_route_unresolved", unresolved_routes)
    block = replace_scalar(block, "latest_acquisition_finished_at", str(run["finished_at"]))

    finished_date = str(run["finished_at"])[:10]
    block = replace_scalar(block, "checked_at", finished_date)

    updated = text[: match.start()] + block + text[match.end() :]
    MASTER.write_text(updated, encoding="utf-8")
    print(
        json.dumps(
            {
                "record_type": "PDN_SECURITY_STACK_MASTER_RECONCILIATION",
                "identified": identified,
                "immutable_sha256_verified": immutable,
                "pending_raw_capture": pending,
                "exact_official_route_unresolved": unresolved_routes,
                "source_run": str(STACK_RUN.relative_to(ROOT)).replace("\\", "/"),
                "finished_at": run["finished_at"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
