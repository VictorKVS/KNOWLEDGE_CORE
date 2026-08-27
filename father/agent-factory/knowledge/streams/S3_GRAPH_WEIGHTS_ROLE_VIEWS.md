# S3 — Knowledge graph, weights and role views

Mission: convert extracted knowledge into a reusable graph shared by Architect, Software Engineer, Information Security, Lawyer, Manager and Product roles.

Deliverables:
- canonical node taxonomy: CONCEPT, DEFINITION, CLAIM, PRINCIPLE, PATTERN, ANTI_PATTERN, DECISION_RULE, TRADE_OFF, CHECKLIST, METRIC, FAILURE_MODE, TEST, EXAMPLE, REQUIREMENT;
- edge taxonomy: DEFINES, SUPPORTS, CONTRADICTS, REFINES, DEPENDS_ON, PART_OF, APPLIES_TO, CAUSES, MITIGATES, IMPLEMENTS, DERIVED_FROM, EVIDENCE_FOR, SAME_AS;
- component score vector: source_authority, extraction_confidence, translation_confidence, ambiguity, cross_source_support, recency, applicability, model_agreement, reviewer_confidence;
- role-specific weighting policies without cloning knowledge nodes;
- graph integrity checks for dangling/duplicate/conflicting edges;
- contradiction records and provenance for every inferred relation.

Acceptance gate: one canonical node is consumable by all six roles through role views, while evidence and score components remain shared and traceable.