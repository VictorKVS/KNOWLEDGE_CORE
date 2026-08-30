# FATHER Library Probe V2 — acceptance baseline

Date: 2026-08-30
Status: LOCALLY EXECUTED / USER-PROVIDED TELEMETRY / ACCEPTED FOR STAGE-3 ROUTING

## Measured result

- records_total: 1354
- canonical_records_probed: 1036
- duplicate_aliases_skipped: 318
- elapsed_seconds: 456.811
- file_errors_total: 0

Probe statuses:
- IDENTIFIED: 512
- UNRESOLVED: 343
- OCR_REQUIRED: 122
- DUPLICATE_ALIAS: 318
- REVIEW_REQUIRED: 28
- PDF_REPAIR_REQUIRED: 8
- PRIVATE_REVIEW: 23

Verified types:
- BOOK: 406
- STANDARD: 88
- LAW: 22
- GOVERNMENT_DECREE: 27
- AGENCY_ORDER: 7
- UNRESOLVED: 486
- DUPLICATE_ALIAS: 318

## QA conclusions

1. Exact duplicate routing is internally consistent: Scan-01 reported 533 file instances in 215 duplicate groups. Keeping one canonical occurrence per group implies 533 - 215 = 318 aliases, exactly matching Probe V2.
2. Regulatory false positives were materially reduced: LAW classification dropped from 344 in Probe V1 to 22 in V2 after changing to precision-first title/header evidence.
3. Broken PDFs are isolated as PDF_REPAIR_REQUIRED instead of being silently classified from weak filename evidence.
4. Image-only/insufficient-text PDFs are isolated as OCR_REQUIRED.
5. SOURCE_OCCURRENCE_ID and CONTENT_ID are now separated conceptually: one identifies a concrete path, the other byte-identical content.
6. No source originals were moved, renamed, deleted, uploaded or modified.

## Measured performance comparison

Probe V1 elapsed: 568.325 s
Probe V2 elapsed: 456.811 s
Elapsed reduction V2 vs V1: 19.62%
Registry throughput V1: 2.38 records/s
Registry throughput V2: 2.96 records/s
Throughput increase V2 vs V1: 24.41%

Important: this is V1-vs-V2 measured runtime comparison, not a one-stream parallelism baseline. speedup_vs_1_stream remains N/A.

## Promotion gate

Only these records may enter Stage 3 automatic routing:
- probe_status = IDENTIFIED
- verified_type in {LAW, GOVERNMENT_DECREE, AGENCY_ORDER, STANDARD, BOOK}

Quarantine:
- REVIEW_REQUIRED
- OCR_REQUIRED
- PDF_REPAIR_REQUIRED
- PRIVATE_REVIEW
- UNRESOLVED
- DEPENDENCY_MISSING / EXTRACT_FAILED if present

DUPLICATE_ALIAS records never re-enter expensive extraction. They retain lineage to canonical CONTENT_ID / canonical occurrence.

## Stage 3 target

Create authoritative processing lanes:

LEGAL -> authority/applicability/version metadata -> atomic legal norms -> crosswalk
STANDARD -> clauses/requirements/processes/artifacts/verification methods -> crosswalk
BOOK -> metadata/language/rights -> translation if needed -> concepts/patterns/trade-offs -> crosswalk

No knowledge node reaches KB_READY without evidence and review gates.
