# Reliability Engineering Knowledge

Reliability knowledge describes how systems fail, recover and degrade under realistic operating conditions.

## Core questions

- What can fail?
- How is failure detected?
- What is the acceptable blast radius?
- What data may be lost?
- What are the recovery objectives?
- What dependencies can become unavailable or slow?
- What should degrade gracefully?
- Which failure assumptions have actually been tested?

## Initial decision families

- fail-fast vs retry vs fallback;
- bounded retry with jitter vs no retry;
- circuit breaker vs direct propagation;
- active/passive vs active/active redundancy;
- graceful degradation vs hard failure;
- synchronous replication vs asynchronous replication;
- local buffering vs dropping vs backpressure.

## Required evidence

Reliability claims should prefer fault-injection results, restore tests, incident history, load tests, controlled experiments and documented guarantees over optimistic architecture diagrams.

← [Engineering Knowledge](../README.md)
