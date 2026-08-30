# FATHER Visual Knowledge Workspace — Standards Crosswalk: System/AI Standards vs FSTEC Security Standards

Status: DRAFT BASELINE
Purpose: compare the current FATHER standards stack with active Russian information-security standards developed by or with FSTEC Russia, identify semantic overlaps and engineering gaps.

> Important: this is a semantic/engineering crosswalk, not a statement of legal equivalence or mandatory applicability. Applicability depends on system class, certification scope, regulatory context and product profile.

## 1. Current FATHER baseline

Current system/AI/engineering standards already referenced by the project include:
- GOST R 57100-2025 / ISO/IEC/IEEE 42010 — architecture descriptions;
- GOST R 57193-2025 / ISO/IEC/IEEE 15288 — system life cycle;
- GOST R ISO/IEC 12207-2010 / ISO/IEC/IEEE 12207 — software life cycle;
- GOST R 59194-2020 / ISO/IEC/IEEE 29148 — requirements engineering;
- GOST R ISO/IEC 25010-2015 / ISO/IEC 25010 — software/product quality;
- GOST R ISO 9241-210-2016 / ISO 9241-210 — human-centred design;
- GOST R ISO/IEC 42001-2024 / ISO/IEC 42001 — AI management system;
- PNST 838-2023 / ISO/IEC 23053 — AI/ML system framework;
- ISO/IEC 27001 family / Russian national adoption — information-security management;
- C4, UML/BPMN, OpenAPI and OpenTelemetry as engineering notations/specifications.

## 2. FSTEC-developed / FSTEC-related standards that matter to FATHER

### FSTEC-01 — GOST R 72118-2025
**Systems secure by design. Development methodology.**

Overlap with FATHER:
- system life-cycle engineering;
- architecture and architecture decisions;
- security requirements and trust boundaries;
- verification/validation gates;
- security-by-design principle.

What it adds beyond the current baseline:
- security is a constructive system property, not a later overlay;
- explicit security methodology across system development;
- stronger relationship between requirements, architecture and trust;
- need to prove the security properties of the resulting system.

FATHER gap:
- security concerns are not yet first-class nodes for every architecture element;
- no mandatory SECURITY_VIEW / SECURITY_CONCERN / SECURITY_ARGUMENT chain;
- no security-by-design acceptance profile bound to every development gate.

Required action:
`REQ -> SECURITY_REQUIREMENT -> ARCH_ELEMENT -> SECURITY_MECHANISM -> VERIFY -> EVIDENCE`

Priority: **P0**.

---

### FSTEC-02 — GOST R 56939-2024
**Secure software development. General requirements.**

Overlap with FATHER:
- software life cycle;
- quality gates;
- DevSecOps;
- code review/testing;
- vulnerability remediation;
- traceable development evidence.

What it adds:
- explicit secure-SDLC process;
- static analysis, dynamic analysis, composition analysis and functional testing as security activities;
- vulnerability handling as a managed engineering process;
- security evidence for process conformity.

FATHER gap:
- no formal SECURE_SDLC profile yet;
- SAST/DAST/SCA are tools in plans but not mandatory lifecycle gates;
- vulnerability records are not yet linked as first-class nodes to source code, component, release, fix and verification evidence;
- no release gate that blocks unsafe artifacts based on this profile.

Required action:
`CODE -> SAST/DAST/SCA/TEST -> FINDING -> FIX -> RETEST -> SECURITY_APPROVAL -> RELEASE`

Priority: **P0**.

---

### FSTEC-03 — GOST R 58412-2019
**Secure software development. Security threats during software development.**

Overlap with FATHER:
- risk register;
- threat modelling;
- supply-chain/security concerns;
- evidence-based review.

What it adds:
- threat set specifically for the software-development process/environment;
- mapping from development threats to protective measures;
- explicit treatment of the development environment as part of the attack surface.

FATHER gap:
- current risk register focuses mainly on product/runtime risks;
- no DEVELOPMENT_THREAT model linked to repo, developer workstation, CI/CD, dependency, build artifact and release;
- no threat-to-control traceability for the development environment.

Required action:
`DEV_ASSET -> DEV_THREAT -> CONTROL -> CHECK -> EVIDENCE -> RESIDUAL_RISK`

Priority: **P0/P1**.

---

### FSTEC-04 — GOST R 71207-2024
**Secure software development. Software static analysis. General requirements.**

Overlap with FATHER:
- SAST;
- quality and security verification;
- automated testing;
- CI gates.

What it adds:
- requirements to the static-analysis process itself;
- classification of defects/errors found by static analyzers;
- requirements to methods, tools and specialists;
- verification methodology for static-analysis tools.

FATHER gap:
- currently a tool such as Semgrep/Bandit can be configured, but tool qualification, error taxonomy and evidence standard are not formalized;
- no SAST_EVIDENCE object and no explicit false-positive/review lifecycle.

Required action:
`SAST_RUN -> FINDING -> CLASSIFICATION -> TRIAGE -> FIX/ACCEPT -> RETEST -> EVIDENCE`

Priority: **P1**.

---

### FSTEC-05 — GOST R 59547-2021
**Information-security monitoring. General provisions.**

Overlap with FATHER:
- observability;
- monitoring;
- trace/log/metric architecture;
- incident awareness.

Key distinction:
**observability != information-security monitoring.**

FATHER gap:
- TRACE_EVENT is currently primarily engineering/runtime provenance;
- no separate security-monitoring model with detection rules, monitored security states, security alerts and analyst resolution.

Required action:
create separate but correlated domains:
`TRACE_EVENT` — engineering/debug lineage;
`SECURITY_EVENT` — security-relevant occurrence;
`ALERT` — detection result;
`INCIDENT_CANDIDATE` — case/review object.

Correlation:
`trace_id / request_id / entity_id / actor_id / session_id`.

Priority: **P1**.

---

### FSTEC-06 — GOST R 59548-2022
**Security event logging. Requirements for recorded information.**

Overlap with FATHER:
- Audit Emitter;
- trace/event records;
- append-only history;
- investigation timeline.

What it adds:
- security-specific minimum semantic information for registered events;
- events must be usable for monitoring, security analysis, incident detection and operational control.

FATHER gap:
- trace schema is not yet a security-event schema;
- actor/auth context, security outcome, target resource and policy decision are not mandatory for all relevant events;
- retention/integrity profile for security events is not yet separated from debug traces.

Required action:
introduce `security_event.schema.json` and mapping:
`TRACE_EVENT <-> SECURITY_EVENT` where applicable.

Priority: **P0/P1** because the user requires tracing everywhere.

---

### FSTEC-07 — GOST R 70262.1-2022 + GOST R 70262.2-2025
**Identification and authentication assurance levels.**

Overlap with FATHER:
- Backend auth facade;
- users/roles;
- trust boundaries.

What it adds:
- explicit identification/authentication assurance levels;
- assurance as a formal attribute of an authentication result.

FATHER gap:
- authentication is currently architectural plumbing, not a first-class assurance model;
- no `IDENTITY_ASSURANCE_LEVEL` / `AUTHENTICATION_ASSURANCE_LEVEL` in session/access decisions;
- no relationship between operation criticality and required authentication assurance.

Required action:
`ACTOR -> IDENTITY -> AUTH_METHOD -> ASSURANCE_LEVEL -> SESSION -> POLICY_DECISION`

Priority: **P1** for MVP, **P0** before regulated production.

---

### FSTEC-08 — GOST R 71753-2024
**Automated account and access-right management systems. General requirements.**

Overlap with FATHER:
- role-based views;
- project/workspace users;
- API authorization.

Critical distinction:
`ROLE_VIEW` is a knowledge perspective, not an access-control role.

FATHER gap:
- role views and security roles must be separated explicitly;
- no full account-right lifecycle yet: create/change/approve/revoke/review;
- no access-governance evidence chain.

Required action:
separate:
- `KNOWLEDGE_ROLE_VIEW` — Architect/Lawyer/Security/etc.;
- `SECURITY_ROLE` / `ENTITLEMENT` — actual authorization.

Add:
`ACCOUNT -> ROLE -> ENTITLEMENT -> APPROVAL -> REVIEW -> REVOKE`.

Priority: **P1**.

---

### FSTEC-09 — GOST R 59453.2-2021, 59453.3-2025, 59453.4-2025
**Formal access-control model: verification/development/verification of protection mechanisms.**

Overlap with FATHER:
- policy gates;
- authorization;
- graph of actors/resources/actions;
- testable architecture contracts.

What it adds:
- formal access-control model;
- formal verification approach;
- stronger proof requirements for high-assurance protection functions.

FATHER gap:
- authorization is not formally modelled;
- no machine-verifiable access-control model independent from application code.

Required action:
create `ACCESS_CONTROL_MODEL` as an optional high-assurance profile and make policies exportable/testable.

Priority: **P2 for MVP**, **P0/P1 for high-assurance/certification profile**.

---

### FSTEC-10 — GOST R 56938-2016
**Information protection when using virtualization technologies.**

Overlap with FATHER:
- Docker/VM/cloud deployment;
- trust boundaries;
- infrastructure security.

FATHER gap:
- virtualization/container threat profile is not yet a dedicated architecture concern;
- runtime isolation and host/hypervisor assumptions are not explicit architecture evidence.

Priority: **P2 until container/VM production deployment**, then P1.

---

### FSTEC-11 — GOST R 71206-2024
**Secure compiler for C/C++. General requirements.**

Overlap with FATHER:
- compiler/toolchain trust;
- software supply chain;
- reproducible build/security evidence.

FATHER gap:
- not relevant to the current Python/TypeScript-first MVP unless C/C++ components are introduced;
- should exist as a conditional technology profile rather than mandatory project baseline.

Priority: **CONDITIONAL**.

## 3. Coverage summary

| Domain | Current FATHER coverage | FSTEC additions | Result |
|---|---|---|---|
| Requirements | strong | security requirements/assurance | PARTIAL GAP |
| Architecture | strong | constructive security methodology | PARTIAL GAP |
| System lifecycle | strong | security integrated into lifecycle | PARTIAL GAP |
| Software lifecycle | strong | secure SDLC | MAJOR GAP |
| Quality | strong | vulnerability/security quality evidence | PARTIAL GAP |
| UX | strong | little direct overlap | COVERED BY OWN STACK |
| AI governance | strong | FSTEC layer not the primary source | COVERED BY OWN STACK |
| Threat modelling | generic | development-environment threat model | MAJOR GAP |
| Static analysis | planned | formal process/tool/evidence requirements | MAJOR GAP |
| Dynamic/SCA security testing | planned | lifecycle-gated security activity | GAP |
| Observability | strong conceptually | security monitoring semantics | MAJOR GAP |
| Trace/audit | strong conceptually | security-event semantics | MAJOR GAP |
| IAM | basic architecture | assurance levels + account/right lifecycle | MAJOR GAP |
| Access-control formalization | low | formal models and verification | GAP / HIGH-ASSURANCE |
| Virtualization/container security | generic | dedicated protection profile | PARTIAL GAP |
| C/C++ toolchain assurance | not current scope | secure compiler profile | CONDITIONAL |

## 4. New mandatory FATHER security objects

To close the meaningful gaps without corrupting the existing domain model, add first-class objects:

- `SECURITY_REQUIREMENT`
- `SECURITY_CONCERN`
- `SECURITY_ARGUMENT`
- `DEV_ASSET`
- `DEV_THREAT`
- `CONTROL`
- `SAST_RUN`
- `SECURITY_FINDING`
- `VULNERABILITY`
- `SECURITY_EVENT`
- `ALERT`
- `INCIDENT_CANDIDATE`
- `IDENTITY`
- `AUTH_METHOD`
- `ASSURANCE_LEVEL`
- `SECURITY_ROLE`
- `ENTITLEMENT`
- `POLICY_DECISION`
- `ACCESS_CONTROL_MODEL`
- `SECURITY_EVIDENCE`

Do not reuse `ROLE_VIEW` for authorization.

## 5. New canonical security trace

```text
REQUIREMENT
-> SECURITY_REQUIREMENT
-> THREAT
-> CONTROL
-> ARCH_ELEMENT
-> IMPLEMENTATION
-> TEST / SAST / DAST / SCA
-> SECURITY_FINDING
-> FIX
-> RETEST
-> SECURITY_APPROVAL
-> RELEASE
-> SECURITY_EVENT / MONITORING
-> INCIDENT / OUTCOME
-> LESSON
```

Every node retains evidence, owner, status, timestamps, version and trace references.

## 6. Integration priority

### P0 — add before serious implementation
1. GOST R 72118-2025 profile: secure-by-design architecture.
2. GOST R 56939-2024 profile: secure SDLC.
3. GOST R 58412-2019: development threat model.
4. Security-event model compatible with GOST R 59548-2022.

### P1 — build into MVP architecture
5. GOST R 71207-2024: SAST process/evidence.
6. GOST R 59547-2021: security monitoring.
7. GOST R 70262.1/.2: identity/auth assurance.
8. GOST R 71753-2024: account/right lifecycle.

### P2 / profile-specific
9. GOST R 59453.x formal access-control model.
10. GOST R 56938-2016 virtualization.
11. GOST R 71206-2024 secure C/C++ compiler.

## 7. Important non-FSTEC gap discovered

For the AI product itself also add **GOST R 71752-2024 — Artificial intelligence. Technical assignment. Requirements to contents**. It is not a FSTEC standard, but it directly strengthens `MASTER_TZ_V1.md` and the AI-specific acceptance/contract sections.

## 8. Engineering conclusion

The current FATHER stack is strong in **system architecture, requirements, lifecycle, quality, UX and AI governance**.

The FSTEC family contributes the missing **security engineering spine**:

`SECURE-BY-DESIGN -> SECURE SDLC -> DEV THREAT MODEL -> SECURITY TESTING -> IAM/ACCESS -> SECURITY EVENTS -> MONITORING -> EVIDENCE`.

The correct target is not replacement but composition:

```text
SYSTEM / AI STANDARDS
+ FSTEC SECURITY STANDARDS
+ C4 / OpenAPI / OpenTelemetry engineering specifications
+ verified books and production evidence
= FATHER ENGINEERING METHOD
```
