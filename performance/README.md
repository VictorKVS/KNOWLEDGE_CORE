# Performance Engineering Knowledge

Performance decisions are measurement-driven and workload-specific.

## Core questions

- What latency or throughput target actually matters?
- Where is time or memory spent?
- Is the bottleneck CPU, memory, I/O, network, lock contention or dependency latency?
- What percentile matters: median, p95, p99 or worst-case bound?
- Does optimization change correctness, security or maintainability?
- Are setup and steady-state costs separated?

## Initial decision families

- optimize algorithm vs implementation detail;
- cache vs recompute;
- batch vs individual operations;
- copy vs reference/view where safe;
- synchronous vs concurrent execution;
- local work vs remote call;
- interpreted/orchestrated component vs compiled/native component.

## Measurement rule

No production performance claim becomes `MEASURED` without workload definition, environment metadata, correctness verification, repeated runs and recorded dispersion. Microbenchmark winners do not automatically become production choices.

← [Engineering Knowledge](../README.md)
