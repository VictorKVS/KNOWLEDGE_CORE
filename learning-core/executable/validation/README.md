# Executable Learning Object — Boundary Validation

This package turns the trust-boundary validation lesson into executable practice for Python, Go and C++.

The shared contract is intentionally small:

- username is trimmed;
- username length is 1..64;
- age is an integer-domain value in 0..130;
- invalid data is rejected before entering trusted application logic.

The language implementations are not required to look identical. They should express the same engineering contract idiomatically.

## Why this object matters

This is a production-oriented exercise rather than an algorithm research exercise. No literature search is needed to invent a novel algorithm. The Programming Agent practices explicit contracts, boundary validation, tests and readable failure behaviour.

## Maturity

Current target: **tested** once the repository CI executes all three suites successfully.

Evidence-linked and production-reviewed are later promotions and must not be inferred merely from the presence of tests.
