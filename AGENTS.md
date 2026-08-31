# KNOWLEDGE_CORE — Codex operating contract

Codex must read and obey this file before changing the repository.

## Repository mission

Maintain an evidence-first, auditable knowledge repository. The canonical Security Knowledge product tree is `security-knowledge/`.

## Existing governance is authoritative

Before material work, inspect and obey:
- `REPOSITORY_STRUCTURE_PROTECTION.yaml`
- `.ai/agent-collaboration-policy.yaml`
- `.ai/evidence-policy.yaml`
- `.ai/agent-knowledge-access-policy.yaml`
- `.ai/agent-knowledge-routing.yaml`
- any closer `AGENTS.md` / `AGENTS.override.md`

Never move, rename, merge or delete protected paths as generic cleanup.

## Default autonomy

For an explicit request to change/build/fix, make in-scope local changes and run non-destructive validation without asking again. Do not perform destructive operations, rewrite history, delete evidence, publish externally, or materially expand scope without explicit authorization.

Use one focused task/branch/worktree at a time. Keep unrelated streams out of the diff.

## Evidence discipline

- Prefer primary/authoritative sources.
- Prefer `UNKNOWN`/`PENDING` over unsupported certainty.
- Preserve conflicting evidence and uncertainty.
- Record version applicability and status for version-sensitive claims.
- Never invent source URL, retrieval timestamp, MIME, byte length, hash, registration/publication data, status, or applicability.
- Do not treat search rank, secondary summaries, mirrors, or model memory as primary authority.

## Large artifacts

Git is the control plane for code, source cards, manifests, hashes, indexes, derived text, graph edges and audit records. Large original artifacts should live in the configured content-addressed blob store unless repository policy explicitly permits committing them.

Use `KNOWLEDGE_CORE_BLOB_ROOT` for the local immutable blob root when the relevant workflow supports it. Prefer SHA-256 content addressing and deduplication.

## Completion gate

Before declaring a task complete:
1. validate changed structured data;
2. run the narrowest relevant tests/validators/reconciliation;
3. inspect `git diff` for unrelated changes;
4. report exact evidence gaps and failures;
5. do not promote a pending item merely because a target/effective date arrived.

## Code review rules

Prioritize findings that could corrupt provenance, hashes, legal/version status, applicability boundaries, canonical graph identity, counters, or protected repository structure. Treat silent evidence promotion and cross-regime requirement leakage as high severity.