# FATHER Visual Workbench — Live Interaction Specification

Status: `CANDIDATE / INTERACTION CONTRACT / NO RUNTIME AUTHORITY`

## 1. Goal

The FATHER canvas must behave like a professional engineering instrument, not a static diagram. Every node is a live projection of canonical engineering data and can be inspected, expanded, edited within authority, traced backward to evidence, and traced forward to impact.

Primary interaction principle:

```text
hover = glance
single click = inspect
second click / explicit Open = focus
 double click = drill down / change graph context
right click = action menu
edge click = relationship details
breadcrumb = go back without losing context
```

The same canonical node is reused across all views. UI state never becomes an independent source of truth.

---

## 2. Competitor-derived patterns adopted

### Ardoq
Adopt:
- single click in a visualization opens focused component details without leaving context;
- detail drawer can expose Overview / Fields / References / Viewpoints / Styles-like sections;
- double click explores immediate connected neighborhood;
- in-view editing keeps the user inside the visualization;
- one component can appear in many viewpoints.

### IcePanel
Adopt:
- selected object opens a right-hand inspector;
- object carries description, connections, history, status, ownership, diagrams and flows;
- model object is global/reusable and edits propagate to every diagram;
- flows animate/step through a scenario over the same diagram;
- tags/perspectives change the story without duplicating the model.

### KNIME
Adopt:
- composite node / metanode hides internal complexity;
- node state is visible directly on canvas;
- composite node can be opened to inspect internal subworkflow;
- inputs/outputs remain explicit at the boundary.

### Node-RED
Adopt:
- palette + central workspace + sidebars;
- status/error indicators on the node itself;
- minimap/navigator for large graphs;
- quick access to information/help/debug-like panels.

### Camunda
Adopt only for human workflow:
- explicit user-task forms;
- waiting state until human completion;
- play/test mode separated from deployed state;
- versioned/deployable process bundles.

### Structurizr / C4
Adopt:
- one model, many views;
- hierarchy Context → Container → Component;
- dynamic/deployment views derived from same model;
- architecture docs and ADRs linked to model elements.

---

## 3. Screen anatomy

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Project | Stage | Gate | Perspective | Search | History | Compare | Runbook │
├─────────────┬─────────────────────────────────────┬──────────────────────────┤
│ PALETTE     │              CANVAS                 │ INSPECTOR DRAWER         │
│             │                                     │                          │
│ Sources     │  [Input] → [Node] → [Output]       │ Overview                 │
│ Product     │                  │                  │ Inputs / Outputs         │
│ System      │                  ▼                  │ Evidence                 │
│ Security    │              [Subgraph]             │ Algorithm / Method       │
│ Requirements│                                     │ Requirements / Risks     │
│ Arch        │                                     │ Tests / Gate             │
│ Test        │                                     │ Owner / Reviewers        │
│ Delivery    │                                     │ History / Diff           │
├─────────────┴─────────────────────────────────────┴──────────────────────────┤
│ Timeline / selected flow / blocked reasons / conflicts / UNKNOWN / audit    │
└──────────────────────────────────────────────────────────────────────────────┘
```

No modal is used for ordinary inspection because it breaks spatial context. Modal dialogs are reserved for consequential actions such as approval, reject, accept residual risk, destructive change, or promotion.

---

## 4. Node appearance on canvas

Every station/node shows only the information needed for orientation:

```text
┌──────────────────────────────┐
│ S17  SYSTEM CONTEXT          │  status badge
│ System Engineer              │  owner
│                              │
│  3 inputs     2 outputs      │
│  1 UNKNOWN    0 CONFLICT     │
│                              │
│  Gate impact: SYSTEM_READY   │
└──────────────────────────────┘
```

Visual overlays:
- green border = VERIFIED/READY;
- amber = PARTIAL/OWNER_REVIEW;
- red = CONFLICTED/BLOCKED;
- gray = NOT_APPLICABLE;
- blue dot = changed since last reviewed baseline;
- lock = human authority required;
- shield = security-critical;
- flask = experiment/PoC evidence;
- test icon = test oracle exists;
- broken-link icon = unresolved evidence/source;
- snowflake = frozen/stale-dependent downstream.

Color is never the only carrier of status; icon + text label are mandatory.

---

## 5. Hover behavior

Hover must answer "what is this?" in under 2 seconds.

Small non-blocking popover:

```text
S17 — System Context
Owner: System Engineer
Status: PARTIAL
Inputs: 3/4 ready
Outputs: SYSTEM_CONTEXT, SYSTEM_BOUNDARY
Blocks: Threat Model v0
Issue: external dependency owner UNKNOWN
```

No editing on hover.

---

## 6. Single-click behavior — Inspector Drawer

Single click selects the node and opens a persistent right-hand drawer while keeping the full graph visible.

Tabs:

### Overview
- purpose;
- macro stage / station;
- current status;
- owner/reviewers;
- upstream/downstream count;
- gate impact;
- latest decision/review.

### Inputs / Outputs
Typed ports with each item state:
- source;
- producer;
- version;
- status;
- missing/conflicted/stale flags.

Clicking a port highlights corresponding upstream/downstream nodes on canvas.

### Evidence
- source documents;
- exact evidence refs;
- normative refs;
- professional/book/science refs;
- evidence freshness;
- unresolved citation/source failures.

Each evidence row can open a preview without leaving the canvas.

### Algorithm
- algorithmRef;
- problem statement;
- baseline/simple method;
- selected method;
- assumptions/invariants;
- complexity;
- failure modes;
- falsification/tests;
- automation level L0–L5.

### Requirements / Risks
- linked BUS/REQ/NFR/RISK/THREAT/CTRL;
- trace backward to source;
- trace forward to control/test/release.

### Tests / Gate
- local oracle;
- required test cases;
- last test/eval result;
- gate minimum evidence;
- authority required;
- block reasons.

### People
- accountable owner;
- producers;
- reviewers;
- final authority;
- role maturity/certification state for future AI-assisted roles.

### History
- versions;
- diffs;
- supersession;
- review/approval history;
- rework events;
- incidents that reopened the node.

---

## 7. Double-click behavior — Drill-down

Double click does not merely zoom. It changes the current graph context to the internals of the selected composite node.

Example:

```text
Z1:
[S17 SYSTEM CONTEXT]

Double click

Z2:
[Source facts]
   ↓
[Terminology normalize]
   ↓
[Actors / external systems]
   ↓
[Boundary classification]
   ↓
[Context consistency check]
   ↓
[Owner review]
   ↓
[SYSTEM_CONTEXT output]
```

Top breadcrumb preserves context:

`Project > A3 System Engineering > S17 System Context`

Back returns to the exact previous viewport/selection.

---

## 8. Right-click behavior — Context menu

Allowed actions depend on role and node status.

Examples:
- Open details;
- Open internals;
- Trace upstream;
- Trace downstream;
- Show only dependencies;
- Open evidence;
- Open tests;
- Compare versions;
- Create review task;
- Mark NOT_APPLICABLE (authority required);
- Request missing input;
- Reopen upstream cause;
- Create change request;
- Add note/comment;
- Copy deep link.

Consequential actions never execute immediately; they open a confirmation/reason form.

---

## 9. Edge interaction

Connections are first-class objects, not decorative arrows.

Clicking an edge opens relationship details:
- source node/port;
- target node/port;
- relation type;
- artifact/evidence carried;
- version;
- transformation semantics;
- schema/contract;
- security classification;
- owner;
- test/validation;
- change history.

Hover edge label example:

`SYSTEM_CONTEXT v3 → used by THREAT_MODEL_V0 / VERIFIED`

Broken or incompatible edges are visible before the target gate.

---

## 10. Focus modes

The graph should support one-click focus modes without creating duplicate diagrams.

### Trace upstream
Shows only provenance path to the selected node.

### Trace downstream
Shows blast radius if selected artifact changes.

### Security perspective
Shows only:
`asset → threat → scenario → requirement → control → test → residual risk`.

### Verification perspective
Shows only:
`requirement/risk → oracle → test → evidence`.

### Compliance perspective
Shows only:
`source/clause → requirement → artifact field → control → evidence`.

### Change impact
Compares baseline vs candidate and highlights every potentially stale dependent node.

---

## 11. Live flow mode

Borrow the storytelling idea from IcePanel Flows and execution preview from Camunda/KNIME.

A designer selects a scenario such as:
- "new requirement enters";
- "security finding appears";
- "architecture option rejected";
- "test fails";
- "production incident occurs".

The canvas then advances step-by-step, highlighting the exact stations and data moving between them.

Example:

```text
Test FAIL
  → defect classification
  → trace root cause
  → reopen A9 Detailed Design
  → update component contract
  → invalidate downstream implementation evidence
  → rerun affected tests
```

This is presentation/simulation of the canonical graph, not a separate process model.

---

## 12. Window policy

Use four UI surfaces only:

1. **Popover** — glance information on hover.
2. **Right drawer** — ordinary inspection/editing while preserving canvas context.
3. **Full-canvas drill-down** — internal subgraph of composite node.
4. **Modal** — only consequential authority action or destructive confirmation.

Avoid opening many floating windows because they destroy spatial memory and become hard to manage on large projects.

---

## 13. Designer ergonomics

Required:
- Ctrl/Cmd+K global search;
- breadcrumbs;
- minimap;
- keyboard navigation among connected nodes;
- "back to last context";
- deep links to node/edge/view;
- save named viewpoints;
- saved filters/perspectives;
- side-by-side version diff;
- comments/review threads anchored to nodes/fields/edges;
- undo/redo for candidate edits;
- draft vs verified baseline clearly separated;
- dark/light mode later, not a modeling concern.

---

## 14. Source of truth rule

The visual canvas serializes only references and presentation state.

Canonical engineering truth remains in structured project objects:

```text
artifacts
relationships
methods
requirements
risks
sources/evidence
tests
gates
approvals
versions
```

Changing an object from any valid view updates the same canonical object. No per-diagram copies.

---

## 15. Implementation implication

After paper-pipeline approval, recommended UI foundation:

- React Flow for canvas, custom nodes, typed handles, nested subflows, minimap, selection and viewport state;
- right drawer built from FATHER node contract;
- optional bpmn-js for human process/approval view only;
- Structurizr export/view for C4 representations;
- canonical Markdown/YAML/JSON/DB object model beneath the UI.

This specification defines interaction semantics only. It does not unlock automation or Model Zoo authority.
