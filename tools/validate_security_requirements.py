from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SECURITY_ROOT = ROOT / "security-knowledge"
ALLOWED_VERIFICATION_STATES = {"UNVERIFIED", "EXTRACTED", "REVIEWED", "VERIFIED"}


def has_nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def requirement_files(root: Path = SECURITY_ROOT):
    for path in root.rglob("*.yaml"):
        if "requirements" not in path.parts:
            continue
        if path.name == "schema.yaml":
            continue
        yield path


def validate_requirement_document(path: Path, data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return errors

    requirements = data.get("requirements")
    if requirements is None:
        return errors
    if not isinstance(requirements, list):
        return [f"{path}: requirements must be a list"]

    source_document = data.get("document") or data.get("document_id") or data.get("source_document_id")

    for index, item in enumerate(requirements):
        label = f"{path}: requirements[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue

        requirement_id = item.get("id") or item.get("requirement_id")
        if not has_nonempty(requirement_id):
            errors.append(f"{label} requires id/requirement_id")

        state = str(item.get("verification", "")).upper()
        if state not in ALLOWED_VERIFICATION_STATES:
            errors.append(f"{label} has invalid or missing verification state {state or '<empty>'}")
            continue

        if state != "VERIFIED":
            continue

        if not has_nonempty(source_document):
            errors.append(f"{label} VERIFIED requires source document identity")
        if not has_nonempty(item.get("source_locator")):
            errors.append(f"{label} VERIFIED requires exact source_locator")
        if not has_nonempty(item.get("source_quote")):
            errors.append(f"{label} VERIFIED requires source_quote from the admitted source")

    return errors


def main() -> int:
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    files_checked = 0
    requirements_checked = 0
    verified_checked = 0

    for path in requirement_files():
        files_checked += 1
        rel = path.relative_to(ROOT)
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{rel}: invalid YAML: {exc}")
            continue

        errors.extend(validate_requirement_document(rel, data))
        if not isinstance(data, dict) or not isinstance(data.get("requirements"), list):
            continue

        for item in data["requirements"]:
            if not isinstance(item, dict):
                continue
            requirements_checked += 1
            requirement_id = item.get("id") or item.get("requirement_id")
            if has_nonempty(requirement_id):
                requirement_id = str(requirement_id)
                if requirement_id in seen_ids:
                    errors.append(
                        f"{rel}: duplicate atomic requirement id {requirement_id}; "
                        f"first seen in {seen_ids[requirement_id]}"
                    )
                else:
                    seen_ids[requirement_id] = rel
            if str(item.get("verification", "")).upper() == "VERIFIED":
                verified_checked += 1

    if errors:
        print("Security atomic requirement quality gate FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Security atomic requirement quality gate PASSED. "
        f"Checked {files_checked} files / {requirements_checked} atomic requirements / "
        f"{verified_checked} VERIFIED requirements."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
