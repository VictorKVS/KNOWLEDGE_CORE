from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "father/domain-knowledge/domain-registry.yaml"
MATURITY_MODEL = ROOT / "father/domain-knowledge/PROFESSIONAL_KB_MATURITY_MODEL.yaml"
REVIEW_PROTOCOL = ROOT / "father/domain-knowledge/PROFESSIONAL_KB_REVIEW_PROTOCOL.yaml"

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
    "review_policy",
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

REQUIRED_REVIEW_ROLES = {
    "DOMAIN_SPECIALIST",
    "ALTERNATIVES_ANALYST",
    "SENIOR_PRACTITIONER_REVIEWER",
    "SKEPTICAL_CRITIC",
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
    if model.get("common_review_protocol_ref") != "father/domain-knowledge/PROFESSIONAL_KB_REVIEW_PROTOCOL.yaml":
        fail("professional maturity model must bind the common review protocol")
    invariants = model.get("core_invariants", [])
    required = {
        "facts_interpretations_recommendations_and_decisions_are_distinct_objects",
        "model_output_is_candidate_material_not_primary_authority",
        "maturity_is_bounded_by_the_weakest_required_gate_for_the_claimed_scope",
        "material_producer_and_final_senior_reviewer_use_separate_assignments",
        "senior_review_must_search_for_better_alternatives_not_only_find_faults",
    }
    if not required.issubset(set(invariants)):
        fail("professional maturity model is missing required evidence/objectivity/review invariants")

    review = load_yaml(REVIEW_PROTOCOL)
    roles = set(review.get("production_roles", {}).keys())
    if not REQUIRED_REVIEW_ROLES.issubset(roles):
        fail("professional review protocol is missing required specialist/alternative/senior/critic roles")
    principles = set(review.get("principles", []))
    for required_principle in {
        "producer_and_final_senior_reviewer_are_separate_assignments",
        "criticism_without_actionable_alternative_or_reasoned_no_better_alternative_statement_is_incomplete",
        "repeated_generic_pattern_is_not_professional_evidence",
    }:
        if required_principle not in principles:
            fail(f"professional review protocol missing principle: {required_principle}")


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
    review_policy_ref = entry.get("review_policy_ref")
    roadmap_ref = entry.get("roadmap_ref")
    for name, value in {
        "canonical_tree": canonical_tree,
        "logical_knowledge_space_ref": logical_ref,
        "maturity_ref": maturity_ref,
        "source_policy_ref": source_policy_ref,
        "review_policy_ref": review_policy_ref,
        "roadmap_ref": roadmap_ref,
    }.items():
        if not value:
            fail(f"{domain_id}: activated domain missing {name}")

    domain_path = ROOT / maturity_ref
    source_policy_path = ROOT / source_policy_ref
    review_policy_path = ROOT / review_policy_ref
    roadmap_path = ROOT / roadmap_ref
    for path in (domain_path, source_policy_path, review_policy_path, roadmap_path):
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

    review_policy = load_yaml(review_policy_path)
    if review_policy.get("domain_id") != domain_id:
        fail(f"{domain_id}: REVIEW_POLICY domain_id mismatch")
    independent_roles = set(review_policy.get("independent_review_roles", []))
    if not {"SENIOR_PRACTITIONER_REVIEWER", "SKEPTICAL_CRITIC"}.issubset(independent_roles):
        fail(f"{domain_id}: review policy must include independent senior and skeptical review")
    independence = review_policy.get("independence", {})
    if "separate_from_producer_assignment" not in str(independence.get("D2", "")):
        fail(f"{domain_id}: D2 review must be separate from producer assignment")
    outputs = set(review_policy.get("review_outputs", {}).get("required", []))
    required_outputs = {
        "verdict",
        "strongest_objection",
        "viable_alternatives",
        "improved_option_or_reason_no_better_option_found",
        "reversal_conditions",
    }
    if not required_outputs.issubset(outputs):
        fail(f"{domain_id}: review policy lacks actionable senior challenge outputs")

    domain_review = domain.get("review_policy", {})
    if domain_review.get("domain_policy_ref") != review_policy_ref:
        fail(f"{domain_id}: DOMAIN review policy ref mismatch")
    if domain_review.get("material_producer_and_final_senior_reviewer_separate") is not True:
        fail(f"{domain_id}: DOMAIN must require producer/reviewer separation")

    roadmap = load_yaml(roadmap_path)
    if roadmap.get("domain_id") != domain_id:
        fail(f"{domain_id}: ROADMAP domain_id mismatch")
    if roadmap.get("current_level") != level:
        fail(f"{domain_id}: ROADMAP current_level disagrees with DOMAIN")


def main() -> int:
    validate_common_model()
    registry = load_yaml(REGISTRY)
    if registry.get("common_review_protocol_ref") != "father/domain-knowledge/PROFESSIONAL_KB_REVIEW_PROTOCOL.yaml":
        fail("domain registry must bind common professional review protocol")
    domains = registry.get("domains", [])
    ids = [item.get("id") for item in domains]
    if len(ids) != len(set(ids)):
        fail("duplicate domain id in domain registry")
    for entry in domains:
        validate_domain_entry(entry)
    print(f"OK: validated {len(domains)} professional domains; maturity and independent review contracts are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
