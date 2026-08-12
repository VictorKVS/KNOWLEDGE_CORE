# Olympiad Elegance in Production Engineering

Competitive programming contributes valuable habits to engineering: precise problem reduction, strong invariants, careful complexity reasoning, compact expression, data-structure awareness and the ability to find non-obvious solutions.

The repository treats these qualities as a source of **engineering elegance**, not as permission for code golf.

## Principle

Beautiful code should be:

- correct;
- secure;
- asymptotically and practically appropriate;
- compact without becoming cryptic;
- explicit about important invariants;
- easy to test;
- easy to review;
- easy to modify by another engineer;
- idiomatic for the language;
- visually and structurally clean.

## Priority order

1. Correctness and invariant preservation.
2. Security and defined behaviour.
3. Fit to the actual constraints.
4. Reliability and testability.
5. Clarity and maintainability.
6. Performance where it matters.
7. Elegance and compactness.

Elegance is a multiplier on a good solution, not a substitute for the previous requirements.

## Good competitive-programming influence

Prefer:

- reducing a problem to a smaller canonical form;
- eliminating unnecessary state;
- choosing the data structure that naturally expresses the operation;
- writing loops around clear invariants;
- exploiting language/library primitives when they make intent clearer;
- removing accidental complexity;
- making the happy path visually obvious;
- producing small functions with strong contracts;
- using mathematical structure when it simplifies both implementation and proof of correctness.

## What must not leak from contests into production

Reject:

- one-letter names outside tiny conventional scopes;
- clever expressions that require mental decompilation;
- hidden mutation or surprising side effects;
- macros/metaprogramming used only to shorten code;
- relying on undefined, implementation-specific or version-sensitive behaviour without explicit justification;
- compressing multiple semantic steps into one line when it harms reviewability;
- omitting error handling because the contest input was guaranteed valid;
- assuming trusted input, unlimited memory or bounded execution time when production cannot make those assumptions;
- premature micro-optimization that makes the implementation harder to verify.

## Elegance test

A solution may be called elegant only if an experienced engineer can answer quickly:

1. What invariant makes this work?
2. Why is this data structure / pattern appropriate?
3. What are the complexity and resource bounds?
4. Where can it fail?
5. What assumptions are being made?
6. Can it be tested without understanding hidden tricks?
7. Would a competent engineer unfamiliar with the code be able to change it safely later?

If compactness makes any of those answers materially harder, the code is not elegant; it is merely clever.

## Two representations when useful

For educational and analytical material it is acceptable to preserve two variants:

- **Olympiad / minimal form** — exposes the mathematical or algorithmic core.
- **Production form** — adds naming, contracts, validation, observability, error handling, security controls and maintainability.

Both should link to the same problem, algorithm/evidence records and tests. This makes the difference between algorithmic beauty and production engineering explicit instead of pretending they are identical.

## Desired style

The target is code that makes a reviewer think:

> “That is unexpectedly small and clean — and I can immediately see why it is correct.”

Not:

> “That is impressive, but I need twenty minutes to understand what happened.”

---

[← Programming Practice](README.md)
