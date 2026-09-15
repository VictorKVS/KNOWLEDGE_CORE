# Backend Test & Acceptance Gate

Status: `DRAFT_V0.1 / TEST-DESIGN-BEFORE-IMPLEMENTATION`

## 1. Purpose

Define test oracles for the backend design before code exists. Implementation is accepted only when it proves the designed invariants and failure semantics.

## 2. Test layers

- domain unit tests;
- application command tests;
- persistence integration tests;
- API contract tests;
- authorization/authority tests;
- concurrency/idempotency tests;
- source/evidence integrity tests;
- graph/impact tests;
- job/outbox tests;
- backup/restore tests;
- security tests;
- performance/capacity tests;
- migration tests;
- end-to-end governance scenarios.

## 3. Domain invariant tests

Mandatory examples:

### T-DOM-001 Immutable baseline
Given promoted baseline, when update membership attempted, then command fails and baseline remains unchanged.

### T-DOM-002 Stable logical identity
Creating new revision preserves logical object ID and creates new revision ID.

### T-DOM-003 Illegal state transition rejected
`VERIFIED → RECEIVED` without explicit rework/supersession command must fail.

### T-DOM-004 Typed relation validation
Invalid source/target class for relation type must fail.

### T-DOM-005 Risk acceptance authority
Non-risk-owner cannot accept residual risk.

### T-DOM-006 Human-only decision
AI/service identity cannot satisfy command policy requiring human authority.

## 4. Evidence tests

### T-EV-001 Source hash integrity
Stored bytes hash equals registered source version hash.

### T-EV-002 Locator resolvability
Line/page/block locator resolves against exact source revision.

### T-EV-003 Source supersession
Superseding source version does not rewrite existing evidence links to new version.

### T-EV-004 Field coverage
Material field without required evidence is reported as uncovered, not silently inferred.

### T-EV-005 Conflict preservation
Conflicting evidence sources remain separately visible until resolved.

## 5. Trace/impact tests

### T-TR-001 Cycle safety
Cyclic relation graph traversal terminates within configured bounds.

### T-TR-002 Shortest path
BFS path query returns expected shortest path under relation filters.

### T-TR-003 Requirement change impact
Material NFR change marks dependent test oracle/review/gate according to impact rules.

### T-TR-004 Cosmetic change
Non-semantic metadata edit does not invalidate unrelated downstream engineering objects.

### T-TR-005 Explainability
Every stale/impact result includes trigger + rule ID + relation path.

## 6. Version/concurrency tests

### T-VC-001 Optimistic conflict
Two writers on same revision: second stale write receives conflict and no last-write-wins mutation.

### T-VC-002 Idempotent material create
Retry with same idempotency key does not create duplicate canonical object.

### T-VC-003 Revision history reconstruction
Object history reconstructs every accepted revision in order.

### T-VC-004 Baseline compare
Baseline diff correctly reports added/removed/changed object and relation revisions.

## 7. Gate/review tests

### T-GT-001 Readiness ≠ decision
Deterministic READY state does not automatically produce PASSED gate.

### T-GT-002 Missing authority
Gate decision without required authority fails closed.

### T-GT-003 Evidence snapshot
Gate decision retains exact evidence/object revision snapshot.

### T-GT-004 Independent review
When separation-of-duty required, producer self-review cannot satisfy gate.

### T-GT-005 Reopen on stale evidence
Material upstream staleness reopens evaluation according to policy.

## 8. Job/outbox tests

### T-JOB-001 Transaction/outbox atomicity
Canonical change and outbox record commit together.

### T-JOB-002 Worker crash retry
Crash after job claim but before success returns job to retry after lease expiration.

### T-JOB-003 Idempotent processing
Repeated parse/export/webhook job does not create duplicate canonical effect.

### T-JOB-004 Dead letter
Permanent repeated failure becomes visible DEAD_LETTER requiring review.

### T-JOB-005 External failure isolation
Connector outage does not rollback already committed canonical command unless external side effect is part of explicit precondition.

## 9. Authorization/security tests

Mandatory negative matrix:
- unauthorized object read;
- cross-project access;
- restricted source download;
- fake client-side role claim;
- unauthorized baseline promotion;
- unauthorized risk acceptance;
- unauthorized gate decision;
- reviewer conflict-of-interest violation;
- AI identity invoking human-only commands;
- break-glass without reason/reauth;
- SSRF attempts;
- malicious upload/archive bomb;
- stored XSS content;
- oversized graph/search/import denial attempt.

## 10. Persistence tests

- referential integrity;
- relation endpoint indexes;
- baseline membership exactness;
- audit append-only policy;
- transaction rollback on invariant failure;
- source/object store key consistency;
- schema migration pre/post invariants.

## 11. Search tests

- exact ID precedence;
- normalized term search;
- structured filters;
- typo-tolerant fallback where enabled;
- project/classification scoping;
- no restricted result leakage through counts/snippets.

## 12. Backup/restore tests

Required scenario:
1. create project with sources, requirements, relations, gate and baseline;
2. backup;
3. restore to clean environment;
4. verify hashes/counts/revisions;
5. run trace query;
6. open baseline;
7. verify authority/audit records;
8. record RTO/RPO evidence when production NFR defined.

## 13. Performance tests

No fake targets yet. Test harness must support measuring:
- object lookup;
- filtered list;
- search;
- trace depth N;
- impact preview;
- baseline diff;
- import size;
- concurrent editors;
- audit throughput;
- job backlog.

Targets are baselined after representative workload definition.

## 14. End-to-end paper-derived scenarios

### E2E-BE-01 Greenfield requirement path
Source/business need → requirement → architecture decision → component → oracle/test → gate → baseline.

### E2E-BE-02 Brownfield import
Existing docs/code → parse/mapping → conflicts/gaps → owner review → canonical candidates; no automatic truth promotion.

### E2E-BE-03 Threat-to-test
Asset/consequence → threat scenario → security requirement → control → security test → evidence → residual risk decision.

### E2E-BE-04 Material change
Change NFR threshold → impact preview → affected ADR/component/test/gate → rework → new baseline.

### E2E-BE-05 Source supersession
Normative/source version superseded → affected evidence flagged → dependent requirements/gates reviewed; historical baseline preserved.

### E2E-BE-06 Failed security test
Security test fails → vulnerability → rework target selected → fix evidence → retest → gate reassessment.

### E2E-BE-07 Unauthorized approval
User with contributor permission but without authority attempts gate/risk approval → backend denies and audits attempt.

### E2E-BE-08 Recovery
Crash/restart during async parsing/notification does not duplicate canonical effects.

## 15. Backend design review gate

Before implementation, reviewers must confirm:
- every module invariant has test intent;
- every state transition has positive/negative cases;
- every high-risk command has authority tests;
- every async flow has retry/idempotency test;
- backup has restore test;
- graph impact has cycle/limit tests;
- security threat register has corresponding verification plan.

## 16. `BACKEND_DESIGN_READY`

Allowed outcomes:
- `NOT_READY`;
- `READY_WITH_EXPLICIT_UNKNOWNS`;
- `READY_FOR_IMPLEMENTATION_PLANNING`.

No code authorization is implied until overall `PRE_CODE_EVIDENCE_GATE` is also satisfied.
