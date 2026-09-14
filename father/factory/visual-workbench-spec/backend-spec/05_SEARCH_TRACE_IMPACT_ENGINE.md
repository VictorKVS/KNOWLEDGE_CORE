# Search, Trace & Impact Engine

Status: `DRAFT_V0.1`

## 1. Purpose

Provide deterministic navigation through engineering evidence and dependencies. The engine must answer not only “where is object X?” but also “why does it exist?”, “what does it affect?”, “what must be retested?”, and “which gates are now suspect?”.

## 2. Separation of concerns

- **Search** finds objects/sources by text and structured attributes.
- **Trace** traverses explicit typed relations.
- **Impact** evaluates consequences of a proposed or committed change.
- **Semantic suggestion** may later propose missing links but is not canonical until reviewed.

## 3. Search model

Search dimensions:
- text/name/ID;
- object type;
- source class;
- project/baseline;
- stage/station;
- status;
- owner/reviewer;
- classification;
- tag;
- changed-since;
- evidence coverage;
- test coverage;
- conflict/UNKNOWN/stale flags;
- relation presence/absence.

## 4. Search ranking baseline

Start simple:
1. exact ID;
2. exact normalized name/term;
3. prefix/token match;
4. FTS rank;
5. trigram fallback.

Do not introduce embeddings until measured discovery/eval demonstrates benefit.

## 5. Trace operations

### Upstream trace
Examples:
- Requirement → source/evidence/business need;
- ADR → drivers/NFR/requirements/PoC evidence;
- Test → requirement/control/oracle;
- Risk acceptance → risk/evidence/owner.

### Downstream trace
Examples:
- Requirement → ADR/component/test;
- Threat → security requirement/control/test;
- Source → claims/requirements/decisions depending on it;
- Component → deployment/monitoring/SLO/tests.

### Path query
Return explicit path between two objects if one exists under relation filters.

## 6. Traversal algorithm

Baseline algorithm: bounded BFS for shortest semantic path; DFS optional for enumerating all paths within a bounded depth.

Every traversal has:
- project/baseline scope;
- allowed relation types;
- direction;
- max depth;
- max nodes/edges;
- visited set;
- timeout/budget;
- cycle detection.

## 7. Trace result

Each edge in result includes:
- relation type;
- exact source/target revisions in selected baseline when applicable;
- rationale/evidence status;
- current/stale/superseded state;
- authority context if relation derives from decision.

## 8. Coverage queries

First-class deterministic reports:
- Requirements without evidence;
- Requirements without acceptance criteria;
- Requirements without tests;
- Security requirements without controls;
- Controls without tests;
- Threat scenarios without treatment/risk disposition;
- ADRs without driver/evidence trace;
- Components without requirements;
- SLOs without monitoring signal;
- Risks without owner;
- Gate decisions with stale evidence;
- Verified objects with unresolved conflict/UNKNOWN policy violation.

## 9. Impact preview

`ImpactPreview(change_candidate, baseline)` returns:
- directly affected objects;
- transitively affected objects;
- relation path explaining each impact;
- stale candidates;
- tests to rerun;
- reviews to reopen;
- gates to reevaluate;
- suggested station rework targets;
- uncertainty/semantic-review candidates.

Preview never mutates state.

## 10. Impact rule registry

Deterministic rules keyed by source object type + relation type + change category.

Example:

```yaml
source_type: REQUIREMENT
relation: VERIFIED_BY
change: MATERIAL_SEMANTIC_CHANGE
action:
  - MARK_TEST_ORACLE_REVIEW_REQUIRED
  - RERUN_TEST_REQUIRED
```

Another:

```yaml
source_type: SOURCE_VERSION
relation: SUPPORTS
change: SOURCE_SUPERSEDED
action:
  - MARK_DEPENDENT_EVIDENCE_STALE_CANDIDATE
  - REEVALUATE_GATES_USING_EVIDENCE
```

## 11. Change categories

At minimum:
- cosmetic/non-semantic;
- metadata-only;
- semantic field change;
- threshold/NFR change;
- evidence/source version change;
- relation added/removed;
- authority/owner change;
- security classification change;
- component/interface contract change;
- deployment topology change.

Impact is based on category, not merely any edit.

## 12. Stale propagation

Stale propagation is a queue of deterministic impact facts, not recursive destructive mutation.

Each propagation record stores:
- trigger change;
- rule ID;
- affected object;
- path;
- action;
- timestamp;
- resolution state.

This allows explanation: “TEST-18 became review-required because REQ-14 threshold changed through relation VERIFIED_BY.”

## 13. Rework target selection

Use paper-pipeline stage/station ownership and dependency graph.

Algorithm:
1. collect affected canonical objects;
2. map each to owning station(s);
3. find earliest materially affected station(s);
4. remove stations whose outputs are fully covered by later isolated change when policy allows;
5. present minimal rework set and rationale;
6. human/project policy may widen scope.

No automatic “restart project from A0” unless evidence supports it.

## 14. Compare baselines

Compare returns:
- added/removed logical objects;
- changed revisions;
- added/removed/changed relations;
- changed gate decisions;
- changed risk acceptances;
- changed source/evidence dependencies;
- resulting trace coverage delta.

## 15. UI projection support

Backend returns graph fragment optimized for canvas:
- canonical IDs;
- display summary;
- relation semantics;
- node status;
- blocker flags;
- optional layout hints;
- continuation token for large graph expansion.

Backend does not return an uncontrolled whole-project graph by default.

## 16. Explainability requirement

Every impact/stale/rework recommendation must provide machine-readable reason path.

Bad:
`Object became stale because system decided so.`

Required:
`SRC-22 v3 SUPERSEDED → EV-91 SUPPORTS → REQ-14 → ADR-03 → TEST-18; rules IR-07/IR-11 triggered.`

## 17. Future semantic/LLM assistance

Possible future layer:
- suggest unmodeled dependencies;
- compare semantic meaning across revisions;
- classify likely change category;
- propose missing tests.

All such results are `CANDIDATE` and must be distinguished from deterministic graph results.

## 18. Performance design

Before graph DB or distributed search:
- benchmark representative project sizes;
- instrument traversal latency/node counts;
- maintain adjacency indexes;
- cache only rebuildable read projections;
- bound user queries.

Escalation technology decision requires benchmark + ADR.
