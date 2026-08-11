# Test Contract

Every reusable engineering solution must be verified against a common test contract before it can be promoted into decision memory.

## Required test classes

1. **Nominal cases** — typical valid inputs.
2. **Boundary cases** — empty, single-item, minimum/maximum relevant sizes.
3. **Negative cases** — absent values, invalid inputs, unsupported states.
4. **Property checks** — invariants that should hold across many inputs.
5. **Adversarial cases** — malformed, oversized or attacker-influenced inputs where relevant.
6. **Regression cases** — previously discovered failures.

## Required metadata

Each test suite should record:

- problem ID;
- implementation ID;
- language/runtime/compiler version;
- test framework;
- expected behaviour;
- pass/fail status;
- known limitations;
- security-relevant cases;
- date/version of the implementation under test.

## Promotion rule

A solution is not eligible for reusable decision memory unless:

- correctness tests pass;
- known failure modes are documented;
- security-relevant cases are covered when applicable;
- benchmark claims, if any, are measured separately under the benchmark contract.

Testing proves behaviour for tested conditions. It does not prove universal correctness.

← [Engineering Knowledge](../README.md)
