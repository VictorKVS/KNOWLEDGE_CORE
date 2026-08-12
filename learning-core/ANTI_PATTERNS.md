# Programming Anti-Patterns

Anti-patterns are stored as context-dependent failure modes, not slogans.

## Core anti-pattern families

### Accidental complexity
- premature abstraction;
- wrapper layers with no policy value;
- factories for objects with no construction variability;
- inheritance used only to share code;
- configuration systems more complex than the application.

### Cleverness debt
- compressed control flow;
- unexplained bit tricks outside justified hot paths;
- one-liners hiding multiple state transitions;
- relying on language corner cases for routine logic;
- contest-style global state in production code.

### Performance folklore
- optimizing before measurement;
- replacing library primitives with custom code without evidence;
- microbenchmark conclusions applied to a different workload;
- cache introduction without invalidation and memory-cost analysis.

### Reliability mistakes
- unbounded queues;
- infinite retries;
- swallowed errors;
- missing timeout/cancellation paths;
- hidden partial failure;
- non-idempotent retryable operations.

### Security mistakes
- trusting input because it came from an internal service;
- custom cryptography where vetted primitives exist;
- secrets in source or logs;
- excessive privileges;
- dependency addition without provenance or maintenance review.

## Anti-pattern record rule

Every anti-pattern should capture:
- context where it appears;
- why it is attractive;
- failure mechanism;
- symptoms;
- safer alternatives;
- evidence or incident references;
- cases where the technique is actually valid.

The goal is not to ban techniques universally. The goal is to teach the agent to recognize when a useful technique has crossed into harmful use.
