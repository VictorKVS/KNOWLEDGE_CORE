from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

VERIFIED_SOURCE = "STATUS_VERIFIED"
VERIFIED_FACT = "VERIFIED"
OFFICIAL_PUBLICATION_HOST = "publication.pravo.gov.ru"
OFFICIAL_TEXT_HOST = "ips.pravo.gov.ru"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("document root must be a mapping")
    return value


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def present_scalar(value: Any) -> bool:
    return nonempty(value) or isinstance(value, date)


def valid_official_url(value: Any, hostname: str) -> bool:
    if not nonempty(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname == hostname


def validate_pack(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        pack = load_yaml(path)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        return [f"{path}: invalid YAML: {exc}"]

    pack_id = pack.get("pack_id")
    if not nonempty(pack_id):
        errors.append(f"{path}: pack_id is required")

    sources = pack.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append(f"{path}: sources must be a non-empty list")
        return errors

    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        where = f"{path}: sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{where}: source must be a mapping")
            continue
        source_id = source.get("source_id")
        if not nonempty(source_id):
            errors.append(f"{where}: source_id is required")
            continue
        if source_id in source_ids:
            errors.append(f"{where}: duplicate source_id {source_id}")
        source_ids.add(source_id)

        if source.get("verification_status") == VERIFIED_SOURCE:
            publication = source.get("official_publication")
            official_text = source.get("official_text")
            has_publication = isinstance(publication, dict)
            has_official_text = isinstance(official_text, dict)

            if not has_publication and not has_official_text:
                errors.append(
                    f"{where}: VERIFIED source requires official_publication or official_text"
                )
                continue

            if has_publication:
                if not nonempty(publication.get("publication_number")):
                    errors.append(
                        f"{where}: VERIFIED source requires official_publication.publication_number"
                    )
                if not present_scalar(publication.get("publication_date")):
                    errors.append(
                        f"{where}: VERIFIED source requires official_publication.publication_date"
                    )
                url = publication.get("url")
                if not valid_official_url(url, OFFICIAL_PUBLICATION_HOST):
                    errors.append(
                        f"{where}: official_publication.url must use https://{OFFICIAL_PUBLICATION_HOST}"
                    )

            if has_official_text:
                url = official_text.get("url")
                if not valid_official_url(url, OFFICIAL_TEXT_HOST):
                    errors.append(
                        f"{where}: official_text.url must use https://{OFFICIAL_TEXT_HOST}"
                    )
                if not nonempty(official_text.get("edition_as_of")) and not isinstance(
                    official_text.get("edition_as_of"), date
                ):
                    errors.append(
                        f"{where}: VERIFIED official_text requires edition_as_of"
                    )

    facts = pack.get("atomic_facts", [])
    if not isinstance(facts, list):
        errors.append(f"{path}: atomic_facts must be a list when present")
        return errors

    fact_ids: set[str] = set()
    for index, fact in enumerate(facts):
        where = f"{path}: atomic_facts[{index}]"
        if not isinstance(fact, dict):
            errors.append(f"{where}: fact must be a mapping")
            continue
        fact_id = fact.get("fact_id")
        if not nonempty(fact_id):
            errors.append(f"{where}: fact_id is required")
        elif fact_id in fact_ids:
            errors.append(f"{where}: duplicate fact_id {fact_id}")
        else:
            fact_ids.add(fact_id)

        source_id = fact.get("source_id")
        if source_id not in source_ids:
            errors.append(f"{where}: source_id {source_id!r} does not resolve inside the pack")

        if fact.get("verification_status") == VERIFIED_FACT:
            if not nonempty(fact.get("locator")):
                errors.append(f"{where}: VERIFIED fact requires an exact source locator")
            if not nonempty(fact.get("statement")):
                errors.append(f"{where}: VERIFIED fact requires a conservative atomic statement")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on Security Knowledge source packs that overstate verification."
    )
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    for path in args.files:
        errors.extend(validate_pack(path))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"security-source-pack-gate: FAIL ({len(errors)} error(s))")
        return 1

    print(f"security-source-pack-gate: PASS ({len(args.files)} pack(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
