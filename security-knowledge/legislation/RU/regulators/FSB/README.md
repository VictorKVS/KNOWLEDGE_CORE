# FSB regulatory corpus

This branch stores FSB regulatory knowledge relevant to information security, cryptographic protection, critical information infrastructure, GosSOPKA and computer-incident coordination.

## P0 ingestion order

1. FSB-117-2025 — cryptographic protection of information in specified government information systems.
2. FSB-539-2025 — obtaining information about means/methods of attacks and methods of prevention/detection.
3. FSB-546-2025 — exchange of attack/incident information.
4. FSB-547-2025 — informing FSB, response and consequence elimination.
5. FSB-548-2025 — continuous interaction with GosSOPKA.
6. FSB-553-2025 — installation and operation conditions for attack-detection/response means.
7. FSB-554-2025 — requirements for those means.
8. FSB-540-2025 + FSB-366-2018 — NCCC/NKTsKI governance chain.
9. Legacy crypto acts, including FSB-378-2014, only after current-status verification.

## Processing model

`OFFICIAL SOURCE -> VERSION -> STRUCTURE -> CHUNKS -> DEFINITIONS -> ATOMIC REQUIREMENTS -> APPLICABILITY -> WORKFLOW -> CHECKLIST -> EVIDENCE -> CROSS-LINKS -> EXPERT REVIEW`

## Required cross-links

- Federal Law 187-FZ and its current obligations;
- Presidential Decree 250 and related governance requirements where applicable;
- FSTEK 235/239 for significant CII objects;
- incident-response and GosSOPKA processes;
- cryptographic controls and later FSB-certified/approved product/certificate registries;
- organizational roles, notification deadlines, channels, evidence and retest/verification artifacts.

## Quality barrier

A legacy act or secondary citation is not sufficient for VERIFIED status. Exact source/version/status must be confirmed against an authoritative source. If current status cannot be established, the node remains STATUS_PENDING and downstream rules inherit that uncertainty.
