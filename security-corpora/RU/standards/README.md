# Russian standards in the knowledge base

This directory contains searchable knowledge records for GOST, GOST R, PNST and related standards.
It does not contain acquired full-text PDFs.

## Layout

```text
security-corpora/RU/standards/
  information-security/
    SEC-STD-RU-GOST-R-53114-2008.yaml
  software-security/
    SEC-STD-RU-GOST-R-56939-2024.yaml

_LOCAL_SOURCE_PACK/standards/       # ignored by Git
  originals/                        # PDF, ODT, RTF or XML
  ocr/                              # OCR output for local indexing
```

Create one YAML record for each specific edition. Use
`templates/security-standard-source.yaml`. A replacement or amendment is a separate record linked
through `replaces` and `replaced_by`; never overwrite the historical edition.

## What is committed

- designation, canonical title, issuer and dates;
- official catalogue and information links;
- SHA-256 of the local original;
- lifecycle status and replacement relations;
- original abstracts, applicability notes, clause locators and concise summaries;
- crosswalks to laws, regulator requirements and security controls.

## What stays local

- acquired full-text PDF/ODT/RTF/XML files;
- page images and OCR dumps;
- books, commentaries and third-party compilations;
- any complete text whose redistribution basis has not been recorded.

The local file path is only a hint. Integrity is established by SHA-256, so a renamed local file does
not create a second standard record.
