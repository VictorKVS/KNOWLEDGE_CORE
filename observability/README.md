# Observability Engineering

Observability is part of program design, not an afterthought added after deployment.

## Core questions

- Which failures must operators be able to distinguish?
- Which state transitions matter?
- What latency, throughput, saturation or error signals determine health?
- Which identifiers are needed to trace one request or job safely?
- What information must never be logged?
- Which signals are actionable rather than merely available?

## Signal families

- structured logs;
- metrics;
- traces;
- health/readiness signals;
- audit events;
- domain-specific business or workflow signals.

## Design rules

- instrument important boundaries and failure paths;
- preserve correlation without leaking secrets or sensitive data;
- prefer structured, queryable events over prose-only logging;
- distinguish expected domain failures from system failures;
- expose queue depth/saturation when bounded work can accumulate;
- make timeouts, retries and fallback behaviour observable;
- avoid high-cardinality or unbounded labels without explicit justification.

## Level interpretation

**Junior:** use existing logging/metrics conventions and do not leak sensitive data.  
**Middle:** define useful component-level diagnostics and correlation.  
**Senior:** design observability around failure hypotheses, operational decisions, incident response and cost.

← [Engineering Knowledge](../README.md)
