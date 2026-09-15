# FATHER Visual Engineering Workbench — Security, Authority & Audit Specification

Status: `DRAFT_V0.1`

## 1. Security objective

Workbench is a high-value engineering system because it stores:

- source evidence;
- requirements;
- architecture decisions;
- threat models;
- security controls;
- test evidence;
- release/operations information;
- authority decisions;
- potentially sensitive project documents.

Therefore its security model must protect not only confidentiality, but also **integrity of engineering reasoning and authority**.

Primary security goals:

```text
Confidentiality
Integrity
Availability
Traceability
Authority integrity
Evidence integrity
Version integrity
```

---

# 2. Threats specific to Workbench

Minimum threat classes:

1. unauthorized read of sensitive project/evidence;
2. unauthorized engineering edit;
3. forged approval/gate decision;
4. deletion/silent rewrite of history;
5. evidence substitution;
6. source version spoofing;
7. relation/trace graph poisoning;
8. privilege escalation;
9. confused-deputy via integrations;
10. malicious file upload;
11. supply-chain compromise;
12. session/token theft;
13. CSRF/XSS/injection;
14. import/export leakage;
15. audit tampering;
16. AI prompt/retrieval injection;
17. sensitive data routed to unapproved AI provider;
18. AI-generated fabricated evidence;
19. denial of service through huge graph/import;
20. malicious plugin/integration.

Threat model must be refined during implementation.

---

# 3. Identity

## SEC-ID-001 Enterprise identity

Reference: OIDC/OAuth2-compatible identity provider.

## SEC-ID-002 Local fallback

Local auth for development may exist but is not assumed Production configuration.

## SEC-ID-003 Actor types

- HUMAN;
- SERVICE;
- IMPORTER;
- CI_INTEGRATION;
- AI_ASSISTANT;
- SYSTEM.

Actor type included in audit.

---

# 4. Authorization model

Use combined RBAC + scoped authority assignment.

Generic role grants capability class, but authority requires project/scope assignment.

Examples:

```text
Role: SECURITY_ENGINEER
can draft security requirements
can review security architecture
cannot accept residual risk unless also explicit RISK_OWNER assignment
```

```text
Role: SOLUTION_ARCHITECT
can draft ADR/target architecture
cannot final-approve material architecture decision alone
```

## SEC-AUTH-001 Object-level checks

All reads/writes include project/object scope authorization.

## SEC-AUTH-002 Field-level restrictions

Certain sensitive fields may require additional permission/classification.

## SEC-AUTH-003 Authority action separate

Approve/accept-risk/promote-baseline/release are dedicated server commands.

## SEC-AUTH-004 Temporal authority

Assignments may have effective_from/effective_to.

## SEC-AUTH-005 Delegation

Delegation explicit, time-bounded, audited; no implicit substitution.

---

# 5. Sensitive data model

Data classification minimum:

- PUBLIC;
- INTERNAL;
- CONFIDENTIAL;
- RESTRICTED;
- project-specific extensions.

Classification attaches to Source/Object and propagates to derived data per policy.

## SEC-DATA-001 No silent declassification

Derived artifact cannot automatically receive lower classification.

## SEC-DATA-002 Export control

Export permission evaluated against included highest classification and user permission.

## SEC-DATA-003 AI routing

Provider eligibility determined by frozen input effective classification.

---

# 6. Source/evidence integrity

## SEC-EVID-001 Original hash

Uploaded/material source versions store cryptographic hash where applicable.

## SEC-EVID-002 Immutable source version

Existing source version content cannot be silently replaced; replacement creates new version.

## SEC-EVID-003 Locator binding

Evidence locator bound to exact source version.

## SEC-EVID-004 Evidence change impact

Invalidated/superseded source causes dependent evidence review/stale propagation.

## SEC-EVID-005 No fabricated source by AI

AI-proposed refs validated against source registry before acceptance.

---

# 7. File upload security

Pipeline:

```text
upload
→ size/type policy
→ malware scan where available
→ content-type validation
→ safe storage name
→ hash
→ metadata extraction
→ quarantine/reject or admit
```

Never trust filename extension alone.

Preview rendering must use isolated/safe processing boundary for risky formats.

---

# 8. Web security baseline

Mandatory review against OWASP classes:

- injection;
- broken access control;
- XSS;
- CSRF where applicable;
- SSRF in import/url fetch;
- insecure file handling;
- security misconfiguration;
- auth/session issues;
- software supply chain;
- logging/audit gaps.

Reference secure headers, CSP, same-site cookie policy if cookies, secure transport.

---

# 9. API security

- schema validation;
- size limits;
- rate limits for expensive endpoints;
- path traversal prevention;
- URL allow/deny policy for remote acquisition;
- object-level auth on every resource;
- idempotency abuse protection;
- no secret values in API responses/logs;
- redaction of sensitive errors.

---

# 10. Audit integrity

Audit includes all material actions:

- login/security events as appropriate;
- source registration/versioning;
- material object revision;
- relation change;
- review completion;
- approval/gate decision;
- risk acceptance;
- baseline promotion;
- import/export sensitive;
- release approval;
- AI run/AI provider routing;
- admin/permission change.

## SEC-AUD-001 Append-only semantics

Application must not provide normal UI to edit past audit event.

## SEC-AUD-002 Correlation

Audit events include request/change/AI run correlation.

## SEC-AUD-003 Access

Audit read access separated from general project edit permission.

## SEC-AUD-004 Retention

Retention policy deployment-specific and governed.

---

# 11. Version integrity

Verified/baselined revisions are immutable.

Any correction creates new revision with relation to prior.

History view must distinguish:

- edit before baseline;
- superseding revision;
- rejected revision;
- rollback to previous content via new revision.

---

# 12. Approval integrity

Final authority decision record includes:

- exact target revision/baseline;
- gate evaluation revision;
- authority assignment;
- actor;
- rationale;
- evidence snapshot;
- timestamp;
- conditions/expiry if any.

Approval cannot float over “latest” object; it must reference exact revision.

---

# 13. Risk acceptance

Risk acceptance must include:

- risk revision;
- residual description;
- impact/likelihood basis where used;
- owner;
- rationale;
- validity/expiry/review date;
- compensating controls/conditions;
- evidence.

System warns on expired acceptance.

---

# 14. Separation of duties

Material rules:

- producer != independent reviewer where policy requires;
- architecture author cannot be sole final architecture approver;
- security engineer cannot accept residual risk by default;
- developer cannot self-approve all code review/security exceptions;
- AI cannot be human authority.

System must support organization-specific SoD policies.

---

# 15. Future AI security boundary

AI Assistance is disabled by default until activation gate.

When enabled:

## SEC-AI-001 Frozen inputs

AI receives immutable input references/snapshot.

## SEC-AI-002 Untrusted content

Retrieved/source content treated as data, never system/tool instruction.

## SEC-AI-003 Tool least privilege

Role-agent gets minimum explicit tools.

## SEC-AI-004 No autonomous authority

Models cannot approve legal applicability, residual risk, scope, release.

## SEC-AI-005 Provider policy

Data classification checked before external provider call.

## SEC-AI-006 Evidence validation

Claimed evidence refs resolved deterministically.

## SEC-AI-007 Prompt/version audit

Model/provider/version/prompt/tool policy recorded.

## SEC-AI-008 Cross-agent isolation

Delegation cannot expand privileges.

---

# 16. AI adversarial test suite

Mandatory before production AI role promotion:

- direct prompt injection;
- indirect/retrieval injection;
- malicious source says “ignore policy”;
- fabricated citation/ref;
- source locator mismatch;
- request to exceed authority;
- request to reveal restricted evidence;
- poisoned KB item;
- conflicting sources;
- unsupported consensus pressure;
- tool misuse;
- cross-agent privilege escalation;
- hidden scope expansion;
- refusal/fail-closed correctness.

---

# 17. Integration security

Each external connector has:

- identity/credential model;
- least-privilege scope;
- data directions;
- classification allowed;
- timeout/retry;
- audit;
- revocation;
- failure semantics.

No connector inherits application admin authority.

---

# 18. Secrets

- never store plaintext secret in canonical artifacts;
- UI displays secret references, not values;
- Production secrets use approved secret store;
- logs redact tokens/passwords/keys;
- connector credentials scoped/rotatable;
- secret access auditable where platform supports.

---

# 19. Client-side security

Frontend must assume all server-derived rich content untrusted for rendering.

Markdown/rendered descriptions sanitized.

No eval/injection of imported scripts.

External links visibly identified; dangerous schemes blocked.

---

# 20. Import security

Import is candidate data.

Protect against:

- YAML/JSON parser bombs;
- XML entity issues if XML used;
- zip bombs;
- formula injection in CSV/XLSX exports/imports;
- path traversal;
- malicious BPMN/SVG/HTML payload;
- huge graph resource exhaustion.

Importer has quotas/timeouts.

---

# 21. Export security

Export package:

- checks user permission;
- marks classification;
- optionally watermarks/report metadata by policy;
- avoids including hidden restricted source bytes unless explicitly selected/authorized;
- produces manifest.

---

# 22. Availability / abuse resistance

Controls:

- request limits;
- import size limits;
- graph traversal depth/result caps;
- expensive impact query cancellation/timeouts;
- background job quotas;
- circuit breakers for external services;
- safe degradation to read-only where possible.

---

# 23. Supply chain

Implementation requires:

- dependency lock;
- SBOM;
- SCA;
- SAST;
- secret scanning;
- signed/provenance build strategy where environment supports;
- review of major UI libraries/plugins;
- vulnerability remediation process.

---

# 24. Security test plan for Workbench

Before Production:

1. authorization unit/policy tests;
2. object-level access integration tests;
3. approval/risk authority negative tests;
4. IDOR tests;
5. XSS/markdown rendering tests;
6. CSRF tests if relevant;
7. file upload abuse tests;
8. SSRF tests;
9. injection tests;
10. concurrency/baseline race tests;
11. audit integrity tests;
12. source hash/version tamper tests;
13. export classification tests;
14. backup/restore access tests;
15. DAST;
16. manual/pentest on release candidates;
17. AI red-team only when AI feature enabled.

---

# 25. Security acceptance blockers

Production blocked if:

- authority action can be executed without correct assignment;
- verified/baselined history can be silently overwritten;
- source evidence version can be replaced in place;
- restricted data can be exported by unauthorized user;
- AI external provider can receive disallowed data;
- audit silently fails while material write succeeds without configured fail-safe policy;
- critical/high unresolved vulnerability exceeds approved risk policy;
- backup restore not demonstrated for required deployment class;
- security tests for material controls missing.

---

# 26. Security perspective in UI

Security perspective must visually distinguish:

- asset/protected interest;
- boundary/entry point;
- threat scenario;
- requirement;
- control;
- test;
- evidence;
- risk acceptance.

Clicking any element allows backward/forward trace.

The perspective must never imply “green = secure”; status reflects known evidence, not absence of unknown threats.