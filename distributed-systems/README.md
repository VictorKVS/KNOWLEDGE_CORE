# Distributed Systems Engineering

Distributed systems are introduced only when the problem actually requires distribution.

## Admission questions

- What cannot be solved inside one process or one deployable unit?
- Is independent scaling required?
- Are there organizational or trust boundaries?
- What availability or locality requirement forces distribution?
- What consistency model is acceptable?
- What happens during network delay, duplication, partition or partial failure?

## Required concepts

- idempotency;
- retries and retry budgets;
- timeouts and deadlines;
- duplicate delivery;
- ordering;
- consistency and convergence;
- leader/coordination assumptions;
- queues and backpressure;
- partial failure;
- clock/time assumptions;
- schema and protocol evolution;
- migration and rollback.

## Default rule

Do not distribute a system because microservices are fashionable. Distribution must pay for its own operational, testing, security and observability costs.

## Level interpretation

**Junior:** consume established distributed interfaces correctly.  
**Middle:** design reliable component-to-component interactions with timeouts, idempotency and failure handling.  
**Senior:** challenge the need for distribution, define consistency/failure semantics and minimize irreversible coupling.

← [Engineering Knowledge](../README.md)
