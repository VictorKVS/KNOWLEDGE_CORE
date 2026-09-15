# FATHER Visual Engineering Workbench — Competitor / Reference Pattern Crosswalk

Status: `DRAFT_V0.1 / DESIGN RESEARCH`

## 1. Purpose

FATHER should reuse proven interaction patterns while keeping its own engineering data model. This document records the rationale so implementation does not drift into copying a competitor wholesale.

Selection principle:

```text
adopt interaction pattern
≠
adopt competitor information model
```

---

# 2. Ardoq

Official reference:

- https://help.ardoq.com/

Observed useful concepts:

- components as typed model elements;
- relationships/references as first-class architecture data;
- people/roles modeled explicitly rather than only text fields;
- data-driven views over model repository;
- enterprise architecture repository orientation.

## Adopt

1. Treat engineering things as first-class typed objects.
2. Treat relations as data, not diagram lines.
3. Model ownership/responsibility explicitly.
4. Allow one object to appear in multiple views.
5. Detail panel/inspector for selected object.

## Do not copy blindly

- enterprise metamodel complexity at MVP start;
- highly generic architecture ontology before FATHER core contracts stabilize;
- configuration-heavy experience that obscures lifecycle flow.

## FATHER adaptation

FATHER graph is narrower and stronger semantically:

```text
source → requirement → threat/risk → decision → component → test → evidence
```

The primary navigation is the engineering lifecycle/conveyor, not an abstract enterprise repository.

---

# 3. IcePanel

Official references:

- https://docs.icepanel.io/getting-started
- https://docs.icepanel.io/core-features/diagramming
- https://docs.icepanel.io/visual-storytelling/flows
- https://docs.icepanel.io/visual-storytelling/perspective-tags

Observed patterns:

- model-based rather than independent diagram objects;
- C4 abstraction/zoom levels;
- objects reused across diagrams;
- changes synchronize through model views;
- right-hand details panel;
- zoom into nested object;
- Flows step through messages/scenarios on the same diagram;
- Tags show risk/cost/security/deployment perspectives without duplicating diagrams;
- versions/timeline for architecture evolution.

## Adopt

1. One model, many views.
2. Right-side object inspector.
3. Drill-down from high-level object to lower-level diagram/subgraph.
4. Scenario/Flow playback over static graph.
5. Perspectives that highlight risk/security/cost/etc.
6. Version timeline and current/future comparison.

## Extend beyond IcePanel

FATHER needs more than architecture storytelling:

- source evidence;
- normative clauses;
- requirements;
- security threat/risk chain;
- test oracles/results;
- authority decisions;
- rework/stale propagation;
- lifecycle gates.

## Do not copy blindly

- C4 hierarchy as the only hierarchy;
- architecture object taxonomy as whole FATHER domain model;
- tags as replacement for typed engineering relations.

---

# 4. KNIME

Official reference:

- https://docs.knime.com/ap/latest/analytics_platform_components_guide/

Useful patterns:

- nodes with explicit ports;
- components encapsulate sub-workflows;
- metanodes collapse complexity;
- components can have custom configuration/view;
- execution/readiness state visible as traffic-light-like state;
- output port states reflect internal execution result;
- component boundary preserves explicit inputs/outputs.

## Adopt

1. Station/component black-box boundary.
2. Explicit typed ports.
3. Collapse/expand subgraph.
4. Status visible directly on node.
5. Internal failure reflected at boundary.
6. Reusable component concept later for stable FATHER templates.

## Do not copy blindly

- execution semantics of data analytics pipeline as project lifecycle truth;
- auto-execution assumption for human-owned engineering decisions.

## FATHER adaptation

Station readiness is not “node executed”. It means required evidence/review/gate conditions are satisfied.

---

# 5. Node-RED

Official references:

- https://nodered.org/docs/user-guide/editor/
- https://nodered.org/docs/user-guide/editor/workspace/
- https://nodered.org/docs/user-guide/editor/palette/
- https://nodered.org/docs/user-guide/editor/sidebar/
- https://nodered.org/docs/user-guide/editor/workspace/subflows

Useful patterns:

- central workspace;
- palette;
- left/right sidebars;
- flow tabs;
- navigator/minimap;
- subflows collapsed into reusable node;
- drag-and-wire simplicity.

## Adopt

1. Workspace ergonomics.
2. Palette + canvas + inspector composition.
3. Minimap/navigator.
4. Subflow concept.
5. Fast search/filter of palette items.

## Do not copy blindly

- unrestricted wiring;
- generic function nodes in core engineering workflow;
- “deploy” as equivalent to engineering approval.

## FATHER adaptation

Connections are type-checked engineering relations. Invalid wiring is rejected.

---

# 6. BPMN / bpmn-js / Camunda-style process modeling

Official toolkit:

- https://bpmn.io/toolkit/bpmn-js/

Useful patterns:

- browser-embedded BPMN viewer/editor;
- user tasks;
- gateways;
- waiting states;
- process simulation/extensions possible;
- process representation can be embedded in another product.

## Adopt

1. Optional process view.
2. Human approval task visualization.
3. Exclusive/parallel branch semantics where lifecycle process needs them.
4. Waiting/approval visual states.
5. Embed bpmn-js instead of writing BPMN renderer.

## Do not use as FATHER core model

BPMN token flow cannot express the full evidence/traceability semantics required by FATHER.

Canonical FATHER graph remains richer; BPMN is a view/adaptor.

---

# 7. Structurizr / C4

Official references:

- https://docs.structurizr.com/
- https://docs.structurizr.com/dsl
- https://docs.structurizr.com/dsl/language

Useful patterns:

- model as code;
- model + views separated;
- system landscape/context/container/component;
- filtered/dynamic/deployment views;
- documentation/ADRs alongside model;
- Git-friendly DSL.

## Adopt

1. Separation of model and view.
2. Multiple views from same model.
3. Context/Container/Component abstraction.
4. Dynamic/deployment representations.
5. Export adapter / interoperability.

## Do not copy blindly

- architecture model as complete project lifecycle;
- textual DSL as only editing interface for FATHER users.

## FATHER adaptation

C4 is a projection of architecture subset inside a broader engineering graph.

---

# 8. React Flow / XYFlow

Official references:

- https://reactflow.dev/
- https://reactflow.dev/learn/customization/handles

Useful capabilities:

- custom nodes;
- source/target handles;
- multiple handles with IDs;
- custom edges;
- pan/zoom;
- selection;
- nested/group/subflow patterns;
- minimap ecosystem/examples;
- web-native React integration.

## Adopt as implementation candidate

React Flow is a strong candidate for the generic canvas renderer.

FATHER still implements:

- typed port rules;
- semantic zoom;
- station/node design system;
- authority/status semantics;
- graph projection/query;
- inspector;
- trace/impact logic.

## Risk

Do not let React Flow JSON become canonical project storage format.

---

# 9. CAD/BIM reference patterns

Not one specific product dependency, but interaction principles:

- layers/perspectives;
- object selection → properties inspector;
- hierarchical zoom/detail;
- stable coordinate/context;
- annotations/measurements;
- object library;
- current vs proposed design;
- model validation;
- change impact;
- print/export views derived from model.

FATHER analogy:

```text
building element       → engineering artifact/component
material/specification → requirement/control/contract
construction drawing   → architecture/system view
inspection             → verification/test evidence
permit/approval        → gate/authority decision
revision cloud         → semantic diff/change impact
```

---

# 10. Combined FATHER UX formula

```text
Ardoq: typed architecture repository
+
IcePanel: model-based zoom + flows + perspectives
+
KNIME: black-box components + typed ports + status
+
Node-RED: palette/workspace/sidebar/minimap ergonomics
+
bpmn-js: human workflow/gate view
+
Structurizr: one architecture model / many C4 views
+
React Flow: web canvas implementation substrate
+
FATHER: evidence + lifecycle + authority + tests + security + traceability
```

---

# 11. Explicit differentiation

FATHER is not competing by drawing prettier boxes.

Its differentiation is the linked engineering chain:

```text
SOURCE
→ FACT/CLAIM
→ BUSINESS NEED
→ REQUIREMENT/NFR
→ SYSTEM MODEL
→ THREAT/RISK
→ ARCHITECTURE DRIVER
→ OPTION/ADR
→ COMPONENT/CONTRACT
→ TEST ORACLE
→ TEST RESULT
→ RELEASE
→ OPERATION EVIDENCE
→ FEEDBACK
```

and the ability to visually prove why each material object exists.

---

# 12. Design decisions derived from competitor study

## CD-01
Use model-driven views, never independent diagram copies.

## CD-02
Use right Inspector for ordinary object work; modal only for high-impact authority actions.

## CD-03
Use drill-down black boxes and breadcrumbs.

## CD-04
Use typed ports, not free-form wires.

## CD-05
Use live scenario flows over same graph.

## CD-06
Use perspectives/layers rather than duplicated diagrams.

## CD-07
Preserve version timeline/current-vs-future comparison.

## CD-08
Use BPMN as optional process view, not canonical data model.

## CD-09
Use React Flow as rendering substrate candidate, not project schema.

## CD-10
Keep canonical data exportable/versionable outside UI.

These design decisions should receive ADRs before implementation begins.