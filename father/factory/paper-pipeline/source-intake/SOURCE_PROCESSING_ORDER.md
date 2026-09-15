# FATHER Source Processing Order

Status: `ACTIVE A0 WORK PLAN`

Goal: process the complete source universe without repeatedly rereading the same material or mixing authority classes.

## Batch 0 — Canonical FATHER self-inventory

Purpose: establish what FATHER already claims before importing more knowledge.

Process:
1. enumerate all current factory/paper-pipeline/workbench/backend artifacts;
2. classify each as FACT / CANDIDATE / POLICY / REQUIREMENT / METHOD / UI PROJECTION;
3. record dependencies and duplicate truths;
4. identify contradictions and stale files;
5. produce one canonical design index.

Output:
- current FATHER truth map;
- duplicate/overlap report;
- missing canonical owners;
- baseline for all future comparison.

## Batch 1 — Real project evidence: OSINT_deepseek

Purpose: prove the paper pipeline on a real brownfield/hybrid system.

Process:
1. repository inventory;
2. current code/config/test/docs evidence;
3. project history only where needed for rationale;
4. map existing evidence to S00–S59;
5. label COMPLETE / PARTIAL / CONFLICTED / GAP / STALE;
6. do not generate missing documents until mapping is complete.

Output:
- first full walkthrough evidence pack;
- proof of which paper-pipeline steps are useful/redundant/missing.

## Batch 2 — Mandatory and normative core

Purpose: establish non-negotiable lifecycle/document/security constraints.

Priority groups:

### 2A Lifecycle / documentation / architecture
- ГОСТ Р 57193-2025
- ГОСТ Р 58609-2019
- ГОСТ Р ИСО/МЭК 12207-2010
- ГОСТ Р 57100-2025
- ГОСТ Р 57101-2016
- ГОСТ Р 59793-2021
- ГОСТ 34.201-2020
- ГОСТ Р 59795-2021
- ГОСТ 34.602-2020
- ГОСТ Р 59792-2021

### 2B Secure development / threat modeling
- ГОСТ Р 56939-2024
- ГОСТ Р 71207-2024
- Методика ФСТЭК оценки угроз 2021

### 2C Regulatory overlays
- current state-system requirements
- personal-data requirements
- cryptographic overlay when applicable
- KII categorization/security requirements
- federal-law and sector overlays still missing from registry

Processing output for every document:
`source → clause → atomic requirement → applicability → artifact field → role → station → gate/test`.

## Batch 3 — OTUS 01–31

Purpose: use the course as a method/capability catalogue, not as lifecycle authority.

For every lesson:
- exact lesson purpose;
- methods/patterns;
- homework acceptance criteria;
- artifacts it can improve;
- FATHER stations it strengthens;
- conflicts/limitations;
- what becomes a reusable method candidate.

Output:
- exact OTUS method catalogue;
- lesson → S-station crosswalk;
- method gaps not covered by the course.

## Batch 4 — Professional books

Purpose: build role knowledge and design methods from user-owned sources.

For every book:
1. verify exact source/version/rights basis;
2. preserve original locator;
3. extract only atomic reusable ideas;
4. classify: definition / principle / pattern / trade-off / decision criterion / failure mode / example;
5. compare with normative sources and other books;
6. map to roles/stations/methods;
7. independent review before promotion.

No long copyrighted text is copied into public knowledge artifacts.

## Batch 5 — Scientific/primary technical evidence

Purpose: justify material algorithms scientifically.

Prioritize only algorithms that need stronger evidence, for example:
- information retrieval/ranking;
- graph traversal/impact propagation;
- uncertainty/calibration;
- statistical comparison/evaluation;
- reliability/capacity models;
- GenAI/RAG metrics;
- security/adversarial evaluation.

Scientific papers support method adequacy; they do not replace applicable law, owner authority or project facts.

## Batch 6 — Vendor and implementation documentation

Only after candidate technologies are selected.

Examples:
- PostgreSQL behavior/limits;
- FastAPI/OpenAPI behavior;
- React Flow interaction/rendering contracts;
- object storage;
- selected auth provider;
- backup tooling.

Vendor docs constrain implementation, not product need.

## Batch 7 — Competitor/reference systems

Use to validate UX/process ideas:
- Ardoq;
- IcePanel;
- KNIME;
- Node-RED;
- Camunda/BPMN;
- Structurizr/C4;
- React Flow.

For each pattern record:
`problem → competitor solution → benefit → limitation → FATHER adaptation → acceptance test`.

## Universal output contract

No source batch is considered processed just because it has a summary.

Each material extracted item must end in one or more explicit links:

```text
SOURCE
  ↓
CLAUSE / LOCATOR / EVIDENCE
  ↓
ATOMIC ITEM
  ↓
{ REQUIREMENT | CONSTRAINT | METHOD | DECISION CRITERION | FAILURE MODE }
  ↓
FATHER ARTIFACT / STATION / ROLE
  ↓
TEST / GATE / REVIEW
```

## Stopping rule

Do not wait for every source in existence before designing.

A station may be reviewed when:
- mandatory known sources for that station are covered;
- material gaps are explicit;
- professional/scientific sources are sufficient to justify the selected method;
- additional sources are expected to refine rather than overturn the basic model.

If a new source later invalidates an assumption, the dependency graph reopens only the affected stations.
