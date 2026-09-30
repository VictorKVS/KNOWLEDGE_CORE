# Architecture Engineering Knowledge

Architecture decisions are treated as constrained engineering choices, not style preferences.

> **Repository note:** this top-level `architecture/` tree is a legacy/candidate knowledge surface. Canonical professional software-architecture practice lives under `professional-knowledge/software-engineering/` and is governed by the professional evidence/review contracts.

## Start here: project intake before design

Before selecting topology or technology, establish whether the project context is sufficiently known.

Canonical practice candidate:

- [Architect Project Intake Playbook](../professional-knowledge/software-engineering/practice/ARCHITECT_PROJECT_INTAKE_PLAYBOOK.md) — expected project inputs, owners, acquisition routes, quality checks, missing-input recovery and the architect-owned working registers.

The key rule is simple: an architect may reconstruct a missing artifact, but an architect-generated draft does not become business/product/security/legal truth until the authoritative owner confirms it.

## Core questions

- What problem boundary is being designed?
- Which constraints are hard, and which are negotiable?
- What failure model is assumed?
- What trust boundaries exist?
- What coupling and operational burden does each option introduce?
- Which parts must scale independently?
- What must remain observable, replaceable and testable?
- What evidence supports the chosen topology?

## Initial decision families

- modular monolith vs distributed services;
- synchronous request/response vs asynchronous messaging;
- centralized vs decentralized state;
- stateless vs stateful components;
- build vs buy vs managed service;
- batch vs streaming;
- event-driven vs command-driven flows;
- local component vs remote service;
- homogeneous stack vs polyglot architecture.

## Selection principle

Prefer the smallest architecture that satisfies current verified constraints and preserves a credible evolution path. Do not introduce distributed-system complexity before the workload, reliability or organizational constraints justify it.

Every major architecture choice should connect to `ADR-*`, `SRC-*`, `CLM-*`, `SEC-REV-*`, tests, experiments and operational outcomes.

← [Engineering Knowledge](../README.md)
