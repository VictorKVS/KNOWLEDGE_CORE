from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "REPOSITORY_STRUCTURE_PROTECTION.yaml"
DOMAIN_REGISTRY = ROOT / "father" / "domain-knowledge" / "domain-registry.yaml"
ALLOWED_CLASSES = {"DO_NOT_MOVE", "MIGRATION_ONLY", "CAN_REORGANIZE"}
ALLOWED_KINDS = {"file", "directory"}
INACTIVE_DOMAIN_STATES = {"PLANNED", "IN_PROGRESS"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a YAML mapping")
    return data


def validate() -> None:
    data = load_yaml(REGISTRY)
    if data.get("status") != "ACTIVE":
        fail("repository structure protection registry must be ACTIVE")
    if data.get("repository") != "VictorKVS/KNOWLEDGE_CORE":
        fail("repository identity mismatch in structure protection registry")

    entries = data.get("protected_surfaces")
    if not isinstance(entries, list) or not entries:
        fail("protected_surfaces must be a non-empty list")

    ids: set[str] = set()
    paths: set[str] = set()
    path_classes: dict[str, str] = {}
    has_self_protection = False
    for entry in entries:
        if not isinstance(entry, dict):
            fail("every protected surface must be a mapping")
        entry_id = entry.get("id")
        path_text = entry.get("path")
        kind = entry.get("kind")
        protection_class = entry.get("class")
        owner = entry.get("owner")
        reason = entry.get("reason")
        if not all(isinstance(v, str) and v.strip() for v in (entry_id, path_text, owner, reason)):
            fail(f"invalid protected surface entry: {entry!r}")
        if entry_id in ids:
            fail(f"duplicate protected surface id: {entry_id}")
        if path_text in paths:
            fail(f"duplicate protected surface path: {path_text}")
        ids.add(entry_id)
        paths.add(path_text)
        path_classes[path_text] = protection_class

        if kind not in ALLOWED_KINDS:
            fail(f"{entry_id}: unsupported kind {kind!r}")
        if protection_class not in ALLOWED_CLASSES:
            fail(f"{entry_id}: unsupported protection class {protection_class!r}")

        path = ROOT / path_text
        if not path.exists():
            fail(f"{entry_id}: protected path missing: {path_text}")
        if kind == "file" and not path.is_file():
            fail(f"{entry_id}: expected file: {path_text}")
        if kind == "directory" and not path.is_dir():
            fail(f"{entry_id}: expected directory: {path_text}")
        if path_text == "REPOSITORY_STRUCTURE_PROTECTION.yaml" and protection_class == "DO_NOT_MOVE":
            has_self_protection = True

    if not has_self_protection:
        fail("registry must protect itself as DO_NOT_MOVE")

    prefixes = data.get("reserved_protected_prefixes", [])
    if not isinstance(prefixes, list):
        fail("reserved_protected_prefixes must be a list")
    for item in prefixes:
        prefix = item.get("prefix") if isinstance(item, dict) else None
        rule = item.get("rule") if isinstance(item, dict) else None
        if not isinstance(prefix, str) or not prefix.strip() or not isinstance(rule, str) or not rule.strip():
            fail("each reserved protected prefix requires prefix and rule")

    # Every activated non-Security professional domain becomes a stable structural identity.
    # The domain cannot be activated while remaining only implicitly covered by the root prefix:
    # it must receive its own DO_NOT_MOVE entry so future restructures have an explicit inventory.
    domain_registry = load_yaml(DOMAIN_REGISTRY)
    for domain in domain_registry.get("domains", []):
        if not isinstance(domain, dict):
            fail("domain registry entries must be mappings")
        domain_id = domain.get("id")
        status = domain.get("status")
        canonical_tree = domain.get("canonical_tree")
        if domain_id == "SECURITY" or status in INACTIVE_DOMAIN_STATES:
            continue
        if not isinstance(canonical_tree, str) or not canonical_tree.startswith("professional-knowledge/"):
            fail(f"{domain_id}: activated professional domain must use professional-knowledge/ canonical_tree")
        canonical_path = canonical_tree.rstrip("/")
        if path_classes.get(canonical_path) != "DO_NOT_MOVE":
            fail(
                f"{domain_id}: activated canonical tree must be explicitly registered as DO_NOT_MOVE: "
                f"{canonical_path}"
            )

    migration = data.get("migration_requirements", {})
    prefix = migration.get("required_record_path_prefix")
    required_fields = migration.get("required_fields")
    if not isinstance(prefix, str) or not prefix.strip():
        fail("migration record path prefix is required")
    migration_dir = ROOT / prefix.rstrip("/")
    if not migration_dir.is_dir():
        fail(f"migration record directory missing: {prefix}")
    if not isinstance(required_fields, list) or not required_fields:
        fail("migration required_fields must be non-empty")

    print(
        f"OK: {len(entries)} protected KNOWLEDGE_CORE surfaces are present; "
        "activated professional domains have explicit structural protection"
    )


def main() -> int:
    validate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
