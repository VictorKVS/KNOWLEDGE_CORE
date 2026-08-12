# Evidence Claims

`CLM-*` records are the smallest reusable units of technical assertion in Engineering Knowledge.

A claim must be narrow enough to verify, contradict, version, measure or supersede independently.

Good claim:

> For workload X under environment Y, strategy A has lower measured lookup latency than strategy B.

Weak claim:

> A is faster.

## Lifecycle

```text
DRAFT
  ↓
EVIDENCE ATTACHED
  ↓
REVIEWED
  ↓
USED BY DECISION
  ↓
REVALIDATED / SUPERSEDED / STALE
```

## Evidence states

- `DOCUMENTED` — supported by applicable documentation/specification/research.
- `MEASURED` — supported by a recorded benchmark or experiment with environment metadata.
- `DERIVED` — logically derived from explicit premises and evidence.
- `EXPERT_ESTIMATE` — useful professional judgement, visibly marked as such.
- `UNKNOWN` — insufficient evidence.

A claim may have both supporting and contradicting evidence. This is expected and must not be erased merely to make selection easier.

## Agent use

Agents should retrieve claims before raw documents where a reviewed claim already exists, then follow references to the source or measurement when confidence, version applicability or disagreement matters.

This keeps the common path fast while preserving the ability to reconstruct the evidence chain.

← [Sources & Evidence](../sources/README.md) · [Engineering Knowledge](../README.md)
