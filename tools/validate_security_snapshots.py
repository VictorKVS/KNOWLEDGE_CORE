from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "security-knowledge" / "corpus" / "snapshots"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_STATES = {
    "CANDIDATE",
    "SOURCE_VERIFIED",
    "ATOMIZED",
    "APPLICABILITY_REVIEWED",
    "CONTROL_MAPPED",
    "EXPERT_REVIEWED",
    "VERIFIED",
    "STALE",
    "DISPUTED",
    "SUPERSEDED",
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def git_object_bytes(commit: str, rel_path: str) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{rel_path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"PINNED_GIT_OBJECT_UNRESOLVABLE:{detail}")
    return proc.stdout


def validate_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValueError("INVALID_REPOSITORY_RELATIVE_PATH")
    normalized = path.as_posix()
    if not normalized.startswith("security-knowledge/"):
        raise ValueError("OBJECT_OUTSIDE_SECURITY_KNOWLEDGE_ROOT")
    return normalized


def digest_material(data: dict) -> dict:
    selected = []
    for item in sorted(data["selected_objects"], key=lambda row: (str(row["object_id"]), str(row["version_id"]))):
        selected.append(
            {
                "object_id": item["object_id"],
                "version_id": item["version_id"],
                "object_type": item["object_type"],
                "repository_relative_path": item["repository_relative_path"],
                "content_digest_sha256": item["content_digest_sha256"],
                "knowledge_state": item["knowledge_state"],
                "selection_reason": item["selection_reason"],
                "source_locator_ref": item.get("source_locator_ref"),
            }
        )
    return {
        "manifest_id": data["manifest_id"],
        "knowledge_space_id": data["knowledge_space_id"],
        "canonical_repository": data["canonical_repository"],
        "repository_commit_sha": data["repository_commit_sha"],
        "content_root": data["content_root"],
        "selection_request_ref": data["selection_request_ref"],
        "selected_objects": selected,
        "hash_algorithm": data["hash_algorithm"],
    }


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path.relative_to(ROOT)}: invalid YAML: {exc}"]

    rel = path.relative_to(ROOT)
    if not isinstance(data, dict):
        return [f"{rel}: manifest must be an object"]

    required = {
        "manifest_id",
        "knowledge_space_id",
        "canonical_repository",
        "repository_commit_sha",
        "content_root",
        "selection_request_ref",
        "selected_objects",
        "manifest_digest",
        "hash_algorithm",
    }
    missing = sorted(required - set(data))
    if missing:
        return [f"{rel}: missing required fields {missing}"]

    commit = str(data["repository_commit_sha"]).lower()
    if not SHA40_RE.fullmatch(commit):
        errors.append(f"{rel}: repository_commit_sha must be exact 40-hex commit")
    if data["knowledge_space_id"] != "KB-SECURITY":
        errors.append(f"{rel}: knowledge_space_id must be KB-SECURITY")
    if data["canonical_repository"] != "VictorKVS/KNOWLEDGE_CORE":
        errors.append(f"{rel}: unexpected canonical_repository")
    if data["content_root"] != "security-knowledge/":
        errors.append(f"{rel}: unexpected content_root")
    if data["hash_algorithm"] != "sha256":
        errors.append(f"{rel}: unsupported hash_algorithm")

    objects = data.get("selected_objects")
    if not isinstance(objects, list) or not objects:
        errors.append(f"{rel}: selected_objects must be a non-empty list")
        return errors

    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(objects):
        label = f"{rel}: selected_objects[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        for key in (
            "object_id",
            "version_id",
            "object_type",
            "repository_relative_path",
            "content_digest_sha256",
            "knowledge_state",
            "selection_reason",
        ):
            if not item.get(key):
                errors.append(f"{label}: missing {key}")

        object_id = str(item.get("object_id", ""))
        version_id = str(item.get("version_id", ""))
        pair = (object_id, version_id)
        if pair in seen:
            errors.append(f"{label}: duplicate object/version {pair}")
        seen.add(pair)

        state = str(item.get("knowledge_state", ""))
        if state not in ALLOWED_STATES:
            errors.append(f"{label}: invalid knowledge_state {state}")
        if state in {"SOURCE_VERIFIED", "VERIFIED"} and not item.get("source_locator_ref"):
            errors.append(f"{label}: {state} requires source_locator_ref")

        digest = str(item.get("content_digest_sha256", "")).lower()
        if not SHA256_RE.fullmatch(digest):
            errors.append(f"{label}: invalid content_digest_sha256")
            continue

        try:
            rel_path = validate_path(str(item.get("repository_relative_path", "")))
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
            continue

        if SHA40_RE.fullmatch(commit):
            try:
                pinned_bytes = git_object_bytes(commit, rel_path)
            except ValueError as exc:
                errors.append(f"{label}: {exc}")
            else:
                actual = hashlib.sha256(pinned_bytes).hexdigest()
                if actual != digest:
                    errors.append(f"{label}: PINNED_CONTENT_DIGEST_MISMATCH expected={digest} actual={actual}")

    expected_manifest_digest = str(data.get("manifest_digest", "")).lower()
    if not SHA256_RE.fullmatch(expected_manifest_digest):
        errors.append(f"{rel}: invalid manifest_digest")
    else:
        actual_manifest_digest = hashlib.sha256(canonical(digest_material(data))).hexdigest()
        if actual_manifest_digest != expected_manifest_digest:
            errors.append(
                f"{rel}: MANIFEST_DIGEST_MISMATCH expected={expected_manifest_digest} actual={actual_manifest_digest}"
            )

    return errors


def main() -> int:
    if not SNAPSHOT_DIR.exists():
        print("Security snapshot validation: no snapshot directory; nothing to validate.")
        return 0

    manifests = sorted(SNAPSHOT_DIR.glob("*.yaml"))
    if not manifests:
        print("Security snapshot validation: no manifests; nothing to validate.")
        return 0

    errors: list[str] = []
    for manifest in manifests:
        errors.extend(validate_manifest(manifest))

    if errors:
        print("Security snapshot validation FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Security snapshot validation PASSED for {len(manifests)} manifest(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
