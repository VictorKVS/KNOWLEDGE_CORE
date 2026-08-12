# Languages

This layer contains language-specific engineering knowledge for **Python, Go and C++**.

The goal is not to teach syntax in isolation. It is to help an engineer or agent choose a construct, implementation strategy or language boundary from the actual problem constraints and evidence.

## Shared decision model

Every important language choice should answer:

- what problem is being solved;
- which constraints are hard requirements;
- which alternatives are viable;
- when the construct/language should be used;
- when it should be avoided;
- what performance, reliability, maintenance and security costs exist;
- which claims are documented, measured, derived or still unknown;
- whether another language or a mixed-language boundary is more appropriate.

## Engineering maps

- [Python](python/README.md) · [`LANG-PY-001`](python/topic-map.yaml)
- [Go](go/README.md) · [`LANG-GO-001`](go/topic-map.yaml)
- [C++](cpp/README.md) · [`LANG-CPP-001`](cpp/topic-map.yaml)
- [Python vs Go vs C++ — selection framework](LANGUAGE_SELECTION.md)

## Shared topic model

Each language progressively covers numeric/data types, collections, memory and lifetime, error handling, concurrency, networking/I/O, testing, performance, security, build/deployment, production pitfalls, typical problem classes and cross-language alternatives.

## Agent path

```text
Task
  ↓
Decision Memory
  ↓
Language Topic Map
  ↓
Verified Claims / Sources
  ↓
Benchmark or Prototype if needed
  ↓
Language / Boundary Decision
  ↓
ADR + Tests + Security Review
```

Machine policy: [`.ai/language-selection-policy.yaml`](../.ai/language-selection-policy.yaml)

The language is never selected because it is fashionable, familiar to the model or the winner of an unrelated microbenchmark.

[← Engineering Knowledge root](../README.md)
