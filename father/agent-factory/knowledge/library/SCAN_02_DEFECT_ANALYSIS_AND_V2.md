# FATHER Library — Stage 2 defect analysis and V2 remediation

Date: 2026-08-30

## Observed Stage-2 result

- records_total: 1354
- IDENTIFIED: 1143
- OCR_REQUIRED: 141
- UNRESOLVED: 32
- PRIVATE_REVIEW: 38
- BOOK: 765
- LAW: 344
- STANDARD: 40
- GOVERNMENT_DECREE: 25
- AGENCY_ORDER: 6
- file_errors_total: 0
- elapsed_seconds: 568.325

## Defects found

### D1 — Regulatory over-classification
The V1 classifier treated any occurrence of `Федеральный закон`, `NN-ФЗ`, `ГОСТ`, etc. anywhere in the bounded probe text as strong evidence that the entire source was a law or standard. Technical/legal books often cite laws and standards, so this produced an implausible inflation from Scan-01 `LAW=37` to Probe-V1 `LAW=344`.

**Remediation:** V2 is precision-first. Strong regulatory classification requires filename/header/official-form evidence. Deep body citations are weak evidence only.

### D2 — Broken PDF handling
V1 could receive pypdf parse errors (`invalid pdf header`, `EOF marker not found`) and still fall through to filename/fallback classification.

**Remediation:** V2 routes extractor errors to `PDF_REPAIR_REQUIRED` (PDF) or `EXTRACT_FAILED` (other formats). Image-only / insufficient-text PDFs route to `OCR_REQUIRED`.

### D3 — Duplicate identity collision
Scan-01 legacy `source_id` was SHA-derived. Exact byte duplicates therefore shared the same `source_id`. Probe-V1 selected a canonical duplicate by `source_id`, so duplicate aliases could not be distinguished and were re-read.

**Remediation:** V2 introduces two identities:

- `SOURCE_OCCURRENCE_ID` — concrete library occurrence/path;
- `CONTENT_ID` — byte-identical content identity derived from SHA-256.

Duplicate canonicalization is performed by concrete `relative_path` inside each SHA duplicate group.

## V2 acceptance gate

Do not start legal analysis or book knowledge extraction until V2 demonstrates:

1. duplicate aliases are actually skipped;
2. law/standard counts are plausible against Scan-01 and the Stage1↔Stage2 crosswalk;
3. broken PDFs are isolated from semantic queues;
4. OCR candidates are isolated;
5. ambiguous classifications route to `REVIEW_REQUIRED` rather than being promoted automatically;
6. originals remain unchanged.

## Production statistics

No speedup-vs-1-stream percentage or ETA is claimed because no measured one-stream baseline exists for this workload.
