# ENG-NUM-001 — Representing Money Safely

**Question:** How should monetary values be represented in application code?

## Short answer

For most transactional systems, prefer **integer minor units** (for example, cents) when the currency and scale are fixed and well-defined. Use a **decimal arithmetic type** when decimal semantics, configurable scale, accounting-style rounding, or heterogeneous monetary precision are required. Avoid binary floating point as the authoritative representation of money unless the domain explicitly tolerates approximation and rounding behavior is carefully controlled.

This is a context-sensitive engineering decision, not a universal ban on floating point.

## Why this decision exists

Binary floating-point formats cannot exactly represent many common decimal fractions. That makes them excellent for many scientific and numerical workloads, but potentially awkward as the authoritative representation for quantities whose semantics are defined in decimal units.

## Candidate approaches

### 1. Integer minor units

Example: store EUR 12.34 as `1234` cents.

**Strengths**
- exact integer arithmetic within range;
- simple equality and comparison semantics;
- usually compact and fast;
- easy to validate and serialize.

**Costs / risks**
- scale must be explicit;
- not every currency or financial instrument uses the same number of fractional units;
- multiplication/division still requires an explicit rounding policy;
- overflow limits remain relevant.

**Prefer when**
- currency scale is fixed and known;
- transactional amounts dominate;
- simple, auditable arithmetic is valuable.

### 2. Decimal arithmetic

Examples include Python `decimal.Decimal`; other ecosystems may require a standard-library or external decimal implementation.

**Strengths**
- decimal fractions such as 0.1 can be represented exactly within the decimal model;
- configurable precision and rounding policies;
- often maps naturally to accounting rules and database `DECIMAL`/`NUMERIC` columns.

**Costs / risks**
- more complex than integer minor units;
- performance characteristics differ from native binary floating point;
- contexts, precision and rounding policy must be controlled consistently.

**Prefer when**
- business rules are expressed directly in decimal arithmetic;
- multiple scales or precision requirements exist;
- accounting-grade rounding semantics are central.

### 3. Binary floating point

Examples: Python `float`, Go `float64`, common C++ floating-point types.

**Strengths**
- hardware-supported and highly efficient on mainstream systems;
- appropriate for a very large class of scientific, engineering, graphics and statistical workloads;
- standardized floating-point behavior is widely available through IEEE 754 / ISO/IEC 60559 families, though language-level details vary.

**Costs / risks for money**
- many decimal fractions are only approximations in binary representation;
- equality, accumulation and rounding require care;
- reproducibility details may differ across language/compiler/platform contexts.

**Prefer when**
- approximation is acceptable;
- numerical analysis has established error bounds;
- the quantity is not an authoritative decimal financial value.

## Selection rule

```text
Fixed currency + fixed minor-unit scale?
        │
       yes ──► integer minor units
        │
       no
        ▼
Decimal business semantics / controlled decimal rounding required?
        │
       yes ──► decimal arithmetic
        │
       no
        ▼
Approximation acceptable and numerical error understood?
        │
       yes ──► binary floating point
        │
       no ──► refine requirements before implementation
```

## Cross-language guidance

### Python
- integer minor units: built-in `int`;
- decimal arithmetic: `decimal.Decimal`;
- binary floating point: `float`.

Python documentation explicitly notes that many decimal fractions cannot be represented exactly in binary floating point and points to `decimal` when exact decimal representation is required.

### Go
- integer minor units: built-in integer types, with range chosen from domain constraints;
- exact rational or arbitrary-precision arithmetic: `math/big` provides `Int`, `Rat` and `Float`;
- production decimal-money semantics generally require either integer minor units or a deliberately selected decimal package/design.

### C++
- integer minor units are often represented with a fixed-width integer type selected for range requirements;
- built-in floating-point semantics require explicit attention to implementation and reproducibility constraints;
- WG21 continues active work clarifying and tightening floating-point semantics, which is itself evidence that portability/reproducibility assumptions should be documented rather than guessed.

## Security and reliability review

Check at minimum:

- integer overflow / underflow;
- currency and scale confusion;
- untrusted values causing extreme allocations or pathological computations in arbitrary-precision types;
- inconsistent rounding between services;
- parsing ambiguity and locale-dependent input;
- database/application scale mismatch;
- serialization and API contracts;
- boundary tests for maximum/minimum transaction values.

## Evidence status

| Claim | Status | Evidence |
|---|---|---|
| Many decimal fractions are not exact in binary floating point | DOCUMENTED | Python docs; IEEE 754 family |
| Python Decimal supports decimal arithmetic with explicit precision/rounding | DOCUMENTED | Python standard library docs |
| Go `math/big` provides arbitrary-precision Int, Rat and Float | DOCUMENTED | Go official source/docs |
| Integer minor units are always best for every financial system | **NOT CLAIMED** | Context dependent |
| A specific approach is fastest in this project | UNKNOWN until benchmarked | Requires workload benchmark |

## Required project-level validation

Before an agent applies this decision to production code it must know:

1. currencies involved;
2. required scale and rounding rules;
3. maximum amount and accumulation ranges;
4. database representation;
5. external API representation;
6. regulatory/accounting constraints;
7. performance requirements.

If these are unknown, the agent should ask or mark the decision **INSUFFICIENT_CONTEXT** rather than invent assumptions.

## Sources

- [SRC-NUM-001 — IEEE 754-2019](../../sources/numerics/SRC-NUM-001-ieee-754.md)
- [SRC-PY-001 — Python floating-point issues and limitations](../../sources/python/SRC-PY-001-floating-point.md)
- [SRC-PY-002 — Python `decimal`](../../sources/python/SRC-PY-002-decimal.md)
- [SRC-GO-001 — Go `math/big`](../../sources/go/SRC-GO-001-math-big.md)
- [SRC-CPP-001 — WG21 floating-point semantics](../../sources/cpp/SRC-CPP-001-floating-semantics.md)

---

[← Engineering Knowledge](../../README.md) · [Languages](../../languages/README.md)
