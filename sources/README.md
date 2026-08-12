# Sources & Evidence

This directory is the provenance layer of Engineering Knowledge.

A source is not stored merely because it is interesting. It is stored because it can support, contradict, refine or supersede a concrete engineering claim or decision.

## Evidence chain

```text
Source
  ↓
Claim
  ↓
Applicability
  ↓
Alternative comparison
  ↓
Decision
  ↓
Implementation
  ↓
Tests / Benchmark / Security Review
  ↓
Decision Memory
```

## Source classes

Preferred order depends on the question, but critical technical claims should normally prioritize:

1. specifications, standards and RFCs;
2. official language/runtime/library documentation;
3. peer-reviewed papers and recognized academic publications;
4. authoritative books and conference material;
5. vendor engineering reports with clear methodology;
6. independent reproducible benchmarks and engineering reports;
7. community material as supporting context or hypotheses.

Popularity is not an evidence tier.

## Required provenance

Every reusable source record should identify, where applicable:

- authors or responsible organization;
- publication or issuing body;
- year / edition / version;
- DOI, ISBN, RFC, standard or official identifier;
- canonical URL;
- date checked;
- scope and version applicability;
- whether the source is primary, peer reviewed or reproducible;
- known limitations;
- whether it has been superseded or withdrawn.

## Claim-level evidence

Sources do not directly become decisions. They support explicit claims stored as `CLM-*` records.

Example relationship:

```text
SRC-0012 ──supports──► CLM-0041
SRC-0048 ─contradicts─► CLM-0041
CLM-0041 ──used-by──► ADR-0023
BENCH-009 ─measures──► ADR-0023
```

A decision should be able to expose both supporting and conflicting evidence rather than hiding disagreement.

## Staleness

Version-sensitive material must be revalidated when the relevant language, compiler, runtime, library, protocol or operating environment changes materially.

A stale source may remain historically useful but must not silently remain authoritative for a current FAST PATH decision.

## Copyright and local storage

The knowledge base should prefer bibliographic metadata, lawful links, summaries, derived claims and permitted excerpts rather than becoming a dump of copyrighted books or articles.

← [Engineering Knowledge](../README.md)
