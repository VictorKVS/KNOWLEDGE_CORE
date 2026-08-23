#!/usr/bin/env python3
"""Reconcile Stream-2 telemetry from the accepted acquisition run record."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STACK = ROOT / "security-corpora" / "RU" / "152-FZ" / "security-stack"
SOURCE_DIR = STACK / "source"
RUN_FILE = STACK / "PDN_SECURITY_STACK_ACQUISITION_RUN.json"
STATUS_FILE = STACK / "STREAM2_STATUS_2026-08-22.yaml"

STATUS_RE = re.compile(r"(?m)^status:\s*([^\s#]+)\s*$")
PUB_RE = re.compile(r"(?m)^  official_publication_id:\s*[\"']?[0-9]{16}[\"']?\s*$")
URL_RE = re.compile(r"(?m)^  url:\s*[\"'][^\"']+[\"']\s*$")


def replace_scalar(text: str, key: str, value: object) -> str:
    quoted = json.dumps(value, ensure_ascii=False) if isinstance(value, str) else str(value)
    return re.sub(rf"(?m)^(  {re.escape(key)}:)\s*[^\n]+$", rf"\1 {quoted}", text, count=1)


def main() -> int:
    if not RUN_FILE.is_file() or not STATUS_FILE.is_file():
        print("STREAM2_TELEMETRY_INPUT_MISSING")
        return 2
    run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
    verified = 0
    publication_targets = 0
    canonical_targets = 0
    for path in SOURCE_DIR.glob("*.yaml"):
        source = path.read_text(encoding="utf-8")
        status = STATUS_RE.search(source)
        if not status or status.group(1) != "METADATA_VERIFIED":
            continue
        verified += 1
        if PUB_RE.search(source):
            publication_targets += 1
        elif URL_RE.search(source):
            canonical_targets += 1

    text = STATUS_FILE.read_text(encoding="utf-8")
    static_values = {
        "sources_identified": int(run["sources_registered"]),
        "sources_metadata_verified": verified,
        "official_publication_id_targets": publication_targets,
        "official_canonical_targets": canonical_targets,
        "exact_official_route_unresolved": len(run.get("unrouted_source_ids", [])),
        "raw_downloaded_exact": int(run["immutable_total"]),
        "immutable_sha256_verified": int(run["immutable_total"]),
        "pending_raw_capture": int(run["pending_after_run"]),
    }
    for key, value in static_values.items():
        text = replace_scalar(text, key, value)

    latest_values = {
        "latest_run_finished_at": str(run["finished_at"]),
        "reused_immutable_in_latest_run": int(run["reused_immutable"]),
        "network_targets_attempted_in_latest_run": int(run["network_targets_attempted"]),
        "new_immutable_in_latest_run": int(run["new_immutable_captured"]),
        "immutable_total_after_latest_run": int(run["immutable_total"]),
        "pending_after_latest_run": int(run["pending_after_run"]),
    }
    for key, value in latest_values.items():
        text = replace_scalar(text, key, value)

    state = "IMMUTABLE_CAPTURE_COMPLETE" if int(run["pending_after_run"]) == 0 else "PARTIAL_IMMUTABLE_CAPTURED"
    text = replace_scalar(text, "status", state)
    STATUS_FILE.write_text(text, encoding="utf-8")
    print(json.dumps({"status": state, **static_values, **latest_values}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
