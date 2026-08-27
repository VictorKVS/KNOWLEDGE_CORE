# RU standards intake for Security Knowledge

This directory is the source-registration layer for Russian security standards admitted into the Security Knowledge pipeline.

## Separation of layers

1. **Local/source artifact** — the user's original PDF/RTF/etc. on the workstation.
2. **Identity/provenance registry** — designation, local path, size, known hash, source/status evidence.
3. **Verified source text** — exact text acquired from a lawful/authoritative source or a verified local artifact.
4. **Derived knowledge** — definitions, requirements, methods, controls, checks and relations extracted with exact anchors.

A registry entry is not itself the full text of a standard and does not prove legal applicability.

## Public repository rule

`VictorKVS/KNOWLEDGE_CORE` is public. Full GOST texts are not republished here merely because a local or third-party copy exists. This repository may store metadata, provenance, currentness evidence and derived knowledge. Any raw-text publication must pass a separate rights/source gate.

## Promotion gates

- Local filename match -> `REGISTERED_SOURCE_TEXT_EXTRACTION_PENDING`.
- Exact artifact identity requires SHA-256 or equivalent byte evidence.
- Currentness is verified separately against Rosstandart/protect.gost.ru.
- Currentness does **not** imply applicability.
- Atomic requirements are created only from verified source text with exact anchors under `.ai/regulatory-extraction-policy.yaml`.
- Ambiguous or conflicting variants remain under review; no preferred copy is selected silently.

## Current intake

The 2026-08-27 local intake is recorded in `gost-local-source-registry-2026-08-27.yaml`. It represents the standards found in the user-supplied local library inventory and intentionally does not copy the underlying GOST files into this public repository.
