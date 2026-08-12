# Concurrency Engineering

Concurrency knowledge is treated as a decision problem, not as a catalogue of primitives.

## Core questions

- Is concurrency needed at all?
- Is the workload CPU-bound, I/O-bound or latency-sensitive?
- What state is shared?
- What ordering guarantees matter?
- What cancellation, timeout and backpressure behaviour is required?
- What failure happens when work is duplicated, delayed or partially completed?
- Is concurrency local to one process or distributed across services?

## Strategy families

- sequential execution;
- asynchronous I/O;
- threads;
- processes;
- goroutines/tasks;
- worker pools;
- actor/message-passing styles;
- lock-based shared state;
- lock-free/atomic approaches where justified;
- batching and pipelines.

## Default rule

Prefer the lowest concurrency complexity that satisfies throughput and latency requirements. Concurrency is not a free performance upgrade: it adds scheduling, coordination, cancellation, testing and failure complexity.

## Required review

Any non-trivial concurrency choice should document:

- ownership of mutable state;
- synchronization strategy;
- cancellation path;
- boundedness/backpressure;
- timeout behaviour;
- deadlock/livelock/starvation risks;
- race testing where tooling exists;
- observability for stuck or saturated work.

## Level interpretation

**Junior:** use an established project primitive safely.  
**Middle:** choose a bounded local concurrency pattern and test edge cases.  
**Senior:** question whether concurrency belongs here at all, define ownership/backpressure/failure semantics and minimize coordination cost.

← [Engineering Knowledge](../README.md)
