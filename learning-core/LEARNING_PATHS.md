# Learning Paths

Learning paths are views over the same evidence-driven knowledge graph. They do not duplicate source knowledge.

## Three competency paths

### Junior — Reliable Implementation
Goal: turn a clear contract into correct, readable and safely tested code.

Sequence:
1. values, types and data representation;
2. control flow and functions;
3. collections and basic data structures;
4. errors and boundary validation;
5. search and sorting;
6. tests and debugging;
7. files, I/O and APIs;
8. simple composition;
9. secure defaults;
10. Elegant → Production transformations.

Exit evidence:
- can implement a defined task in Python, Go or C++;
- can explain invariants and complexity at the required level;
- writes tests for normal and boundary cases;
- does not hide uncertainty or invent evidence.

### Middle — Engineering Choice
Goal: independently choose a sound implementation strategy for a component.

Sequence:
1. representation and data-structure choice;
2. patterns and anti-patterns;
3. interfaces and module boundaries;
4. concurrency strategies;
5. database/network integration;
6. property/fuzz testing where useful;
7. profiling and benchmark interpretation;
8. dependency and supply-chain decisions;
9. observability and failure handling;
10. decision-memory reuse.

Exit evidence:
- compares alternatives instead of defaulting to habit;
- understands preparation/update/query trade-offs;
- recognizes trust and failure boundaries;
- can adapt a verified prior solution without blindly copying it.

### Senior — System Outcome
Goal: minimize total system complexity while preserving correctness, security, reliability and reversibility.

Sequence:
1. requirements pressure and constraint challenge;
2. architecture boundaries;
3. distributed-system trade-offs;
4. consistency, idempotency and partial failure;
5. capacity/performance strategy;
6. security architecture and abuse cases;
7. migration and rollback;
8. observability and operations;
9. evidence gaps and analyst delegation;
10. reusable decision creation and retirement of obsolete knowledge.

Exit evidence:
- can remove unnecessary architecture rather than merely add it;
- makes irreversible decisions explicit;
- separates measured fact from engineering judgement;
- delegates research-heavy algorithmic questions to Analyst/Research Agent;
- leaves behind reusable, traceable engineering knowledge.

## Cross-language path

A topic should not be repeated three times as unrelated tutorials. The learning object defines the engineering concept; Python, Go and C++ show how language semantics change the implementation.

Example:

`Membership lookup → same problem → list/slice/vector → set/map/unordered_set → different runtime and ownership implications`

## Competitive/elegance path

Selected problems also expose a reasoning path:

`Brute force → observation → invariant → transformation → elegant solution → proof → production hardening`

This path trains concise problem solving without teaching code golf.

## Evidence path

For users who want to inspect why a decision is trusted:

`Learning Object → Decision/Claim → Source → Benchmark/Experiment → Decision Memory`

The future site should allow this path to be opened progressively rather than overwhelming beginners with research metadata by default.
