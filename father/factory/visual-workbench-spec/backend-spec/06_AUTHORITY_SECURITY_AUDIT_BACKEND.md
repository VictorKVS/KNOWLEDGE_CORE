# Backend Authority, Security & Audit Model

Status: `DRAFT_V0.1`

## 1. Purpose

The Workbench stores and governs high-value engineering truth: requirements, security decisions, risk acceptances, gates and production readiness. Backend compromise or authority bypass can therefore corrupt the design process itself.

## 2. Security principles

- deny by default;
- least privilege;
- server-side authorization only;
- separation of duties for material decisions;
- classification-aware data handling;
- immutable/auditable material decisions;
- no secret material in client-visible payload unless required;
- no model/agent final authority;
- no trust in source content as executable instruction.

## 3. Identity types

- human user;
- team/group;
- service identity;
- connector identity;
- future AI worker identity;
- break-glass administrator.

Every action is attributed to one identity type and concrete subject.

## 4. Permission vs authority

Permission means ability to invoke command category.
Authority means domain mandate to make a particular decision.

Example:
- a security engineer may have permission to submit risk analysis;
- only assigned risk owner may have authority to `AcceptResidualRisk`.

Backend checks both.

## 5. RBAC baseline roles

Application permission roles may include:
- Viewer;
- Contributor;
- Reviewer;
- ProjectManager;
- SecurityEngineer;
- Architect;
- QAEngineer;
- ServiceOwner;
- RiskOwner;
- LegalCompliance;
- BaselineManager;
- Administrator.

Professional project roles from FATHER Role Matrix remain separate domain assignments.

## 6. ABAC/context conditions

Authorization may consider:
- project membership;
- object classification;
- source classification;
- stage/gate state;
- assignment validity period;
- organizational boundary;
- external-provider restrictions;
- conflict of interest/separation of duty;
- break-glass state.

## 7. Authority snapshots

Material decisions record authority snapshot at decision time:
- subject ID;
- project role;
- assignment ID/version;
- effective period;
- policy version;
- decision scope.

Later role change does not erase historical authority context.

## 8. Separation of duties

Configurable policy examples:
- material architecture producer cannot be sole final reviewer;
- risk analyst and risk accepter may be same person only if policy explicitly permits;
- gate producer cannot self-approve when independent review required;
- AI worker cannot satisfy human independence requirement.

## 9. High-risk commands

Dedicated authority checks for:
- PromoteBaseline;
- DecideGate;
- AcceptResidualRisk;
- ApproveRegulatoryApplicability;
- ApproveDataClassification;
- ApproveProductionReadiness;
- OverrideBlocker;
- ExportRestrictedData;
- BreakGlassAccess.

## 10. Break-glass

Break-glass is explicit exceptional workflow:
- strong reauthentication;
- reason required;
- time-bounded privilege;
- narrow scope;
- alert/notification;
- immutable audit;
- mandatory post-review.

## 11. Authentication assumptions

Initial backend should integrate with proven identity provider/OIDC rather than implement password identity system from scratch.

Required:
- secure token validation;
- audience/issuer checks;
- short-lived access where appropriate;
- session revocation strategy;
- MFA expectation delegated to IdP for privileged roles;
- no role trust from unsigned client claims.

## 12. API security

- object-level authorization for every resource;
- project scoping in query layer;
- rate limiting for expensive graph/search endpoints;
- bounded pagination/traversal;
- input validation;
- idempotency replay protection;
- CSRF protection for cookie-authenticated mutation flows;
- strict CORS policy;
- content security policy at web tier;
- anti-enumeration considerations for restricted projects.

## 13. Upload security

- streaming size limits;
- quarantine;
- MIME/content mismatch detection;
- filename not used as storage path;
- generated safe storage key;
- malware scanning hook;
- archive bomb/decompression limits;
- parser sandbox/isolation where possible;
- image/document metadata handling policy;
- restricted preview rendering.

## 14. SSRF and connectors

External URL/connector acquisition must:
- restrict protocols;
- resolve/validate host policy;
- block metadata/internal address ranges where applicable;
- enforce redirect limits;
- apply time/size limits;
- use connector allowlists/permissions;
- record acquisition provenance.

## 15. Data classification enforcement

Classification can restrict:
- who can view metadata/content;
- download/export;
- external connector/model routing;
- cache/log content;
- retention;
- backup handling.

Policy decision is server-side.

## 16. Secrets

- no API secrets in repository;
- secret manager/environment injection;
- never return secrets via generic object endpoints;
- redact logs;
- rotate/revoke process;
- connector credential references separated from canonical project data.

## 17. Audit security

Audit event is append-only and cannot be edited by ordinary application commands.

Required audit coverage:
- login/security events as appropriate;
- material object revision;
- relation changes;
- authority assignment changes;
- gate decisions;
- risk acceptances;
- baseline promotions;
- imports/exports;
- restricted downloads;
- break-glass;
- security policy changes.

## 18. Audit integrity

Initial controls:
- database permissions separating audit writer from ordinary mutation paths;
- sequence/time/correlation continuity checks;
- periodic export/backup.

Later stronger options if required:
- hash chaining;
- WORM/external immutable log;
- signed audit batches.

These require threat/risk justification.

## 19. AI worker security

Future AI service identity receives only scoped capabilities:
- read approved context;
- submit candidate output;
- create review candidate;
- never call human-only approval commands;
- never read restricted sources outside assigned data policy;
- every run has model/prompt/input/output refs and correlation ID.

## 20. Prompt/retrieval injection boundary

Source content is data. It cannot redefine backend policy, tools, credentials or authority.

Any model orchestration layer must separate:
- trusted system policy;
- authorized task;
- retrieved untrusted content;
- tool results.

## 21. Threat model categories

Backend threat model must include:
- broken object authorization;
- privilege escalation;
- stale authority assignment;
- forged approval;
- audit tampering;
- evidence tampering;
- source substitution;
- malicious file/parser exploit;
- SSRF;
- mass export/data exfiltration;
- SQL/injection classes;
- stored XSS in project content;
- denial via graph/search/import;
- revision race/lost update;
- connector compromise;
- backup exposure;
- AI prompt/evidence poisoning.

## 22. Security acceptance evidence

Before production readiness:
- threat model reviewed;
- authz unit/integration matrix tests;
- IDOR/BOLA negative tests;
- upload malicious cases;
- SSRF tests;
- audit mutation tests;
- revision/concurrency tests;
- secrets scan;
- SAST/SCA;
- DAST/API security tests;
- backup access controls;
- AI authority negative tests when AI enabled.
