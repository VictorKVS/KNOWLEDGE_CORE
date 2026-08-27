# FATHER Agent Factory — Layer 1: Technical Book Translator

Status: M1 IMPLEMENTED / PILOT READY

## Purpose

This is the first production layer of the FATHER Agent Factory: a local, evidence-preserving EN→RU translator for high-value professional books before they enter the Knowledge Factory.

Initial domain priority:

1. software/system/solution architecture;
2. programming and software engineering;
3. information security / AppSec / DevSecOps / KII / privacy;
4. cloud, SRE, DevOps, distributed systems;
5. data/AI/ML when directly related to engineering practice.

The translator is not the analyst. Its job is to produce a faithful Russian working copy while preserving the English original and technical terminology so the downstream analyst can reason from both.

## Canonical pipeline

```text
BOOK ORIGINAL
  -> identity + SHA-256
  -> text extraction
  -> language/domain detection
  -> structural segmentation
  -> shared EN<->RU glossary
  -> first-pass translation
  -> independent QA/reviewer pass
  -> deterministic QA checks
  -> bilingual artifact
  -> translation memory
  -> READY_FOR_KNOWLEDGE_EXTRACTION
  -> FATHER Knowledge Factory / Chief Analyst
```

## Non-negotiable rules

- Never overwrite, move or delete the source book.
- Preserve source SHA-256 and source path in the local manifest.
- Keep `ORIGINAL`, `TRANSLATION`, and `KNOWLEDGE` as separate layers.
- Preserve code, API names, identifiers, config keys, URLs, formulas and numeric values.
- Do not "improve" the author's claim during translation.
- Ambiguous terms remain explicitly ambiguous; do not manufacture precision.
- One shared glossary is used across all workers and all chapters of a book.
- Every translated chunk is traceable to a source chunk hash and source book hash.
- Full copyrighted books and translations remain local. The public repository stores only factory code, schemas, configuration and non-copyrighted metadata.

## Quality model

For each chunk the factory records:

- `source_chunk_sha256`;
- translator model;
- reviewer model;
- glossary version;
- deterministic QA result;
- reviewer verdict;
- issues/corrections;
- final status.

Promotion statuses:

```text
EXTRACTED
TRANSLATED_DRAFT
QA_REVIEW_REQUIRED
QA_PASSED
READY_FOR_KNOWLEDGE_EXTRACTION
BLOCKED
```

A chunk is not promoted merely because two models agree. It must retain source evidence and pass deterministic integrity checks.

## Local runtime

Default local output root:

```text
G:\1\FATHER_TRANSLATION_FACTORY
```

Recommended local subtrees:

```text
inventory\
queue\
original_text\
translated\
translation_memory\
reports\
logs\
```

These are runtime artifacts and should not be committed to the public repository.

## Local LLM interface

The M1 runner uses an OpenAI-compatible local endpoint. Defaults can be overridden with environment variables:

```text
FATHER_LLM_BASE_URL=http://127.0.0.1:8080/v1/chat/completions
FATHER_TRANSLATOR_MODEL=local-model
FATHER_REVIEWER_MODEL=local-model
FATHER_TRANSLATION_WORKERS=4
FATHER_TRANSLATION_QA=1
```

The model router is intentionally externalized: the same factory can benchmark Qwen, GigaChat and other local models without changing book provenance or output contracts.

## Modes

From `scripts`:

```text
RUN_FATHER_TRANSLATION_FACTORY.cmd plan
RUN_FATHER_TRANSLATION_FACTORY.cmd pilot
RUN_FATHER_TRANSLATION_FACTORY.cmd run
```

- `plan`: inventory/classification only, no LLM calls.
- `pilot`: translate the highest-priority eligible English book, limited to a small initial chunk set.
- `run`: process the eligible queue.

## Extractors

M1 supports text/Markdown/HTML directly and uses optional local Python packages for common book formats:

- PDF: `pypdf`
- DOCX: `python-docx`
- EPUB: `ebooklib` + `beautifulsoup4`

Install with `scripts/INSTALL_FATHER_TRANSLATION_DEPS.cmd`.

## Acceptance gate for Layer 1 M1

M1 is accepted when one real English technical book can complete this path:

```text
source file
-> SHA-256
-> extracted text
-> domain/language classification
-> chunk queue
-> translation
-> reviewer pass
-> deterministic QA
-> bilingual Markdown
-> manifest + translation memory
```

without changing the original file and with every output traceable back to the original SHA-256.
