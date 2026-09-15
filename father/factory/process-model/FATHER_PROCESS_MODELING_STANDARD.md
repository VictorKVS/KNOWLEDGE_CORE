# FATHER Process Modeling Standard

Status: `CANDIDATE_MODEL`

## Purpose

FATHER models software/system production as a hierarchy of business processes rather than as a flat document list. The same model must be readable by humans, traceable to artifacts and roles, and later executable/checkable by automation.

## Canonical notation stack

- **BPMN 2.0** — sequence, participants, hand-offs, events, subprocesses and gateways.
- **IDEF0** — functional context of every stage using Input / Control / Mechanism / Output (ICOM).
- **DMN** — gate decisions, applicability rules and decision tables.
- **RACI** — responsibility and accountability for activities and artifacts.
- **Mermaid** — repository-friendly visual projection for GitHub review. Mermaid is a view, not the normative process semantics.

## Decomposition levels

### L0 — Factory

One end-to-end FATHER lifecycle. It shows only major stages and constitutional gates.

### L1 — Stage

Each lifecycle stage is a subprocess. L1 shows its principal activities, primary actors, produced artifacts and the gate that closes the stage.

### L2 — Activity

A single L1 activity is decomposed into concrete role tasks and document transformations:

`input artifact -> specialist action -> produced/updated artifact -> review/check -> output`.

### L3 — Rule / artifact-field level

Critical L2 tasks are decomposed to:

`source clause -> requirement -> applicability -> artifact field -> validation rule -> evidence -> gate decision`.

L3 is the level intended for executable checks and DMN.

## IDEF0 passport for every stage

Every L1 stage must have:

- **Input** — factual/project artifacts transformed by the stage;
- **Control** — constitution, laws, standards, policies, approved constraints and gate criteria;
- **Mechanism** — responsible/supporting roles, tools, knowledge bases and methods;
- **Output** — created or materially updated artifacts and evidence;
- **Gate** — explicit condition allowing downstream work.

A missing input is never silently replaced by a guess. It remains `UNKNOWN`, `GAP`, `PARTIAL` or `CONFLICTED` until resolved or explicitly accepted by the authorized owner.

## Gate semantics

A gate is not a calendar milestone. It is an evidence decision.

Each gate must eventually have a DMN decision table containing at least:

- required artifacts;
- required artifact states;
- mandatory reviews;
- blocking conflicts/UNKNOWNs;
- authority required for exception or residual-risk acceptance;
- PASS / CONDITIONAL / BLOCKED outcome;
- evidence references.

## Role semantics

BPMN lanes show who performs the work. RACI defines authority precisely.

FATHER preserves the constitutional rules that:

- Security enters immediately after Product and remains continuous;
- a producer cannot be the sole final verifier of a material decision;
- an agent may propose or draft, but may not silently assume owner authority;
- professional knowledge promotion requires independent domain review.

## Artifact transformation rule

The unit of production is not a Word file. It is a controlled information artifact.

One physical document may satisfy several canonical artifacts, and one canonical artifact may be represented by Markdown, YAML, JSON, BPMN, OpenAPI, code, a graph, a test report or another controlled format.

The process model therefore tracks:

`knowledge / evidence -> canonical artifact -> state -> review -> downstream use`,

not merely filenames.

## Traceability identifiers

Recommended identifiers:

- Process: `FTH-P-L0-*`, `FTH-P-L1-*`, `FTH-P-L2-*`;
- Gate: existing lifecycle gate id, e.g. `THREAT_MODEL_V0_READY`;
- Artifact: canonical id from `FATHER_ARTIFACT_REGISTRY.yaml`;
- Role: canonical role id from `FATHER_ROLE_MATRIX.yaml`;
- Source: canonical source id from `NORMATIVE_SOURCE_REGISTRY.yaml`;
- Requirement/rule: stable id created during source atomization.

## Change rule

L1/L2 process changes must not violate `FATHER_CONSTITUTION.md`. Local projects may specialize or tighten this model, but may not silently remove constitutional activities or gates.
