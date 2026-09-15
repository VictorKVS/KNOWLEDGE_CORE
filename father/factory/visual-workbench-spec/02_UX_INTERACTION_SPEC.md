# FATHER Visual Engineering Workbench — UX & Live Interaction Specification

Status: `DRAFT_V0.1`

## 1. UX цель

Пользователь должен работать в FATHER как в инженерной среде моделирования: основной контекст — **схема**, а документы, evidence, алгоритмы, approvals и history открываются вокруг неё, не разрушая пространственную ориентацию.

Главный запрет:

> Нельзя превращать Workbench в набор отдельных CRUD-страниц, между которыми пользователь постоянно теряет контекст.

Главная формула взаимодействия:

```text
hover = glance
click = inspect
open/focus = work with object
 double click = drill down into black box
right click = action menu
edge click = inspect relation
breadcrumb = restore parent context
flow mode = tell a story through the graph
```

---

# 2. Desktop layout

Минимальная рабочая ширина для full-mode: 1280 px. Рекомендуемая: 1440+.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR                                                                      │
│ Project | Baseline | Stage | Gate | Perspective | Search | History | Compare│
├────────────────┬───────────────────────────────────┬─────────────────────────┤
│ LEFT SIDEBAR   │ CANVAS                            │ RIGHT INSPECTOR         │
│ palette/tree   │ live engineering graph            │ selected object         │
│                │                                   │ tabs                    │
│                │                                   │                         │
├────────────────┴───────────────────────────────────┴─────────────────────────┤
│ BOTTOM DRAWER / STATUS STRIP                                                 │
│ flow | blockers | conflicts | unknown | stale | audit | test run | timeline │
└──────────────────────────────────────────────────────────────────────────────┘
```

## UX-LAYOUT-001 Left sidebar modes

Sidebar переключается между:

- Palette;
- Project tree;
- Saved views;
- Search results;
- Review queue.

## UX-LAYOUT-002 Right inspector

Right Inspector persistent; width user-resizable. Default ~360–440 px.

## UX-LAYOUT-003 Bottom drawer

По умолчанию collapsed. Раскрывается для:

- live scenario flow;
- test execution results;
- diff details;
- audit timeline;
- error/debug details;
- batch blocker review.

---

# 3. Canvas fundamentals

## UX-CANVAS-001 Infinite-ish workspace

Canvas поддерживает pan/zoom, fit-to-view, selection rectangle, center-on-object, focus neighborhood.

## UX-CANVAS-002 Minimap

Minimap обязателен начиная с Z1. Он показывает viewport и status clusters.

## UX-CANVAS-003 Grid

Optional snapping grid. Engineering relationship не зависит от pixel position.

## UX-CANVAS-004 Auto-layout

Auto-layout доступен как действие, но никогда не должен уничтожать manual layout without preview/undo.

Modes:

- left-to-right conveyor;
- hierarchical;
- radial neighborhood;
- swimlane by role/stage;
- compact dependency.

## UX-CANVAS-005 Virtualization

Large graph renderer должен уметь не рендерить offscreen heavy details.

## UX-CANVAS-006 Layout persistence

Layout metadata хранится отдельно от semantic engineering model.

---

# 4. Node visual anatomy

Compact node:

```text
┌──────────────────────────┐
│ [status] S25 Requirements│
│ owner: Req Eng           │
│ IN 4              OUT 6  │
│ !2   ?1   stale:0        │
└──────────────────────────┘
```

Standard node adds visible ports.

Review node adds:

- gate badge;
- evidence/test counters;
- pending review indicator.

## UX-NODE-001 Status encoding

Status uses combination:

- color;
- icon;
- text/tooltip;
- optional border style.

Never color alone.

## UX-NODE-002 Selected state

Selected node has clear border/highlight and connected edges emphasis.

## UX-NODE-003 Blocked state

Blocked node shows blocker count and strongest blocker class.

## UX-NODE-004 Stale state

Stale node visibly differs from failed node: stale means previous evidence may no longer be valid.

## UX-NODE-005 Composite state

Composite station has expand/drill indicator.

---

# 5. Hover interaction

Hover delay target: 250–400 ms to avoid flicker.

Tooltip shows only high-value summary:

```text
S25 Requirements Normalization
Status: OWNER_REVIEW
Owner: Requirements Engineer
Inputs: 5/5
Outputs: 6
Blockers: 1 conflict
Last material change: 18 min ago
Double-click to open internals
```

No interactive form inside hover tooltip.

---

# 6. Single click — Inspector

Single click selects object and populates Inspector without changing route context.

Tabs:

1. Overview;
2. Inputs/Outputs;
3. Fields;
4. Evidence;
5. Algorithm;
6. Trace;
7. Tests;
8. Gate/Authority;
9. People;
10. History/Diff;
11. Impact;
12. AI Assistance (feature-gated).

## 6.1 Overview

Required:

- ID/name/type;
- purpose;
- status;
- current version;
- owner/reviewers;
- readiness summary;
- blocker summary;
- upstream/downstream counts;
- material change timestamp.

## 6.2 Inputs/Outputs

Каждый port показывает:

- type;
- source/target objects;
- required/optional;
- version;
- validity;
- missing/stale/conflicted state.

## 6.3 Fields

Structured fields, editable only with permission.

Each field can show:

- value;
- source/evidence badge;
- owner;
- status;
- last changed by;
- validation warnings.

## 6.4 Evidence

Evidence table + viewer launch:

- source ID;
- source title;
- version/effective status;
- locator;
- supporting/conflicting;
- freshness;
- open side-by-side.

## 6.5 Algorithm

Show algorithm design card:

- problem;
- selected method;
- simplest baseline;
- assumptions;
- invariants;
- alternatives;
- correctness/adequacy argument;
- complexity;
- failure modes;
- falsification tests;
- normative/professional/scientific refs.

## 6.6 Trace

Interactive mini-subgraph centered on object.

Commands:

- trace to source;
- trace to requirement;
- trace to decision;
- trace to implementation;
- trace to test;
- trace to release.

## 6.7 Tests

Displays planned vs executed evidence separately.

## 6.8 Gate/Authority

Shows:

- affected gate;
- required evidence;
- current unmet conditions;
- authorized final role/person;
- previous decisions.

## 6.9 People

Distinct relations:

- accountable owner;
- contributor;
- reviewer;
- final authority;
- risk owner;
- data owner.

## 6.10 History/Diff

Timeline of revisions with semantic diff.

## 6.11 Impact

Preview downstream impact before committing a material change.

---

# 7. Double click — Drill down

## UX-DRILL-001 Composite station

Double click changes canvas context to internal graph.

Example:

```text
Project > A5 Requirements > S25 Normalize Requirements
```

Internal graph example:

```text
Incoming evidence
  ↓
schema validation
  ↓
atomicity check
  ↓
duplicate/conflict candidates
  ↓
normalization
  ↓
owner clarification
  ↓
review
  ↓
normalized requirements
```

## UX-DRILL-002 Atomic object

If object has no subgraph, double click opens Focus mode: canvas dims unrelated neighborhood and expands Inspector.

## UX-DRILL-003 Preserve context

Parent viewport/zoom/selection stored in navigation stack.

---

# 8. Breadcrumb navigation

Breadcrumb must allow click to any parent level.

On return restore:

- zoom;
- pan;
- selection;
- perspective;
- filters.

Browser Back/Forward should work consistently where possible.

---

# 9. Right-click context menu

Menu is context/permission/status aware.

Common actions:

- Open;
- Drill down;
- Focus neighborhood;
- Trace upstream;
- Trace downstream;
- Show impact;
- Request owner input;
- Create review task;
- Propose change;
- Compare versions;
- Validate;
- Open source/evidence;
- Export subgraph;
- Copy deep link.

Authority actions are separated visually:

- Approve;
- Approve with conditions;
- Reject;
- Accept risk;
- Mark Not Applicable;
- Promote baseline;
- Release approval.

These may require modal confirmation/form.

---

# 10. Modal policy

Modal is reserved for actions that are:

- irreversible or high impact;
- authority-bearing;
- destructive;
- security/legal/risk relevant;
- multi-step with required rationale.

Use modal for:

- final gate decision;
- risk acceptance;
- baseline promotion;
- delete/retire;
- mass status change;
- production release approval;
- provider/data policy exception.

Do NOT use modal for ordinary reading/navigation.

---

# 11. Edge interaction

Single click on edge opens relation Inspector.

Hover shows:

```text
S25 --PRODUCES--> REQ-014
port: normalizedRequirements
version: v3
```

Invalid/broken/stale relation has visual state.

Right click actions:

- inspect contract;
- trace relation evidence;
- propose change;
- detach (permission controlled);
- open endpoints.

---

# 12. Port interaction

Port hover shows accepted types and readiness.

Dragging connection:

1. valid targets highlighted;
2. invalid targets dimmed;
3. drop on invalid target rejected with clear explanation;
4. drop on compatible but transform-required target suggests explicit Adapter Station, never silent cast.

---

# 13. Live Flow mode

Purpose: tell an engineering scenario over the static model.

## UX-FLOW-001 Flow picker

Top bar/Bottom drawer command selects saved or temporary flow.

Examples:

- requirement change;
- security incident;
- test failure;
- architecture decision;
- release rollback;
- source superseded.

## UX-FLOW-002 Playback

Controls:

- Previous;
- Next;
- Play/Pause;
- Restart;
- Jump to step;
- Exit.

Active node/edge highlighted; other graph fades but remains visible.

## UX-FLOW-003 Step narrative

Bottom drawer shows step explanation, evidence and decision.

## UX-FLOW-004 Simulation

Simulation uses copy/preview model and must not mutate canonical project until explicitly converted to Change Request.

---

# 14. Compare mode

Compare supports:

- version A vs B of one object;
- baseline A vs B project slice;
- architecture option A vs B;
- before/after proposed change.

Visual treatment:

- added = plus badge;
- removed = strike/dashed;
- changed = split color/icon;
- unchanged = muted;
- impact = highlighted downstream.

Semantic diff panel shows field/relation/status/evidence/test changes.

---

# 15. Perspective switch

Perspective switch must not reload/navigate away from current object.

Example:

User selected `API-12`, then switches:

- Architecture → shows component/context relations;
- Security → shows auth/threat/control/test;
- Data → shows schemas/classification/lineage;
- Compliance → shows clauses/obligations/evidence;
- Operations → shows SLO/telemetry/incidents.

Selection remains.

---

# 16. Filters

Filters combinable:

- stage/station;
- object type;
- status;
- owner/reviewer;
- tag;
- risk level;
- data class;
- source status;
- gate;
- changed since;
- unresolved unknown;
- conflicted;
- stale;
- no test coverage;
- no evidence.

Saved filters may become Saved Views.

---

# 17. Project tree

Alternative navigation for users who prefer hierarchy.

Tree levels:

```text
Project
  Baselines
  Sources
  Product
  System
  Requirements
  Security
  Architecture
  Tests
  Releases
  Operations
```

Tree selection synchronizes canvas selection.

---

# 18. Palette

Palette is not a generic low-code node library.

Sections:

- Sources;
- Product/Analysis;
- System;
- Security;
- Requirements;
- Architecture;
- Data/Integration;
- Test;
- Delivery/Release;
- Operations;
- Utility/Adapter;
- Human Gate.

Items shown according to project/stage/permission.

Reusable composite templates may appear later only after stable contracts.

---

# 19. Editing mode

Read mode and Edit mode visually distinct.

In edit mode:

- dirty state visible;
- validation errors inline;
- server conflict detection;
- save creates revision;
- cancel restores canonical state;
- material change requires rationale where configured.

No silent autosave of authority decisions.

---

# 20. Review mode

Review mode changes emphasis:

- candidate changes highlighted;
- evidence and diff prominent;
- approve/rework controls visible only to reviewer/authority;
- comments anchored to field/relation/object;
- unresolved review thread count visible.

Review can be completed without editing underlying artifact.

---

# 21. Source/evidence viewer

Preferred split-screen:

```text
artifact/field on left
source page/text on right
```

Features:

- highlight locator;
- previous/next evidence;
- supporting/conflicting toggle;
- source metadata;
- version/effective status;
- copy stable citation/ref;
- map selected fragment to artifact field if authorized.

For PDF/image-based sources, page image must be inspectable.

---

# 22. Error UX

Classes:

- validation error;
- permission error;
- conflict/concurrent modification;
- missing source;
- stale version;
- server/network;
- import failure;
- rendering/layout;
- AI/provider failure.

Every material error display includes:

- what failed;
- object/operation;
- whether data saved;
- user action;
- correlation/reference ID where server involved.

---

# 23. Empty states

Empty is not failure.

Examples:

- no source yet → “Attach/register source to start S01”;
- no risks → “No risks recorded; not equivalent to risk-free”;
- no tests → “Verification coverage not designed”;
- no AI → feature absent without visual warning.

---

# 24. Keyboard model

Minimum:

- `/` focus global search;
- `Ctrl/Cmd+K` command palette;
- `Enter` open selected;
- `Esc` close drawer/modal/exit focus;
- `F` fit selection;
- arrow keys move selection in list/tree contexts;
- `Backspace/Delete` only in edit mode with confirmation for material object;
- `Ctrl/Cmd+Z` draft undo;
- `Alt+Left/Right` context navigation where platform allows.

Shortcuts user-configurable later.

---

# 25. Accessibility

- semantic labels for nodes/ports/actions;
- keyboard-accessible inspector/forms;
- screen-reader alternative list/tree for canvas content;
- status not color-only;
- focus ring;
- contrast compliant target;
- reduced motion option for flow animations;
- zoom controls independent of browser zoom.

---

# 26. Responsive behavior

Primary target desktop/laptop.

Tablet read/review mode supported later.

Mobile is not a full diagram editor in MVP; must support read-only object detail/review tasks where practical.

---

# 27. Visual density and clutter control

Mechanisms:

- semantic zoom;
- collapse composite nodes;
- hide optional ports until selected;
- bundle low-priority edges;
- perspective filters;
- focus neighborhood;
- progressive labels;
- density modes;
- minimap.

System must prefer hiding secondary information over shrinking text below readability.

---

# 28. Notifications and attention design

Canvas attention levels:

- P0 blocker/security/legal authority — high prominence;
- P1 material unresolved — visible badge;
- P2 review/task — normal indicator;
- informational — inspector/timeline only.

No flashing/pulsing except transient user-initiated focus.

---

# 29. Loading states

For large graph:

- show skeleton/partial graph;
- preserve known layout;
- progressive edge loading allowed;
- never show misleading “empty project” while data is loading.

---

# 30. Success UX acceptance scenarios

The UX is not accepted until a user can complete without documentation lookup:

### Scenario A — trace a requirement

1. Search `REQ-014`;
2. inspect source;
3. trace upstream to Business Need;
4. trace downstream to ADR/component/test;
5. switch Security perspective;
6. return to original view.

### Scenario B — change impact

1. open source revision;
2. propose material change;
3. preview stale downstream;
4. inspect impacted gate/tests;
5. create Change Request;
6. cancel preview without mutation.

### Scenario C — drill down station

1. select S25;
2. open Inspector;
3. double-click;
4. inspect internal algorithm;
5. open evidence;
6. return via breadcrumb with viewport restored.

### Scenario D — human gate

1. open pending gate;
2. inspect unmet evidence;
3. when ready, open authority form;
4. record rationale;
5. sign/confirm decision;
6. see resulting state and audit event.

### Scenario E — failed test

1. open failed S54 result;
2. show trace to requirement/control;
3. system suggests possible rework origin classes without deciding root cause;
4. reviewer selects root-cause station;
5. impacted downstream becomes stale.

These scenarios are mandatory E2E UX tests.