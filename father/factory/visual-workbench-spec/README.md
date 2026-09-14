# FATHER Visual Engineering Workbench — Technical Specification

Status: `DRAFT_V0.1 / IMPLEMENTATION NOT AUTHORIZED UNTIL REVIEW`

This directory is the canonical technical specification package for the future **FATHER Visual Engineering Workbench** — an interactive engineering/CAD-like environment for designing, reviewing, implementing and operating software/AI systems through the FATHER paper pipeline.

The specification is intentionally split into maintainable documents instead of one monolithic 100-page file. When exported as one document, the package is expected to form a large engineering specification, but in the repository every section remains independently reviewable, versionable and traceable.

## Read in this order

1. `00_MASTER_TZ.md` — product, scope, architecture, functional and non-functional requirements.
2. `01_STATION_CATALOG_S00_S59.md` — detailed visual conveyor stations from intake to evolution/retirement.
3. `02_UX_INTERACTION_SPEC.md` — screen anatomy, click/hover/drill-down, inspector, live flows, compare/history.
4. `03_CANONICAL_DATA_MODEL.md` — canonical entities, relationships, versioning, statuses and traceability model.
5. `04_API_EVENT_PERSISTENCE_CONTRACT.md` — API boundaries, event model, persistence, import/export and Git synchronization.
6. `05_SECURITY_AUTHORITY_AUDIT.md` — RBAC/ABAC, authority boundaries, audit, data classification and secure AI-assistance requirements.
7. `06_TEST_ACCEPTANCE_STRATEGY.md` — test pyramid, UI/E2E/property/security/performance tests and acceptance criteria.
8. `07_IMPLEMENTATION_ROADMAP.md` — delivery phases, gates, DoR/DoD and controlled evolution from read-only model viewer to engineering platform.
9. `08_COMPETITOR_PATTERN_CROSSWALK.md` — what is adopted from Ardoq, KNIME, Node-RED, BPMN/bpmn-js, Structurizr/C4 and React Flow, and what is explicitly rejected.
10. `09_REQUIREMENTS_TRACEABILITY.yaml` — machine-readable requirement catalogue and verification intent.

## Governing source documents

This specification does not replace the existing canonical lifecycle documents. It implements their visual projection and future execution surface.

Primary upstream sources:

- `father/factory/paper-pipeline/FATHER_PAPER_PIPELINE_ALGORITHM.md`
- `father/factory/paper-pipeline/FATHER_PAPER_PIPELINE.yaml`
- `father/factory/paper-pipeline/ANALYSIS_FIRST_ENGINEERING_POLICY.md`
- `father/factory/paper-pipeline/ALGORITHM_DESIGN_STANDARD.md`
- `father/factory/paper-pipeline/ROLE_COMPETENCY_MATURITY_MODEL.yaml`
- `father/factory/paper-pipeline/PRE_CODE_EVIDENCE_GATE.yaml`
- `father/factory/paper-pipeline/VISUAL_ENGINEERING_WORKBENCH.md`
- `father/factory/paper-pipeline/VISUAL_INTERACTION_SPEC.md`
- `father/factory/FATHER_ARTIFACT_REGISTRY.yaml`
- `father/factory/FATHER_ROLE_MATRIX.yaml`
- `father/factory/NORMATIVE_SOURCE_REGISTRY.yaml`

## Core product principle

```text
The UI is not the engineering truth.
The UI is a live, navigable projection over canonical engineering data.
```

Every visible node, edge, badge, test, source, decision and status must resolve back to canonical project data with a stable identifier and version.

## Design rule

The visual workbench must feel closer to CAD/BIM/visual-programming tooling than to a wiki or dashboard:

```text
INPUTS → ENGINEERING STATION / BLACK BOX → OUTPUTS
                         ↓
                    drill down
                         ↓
        algorithms / evidence / reviews / tests
```

The product must support three levels of abstraction:

- `Z0` — macro lifecycle A0–A16;
- `Z1` — detailed conveyor S00–S59;
- `Z2` — internal logic of one station.

## Implementation freeze

This package is currently specification-only. Runtime/Model Zoo expansion remains frozen under `AUTOMATION_ACTIVATION_GATE.yaml` until the paper pipeline and this workbench specification have completed review and manual walkthroughs.