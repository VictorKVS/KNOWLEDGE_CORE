from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import yaml

SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    return value if isinstance(value, dict) else {}


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_source(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    identity = as_dict(record.get("identity"))
    lifecycle = as_dict(record.get("lifecycle"))
    provenance = as_dict(record.get("provenance"))
    verification = as_dict(provenance.get("verification"))
    fingerprint = as_dict(provenance.get("content_fingerprint"))
    applicability = as_dict(record.get("applicability"))

    for field in ("canonical_title", "source_class", "issuer", "jurisdiction", "edition_or_revision"):
        if not identity.get(field):
            errors.append(f"identity.{field} is required")
    for field in ("publication_date", "effective_from"):
        if not lifecycle.get(field):
            errors.append(f"lifecycle.{field} is required")
    for field in ("official_location", "retrieval_date"):
        if not provenance.get(field):
            errors.append(f"provenance.{field} is required")
    if fingerprint.get("algorithm") != "sha256":
        errors.append("content_fingerprint.algorithm must be sha256")
    if fingerprint.get("value") and not SHA256_RE.match(str(fingerprint.get("value"))):
        errors.append("content_fingerprint.value must be a 64-character SHA-256 hex digest")

    state = str(verification.get("state") or record.get("status") or "UNVERIFIED").upper()
    if state == "VERIFIED":
        for field in ("checked_at", "checked_by"):
            if not verification.get(field):
                errors.append(f"VERIFIED source requires provenance.verification.{field}")
        if not fingerprint.get("value"):
            errors.append("VERIFIED source requires content fingerprint")
        if not any(as_list(applicability.get(k)) for k in ("subjects", "systems", "data_classes", "sectors", "conditions", "exclusions")) and not as_list(applicability.get("notes")):
            errors.append("VERIFIED source requires applicability information")
    return errors


def validate_ingestion(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    capture = as_dict(record.get("capture"))
    verification = as_dict(record.get("verification"))
    normalization = as_dict(record.get("normalization"))
    quality = as_dict(record.get("quality"))
    fingerprint = as_dict(capture.get("fingerprint"))

    if not record.get("source_ref"):
        errors.append("source_ref is required")
    for field in ("retrieved_from", "retrieved_at", "transport_or_method", "media_type", "raw_artifact_ref"):
        if not capture.get(field):
            errors.append(f"capture.{field} is required")
    if fingerprint.get("algorithm") != "sha256":
        errors.append("capture.fingerprint.algorithm must be sha256")
    if fingerprint.get("value") and not SHA256_RE.match(str(fingerprint.get("value"))):
        errors.append("capture.fingerprint.value must be a 64-character SHA-256 hex digest")

    ready = quality.get("ready_for_requirement_extraction") is True
    if ready:
        required_checks = (
            "official_origin_confirmed",
            "title_confirmed",
            "issuer_confirmed",
            "revision_confirmed",
            "effective_status_confirmed",
        )
        for field in required_checks:
            if verification.get(field) is not True:
                errors.append(f"ready ingestion requires verification.{field}=true")
        if normalization.get("structure_preserved") is not True:
            errors.append("ready ingestion requires normalization.structure_preserved=true")
        if as_list(quality.get("missing_pages_or_sections")):
            errors.append("ready ingestion cannot have missing pages or sections")
        if as_list(quality.get("unreadable_fragments")):
            errors.append("ready ingestion cannot have unreadable fragments")
    return errors


def validate(record: dict[str, Any]) -> list[str]:
    kind = record.get("kind")
    if kind == "security-source":
        return validate_source(record)
    if kind == "security-source-ingestion":
        return validate_ingestion(record)
    return ["kind must be security-source or security-source-ingestion"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Security Source Registry and ingestion records")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.paths:
        errors = validate(load(path))
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
