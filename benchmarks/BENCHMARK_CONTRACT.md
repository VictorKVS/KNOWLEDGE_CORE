# Benchmark Contract

Benchmarks in Engineering Knowledge are evidence objects, not decorative speed claims.

## Required benchmark metadata

Every benchmark must record:

- benchmark ID;
- linked knowledge/decision IDs;
- task definition;
- dataset shape and size;
- input generation method;
- language and compiler/runtime version;
- operating system and architecture;
- hardware relevant to the result;
- warm-up policy;
- iteration count;
- timing method;
- memory measurement method when relevant;
- correctness check;
- result distribution, not only a single best number;
- date of measurement;
- known limitations.

## Evidence rule

A benchmark result must be marked **MEASURED** and is only valid for the recorded environment and workload. It must not be generalized to unrelated workloads without additional evidence.

## Cross-language comparison

Python, Go and C++ implementations must solve the same logical problem and consume equivalent input data. Language-specific optimizations are allowed only when they preserve the task contract and are documented.

## Security and reliability checks

Where relevant, benchmark runs should also include:

- pathological inputs;
- large-input resource limits;
- malformed input handling;
- overflow/underflow boundaries;
- timeouts or cancellation behaviour;
- memory exhaustion risks.

## Minimal benchmark record

```yaml
id: BENCH-XXXX
linked_ids: []
status: planned

task:
  description: ""
  input_profile: ""

environment:
  os: ""
  architecture: ""
  cpu: ""
  memory: ""
  runtime_or_compiler: ""
  version: ""

method:
  warmup: ""
  iterations: 0
  timer: ""
  correctness_check: ""

results:
  median: null
  p95: null
  memory_peak: null
  evidence_type: MEASURED

limitations: []
```

← [Engineering Knowledge](../README.md)
