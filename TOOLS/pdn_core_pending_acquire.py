#!/usr/bin/env python3
"""Reuse-first acquisition wrapper for the RU PDN core.

Existing accepted immutable captures are verified locally (manifest proof, artifact
existence and SHA-256) and reused instead of being downloaded again. Only sources
without an accepted local immutable artifact are sent through the network acquirer.
This turns recurring acquisition into a delta process and prevents repeated downloads
of unchanged official publication artifacts.

Sources with dedicated guarded transports are excluded from the generic network loop
so a slow special route cannot delay easy publication-ID deltas such as PP12.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

from pdn_core_acquire import (
    MANIFEST_DIR,
    RAW_DIR,
    ROOT,
    RUN_FILE,
    capture_canonical_snapshot,
    capture_publication_pdf,
    discover_targets,
)
from pdn_core_sync_capture import manifest_is_raw_verified

DEDICATED_CAPTURE_SOURCE_IDS = {"SEC-SRC-RU-PP687-2008"}


def reusable_manifest(source_id: str) -> dict | None:
    path = MANIFEST_DIR / f"{source_id}.json"
    if not path.exists():
        return None
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if manifest.get("source_id") != source_id or not manifest_is_raw_verified(manifest):
        return None
    artifact_ref = manifest.get("artifact_ref")
    expected_sha = str(manifest.get("sha256") or "")
    if not artifact_ref or not expected_sha:
        return None
    artifact = ROOT / str(artifact_ref)
    if not artifact.is_file():
        return None
    actual_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if actual_sha != expected_sha:
        return None
    return manifest


def main() -> int:
    started = dt.datetime.now(dt.timezone.utc)
    targets = discover_targets()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    reused: list[dict[str, object]] = []
    pending_targets: list[dict[str, object]] = []
    dedicated_skipped: list[str] = []
    for target in targets:
        source_id = str(target["source_id"])
        manifest = reusable_manifest(source_id)
        if manifest is not None:
            reused.append({
                "source_id": source_id,
                "status": "REUSED_IMMUTABLE",
                "byte_length": manifest.get("byte_length"),
                "sha256": manifest.get("sha256"),
                "mime": manifest.get("mime"),
                "artifact_ref": manifest.get("artifact_ref"),
                "manifest_ref": f"security-corpora/RU/152-FZ/manifests/{source_id}.json",
            })
        elif source_id in DEDICATED_CAPTURE_SOURCE_IDS:
            dedicated_skipped.append(source_id)
        else:
            pending_targets.append(target)

    attempted: list[dict[str, object]] = []
    for target in pending_targets:
        source_id = str(target["source_id"])
        route = str(target["route"])
        value = str(target["value"])
        expected_number = str(target.get("expected_number") or "")
        source_record = Path(target["path"])
        row: dict[str, object] = {
            "source_id": source_id,
            "route": route,
            "source_document_number": expected_number,
            "status": "PENDING",
        }
        try:
            if route == "publication_pdf":
                manifest = capture_publication_pdf(source_id, value, expected_number, source_record)
            else:
                manifest = capture_canonical_snapshot(source_id, value, expected_number, source_record)
            mpath = MANIFEST_DIR / f"{source_id}.json"
            mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            row.update({
                "status": "IMMUTABLE_CAPTURED",
                "byte_length": manifest["byte_length"],
                "sha256": manifest["sha256"],
                "mime": manifest["mime"],
                "artifact_ref": manifest["artifact_ref"],
                "manifest_ref": str(mpath.relative_to(ROOT)).replace("\\", "/"),
            })
        except Exception as exc:
            row.update({"status": "PENDING", "error": str(exc)})
        attempted.append(row)

    newly_captured = sum(1 for row in attempted if row.get("status") == "IMMUTABLE_CAPTURED")
    pending = sum(1 for row in attempted if row.get("status") == "PENDING")
    run = {
        "schema_version": "1.4",
        "kind": "pdn-core-reuse-first-acquisition-run",
        "identity_scope_guard": "document.official_publication_id only",
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "targets_total": len(targets),
        "reused_immutable": len(reused),
        "network_targets_attempted": len(pending_targets),
        "dedicated_transport_pending": dedicated_skipped,
        "new_immutable_captured": newly_captured,
        "pending_after_run": pending + len(dedicated_skipped),
        "reuse_ratio": (len(reused) / len(targets)) if targets else 1.0,
        "reused": reused,
        "results": attempted,
    }
    RUN_FILE.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "targets_total": run["targets_total"],
        "reused_immutable": run["reused_immutable"],
        "network_targets_attempted": run["network_targets_attempted"],
        "dedicated_transport_pending": run["dedicated_transport_pending"],
        "new_immutable_captured": run["new_immutable_captured"],
        "pending_after_run": run["pending_after_run"],
        "reuse_ratio": run["reuse_ratio"],
    }, ensure_ascii=False))
    return 0 if pending == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
