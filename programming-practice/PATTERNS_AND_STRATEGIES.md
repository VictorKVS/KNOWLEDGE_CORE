# Patterns and Strategies of Modern Programming

This section is the practical core of the Programming Agent.

The objective is not to maximize the number of named patterns in a codebase. The objective is to produce code that is correct, secure, efficient, structurally elegant, easy to verify and appropriate to the real constraints.

## Strategy families

### 1. Simplification strategies
- reduce mutable state;
- make invariants explicit;
- prefer direct data flow;
- remove accidental abstraction;
- isolate side effects;
- separate policy from mechanism;
- choose data structures that make the operation natural.

### 2. Composition strategies
- functions and pure transformations;
- composition over unnecessary inheritance;
- adapters at external boundaries;
- dependency injection when substitution or testing actually requires it;
- pipelines for staged transformations;
- state machines for explicit lifecycle behaviour.

### 3. Data-oriented strategies
- transform representation before adding control-flow complexity;
- index repeated queries when evidence justifies preparation cost;
- normalize only where the data model benefits;
- exploit locality and batching when measured workloads justify it;
- prefer immutable/value-oriented representations when they reduce reasoning cost.

### 4. Reliability strategies
- fail fast on violated invariants;
- validate at trust boundaries;
- make retries bounded and intentional;
- design idempotency where repeated execution is possible;
- expose cancellation and timeouts;
- make partial failure explicit.

### 5. Security strategies
- least privilege;
- deny by default where appropriate;
- minimize exposed state and interfaces;
- parse and validate untrusted input defensively;
- avoid secret material in code/logs;
- prefer safe library primitives over custom security mechanisms.

### 6. Performance strategies
- measure before optimizing;
- optimize the dominant path rather than visually expensive code;
- reduce algorithmic cost before micro-optimizing syntax;
- avoid unnecessary allocations/copies when evidence shows material impact;
- preserve readability unless measured gain justifies complexity.

### 7. Competitive-programming-derived strategies
Use the good parts:
- derive invariants before implementation;
- reduce the problem to a smaller equivalent form;
- precompute when repeated work dominates;
- use monotonicity, prefix information, hashing, two pointers, divide-and-conquer, graph structure and dynamic programming when the problem actually has those properties;
- look for a representation that makes the solution obvious;
- seek a short proof of correctness.

Do not import the bad parts:
- code golf;
- cryptic identifiers outside tiny local scopes;
- undocumented tricks;
- unsafe assumptions about input;
- global mutable contest templates;
- premature micro-optimization.

## Pattern admission rule

A named pattern is admitted only when it solves a demonstrated problem.

Before introducing a pattern, answer:
1. What concrete pressure requires it?
2. What is the simpler alternative?
3. What complexity does the pattern add?
4. Does it improve changeability, testing, safety or clarity enough to pay for itself?
5. Can a future engineer remove it safely if the pressure disappears?

## Code beauty review

A strong implementation should make reviewers answer yes to most of these questions:

- Is the core idea visible quickly?
- Are invariants and ownership understandable?
- Is data flow easy to follow?
- Are names carrying useful meaning?
- Is there unnecessary state or indirection?
- Is error behaviour explicit?
- Is the code shorter because the model is better, rather than because information was hidden?
- Can important behaviour be tested without heroic setup?
- Are security boundaries visible?
- Can performance-sensitive choices be traced to evidence?

## Two-view learning model

For suitable algorithmic exercises, store both:

**Elegant / Olympiad View** — exposes the minimal algorithmic insight and proof.

**Production View** — preserves the insight while adding contracts, naming, validation, errors, tests, security and operational behaviour.

The transformation between the two views is itself reusable programming knowledge.

---

See also: [Olympiad Elegance](OLYMPIAD_ELEGANCE.md) and [Engineering Knowledge](../README.md).
