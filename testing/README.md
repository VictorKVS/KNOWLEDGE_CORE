# Testing & Verification Knowledge

Testing is evidence about behaviour under specified conditions, not a binary proof that software is universally correct.

## Verification layers

- unit tests;
- integration tests;
- contract tests;
- property-based tests;
- regression tests;
- fuzzing;
- static analysis;
- sanitizers and runtime checks;
- performance/load tests;
- failure-injection tests;
- security tests.

## Selection questions

- Which invariant is being verified?
- What failure would be expensive or dangerous?
- Which boundary needs an integration or contract test?
- Which input space is too large for hand-written examples?
- Which historical bugs need permanent regression tests?
- Which properties can be checked automatically?

## Rule

Test depth should follow risk, complexity and trust boundary. Do not optimize for test count or coverage percentage alone; optimize for meaningful evidence about the failure modes that matter.

← [Engineering Knowledge](../README.md)
