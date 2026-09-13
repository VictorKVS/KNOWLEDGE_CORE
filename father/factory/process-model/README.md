# FATHER Software Factory — Process Model

This directory is the visual/process layer above the artifact factory.

## Navigation

1. [`L0_FATHER_SOFTWARE_FACTORY.md`](L0_FATHER_SOFTWARE_FACTORY.md) — one end-to-end factory map.
2. [`L1_STAGE_DECOMPOSITION.md`](L1_STAGE_DECOMPOSITION.md) — decomposition of all 13 lifecycle stages.
3. [`stages/01-product-discovery/README.md`](stages/01-product-discovery/README.md) — first completed L2 stage: Product Discovery with flow, swimlanes, IDEF0/ICOM, evidence analytics and PRODUCT_READY gate.
4. [`FATHER_PROCESS_HIERARCHY.yaml`](FATHER_PROCESS_HIERARCHY.yaml) — machine-readable L0/L1 hierarchy and activities.
5. [`FATHER_PROCESS_MODELING_STANDARD.md`](FATHER_PROCESS_MODELING_STANDARD.md) — BPMN/IDEF0/DMN/RACI modeling rules.

## L2/L3 rule

Every L1 activity is decomposed into:

`role -> input artifacts -> operation -> decisions/checks -> output artifacts -> review -> handoff -> gate`.

Critical gates receive L3 bindings:

`normative source -> clause -> requirement -> applicability -> artifact field -> validation rule -> evidence -> DMN decision`.

Stage 01 already implements this pattern and becomes the reference package for subsequent stages.

## Relationship to the factory registries

- lifecycle truth: `../FATHER_LIFECYCLE_STAGES.yaml`
- artifacts: `../FATHER_ARTIFACT_REGISTRY.yaml`
- roles: `../FATHER_ROLE_MATRIX.yaml`
- normative sources: `../NORMATIVE_SOURCE_REGISTRY.yaml`
- source/artifact mapping: `../SOURCE_ARTIFACT_MAPPING.yaml`
- architect intake crosswalk: `../ARCHITECT_INTAKE_CROSSWALK.yaml`

The diagrams are views over those canonical registries; they must not silently diverge from them.
