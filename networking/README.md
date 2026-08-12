# Networking Engineering Knowledge

Networking decisions must be based on communication semantics, trust boundaries, latency, reliability and protocol requirements.

## Core questions

- Who communicates with whom?
- Across which trust boundary?
- What authentication and authorization are required?
- What latency and throughput matter?
- How are retries, timeouts and backpressure handled?
- Can requests be duplicated, reordered or lost?
- What observability is required?
- Which standards/RFCs define the protocol behaviour?

## Initial decision families

- HTTP request/response vs streaming vs messaging;
- TCP vs UDP where the application legitimately controls transport choice;
- REST vs RPC-style protocols;
- polling vs push/subscription;
- persistent vs short-lived connections;
- public endpoint vs private network boundary;
- direct service communication vs gateway/proxy/broker.

## Security and resilience

Every network decision should consider TLS, identity, authorization, replay, input framing, size limits, timeout budgets, retry storms, rate limiting, connection exhaustion and denial-of-service behaviour.

← [Engineering Knowledge](../README.md)
