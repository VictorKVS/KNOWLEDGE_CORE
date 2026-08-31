# Codex Local Workforce for Security Knowledge

## Purpose

Use local Codex as a governed production workforce for `VictorKVS/KNOWLEDGE_CORE` rather than as an unstructured coding chat. GitHub remains the auditable control plane; large immutable originals may live in a local content-addressed store referenced by manifests and SHA-256.

## What is configured

- Root `AGENTS.md`: repository-wide operating contract.
- `security-knowledge/AGENTS.md`: stricter fail-closed source/evidence/applicability rules.
- `.codex/config.toml`: enables bounded parallel subagents.
- `.codex/agents/*.toml`: specialized custom agents.
- `.ai/codex-local-workforce.yaml`: workforce lanes and handoff contract.
- `.ai/task-queue/security-kb.yaml`: prioritized production queue.

## Agent roles

1. `source_scout` — official source identity, status, exact route and version-chain research.
2. `byte_acquirer` — exact official bytes, MIME/signature, size, SHA-256, immutable artifact and manifest.
3. `legal_applicability` — legal/regulatory applicability boundaries and cross-regime leakage prevention.
4. `taxonomy_classifier` — multi-label InfoSec taxonomy classification independent of legal applicability.
5. `annotation_builder` — concise expandable explanations and glossary candidates with provenance.
6. `reconciler` — deterministic master inventory, graph and counter integration.
7. `qa_guard` — independent skeptical final review.

## Local storage

Set a large local directory for immutable originals. Example PowerShell for the current shell:

```powershell
$env:KNOWLEDGE_CORE_BLOB_ROOT = "G:\KNOWLEDGE_CORE_BLOBS"
New-Item -ItemType Directory -Force $env:KNOWLEDGE_CORE_BLOB_ROOT | Out-Null
```

Preferred physical layout is content addressed, for example `sha256/ab/<full_sha256>`. A single binary should be stored once even when linked to several InfoSec categories.

Do not commit a large binary merely to make GitHub look complete. The Git evidence must be sufficient to locate and verify the immutable object through its manifest.

## Start interactively

From the repository root:

```powershell
git checkout main
git pull --ff-only
codex
```

Codex reads applicable `AGENTS.md` files before work. In the interactive session, verify `/status` and `/permissions` before a long write-heavy run.

Recommended master prompt:

```text
Read AGENTS.md, security-knowledge/AGENTS.md, .ai/codex-local-workforce.yaml and .ai/task-queue/security-kb.yaml. Run the Security KB queue as an evidence-first orchestrator. Delegate independent read-heavy work to the named custom subagents in parallel. Keep write ownership bounded, do not let parallel agents edit the same master inventory, and wait for evidence packets before reconciliation. Today-sensitive P0 tasks must be checked against primary official evidence. After source work, run reconciler, then qa_guard. Do not mark anything complete when the immutable or applicability gate fails.
```

Use `/agent` to inspect active subagent threads.

## Worktrees

For independent write-heavy lanes, prefer separate Git worktrees. This prevents several agents from modifying one checkout at once. `scripts/START_CODEX_SECURITY_KB_WORKFORCE.ps1` prepares five stage-1 worktrees and can optionally launch a Codex CLI session in each.

The intended order is:

```text
parallel stage 1:
  source_scout
  byte_acquirer
  legal_applicability
  taxonomy_classifier
  annotation_builder
        |
        v
integration stage:
  reconciler
        |
        v
independent gate:
  qa_guard
```

Do not run the reconciler against stale branches. Integrate/rebase accepted lane changes first, then reconcile once from the canonical combined state.

## Current first queue items

The queue intentionally starts with date-sensitive 2026-09-01 checks before normal acquisition work:

- verify whether the tracked replacement of FSTEC Order 21 has actually passed the final-act / Minjust / official-publication gate;
- re-evaluate FSTEC Order 60/2026 effective-status transition;
- re-evaluate FSTEC 137/2026 effective-status transition while preserving its public/GIS scope;
- continue exact primary byte acquisition for PP RF 1119, FSB 378, FSB 66/173, FAPSI 152, FSTEC 205 and the remaining FSTEC methodologies;
- backfill the InfoSec taxonomy and seed expandable explanations for existing materials.

A calendar date alone never proves a legal transition.

## Taxonomy rule

The Habr InfoSec guide is a navigation seed only. It does not create legal obligations. One canonical document can be linked to many categories with `CORE`, `CONDITIONAL` and `REFERENCE_ONLY` roles. Legal applicability remains a separate evidence-backed graph edge.

Guide-derived explanatory text must be concise paraphrase with provenance and `SOURCE_PARAPHRASE_DRAFT`, not a long copied passage.

## Completion packet

Every lane must return:

- task ID and branch/worktree;
- changed paths;
- evidence references;
- facts confirmed;
- facts still unknown;
- validators/tests run;
- whether reconciliation is required.

The final run is complete only after deterministic reconciliation and independent QA, with unresolved evidence gaps explicitly preserved.
