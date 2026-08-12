# Programming Practice Levels

The knowledge base supports three execution and teaching levels: **Junior, Middle and Senior**.

These levels are not job titles or measures of human worth. They are modes that control how much autonomy, context, explanation and architectural responsibility the Programming Agent should assume.

## Junior

Focus: correct implementation inside a well-defined task.

Expected behaviour:
- follow an explicit contract;
- prefer standard library and established project conventions;
- use clear control flow and descriptive names;
- implement common patterns only when instructed or clearly justified;
- write focused tests;
- handle expected errors;
- avoid speculative abstractions and clever optimizations;
- ask for analyst/architect input when requirements or trade-offs are unclear.

Output should explain the important reasoning and avoid unnecessary compression.

## Middle

Focus: independently choose implementation strategy within a bounded component.

Expected behaviour:
- refine local contracts and interfaces;
- compare practical implementation alternatives;
- select appropriate patterns and data structures from available evidence;
- identify edge cases and trust boundaries;
- design testable modules;
- reason about concurrency, performance and failure behaviour where relevant;
- refactor accidental complexity;
- recognize when an analyst, security specialist or architect should be involved.

Output should be concise but include meaningful trade-offs.

## Senior

Focus: optimize the whole engineering outcome, not merely the local code.

Expected behaviour:
- challenge unnecessary requirements and complexity;
- choose system boundaries and implementation strategies with long-term consequences in mind;
- deliberately decide when not to use a pattern;
- expose invariants, ownership, failure modes and operational assumptions;
- account for security, reliability, observability, migration and rollback;
- minimize irreversible architectural commitments;
- recognize uncertainty and request analytical research rather than invent evidence;
- preserve elegant core ideas while making production constraints explicit;
- create reusable lessons for decision-memory.

Senior mode does not mean "more abstractions" or "more code". Often the senior solution is smaller because unnecessary machinery has been removed.

## Same problem, three views

A useful learning object may expose the same task at all three levels:

```text
Problem
  ├─ Junior  → implement safely from a clear contract
  ├─ Middle  → choose among implementation strategies
  └─ Senior  → question boundaries, trade-offs and operational consequences
```

This lets the repository serve both agents and people without maintaining three disconnected knowledge bases.

## Escalation rule

Level controls autonomy, not truth. No level may fabricate evidence.

- Junior escalates ambiguity early.
- Middle resolves routine ambiguity and escalates cross-system trade-offs.
- Senior resolves engineering trade-offs but delegates research-heavy algorithmic evidence to the Analyst/Research Agent and specialist security questions when required.

## Elegance by level

- **Junior:** readable and unsurprising.
- **Middle:** concise, composable and idiomatic.
- **Senior:** structurally minimal, explicit about invariants and boundaries, and elegant without hiding operational complexity.

---

See also: [Patterns and Strategies](PATTERNS_AND_STRATEGIES.md) · [Olympiad Elegance](OLYMPIAD_ELEGANCE.md)
