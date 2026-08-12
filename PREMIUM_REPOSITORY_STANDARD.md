# PREMIUM REPOSITORY STANDARD

> A repository must prove its quality through architecture, evidence, tests, documentation, security and machine readability — not through decoration alone.

## North Star

KNOWLEDGE_CORE is developed as a premium engineering product and as the reference standard for future Father/MindForge repositories.

```text
HUMAN READABLE + AGENT READABLE + EVIDENCE DRIVEN + EXECUTABLE + AUDITABLE
```

## Quality dimensions

| Dimension | Weight | Minimum premium target |
|---|---:|---:|
| Architecture | 15 | 90 |
| Documentation | 15 | 90 |
| Code quality | 15 | 90 |
| Tests & CI | 15 | 90 |
| Security | 15 | 90 |
| Evidence & provenance | 15 | 90 |
| Agent readability | 5 | 90 |
| Visual consistency | 5 | 85 |

A repository is `PREMIUM` only when the weighted score is >= 90 and no critical dimension is below its minimum.

## P0 — Trust and correctness

Required before visual polish:

- canonical source-of-truth boundaries are explicit;
- tests and validators are executable;
- CI gates protect important invariants;
- security-sensitive claims have provenance;
- generated/index data is clearly separated from canonical data;
- stale, contradictory and unresolved evidence remains visible;
- no fake badges, fake metrics or unverifiable claims.

## P1 — Human experience

The root README should answer within roughly 30 seconds:

1. What is this?
2. Why does it exist?
3. What is different about it?
4. How does the architecture work?
5. How do I run the smallest useful example?
6. Where are the docs, roadmap, security policy and contribution rules?

Use a consistent visual language, concise diagrams and progressive disclosure. Decorative elements must never obscure technical content.

## P1 — Agent experience

Agents should be able to discover and reason over the repository without scraping prose blindly:

- stable IDs for canonical knowledge objects;
- YAML/JSON schemas or templates;
- explicit typed relations;
- generated knowledge index;
- deterministic query/runtime interfaces;
- provenance and evidence references;
- ownership/routing metadata;
- explicit applicability, uncertainty, health and status.

## P1 — Engineering experience

Expected baseline:

- reproducible setup;
- typed production code where practical;
- tests close to executable behavior;
- lint/format/static checks;
- meaningful commit messages;
- small, understandable modules;
- examples that execute;
- failure states documented;
- ADRs for consequential design decisions.

## P1 — Security experience

Security is part of repository quality, not a final checklist:

- SECURITY.md;
- dependency and secret scanning where applicable;
- least-privilege workflow permissions;
- explicit trust boundaries;
- no secrets or sensitive evidence committed;
- authorized-pentest rules separated from general knowledge;
- primary-source provenance for regulatory/security requirements.

## P2 — Visual system

Preferred section vocabulary:

```text
◆ ARCHITECTURE
◇ KNOWLEDGE
◈ EVIDENCE
⬡ AGENTS
▣ SECURITY
⌁ RESEARCH
✓ VERIFIED
⚠ REVIEW
```

Large ASCII/3D-style headers may be used for major landing pages, but normal technical pages should remain compact and searchable.

## Required repository surfaces

For a mature public repository, expect these surfaces where applicable:

```text
README.md
ARCHITECTURE.md
ROADMAP.md
SECURITY.md
CONTRIBUTING.md
CHANGELOG.md
LICENSE
CODE_OF_CONDUCT.md
.github/workflows/
docs/
examples/
tests/
```

Not every file is mandatory for an early prototype. The Premium Gate must distinguish `not-applicable`, `planned`, `present` and `verified` rather than reward empty placeholder files.

## Premium maturity

```text
LEVEL 0  EXPERIMENT   — idea/code exists
LEVEL 1  STRUCTURED   — repository is navigable
LEVEL 2  VERIFIED     — tests, CI and evidence exist
LEVEL 3  PREMIUM      — >=90 score, no critical gaps
LEVEL 4  REFERENCE    — reusable standard adopted by other repositories
```

## Rule for all future Father repositories

New repositories should inherit this standard from the beginning. Do not postpone architecture, provenance, tests and machine readability until after content growth.
