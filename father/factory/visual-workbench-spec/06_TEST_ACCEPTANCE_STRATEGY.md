# FATHER Visual Engineering Workbench — Test & Acceptance Strategy

Status: `DRAFT_V0.1 / TEST DESIGN BEFORE IMPLEMENTATION`

## 1. Goal

Testing must prove that Workbench preserves engineering truth, authority, traceability and usability under change.

A passing UI screenshot is insufficient. The system is accepted only when canonical model invariants and end-to-end engineering scenarios are proven.

Core chain:

```text
TZ requirement
→ observable acceptance condition
→ test oracle
→ automated/manual test
→ implementation
→ run evidence
```

---

# 2. Test layers

1. schema/contract tests;
2. pure domain unit tests;
3. property/invariant tests;
4. persistence tests;
5. API integration tests;
6. authorization/security tests;
7. frontend component tests;
8. canvas interaction tests;
9. import/export round-trip tests;
10. E2E user journey tests;
11. performance/scale tests;
12. resilience/recovery tests;
13. migration/upgrade tests;
14. accessibility tests;
15. manual expert UX review;
16. future AI eval/security tests.

---

# 3. Domain invariant tests

Mandatory invariants:

## T-DOM-001 Stable logical ID

Rename object; ID remains same.

## T-DOM-002 Immutable revision

Verified revision cannot mutate in place.

## T-DOM-003 Baseline exactness

Baseline reconstruction returns exact referenced revisions.

## T-DOM-004 Evidence locator version binding

Evidence cannot silently jump to new source revision.

## T-DOM-005 Authority validity

Approval invalid if actor lacks effective authority assignment.

## T-DOM-006 Relation type safety

Invalid endpoint relation rejected.

## T-DOM-007 Unknown preservation

UNKNOWN cannot become FACT through generic update/promotion.

## T-DOM-008 Conflict preservation

CONFLICTED state cannot be auto-cleared without resolution record.

## T-DOM-009 Stale propagation

Material upstream revision invalidates configured dependent evidence/objects.

## T-DOM-010 AI evidence rule

Model output cannot be registered as source evidence without external/source admission policy.

---

# 4. Property-based / generative tests

Recommended for graph/state logic.

Properties:

- graph traversal terminates under cycles/depth limits;
- baseline membership always references existing immutable revisions;
- no authority decision references expired/nonmatching assignment;
- status transition respects state machine;
- deleting layout never deletes semantic object;
- projection filters never create new semantic entities;
- import/export of supported structured object preserves stable IDs;
- impact preview is non-mutating;
- random invalid relation combinations rejected.

---

# 5. API contract tests

OpenAPI/schema contract tests must cover:

- request/response validation;
- auth requirement;
- 409 concurrency behavior;
- 403 vs 404 disclosure policy;
- pagination;
- idempotency;
- structured errors;
- version headers/ETag where selected;
- max payload limits.

---

# 6. Persistence tests

## T-DB-001 Transaction atomicity

Domain write and audit/outbox requirements behave according to policy.

## T-DB-002 Concurrent edit

Two clients edit same revision; second commit gets conflict, no silent overwrite.

## T-DB-003 Crash recovery

Partial transaction does not create orphan revision/relation.

## T-DB-004 Migration

Upgrade representative old dataset; invariants preserved.

## T-DB-005 Restore

Backup restore rebuilds exact baseline and source metadata.

---

# 7. Frontend component tests

- node displays status + icon + text;
- required port state;
- inspector tabs render correct data;
- forbidden action hidden/disabled but backend still protects;
- stale/conflict/blocker badges;
- diff rendering;
- source locator open;
- authority modal validation.

---

# 8. Canvas interaction tests

Automated browser tests:

## T-UI-001 Pan/zoom/select

Selection remains stable through pan/zoom.

## T-UI-002 Single click

Inspector opens without route/context loss.

## T-UI-003 Double click

Composite node drills down; breadcrumb appears.

## T-UI-004 Breadcrumb restore

Returning restores previous viewport/perspective/selection.

## T-UI-005 Edge inspect

Click edge opens relation detail.

## T-UI-006 Port validation

Invalid connection rejected with explanation.

## T-UI-007 Perspective switch

Selected logical object remains selected across views when present.

## T-UI-008 Minimap navigation

Viewport updates predictably.

## T-UI-009 Compare mode

Added/removed/changed objects correctly represented.

## T-UI-010 Flow playback

Scenario highlights correct ordered graph path without mutation.

---

# 9. E2E acceptance journeys

## E2E-01 New greenfield project

1. create project;
2. see Z0;
3. open S00;
4. add business request;
5. register source;
6. create Business Need draft;
7. assign owner;
8. see next station availability.

Oracle: project remains traceable and does not fabricate downstream artifacts.

## E2E-02 Brownfield mapping

1. create brownfield project;
2. import existing specification/API/repo metadata;
3. map existing evidence;
4. show partial coverage;
5. list gaps/conflicts;
6. avoid duplicate requirement creation.

## E2E-03 Requirement-to-test trace

1. open requirement;
2. trace source;
3. trace architecture decision/component;
4. trace test oracle/case;
5. open result evidence.

Oracle: every hop references exact objects/revisions.

## E2E-04 Security chain

Trace asset→threat→requirement→control→test→residual risk.

## E2E-05 Material change impact

1. propose source/requirement change;
2. preview impact;
3. confirm change;
4. dependent objects become stale per rules;
5. affected review tasks/gates visible.

## E2E-06 Architecture approval

Architect drafts ADR; independent reviewer reviews; final authority approves exact revision.

Negative oracle: architect alone cannot final approve if policy requires independence.

## E2E-07 Risk acceptance

Security records residual risk; non-risk-owner attempt rejected; Risk Owner accepts with expiry.

## E2E-08 Pre-code gate

Attempt to set CODE_ALLOWED with missing critical test oracle; gate blocks with exact unmet conditions.

## E2E-09 Test failure rework

Failed performance test → impact/rework routing → chosen upstream station reopened → affected downstream stale.

## E2E-10 Release

Release candidate references exact implementation/test baseline; production approval recorded; deployment evidence linked.

---

# 10. Security tests

Detailed list from Security spec plus:

- horizontal privilege escalation;
- vertical privilege escalation;
- authority forgery;
- revision race;
- evidence URL tampering;
- source file replacement;
- audit modification attempt;
- stored XSS in descriptions/comments/source preview metadata;
- malicious SVG/HTML preview;
- SSRF import;
- zip bomb;
- CSV formula injection export;
- excessive graph traversal DoS;
- oversized import;
- deep JSON/YAML nesting;
- unsafe redirect/link schemes.

---

# 11. Performance test profiles

Numbers are provisional design targets and must be baselined.

## PERF-P1 Typical project

- 5k canonical objects;
- 10k relations;
- 200–500 visible canvas elements;
- several hundred sources.

Measure:

- initial graph load;
- pan/zoom interaction;
- inspector open;
- search;
- trace depth 3–5;
- perspective switch.

## PERF-P2 Large project

- 50k canonical objects;
- 150k relations;
- filtered view with 500–1000 visible elements;
- 10k sources/evidence links.

Goal: system remains usable through filtering/virtualization; whole graph need not render simultaneously.

## PERF-P3 Impact analysis

Representative change with thousands of downstream edges.

Measure computation time and cancellation behavior.

## PERF-P4 Import

Large structured import + PDF/source batch; measure throughput and memory.

---

# 12. Canvas performance oracle

Do not define success only by FPS benchmark.

Measure:

- interaction input latency;
- frame drops during pan/zoom;
- selection response;
- layout computation;
- memory growth;
- render time when switching perspective.

Test on agreed browser/hardware profiles.

---

# 13. Search tests

- exact ID;
- prefix;
- free text;
- typo/fuzzy where implemented;
- filters;
- authorization filtering;
- restricted object must not leak through result snippets/count where policy forbids.

---

# 14. Import/export tests

Round-trip fixtures:

- YAML project subset;
- JSON;
- OpenAPI;
- CSV matrix;
- Structurizr adapter;
- source files metadata.

Verify:

- IDs preserved;
- relations preserved;
- classification preserved;
- unsupported fields reported;
- no silent drop;
- export manifest accurate.

---

# 15. Version/diff tests

Cases:

- field changed;
- relation added/removed;
- source evidence changed;
- owner changed;
- status changed;
- supersession;
- revert via new revision;
- compare baselines.

Semantic diff must not report layout move as engineering change.

---

# 16. Stale propagation tests

Fixtures include:

- requirement statement material change;
- source superseded;
- API contract change;
- test oracle change;
- data classification increase;
- owner-only metadata change.

Policy must distinguish material vs non-material changes.

---

# 17. Gate evaluator tests

For each gate:

- all evidence present → eligible;
- one required condition missing → block;
- conditional pass policy;
- wrong authority → reject decision;
- stale evidence → block/warn according to rule;
- expired risk acceptance → block/warn.

---

# 18. Accessibility tests

- automated axe-like checks;
- keyboard navigation;
- focus order;
- screen-reader labels for major controls;
- status not color-only;
- contrast;
- zoom/text scaling;
- reduced motion.

Canvas has alternative object list/tree for nonvisual access.

---

# 19. Browser compatibility

Initial support target to define at implementation kickoff, likely latest stable Chromium + Firefox + Edge enterprise variants.

Safari support decision based on deployment audience.

Compatibility matrix must be explicit before release.

---

# 20. Resilience tests

- DB temporarily unavailable;
- object storage unavailable;
- external connector timeout;
- search cache unavailable;
- AI provider unavailable (future);
- browser reload during draft;
- network loss during save;
- server restart during background import.

System must not corrupt canonical model.

---

# 21. Recovery tests

- restore DB + object storage;
- rebuild search index/cache;
- reconstruct baseline;
- resume/reconcile import job;
- verify audit continuity.

---

# 22. Migration tests

Every migration tested against:

- empty DB;
- small fixture;
- representative old release fixture;
- large fixture when schema materially changes.

Migration result validated by invariant suite.

---

# 23. UI visual regression

Use screenshots only for layout/design regression, not semantic correctness.

Cover:

- main canvas;
- dark/light if enabled;
- inspector tabs;
- modal authority forms;
- blocked/stale/conflict states;
- large graph density.

---

# 24. Manual expert review

At each major UX gate, real engineering walkthrough with roles:

- BA;
- System Engineer;
- Security Engineer;
- Architect;
- QA;
- Project/Product owner.

Each role must perform at least one realistic scenario and record friction/ambiguity.

---

# 25. Future AI testing

No AI feature accepted without:

- frozen eval dataset/version;
- baseline non-AI method;
- task-specific metrics;
- unsupported claim scan;
- evidence coverage;
- security/adversarial pack;
- human review agreement/rework metrics;
- data routing tests;
- fail-closed tests.

Model change triggers regression/recertification.

---

# 26. Test data strategy

Maintain synthetic/reference projects:

1. `GREENFIELD_MINI` — small complete path;
2. `BROWNFIELD_CONFLICTED` — duplicate/conflict/stale sources;
3. `SECURITY_CRITICAL` — threat/risk/authority cases;
4. `LARGE_GRAPH` — scale/performance;
5. `AI_ENABLED_FIXTURE` — future adversarial eval;
6. `MIGRATION_VN` — historical schemas.

No production secrets/PII in test fixtures.

---

# 27. CI stages

Reference:

```text
lint/schema
→ unit/invariants
→ API/persistence
→ security policy tests
→ frontend/component
→ E2E smoke
→ import/export fixtures
→ build
```

Full performance/security/manual suites can run separately/on release gate.

---

# 28. Release quality gate

Release candidate blocked if:

- invariant suite failing;
- critical E2E failing;
- authority/security negative tests failing;
- migration not tested when schema changes;
- unresolved critical/high vulnerability beyond policy;
- backup/restore required but unverified;
- major UI path inaccessible;
- acceptance evidence missing for material new feature.

---

# 29. Acceptance evidence package

Each Workbench release should produce:

- requirement coverage report;
- automated test summary;
- security scan summary;
- E2E report;
- known defects/limitations;
- migration evidence;
- performance benchmark where affected;
- security review where affected;
- release decision record.

---

# 30. Definition of a useful test

A test is useful if failure gives actionable information about violated requirement/invariant/risk.

Avoid tests that merely duplicate implementation details without protecting contract.

For every material test ask:

```text
What requirement/risk does this prove?
What is the oracle?
What defect would this catch?
Will refactoring preserve the test if behavior remains correct?
```

This is the governing verification philosophy for Workbench.