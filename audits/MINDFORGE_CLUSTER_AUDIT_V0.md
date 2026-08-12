# MindForge Cluster Audit v0

Status: first-pass structural audit. No repository has been renamed, archived, merged or deleted.

## Executive direction

The MindForge family should become a product line, not a set of competing repositories.

```text
MindForge Platform
├── MindForge Core        — orchestration/runtime/agents
├── MindForge Studio      — operator UI and visual workbench
├── Knowledge Core        — evidence, memory, decision graph
├── Meta-Foundry          — reusable patterns/foundry/labs
├── Universal Gateway     — integrations and external agent/tool gateway
├── Security Layer        — SecGraph / DevSafe / authorized security components
└── Showcase / Website    — public product surface
```

This is a target architecture, not yet a migration decision.

## Repositories inspected in this pass

### `MindForge`
Observed: root README describes an open-source platform combining parsing, embeddings, vector search, knowledge graphs and LLMs for search, OSINT, analytics and decision support.

Current interpretation: **flagship-name candidate**, but the current README is too small to establish whether it is the canonical runtime implementation.

Action: inspect root tree, runtime/code, tests and history before declaring it the canonical Father runtime.

### `MindForge-v2.0x`
Observed: README currently contains only the title `MindForge v2.0x — Industrial AI Lifecycle Platform`; default development branch is `develop`.

Current interpretation: **version/prototype candidate**, not yet suitable as a separate premium public flagship.

Action: compare its code and history with `MindForge`; decide whether it is successor code, an experiment, or should become a branch/release line rather than a separate public product.

### `MindForge-Studio`
Observed: substantial repository with Python entrypoints and directories including `core`, `docs`, `automation`, `aurora`, plus API/Comfy smoke-test scripts. A conventional `README.md` is absent; there is a file named `# MindForge Studio.md`. `LICENSE` and `ROADMAP.md` exist but are currently empty.

Current interpretation: **strong Studio/workbench candidate** with real implementation content, but poor public surface/hygiene.

Immediate premium issues:
- no canonical `README.md`;
- empty `LICENSE`;
- empty `ROADMAP.md`;
- unconventional landing-page filename;
- repository root contains experimental scripts/output areas that need classification.

Action: preserve implementation, then create premium landing/architecture/setup surface after code-path audit.

### `META-FOUNDRY`
Observed: repository describes itself as an engineering platform combining AI, security and systems architecture. Root includes `.github`, pre-commit configuration, `01_GIN`, `branding`, `docs`, `mkdocs.yml` and a substantial schema document.

Current interpretation: **platform-component / engineering foundry candidate**. It already has stronger documentation/tooling structure than several sibling repositories.

Immediate premium issue: root README is much weaker than the apparent internal structure. Also contains `desktop.ini`, which is repository-hygiene debt.

Action: inspect `01_GIN`, docs and schemas to determine which capabilities are unique versus overlapping with MindForge/Knowledge Core.

### `H-Mindforge-industrial-ai-suite`
Observed: repository is empty.

Current interpretation: **reserved-name / concept-only candidate**.

Action: do not build another implementation here until the canonical product-line roles are fixed. Likely redirect/showcase/archive candidate later, but only after confirming intent.

### `PRODUCT_SPEC_UniversalAgent`
Observed: documentation-heavy repository containing multiple product specifications, gateway architecture posters, schema documents, `docs`, an `ИБ` directory and a nested project directory. No root README. Root also contains Windows artefacts such as `.lnk` and `desktop.ini`.

Current interpretation: **specification / architecture component**, likely useful input for a future Universal Agent Gateway rather than a standalone competing flagship.

Immediate premium issues:
- no root README/navigation;
- duplicated/versioned documents at root;
- Windows shortcut/system artefacts;
- spec/runtime boundary unclear.

Action: audit specification contents; extract canonical gateway architecture and decide whether implementation belongs in MindForge Core or a dedicated gateway repository.

### `gpt-agent`
Observed: no root README. Root is primarily a large collection of Russian-language documents/directories related to information security, organizational roles, information policy and project material, plus DOCX files.

Current interpretation: **historical knowledge/source repository**, not currently a premium agent runtime.

Action: mine valuable security/agent-role knowledge into the evidence pipeline with provenance. Do not present this repository as a flagship implementation in its current form.

## Working product hierarchy

### Tier A — likely flagship surfaces
1. `MindForge` — canonical product name; runtime ownership still to verify.
2. `MindForge-Studio` — likely operator/UI/workbench product.
3. `KNOWLEDGE_CORE` — canonical evidence/decision infrastructure.

### Tier B — likely platform components
- `META-FOUNDRY`
- `PRODUCT_SPEC_UniversalAgent` (after spec cleanup / gateway decision)
- security components from the Security cluster

### Tier C — requires deeper comparison
- `MindForge-v2.0x`
- `spaceai-agent-platform`
- `agent-ecosystem-crkfl`
- `AI-Product-Architect`
- `BotFabrika`
- `BotFerm`
- `mindforge-ai-telegram-bot`
- `Sokrat`
- `ES-Agent-SiteManager`

### Tier D — concept/empty/public-surface candidates
- `H-Mindforge-industrial-ai-suite`
- `PRODUCT_SPEC_UniversalAgent-v2.0` (repository metadata showed zero size in portfolio inventory)

## Premium product-line rule

The public visitor should eventually see this hierarchy:

```text
MindForge
  AI Engineering & Agent Orchestration Platform

  [Core] [Studio] [Knowledge] [Security] [Integrations] [Examples]
```

Not:

```text
MindForge
MindForge-v2.0x
H-Mindforge-industrial-ai-suite
MindForge-Studio
Meta-Foundry
UniversalAgent
...with no declared relationship
```

## Audit sequence from here

1. Compare `MindForge` vs `MindForge-v2.0x` code trees and histories.
2. Audit `MindForge-Studio` runtime entrypoints and dependencies.
3. Audit `META-FOUNDRY/01_GIN` and docs for unique reusable modules.
4. Audit UniversalAgent specs and determine gateway boundary.
5. Inspect remaining agent repositories and assign exact roles.
6. Produce `MINDFORGE_PRODUCT_MAP_V1.md` with KEEP / MERGE-CANDIDATE / COMPONENT / DEMO / ARCHIVE-CANDIDATE states.
7. Only then begin premium README/branding/MVP work on the selected canonical repositories.

## Safety rule

No destructive repository action is authorized by this audit. Old repositories may contain history, source documents, dependencies or ideas worth preserving. Migration decisions require content comparison and a redirect plan.
