from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "father/domain-knowledge/domain-registry.yaml"
MATURITY_MODEL = ROOT / "father/domain-knowledge/PROFESSIONAL_KB_MATURITY_MODEL.yaml"

ALLOWED_STATUSES = {
    "PLANNED",
    "IN_PROGRESS",
    "M0_SCOPE_DEFINED",
    "M1_SOURCES_ADMITTED",
    "M2_ATOMIC_KNOWLEDGE",
    "M3_DECISION_LOGIC",
    "M4_VERIFIED_PRACTICE",
    "M5_BOUNDED_EXPERT_READY",
}

M0_REQUIRED_DOMAIN_KEYS = {
    "domain_id",
    "title",
    "logical_knowledge_space_ref",
    "canonical_tree",
    "maturity",
    "scope",
    "non_scope",
    "ontology",
    "source_taxonomy",
    "source_precedence",
    "freshness_policy",
    "conflict_policy",
    "objectivity_policy",
    "decision_evidence_policy",
    "legacy_material_policy",
    "promotion_plan",
}

LEVEL_TO_STATUS = {
    "M0": "M0_SCOPE_DEFINED",
    "M1": "M1_SOURCES_ADMITTED",
    "M2": "M2_ATOMIC_KNOWLEDGE",
    "M3": "M3_DECISION_LOGIC",
    "M4": "M4_VERIFIED_PRACTICE",
    "M5": "M5_BOUNDED_EXPERT_READY",
}


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def validate_common_model() -> None:
    model = load_yaml(MATURITY_MODEL)
    levels = model.get("levels", {})
    if list(levels.keys()) != ["M0", "M1", "M2", "M3", "M4", "M5"]:
        fail("professional maturity model must define ordered levels M0..M5")
    invariants = model.get("core_invariants", [])
    required = {
        "facts_interpretations_recommendations_and_decisions_are_distinct_objects",
        "model_output_is_candidate_material_not_primary_authority",
        "maturity_is_bounded_by_the_weakest_required_gate_for_the_claimed_scope",
    }
    if not required.issubset(set(invariants)):
        fail("professional maturity model is missing required evidence/objectivity invariants")


def validate_domain_entry(entry: dict) -> None:
    domain_id = entry.get("id")
    status = entry.get("status")
    if not domain_id:
        fail("domain entry without id")
    if status not in ALLOWED_STATUSES:
        fail(f"{domain_id}: unsupported status {status!r}")
    if status in {"PLANNED", "IN_PROGRESS"}:
        return

    canonical_tree = entry.get("canonical_tree")
    logical_ref = entry.get("logical_knowledge_space_ref")
    maturity_ref = entry.get("maturity_ref")
    source_policy_ref = entry.get("source_policy_ref")
    roadmap_ref = entry.get("roadmap_ref")
    for name, value in {
        "canonical_tree": canonical_tree,
        "logical_knowledge_space_ref": logical_ref,
        "maturity_ref": maturity_ref,
        "source_policy_ref": source_policy_ref,
        "roadmap_ref": roadmap_ref,
    }.items():
        if not value:
            fail(f"{domain_id}: activated domain missing {name}")

    domain_path = ROOT / maturity_ref
    source_policy_path = ROOT / source_policy_ref
    roadmap_path = ROOT / roadmap_ref
    for path in (domain_path, source_policy_path, roadmap_path):
        if not path.exists():
            fail(f"{domain_id}: declared artifact does not exist: {path.relative_to(ROOT)}")

    domain = load_yaml(domain_path)
    missing = sorted(M0_REQUIRED_DOMAIN_KEYS - set(domain.keys()))
    if missing:
        fail(f"{domain_id}: M0 domain missing keys: {', '.join(missing)}")
    if domain.get("domain_id") != domain_id:
        fail(f"{domain_id}: DOMAIN.yaml domain_id mismatch")
    if domain.get("logical_knowledge_space_ref") != logical_ref:
        fail(f"{domain_id}: logical knowledge identity mismatch")
    if domain.get("canonical_tree") != canonical_tree:
        fail(f"{domain_id}: canonical tree mismatch")

    maturity = domain.get("maturity", {})
    level = maturity.get("current_level")
    if level not in LEVEL_TO_STATUS:
        fail(f"{domain_id}: invalid maturity level {level!r}")
    if LEVEL_TO_STATUS[level] != status:
        fail(f"{domain_id}: registry status {status} disagrees with DOMAIN maturity {level}")
    if level == "M5" and maturity.get("expert_ready") is not True:
        fail(f"{domain_id}: M5 requires expert_ready: true for the declared bounded scope")
    if level != "M5" and maturity.get("expert_ready") is True:
        fail(f"{domain_id}: expert_ready cannot be true below M5")

    source_policy = load_yaml(source_policy_path)
    if source_policy.get("domain_id") != domain_id:
        fail(f"{domain_id}: SOURCE_POLICY domain_id mismatch")
    prohibited = source_policy.get("prohibited_shortcuts", [])
    if not prohibited:
        fail(f"{domain_id}: source policy must declare prohibited shortcuts")

    roadmap = load_yaml(roadmap_path)
    if roadmap.get("domain_id") != domain_id:
        fail(f"{domain_id}: ROADMAP domain_id mismatch")
    if roadmap.get("current_level") != level:
        fail(f"{domain_id}: ROADMAP current_level disagrees with DOMAIN")


def main() -> int:
    validate_common_model()
    registry = load_yaml(REGISTRY)
    domains = registry.get("domains", [])
    ids = [item.get("id") for item in domains]
    if len(ids) != len(set(ids)):
        fail("duplicate domain id in domain registry")
    for entry in domains:
        validate_domain_entry(entry)
    print(f"OK: validated {len(domains)} professional domains; activated maturity contracts are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
