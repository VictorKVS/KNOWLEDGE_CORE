# Patterns and Strategies of Modern Programming

> Practical engineering knowledge for writing software well after the analytical layer has prepared the evidence.

This section belongs primarily to the **Programming Agent**. Its purpose is not to reproduce broad algorithmic research. It focuses on evidence-backed programming practice: how to structure code, choose implementation patterns, manage complexity, create safe boundaries, test behaviour, refactor safely and operate software reliably.

## Core distinction

**Analyst / Research Agent** owns deep algorithmic research, literature review, comparative evidence, claim extraction, benchmark hypotheses and decision briefs.

**Programming Agent** consumes those outputs and owns implementation practice.

```text
Problem
  ↓
Analyst / Research
  ├─ alternatives
  ├─ sources
  ├─ claims
  ├─ algorithm analysis
  ├─ benchmark evidence
  └─ decision brief
        ↓
Programming Agent
  ├─ implementation strategy
  ├─ patterns
  ├─ code structure
  ├─ interfaces
  ├─ error handling
  ├─ testing
  ├─ refactoring
  ├─ secure coding
  └─ operational quality
```

## Practice domains

### Code structure
- cohesive modules and packages;
- separation of concerns;
- dependency direction;
- explicit interfaces and contracts;
- small understandable units without artificial fragmentation.

### Programming patterns
Patterns are treated as contextual tools, not mandatory recipes.

Examples include:
- composition;
- strategy;
- adapter;
- facade;
- repository;
- dependency injection;
- pipeline;
- state machine;
- event-driven handlers;
- functional core / imperative shell;
- immutable data where useful;
- ports and adapters where boundary complexity justifies it.

Every pattern record should state:
- problem it addresses;
- preconditions;
- advantages;
- costs;
- failure modes;
- anti-patterns;
- simpler alternatives;
- language-specific forms;
- supporting evidence or authoritative practice sources.

### Implementation strategies
- simple synchronous flow vs concurrency;
- batch vs streaming;
- eager vs lazy work;
- validation at boundaries;
- fail-fast vs error accumulation;
- immutable vs mutable state;
- stateful vs stateless components;
- library vs framework;
- local abstraction vs shared abstraction;
- custom code vs standard library / mature dependency.

### Error and failure handling
- explicit error contracts;
- retries only where semantics support them;
- timeouts and cancellation;
- idempotency where repeated execution is possible;
- resource cleanup;
- partial failure handling;
- useful diagnostics without sensitive-data leakage.

### Testing practice
- unit tests for local behaviour;
- integration tests for boundaries;
- property tests for invariants;
- regression tests for fixed defects;
- fuzzing for parsers and hostile inputs where relevant;
- end-to-end tests only where their cost is justified.

### Refactoring and maintainability
- evidence before optimization;
- remove accidental complexity;
- preserve externally visible behaviour;
- make dependencies explicit;
- reduce duplication only when the abstraction is stable enough;
- prefer understandable code over clever code.

### Security-by-construction
- validate untrusted inputs at boundaries;
- least privilege;
- safe defaults;
- secret handling;
- dependency provenance;
- secure serialization and parsing;
- resource bounds;
- concurrency safety;
- avoid dangerous primitives when safer abstractions exist.

### Operational programming
- structured logging;
- metrics and traces where useful;
- health/readiness semantics;
- graceful shutdown;
- configuration validation;
- deterministic migrations;
- rollback awareness;
- backward-compatible interfaces where required.

## Pattern selection rule

A pattern is not evidence of good engineering by itself.

Use a pattern only when it reduces a concrete cost or risk in the current context. If a direct implementation is smaller, clearer, safer and easier to maintain, prefer the direct implementation.

## Programming decision flow

`Requirement → Analyst Brief → Constraints → Simplest Viable Implementation → Pattern Check → Security Check → Tests → Review → Operational Feedback`

If the implementation reveals a new algorithmic, performance or evidence question, return that question to the Analyst rather than silently inventing a rule.

## Relationship to language knowledge

The same programming strategy may look different in Python, Go and C++. Language-specific sections describe idiomatic mechanisms; this section describes the higher-level programming practice that should remain recognizable across languages.

---

[← Engineering Knowledge](../README.md) · [Role boundaries](../.ai/role-boundaries.yaml)
