# Language Selection: Python vs Go vs C++

The repository does not assign a universal ranking to languages. A language is selected from constraints, evidence and operational context.

## Decision sequence

```text
Problem
  ↓
Hard constraints
  ↓
Required ecosystem / interoperability
  ↓
Safety and security boundary
  ↓
Latency / throughput / resource needs
  ↓
Concurrency and lifecycle model
  ↓
Deployment / operations constraints
  ↓
Team and maintenance constraints
  ↓
Candidate languages
  ↓
Evidence / prototype / benchmark when needed
  ↓
Decision
```

## Default reasoning

### Prefer Python as a candidate when

The dominant need is orchestration, AI/data ecosystem integration, automation, research, rapid backend/product iteration or glue code, and the workload does not justify a lower-level component.

### Prefer Go as a candidate when

The dominant need is a compiled operational service, networking, collectors, infrastructure tooling, bounded concurrency or simple deployment, and low-level native control is not the primary constraint.

### Prefer C++ as a candidate when

The problem materially requires native integration, systems-level control, tight resource/performance constraints or a native algorithmic component, and the additional complexity and safety burden can be justified and verified.

These are **candidate-generation rules, not conclusions**.

## Cross-language architecture is allowed

The smallest reliable system may use more than one language. A typical split can be:

```text
Python  → orchestration / AI / control plane
Go      → network services / collectors / operational tooling
C++     → native performance-critical or low-level components
```

A multi-language design is accepted only when the boundary pays for its added build, testing, observability, deployment and security complexity.

## Mandatory questions

Before choosing a language, record:

- hard functional constraints;
- expected workload and scale;
- latency/throughput requirements if they matter;
- trust boundary and security risk;
- memory/resource constraints;
- concurrency model;
- deployment target;
- required libraries/platform APIs;
- maintenance horizon;
- interoperability cost;
- evidence state of any performance claim.

## Anti-patterns

Do not choose a language because:

- it is the author's favorite;
- it is fashionable;
- the model remembers more examples in it;
- a single microbenchmark won;
- "everybody uses it";
- rewriting sounds cleaner than improving the existing system.

## Evidence rule

If two candidates remain plausible and the decision matters, create an ADR and, where relevant, a bounded prototype or benchmark. Keep the conclusion scoped to the measured workload and environment.

← [Languages](README.md)
