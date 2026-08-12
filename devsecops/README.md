# DevSecOps Engineering Knowledge

Security is part of the engineering decision, not a final checklist after implementation.

## Decision path

```text
Requirement
  ↓
Trust boundaries
  ↓
Threat / misuse cases
  ↓
Architecture and implementation alternatives
  ↓
Secure defaults
  ↓
Tests + SAST/SCA/secret checks where applicable
  ↓
Fuzz / DAST / adversarial testing where applicable
  ↓
Deployment controls
  ↓
Observability / incident evidence
  ↓
Decision Memory
```

## Knowledge domains

- threat and misuse modeling;
- input validation and resource bounds;
- authentication and authorization boundaries;
- secrets and key handling;
- dependency and supply-chain risk;
- secure build and CI/CD;
- SAST, SCA, secret scanning and linting;
- DAST and runtime verification;
- fuzzing and parser robustness;
- container and deployment hardening;
- logging, monitoring and evidence preservation;
- vulnerability response and regression tests.

## Core rule

A solution that is faster or shorter but creates an unjustified trust boundary, dependency, parser exposure, unbounded resource path or unverifiable deployment assumption is not automatically the better engineering solution.

## Evidence integration

Security conclusions use the same object model as the rest of the repository: `SRC → CLM → ADR/PROB → TEST/EXP → DM`. Findings that change a reusable decision must become regression tests or explicit selection constraints where possible.

← [Engineering Knowledge](../README.md)
