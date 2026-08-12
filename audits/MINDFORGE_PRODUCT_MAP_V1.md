# MindForge Product Map v1

> Evidence-based role map for the MindForge/agentic cluster. This is a portfolio and architecture decision draft, not permission to delete/archive repositories.

## Executive decision

The current cluster should converge toward a **product family**, not a single giant repository and not a collection of competing names.

```text
MindForge Platform
├── MindForge Core          — orchestration/runtime/agents
├── MindForge Studio        — operator UI + workflows
├── Knowledge Core          — evidence, graph, memory, decisions
├── Universal Agent Gateway — agent-ready service integration
├── Meta-Foundry            — reusable engineering patterns/labs
├── Security Layer          — SecGraph / DevSafe / Security KB
└── Showcase                — website, demos, releases
```

## Repository roles

### KEEP / FLAGSHIP — `MindForge`
**Proposed role:** canonical MindForge Core repository.

Evidence observed:
- Python package metadata via `pyproject.toml`;
- `mf_core/` with `agents`, `api`, `common`, `workers`;
- `tests/`, scripts, installer and GitHub configuration;
- changelog and contributing surfaces already exist;
- root README is currently far too small for the actual repository.

Decision: **KEEP and develop as the canonical runtime/core unless deeper executable testing disproves this choice.**

Premium work:
1. architecture inventory of `mf_core`;
2. runnable quick start;
3. test/CI verification;
4. replace minimal README with flagship landing page;
5. define API boundary with Knowledge Core and Studio;
6. remove duplicate/legacy root clutter only after review.

### MERGE-CANDIDATE / DESIGN SOURCE — `MindForge-v2.0x`
**Proposed role:** architecture/product-design branch whose useful concepts are migrated into canonical MindForge rather than maintained as a competing flagship.

Evidence observed:
- stronger planning structure: `architecture/`, `engineering/`, `product/`;
- long design documents;
- `src/core/` currently contains extremely small placeholder-like Python files (`orchestrator.py`, `security.py`, `telemetry.py`, etc. are only tens of bytes);
- README is effectively only a title.

Decision: **do not present as a second production MindForge. Mine it for architecture/product material, compare with `MindForge`, then migrate unique value.**

Status: `MERGE-CANDIDATE`, not archive yet.

### KEEP / PRODUCT COMPONENT — `MindForge-Studio`
**Proposed role:** visual/operator workspace for MindForge.

Evidence observed:
- significant repository size and real Python files;
- `core/` includes adapters, agents, knowledge, pipeline, profiles, schemas, templates and web pipeline;
- automation and smoke-test-like scripts are present;
- current public presentation is poor: no conventional root `README.md`, empty `LICENSE`, empty `ROADMAP.md`, and some placeholder/experimental clutter.

Decision: **KEEP as a distinct product component.** It should not compete with MindForge Core; it should consume Core APIs/contracts.

Premium work:
1. identify executable entrypoint and UI technology;
2. separate production paths from experiments/generated output;
3. create README + screenshots/demo later;
4. define Core/Studio contract;
5. repair license/roadmap state.

### KEEP / PLATFORM COMPONENT — `KNOWLEDGE_CORE`
**Role:** canonical evidence, graph, decision memory and query runtime.

Decision: **KEEP independent.** MindForge consumes it through stable IDs/query interfaces rather than copying knowledge into agent code.

### KEEP / ENGINEERING LAB — `META-FOUNDRY`
**Proposed role:** reusable engineering patterns, labs, architecture assets and platform construction kit.

Evidence observed:
- `.github`, pre-commit configuration, MkDocs configuration, docs and branding already exist;
- structure is stronger than its current short README suggests;
- contains an engineering/lab-oriented layout rather than a single end-user product.

Decision: **KEEP, but sharply define its boundary.** It should supply reusable patterns/components to product repositories, not become another name for MindForge.

Premium work:
1. rewrite README around its actual engineering-lab role;
2. catalogue reusable modules/patterns;
3. remove OS clutter such as `desktop.ini` after verification;
4. publish docs via a coherent documentation surface.

### KEEP / PRODUCT COMPONENT — `PRODUCT_SPEC_UniversalAgent`
**Proposed role:** Universal Agent Gateway specification and eventual gateway implementation.

Evidence observed:
- product spec defines a clear problem: agent-ready abstraction between services and AI agents;
- explicit concepts include capabilities, policy enforcement, provider connectors, audit/logging and minimal admin UI;
- MVP already has a bounded operation (`create_ticket`) and staged roadmap;
- repository currently mixes specification documents, posters, a Windows shortcut and other presentation clutter.

Decision: **KEEP as a distinct product concept because its boundary is clear and useful.** First convert from specification repository into an executable MVP, rather than folding it blindly into MindForge.

Relationship:
```text
MindForge agents
      ↓
Universal Agent Gateway
      ↓
enterprise/provider services
```

### HISTORICAL / KNOWLEDGE-MINING — `gpt-agent`
**Proposed role:** historical source repository for security-agent concepts, organizational roles and earlier documents.

Evidence observed:
- large amount of documents and domain folders;
- content appears strongly oriented to information-security organizational material rather than a clean modern agent runtime;
- binary documents and broad knowledge storage make it unsuitable as a flagship repository in current form.

Decision: **do not market as flagship.** Mine useful domain knowledge into Security/Knowledge Core with provenance, then decide whether to retain as historical archive.

## Supporting MindForge repositories — next audit queue

These remain unclassified until content inspection:

- `BotFabrika`
- `BotFerm`
- `mindforge-ai-telegram-bot`
- `H-Mindforge-industrial-ai-suite`
- `spaceai-agent-platform`
- `agent-ecosystem-crkfl`
- `AI-Product-Architect`
- `AI-Trainer-Professional`
- `ai-companion-prompt-engineering`
- `Sokrat`
- `ES-Agent-SiteManager`
- `VisionToFigma`
- `MindForge-Factory-Website`

## Target dependency direction

```text
                    MindForge Studio
                          │
                          ▼
                     MindForge Core
                    /      │       \
                   /       │        \
                  ▼        ▼         ▼
        Knowledge Core   Gateway   Security Layer
                  │                  │
                  ▼                  ▼
              evidence          SecGraph/DevSafe

Meta-Foundry → reusable patterns/tools → all engineering repositories
Showcase → consumes demos/releases from flagship repositories
```

## Anti-patterns to eliminate

- multiple repositories appearing to be the same flagship product;
- architecture documents presented as if they were working runtime code;
- empty README/ROADMAP/LICENSE placeholders;
- generated output mixed with source;
- Windows `.lnk` / `desktop.ini` clutter;
- README claims that exceed demonstrable repository behavior;
- duplicated concepts without a canonical owner.

## MVP sequence for the cluster

### Phase A — establish one real vertical slice

```text
User task
  → MindForge Core
  → one specialist agent
  → Knowledge Core query/brief
  → one tool/provider action (or safe mock)
  → result
  → outcome recorded
```

Acceptance: reproducible locally with a documented command and test.

### Phase B — Studio
Studio visualizes the same vertical slice rather than implementing a separate intelligence stack.

### Phase C — Gateway
One real provider, one capability, explicit policy, audit log.

### Phase D — Security
Security review and evidence chain are integrated into the same workflow.

## Current product hierarchy

```text
TIER 1 — FLAGSHIP
  MindForge

TIER 1 — CORE INFRASTRUCTURE
  KNOWLEDGE_CORE

TIER 2 — PRODUCT COMPONENTS
  MindForge-Studio
  PRODUCT_SPEC_UniversalAgent

TIER 2 — ENGINEERING PLATFORM/LAB
  META-FOUNDRY

TIER 4 — HISTORICAL / SOURCE MATERIAL
  gpt-agent

UNCLASSIFIED
  remaining agentic repositories pending inspection
```

## Next action

Audit the remaining agentic repositories and collapse them into this hierarchy. Only after that should repository renames, archives, redirects or merges be proposed.
