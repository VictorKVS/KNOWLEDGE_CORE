from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ALLOWED_FAMILY_STATUSES = {
    "NOT_REGISTERED",
    "REGISTERED",
    "SOURCE_PENDING",
    "SOURCE_ACQUIRED",
    "STATUS_VERIFIED",
    "VERSIONED",
    "CHUNKED",
    "ATOMIZED",
    "LINKED",
    "EXPERT_REVIEWED",
    "COMPLETE",
}

OFFICIAL_HOSTS = {
    "OFFICIAL_PUBLICATION": {"publication.pravo.gov.ru"},
    "OFFICIAL_STANDARD_REGISTRY": {"protect.gost.ru"},
    "PRIMARY_REGULATOR_DYNAMIC_CATALOG": {"bduasutp.fstec.ru"},
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("document root must be a mapping")
    return value


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def present_scalar(value: Any) -> bool:
    return nonempty(value) or isinstance(value, date)


def valid_https_url(value: Any) -> bool:
    if not nonempty(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.hostname)


def load_inventory(path: Path) -> tuple[dict[str, Any], set[str]]:
    inventory = load_yaml(path)
    families = inventory.get("source_families")
    if not isinstance(families, dict):
        raise ValueError("master inventory source_families must be a mapping")
    statuses = inventory.get("status_values")
    if not isinstance(statuses, list) or not statuses:
        raise ValueError("master inventory status_values must be a non-empty list")
    return families, {str(value) for value in statuses}


def validate_registry(path: Path, families: dict[str, Any], inventory_statuses: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        registry = load_yaml(path)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        return [f"{path}: invalid YAML: {exc}"]

    family_id = registry.get("family_id")
    if not nonempty(family_id):
        errors.append(f"{path}: family_id is required")
        return errors

    family = families.get(family_id)
    if not isinstance(family, dict):
        errors.append(f"{path}: family_id {family_id!r} is not present in master-source-inventory.yaml")
        return errors

    priority = registry.get("priority")
    if priority != family.get("priority"):
        errors.append(
            f"{path}: priority {priority!r} does not match inventory priority {family.get('priority')!r}"
        )

    status = registry.get("family_status")
    if status not in ALLOWED_FAMILY_STATUSES or status not in inventory_statuses:
        errors.append(f"{path}: family_status {status!r} is not an allowed inventory status")
    elif status != family.get("status"):
        errors.append(
            f"{path}: family_status {status!r} does not match inventory status {family.get('status')!r}"
        )

    if not present_scalar(registry.get("checked_at")):
        errors.append(f"{path}: checked_at is required")
    if not nonempty(registry.get("status_policy")):
        errors.append(f"{path}: status_policy is required")

    sources = registry.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append(f"{path}: sources must be a non-empty list")
        return errors

    source_ids: set[str] = set()
    has_dynamic_source = False
    for index, source in enumerate(sources):
        where = f"{path}: sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{where}: source must be a mapping")
            continue
        source_id = source.get("id")
        if not nonempty(source_id):
            errors.append(f"{where}: id is required")
        elif source_id in source_ids:
            errors.append(f"{where}: duplicate source id {source_id}")
        else:
            source_ids.add(source_id)

        ingestion_status = source.get("ingestion_status")
        if not nonempty(ingestion_status):
            errors.append(f"{where}: ingestion_status is required")

        authority_class = source.get("authority_class")
        source_url = source.get("source_url")
        if authority_class in OFFICIAL_HOSTS:
            if not valid_https_url(source_url):
                errors.append(f"{where}: {authority_class} requires an HTTPS source_url")
            else:
                hostname = urlparse(source_url).hostname
                if hostname not in OFFICIAL_HOSTS[authority_class]:
                    allowed = ", ".join(sorted(OFFICIAL_HOSTS[authority_class]))
                    errors.append(f"{where}: {authority_class} source_url must use one of: {allowed}")

        if ingestion_status == "STATUS_VERIFIED_METADATA_ONLY":
            if not present_scalar(source.get("status_observed")):
                errors.append(f"{where}: STATUS_VERIFIED_METADATA_ONLY requires status_observed")
            if not valid_https_url(source_url):
                errors.append(f"{where}: STATUS_VERIFIED_METADATA_ONLY requires an HTTPS source_url")

        if ingestion_status == "SOURCE_ACQUIRED_DYNAMIC" or source.get("snapshot_required") is True:
            has_dynamic_source = True
            if source.get("snapshot_required") is not True:
                errors.append(f"{where}: dynamic acquired sources must set snapshot_required: true")
            if not valid_https_url(source_url):
                errors.append(f"{where}: dynamic acquired sources require an HTTPS source_url")

    observations = registry.get("verified_observations", [])
    if not isinstance(observations, list):
        errors.append(f"{path}: verified_observations must be a list when present")
        return errors

    observation_ids: set[str] = set()
    for index, observation in enumerate(observations):
        where = f"{path}: verified_observations[{index}]"
        if not isinstance(observation, dict):
            errors.append(f"{where}: observation must be a mapping")
            continue
        observation_id = observation.get("id")
        if not nonempty(observation_id):
            errors.append(f"{where}: id is required")
        elif observation_id in observation_ids:
            errors.append(f"{where}: duplicate observation id {observation_id}")
        else:
            observation_ids.add(observation_id)

        if observation.get("verification_status") != "VERIFIED_CATALOG_RECORD":
            errors.append(f"{where}: verified observation must use VERIFIED_CATALOG_RECORD")
        if not valid_https_url(observation.get("source_url")):
            errors.append(f"{where}: verified observation requires an HTTPS source_url")
        if has_dynamic_source and not present_scalar(observation.get("observed_at")):
            errors.append(f"{where}: dynamic verified observation requires observed_at")

    blocks = registry.get("red_team_blocks")
    if not isinstance(blocks, list) or not blocks or not all(nonempty(item) for item in blocks):
        errors.append(f"{path}: red_team_blocks must be a non-empty list of explicit limitations")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on Security Knowledge family registries that drift from the master inventory or overstate source evidence."
    )
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    try:
        families, inventory_statuses = load_inventory(args.inventory)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        print(f"ERROR: {args.inventory}: invalid master inventory: {exc}")
        return 1

    errors: list[str] = []
    for path in args.files:
        errors.extend(validate_registry(path, families, inventory_statuses))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"security-source-registry-gate: FAIL ({len(errors)} error(s))")
        return 1

    print(f"security-source-registry-gate: PASS ({len(args.files)} registry file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
