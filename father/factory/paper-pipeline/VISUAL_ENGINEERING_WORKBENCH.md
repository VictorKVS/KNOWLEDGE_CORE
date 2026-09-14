# FATHER Visual Engineering Workbench — reference model

Status: `CANDIDATE / UI-DESIGN LAYER / NO RUNTIME AUTHORITY`

## 1. Purpose

FATHER should behave for a software/system designer the way CAD/BIM/visual-programming tools behave for an architect or engineer: the user sees a **model of the work**, not a folder of documents.

Core visual grammar:

```text
INPUT PORTS  →  ENGINEERING NODE / BLACK BOX  →  OUTPUT PORTS
                        ↓
                 expand internals
                        ↓
              subnodes / algorithms / evidence
```

The canvas is a projection over canonical FATHER artifacts, gates, methods and traceability. It is never a second source of truth.

## 2. Reference interaction patterns

### Dynamo / Grasshopper / LabVIEW pattern
Use for the core canvas:
- node = one bounded engineering transformation;
- typed input/output ports;
- left-to-right data flow;
- invalid/missing input visibly blocks node execution/readiness;
- status by node/port;
- downstream dependency freezing when an upstream artifact becomes invalid/stale;
- expandable composite nodes.

### KNIME pattern
Use for inspectability:
- traffic-light node state;
- execute/review one node, a segment, or full chain;
- components/metanodes collapse complexity;
- node settings are explicit;
- output inspection is first-class.

### Node-RED pattern
Use for workspace ergonomics:
- palette of reusable node types;
- central infinite canvas;
- side panels for info/properties/evidence;
- subflows/reusable templates;
- visible runtime/readiness status.

### Camunda/BPMN pattern
Use only for process-control views:
- human approval tasks;
- exclusive/parallel gates;
- waiting states;
- forms for authoritative input;
- escalation/rework paths.

Do NOT use BPMN as the canonical engineering information model; FATHER needs richer artifact/evidence/dependency semantics than process tokens alone.

### Structurizr/C4 pattern
Use for architecture views:
- one canonical system model;
- multiple views generated from the same model;
- Context / Container / Component / Dynamic / Deployment;
- filtered perspectives: Security, Data, Operations, Cost, Compliance;
- attach docs/ADRs to model elements.

## 3. Main UI layout

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Project / Stage / Gate / Search / View Perspective                         │
├──────────────┬───────────────────────────────────────┬──────────────────────┤
│ PALETTE      │              CANVAS                   │ INSPECTOR            │
│              │                                       │                      │
│ Sources      │ [Input]──▶[Engineering Node]──▶[Out] │ Selected node        │
│ Product      │                 │                     │ Inputs/Outputs       │
│ Analysis     │                 ▼                     │ Evidence             │
│ System       │          [subgraph / black box]      │ Algorithms           │
│ Security     │                                       │ Owner/Reviewers      │
│ Requirements │                                       │ Tests/Gate           │
│ Architecture │                                       │ Normative refs       │
│ Test         │                                       │ Book/science refs    │
│ Delivery     │                                       │ Versions/Diff        │
└──────────────┴───────────────────────────────────────┴──────────────────────┘
│ Timeline / Gate status / UNKNOWN / conflicts / blocked downstream / audit   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 4. Node contract

Every visual node must expose the same minimum anatomy:

- `nodeId`;
- `name`;
- `stage`;
- `purpose`;
- typed `inputPorts`;
- typed `outputPorts`;
- `ownerRole`;
- `reviewerRoles`;
- `methodRefs`;
- `normativeRefs`;
- `professionalRefs`;
- `algorithmRef`;
- `evidenceRefs`;
- `testRefs`;
- `gateImpact`;
- `status`;
- `unknowns`;
- `conflicts`;
- `version`;
- `downstreamConsumers`.

### Suggested status language

`MISSING` · `PARTIAL` · `CONFLICTED` · `READY` · `OWNER_REVIEW` · `VERIFIED` · `STALE` · `BLOCKED` · `NOT_APPLICABLE`

## 5. Port types

Ports are not generic wires. They carry typed engineering information.

Examples:

- `SOURCE_EVIDENCE`;
- `BUSINESS_FACT`;
- `OWNER_DECISION`;
- `REQUIREMENT`;
- `NFR`;
- `DATA_CLASSIFICATION`;
- `THREAT_SCENARIO`;
- `RISK`;
- `ARCHITECTURE_DRIVER`;
- `ARCHITECTURE_OPTION`;
- `DECISION`;
- `CONTRACT`;
- `TEST_ORACLE`;
- `TEST_EVIDENCE`;
- `SLO`;
- `COST`;
- `RELEASE_EVIDENCE`.

Invalid connections should be rejected visually and structurally.

## 6. Three zoom levels

### Z0 — Project conveyor
Shows only A0–A16 macro stages and gates.

### Z1 — Engineering stations
Expands a macro stage into approximately 50–60 bounded stations across the full lifecycle.
Each station should be one understandable transformation with explicit input/output.

### Z2 — Black-box internals
Expands one station into:

```text
inputs
→ deterministic checks
→ source retrieval
→ algorithm/method
→ candidate transformation
→ gap/conflict analysis
→ reviewer/owner actions
→ local tests
→ outputs
```

Only at this level will future LLM/Model Zoo participation be shown.

## 7. Perspectives

The same graph must support filtered overlays instead of duplicated diagrams:

- `Lifecycle` — stages/gates;
- `Business` — need → requirements → value;
- `System` — functions/interfaces/data flows;
- `Security` — asset → threat → requirement → control → test → residual risk;
- `Data` — source → classification → transformation → lineage → use;
- `Architecture` — drivers → options → decisions → components;
- `Verification` — requirement/risk → oracle → test → evidence;
- `Operations` — component → telemetry → SLO → incident → feedback;
- `Cost` — decision/component → resource → cost/TCO;
- `Compliance` — source/clause → requirement → artifact field → evidence.

## 8. Designer workflow

The designer should be able to:

1. drop or select a station/node;
2. see required inputs immediately;
3. attach existing evidence/materials by drag/drop or search;
4. see which fields are already mapped from existing documents;
5. see missing/conflicted/stale inputs;
6. open the black box and inspect the method/algorithm;
7. see supporting normative/book/scientific sources;
8. see owner/reviewer and authority boundary;
9. inspect test oracle before implementation;
10. promote the node only when its local evidence/gate is satisfied;
11. follow downstream impact when an input changes;
12. switch perspectives without duplicating the underlying model.

## 9. Reuse instead of reinvention

Recommended implementation direction after paper-pipeline approval:

- `React Flow` for the generic engineering graph/canvas;
- custom typed nodes/handles for FATHER artifacts;
- nested subflows for black-box internals;
- minimap for large project graphs;
- `bpmn-js` only for optional process/human-approval view;
- Structurizr DSL/export for C4 architecture views;
- Markdown/YAML/JSON remain canonical data sources;
- no UI-only engineering truth.

## 10. Non-goals

- no generic whiteboard;
- no uncontrolled free-form wiring;
- no visual-only information that cannot be serialized;
- no automatic gate because a node is green;
- no Model Zoo shown as the center of the product;
- no requirement that every document becomes a separate node.

The visual workbench is an **engineering instrument panel over the paper pipeline**, not the pipeline itself.
