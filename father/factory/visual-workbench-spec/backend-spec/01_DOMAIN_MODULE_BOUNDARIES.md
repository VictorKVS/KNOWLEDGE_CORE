# Backend Domain Module Boundaries

Status: `DRAFT_V0.1`

## 1. Purpose

Define ownership and interaction boundaries so implementation does not devolve into shared tables and cross-module hidden coupling.

## 2. Boundary rule

A module owns its aggregate state and invariants. Other modules interact through explicit application commands/queries or domain services, not direct persistence access.

## 3. Project & Baseline module

### Aggregates
- Project
- Baseline
- StageState
- StationState

### Commands
- CreateProject
- RenameProject
- SetProjectMode
- CreateBaselineCandidate
- EvaluateBaselineReadiness
- PromoteBaseline
- SupersedeBaseline

### Queries
- GetProject
- ListBaselines
- GetCurrentBaseline
- GetStageStates
- GetStationStates

### Invariants
- baseline immutable after creation;
- promoted baseline references exact object/relation revisions;
- project mode change may require review when it changes lifecycle semantics.

## 4. Object Graph module

### Aggregates
- CanonicalObject
- Relation
- RelationTypeDefinition
- ViewProjection metadata

### Commands
- CreateObjectDraft
- ReviseObject
- RetireObject
- SupersedeObject
- CreateRelation
- ReviseRelation
- RetireRelation

### Queries
- GetObject
- GetRevision
- GetObjectHistory
- ListInboundRelations
- ListOutboundRelations

### Invariants
- stable object ID across revisions;
- relation endpoints must satisfy type registry;
- no relation to non-existent logical object;
- material relation revisions are preserved.

## 5. Source & Evidence module

### Aggregates
- Source
- SourceVersion
- SourceLocator
- EvidenceItem
- EvidenceLink

### Commands
- RegisterSource
- RegisterSourceVersion
- AttachSourceBytes
- MarkSourceSuperseded
- CreateLocator
- CreateEvidenceItem
- LinkEvidence
- VerifyEvidenceLocator
- RetireEvidence

### Invariants
- original bytes content hash immutable;
- source version cannot silently change content;
- evidence link must identify source version/locator or explicit owner evidence;
- evidence verification state independent from claim confidence.

## 6. Product & Requirements module

### Aggregates
- BusinessNeed
- ProductVision
- Stakeholder
- ScopeItem
- Requirement
- NFRScenario
- AcceptanceCriterion
- RequirementBaseline

### Commands
- CreateBusinessNeed
- ConfirmProductVision
- AddScopeItem
- CreateRequirementDraft
- ConfirmRequirement
- SupersedeRequirement
- DefineNFRScenario
- DefineAcceptanceCriterion
- CreateRequirementBaseline

### Invariants
- requirement has owner/source/evidence or explicit owner decision;
- mandatory requirement cannot become VERIFIED only through LLM output;
- NFR must have measurable scenario/oracle where applicable;
- acceptance criterion must point to requirement/product intent.

## 7. System Model module

### Aggregates
- System
- SystemBoundary
- Actor
- Function
- DataFlow
- Interface
- ExternalDependency
- OperationalMode

### Commands
- DefineSystemBoundary
- AddActor
- AddFunction
- AddDataFlow
- AddInterface
- RegisterDependency
- DefineOperationalMode

### Invariants
- each function belongs to a system scope;
- data flow endpoints resolvable;
- external interface/dependency must be classified for trust/security review.

## 8. Security & Risk module

### Aggregates
- ProtectedInterest
- Asset
- NegativeConsequence
- ThreatSource
- TrustBoundary
- EntryPoint
- ThreatScenario
- SecurityRequirement
- SecurityControl
- Risk
- RiskAcceptance

### Commands
- RegisterAsset
- RegisterConsequence
- DefineThreatScenario
- DefineSecurityRequirement
- DefineControl
- LinkControlToThreat
- AssessRisk
- RequestRiskAcceptance
- AcceptResidualRisk
- ExpireRiskAcceptance

### Invariants
- risk acceptance requires named authorized risk owner;
- risk acceptance includes scope, rationale, expiry/revisit trigger;
- security control does not close risk by existence alone; evidence/test required according to policy;
- threat scenario retains trace to assets/consequences/boundaries.

## 9. Architecture & Decision module

### Aggregates
- ArchitectureDriver
- ArchitectureOption
- TradeoffRecord
- ADR
- Component
- APIContract
- EventContract
- DataModelObject
- DeploymentNode
- IAMRule
- SecretRule
- ObservabilitySignal
- SLO
- SizingAssumption

### Commands
- CreateDriver
- ProposeArchitectureOption
- RecordTradeoff
- CreateADRCandidate
- AcceptADR
- SupersedeADR
- DefineComponent
- DefineAPIContract
- DefineEventContract
- DefineDeploymentDesign

### Invariants
- accepted material ADR requires alternatives/rationale/consequences/revisit triggers;
- architect cannot self-approve where independent approval policy applies;
- component/interface changes preserve affected requirement/security trace.

## 10. Verification module

### Aggregates
- TestOracle
- TestCase
- TestSuite
- TestRun
- TestResult
- Defect
- Vulnerability
- VerificationReport
- ValidationReport

### Commands
- DefineTestOracle
- DefineTestCase
- CreateTestSuite
- RegisterTestRun
- RecordTestResult
- OpenDefect
- OpenVulnerability
- CloseDefectWithEvidence
- IssueVerificationReport
- IssueValidationReport

### Invariants
- test case references oracle and target requirement/control/assumption;
- result references exact implementation/config/baseline where applicable;
- defect closure needs evidence, not status toggle only.

## 11. Review / Gate / Authority module

### Aggregates
- ReviewTask
- ReviewFinding
- ApprovalDecision
- GateEvaluation
- GateDecision
- AssignmentSnapshot

### Commands
- CreateReviewTask
- SubmitFinding
- ResolveFinding
- SubmitReviewOutcome
- EvaluateGate
- DecideGate
- ApproveArtifact
- RejectArtifact

### Invariants
- reviewer assignment must comply with separation-of-duty policy;
- gate decision records evidence snapshot;
- missing required authority = hard failure;
- model output cannot impersonate human authority.

## 12. Version / Change / Audit module

### Aggregates
- ChangeRequest
- ChangeSet
- AuditEvent
- RevisionMetadata

### Commands
- CreateChangeRequest
- AttachChangeSet
- PreviewChangeImpact
- ApproveChange
- ApplyChange
- CloseChange

### Invariants
- audit append-only;
- change request impact known before material apply;
- revision chain cannot be rewritten silently.

## 13. Search / Trace / Impact module

Read-model module. It owns derived indexes/projections only.

### Queries
- SearchObjects
- SearchSources
- TraceUpstream
- TraceDownstream
- FindPath
- PreviewImpact
- FindMissingEvidence
- FindMissingTests
- FindConflicts
- FindStaleObjects

It cannot mutate canonical objects directly.

## 14. Import / Export module

### Aggregates
- ImportJob
- ImportMapping
- ImportFinding
- ExportPackage

### Commands
- StartImport
- MapImportObjects
- ValidateImport
- CommitMappedCandidates
- GenerateExport

### Invariants
- import never auto-verifies truth;
- export identifies exact baseline/schema/tool version;
- unknown/unmapped fields preserved in report.

## 15. Cross-module interaction

Synchronous domain/application calls are preferred inside the modular monolith.

Use domain/application events only when:
- side effect may happen after commit;
- multiple projections must update;
- integration/notification needed;
- processing may be retried independently.

Examples:
- RequirementRevised → enqueue impact projection refresh;
- BaselinePromoted → generate export snapshot + notify;
- SourceVersionRegistered → schedule parse/index task;
- GateDecided → audit + downstream station state recompute.

## 16. Forbidden coupling

- UI writing DB directly;
- module A importing repository/table of module B;
- generic `status` setter bypassing state machine;
- external integration writing canonical tables;
- AI worker writing VERIFIED/APPROVED without command policy;
- search projection treated as canonical record.
