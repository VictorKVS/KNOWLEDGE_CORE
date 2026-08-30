# FATHER Visual Knowledge Workspace — Decision Log

This file records durable product and architecture decisions. New decisions are appended; superseded decisions remain visible.

## DEC-001 — Evidence-first canonical model
Status: ACCEPTED

Decision: source evidence remains canonical; model output is candidate data until evidence/review gates pass.

Why: prevents fluent but unsupported answers from becoming trusted knowledge.

## DEC-002 — One canonical graph, many role perspectives
Status: ACCEPTED

Decision: Architect, Programmer, Security, Lawyer, Manager and Product use projections over the same canonical nodes.

Why: avoids semantic drift and duplicated truth.

## DEC-003 — API-first even inside a modular monolith
Status: ACCEPTED

Decision: logical service boundaries are documented by API/event contracts before physical service extraction.

Why: preserves evolvability without premature distributed-system cost.

## DEC-004 — Trace-first everywhere
Status: ACCEPTED

Decision: every material stage propagates trace context and emits start/terminal events.

Why: debugging, audit, reproducibility and user-facing lineage are product requirements, not operational extras.

## DEC-005 — Microservices only with evidence
Status: ACCEPTED

Decision: a separate deployable service requires a material reason: scale, GPU/runtime isolation, trust boundary, release lifecycle, fault isolation, data ownership, concurrency/background queue or external integration.

Why: prevents accidental complexity.

## DEC-006 — Figma is the canonical UX/design source
Status: ACCEPTED

Decision: one long-lived Figma design file holds product map, tokens, reusable components, screens, Architecture Studio and trace UX.

Why: prevents ad-hoc screens and supports multi-year visual consistency.

Master file: https://www.figma.com/design/jxY8XAblIEbEFMnjBv23oK

## DEC-007 — Architecture Studio is first-class, not documentation-only
Status: ACCEPTED

Decision: the product includes an editable architecture workspace supporting C1/C2/C3, sequence, data flow, trust boundaries, API/ADR/requirements overlays and validation.

Why: architecture must stay connected to requirements, code, tests and runtime traces.

## DEC-008 — Visual Workspace is a professional graphical editor
Status: ACCEPTED

Decision: graph visualization supports editing/investigation operations such as pivot, expand, filter, grouping, saved scenes, context actions, evidence panels and productization.

Why: passive dashboards are insufficient for analytical work.

## DEC-009 — Renderer and storage are replaceable projections
Status: ACCEPTED

Decision: graph renderer, vector DB and future graph DB may change without changing logical IDs or source/evidence semantics.

Why: protects the long-lived core from technology churn.

## DEC-010 — Product lineage extends beyond knowledge
Status: ACCEPTED

Decision: lineage continues from knowledge to decision to product to outcome to lesson.

Why: FATHER should learn not only what sources say, but what decisions were made and what happened afterward.
