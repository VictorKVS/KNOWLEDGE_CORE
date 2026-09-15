# Backend State Machine & Transaction Model

Status: `DRAFT_V0.1`

## 1. Principle

Material state is changed only by explicit commands. Status fields are not free-form editable attributes.

## 2. Canonical artifact lifecycle

```text
EXPECTED
→ REQUESTED
→ RECEIVED
→ PARTIAL / CONFLICTED / GAP
→ DRAFT
→ OWNER_REVIEW
→ CONFIRMED
→ VERIFIED
→ STALE
→ DRAFT/OWNER_REVIEW ...

terminal/side states:
REJECTED
NOT_APPLICABLE
SUPERSEDED
RETIRED
```

### Transition rules

- `EXPECTED → REQUESTED`: accountable owner/source request exists.
- `REQUESTED → RECEIVED`: material/source arrived; no truth claim implied.
- `RECEIVED → PARTIAL/CONFLICTED/GAP`: structural analysis result.
- `PARTIAL/GAP → DRAFT`: missing fields completed only with explicit source/owner assumptions.
- `DRAFT → OWNER_REVIEW`: schema complete enough for authoritative review.
- `OWNER_REVIEW → CONFIRMED`: owner accepts project meaning.
- `CONFIRMED → VERIFIED`: required independent/domain/gate checks pass.
- any material upstream invalidation may cause `VERIFIED/CONFIRMED → STALE`.
- `STALE` never silently returns to VERIFIED.

## 3. Source lifecycle

```text
REGISTERED
→ BYTES_PENDING / EXTERNAL_REFERENCE
→ BYTES_VERIFIED
→ PARSED
→ MAPPED
→ EFFECTIVE
→ SUPERSEDED / RETIRED
```

Quarantine branch:

```text
BYTES_RECEIVED → QUARANTINED → REJECTED or RELEASED
```

## 4. Evidence lifecycle

```text
CANDIDATE
→ RESOLVABLE
→ SUPPORT_CHECK_PENDING
→ VERIFIED_SUPPORT / VERIFIED_CONFLICT / INSUFFICIENT
→ STALE / RETIRED
```

Evidence verification never means the associated decision is automatically correct.

## 5. Review task lifecycle

```text
OPEN
→ ASSIGNED
→ IN_REVIEW
→ FINDINGS_OPEN
→ WAITING_REWORK
→ RECHECK
→ COMPLETED
```

Side states:
- CANCELLED
- SUPERSEDED
- BLOCKED_AUTHORITY

Material review completion requires explicit reviewer outcome and unresolved finding summary.

## 6. Gate lifecycle

```text
NOT_EVALUATED
→ EVALUATING
→ NOT_READY / READY_WITH_CONDITIONS / READY
→ DECISION_PENDING
→ PASSED / PASSED_WITH_CONDITIONS / BLOCKED / REJECTED / DEFERRED
```

`READY` is deterministic/advisory readiness. `PASSED` is an authorized decision.

## 7. Risk lifecycle

```text
IDENTIFIED
→ ANALYZED
→ TREATMENT_PLANNED
→ CONTROL_IMPLEMENTED
→ VERIFIED_RESIDUAL
→ ACCEPTANCE_REQUIRED
→ ACCEPTED / NOT_ACCEPTED
→ MONITORED
→ CLOSED / REOPENED
```

Risk acceptance record contains:
- risk scope;
- residual assessment;
- owner;
- rationale;
- expiry/review date;
- triggers;
- evidence snapshot.

## 8. Baseline lifecycle

```text
WORKING_STATE
→ CANDIDATE_SNAPSHOT
→ READINESS_CHECK
→ APPROVAL_PENDING
→ PROMOTED
→ SUPERSEDED
→ ARCHIVED
```

A promoted baseline is immutable.

## 9. Change request lifecycle

```text
DRAFT
→ SUBMITTED
→ IMPACT_ANALYZED
→ REVIEW_PENDING
→ APPROVED / REJECTED / DEFERRED
→ APPLYING
→ APPLIED
→ VERIFIED
→ CLOSED
```

Failure during apply:
`APPLYING → FAILED → ROLLBACK/REWORK`.

## 10. Import job lifecycle

```text
CREATED
→ SOURCE_VALIDATION
→ PARSING
→ MAPPING
→ VALIDATION
→ REVIEW_REQUIRED / READY_TO_COMMIT
→ COMMITTED
```

Side states:
- FAILED_RETRYABLE
- FAILED_FINAL
- CANCELLED
- QUARANTINED

## 11. Background job lifecycle

```text
QUEUED
→ CLAIMED
→ RUNNING
→ SUCCEEDED
```

Failure:
```text
RUNNING
→ RETRY_WAIT
→ QUEUED
...
→ DEAD_LETTER
```

Every job stores idempotency key, attempt count, correlation ID and input snapshot.

## 12. Transaction boundaries

### TX-01 Canonical command
A single canonical mutation command commits all directly coupled invariant changes atomically.

Example `ConfirmRequirement` transaction:
- validate expected revision;
- validate owner authority;
- create new requirement revision;
- update logical current pointer;
- write relation/evidence deltas required atomically;
- write audit event;
- write outbox records;
- commit.

### TX-02 No external I/O inside transaction
Do not call external provider, file parser, model, email, webhook or long-running computation while DB transaction open.

### TX-03 Outbox after canonical commit
After commit, async effects consume outbox events.

### TX-04 Idempotent retry
Retryable commands carry idempotency keys scoped to actor/project/operation.

### TX-05 Optimistic concurrency
Expected revision mismatch returns conflict and does not merge automatically.

## 13. Concurrency model

Default:
- optimistic concurrency per logical object;
- short transactions;
- no distributed lock baseline;
- review/gate assignment may use row-level lock only for short claim/transition operations.

## 14. Conflict resolution

Editing conflict must surface:
- user's base revision;
- current revision;
- field-level diff;
- relation/evidence changes;
- options: reload, reapply manually, create explicit merge candidate.

Backend must not silently last-write-wins material engineering data.

## 15. Stale propagation

Upstream change creates deterministic `ImpactCandidate` set using typed relations and rules.

Policy actions per relation may be:
- NO_EFFECT;
- REVIEW_REQUIRED;
- MARK_STALE;
- INVALIDATE_GATE_READINESS;
- RERUN_TEST_REQUIRED;
- OWNER_RECONFIRMATION_REQUIRED.

Propagation is bounded, cycle-safe and recorded as evidence of why an object became stale.

## 16. Rework semantics

A failed test/review/gate does not mutate upstream evidence automatically. It creates findings/change requests and may reopen the smallest affected stage/station according to the paper pipeline rework model.
