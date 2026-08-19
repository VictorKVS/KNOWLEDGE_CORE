# Russian Personal Data Knowledge Library (152-FZ)

**Library ID:** `RU-PDN-LIB-0001`  
**Status:** ACTIVE / EXPANDING / FAIL-CLOSED  
**Purpose:** build a complete, measurable source universe for Russian personal-data compliance around Federal Law No. 152-FZ, then map every source to atomic requirements, applicability, roles, deadlines, evidence, consequences, regression tests and sector overlays.

## Why this library exists

The Personal Data corpus is not equal to one law. A working consultant must route through general 152-FZ duties, Roskomnadzor supervisory acts, Government decrees, FSTEC/FSB security requirements, incident reporting, destruction/harm evidence, cross-border rules, labor law, biometrics, liability and sector-specific legal bases.

The library therefore separates:

1. `RKN_CONTROL_CORE` — acts explicitly listed by Roskomnadzor in the current mandatory-requirements list.
2. `GENERAL_IMPLEMENTATION_CORE` — cross-sector implementation acts required to operationalize 152-FZ.
3. `SECURITY_TECHNICAL_CORE` — ISPDN, threat modeling, FSTEC/FSB and cryptographic controls.
4. `INCIDENT_AND_EVIDENCE` — incidents, notification, harm, destruction and proof.
5. `SPECIAL_PROCESSING_REGIMES` — anonymization, dissemination consent, cross-border, biometrics and other special regimes.
6. `LIABILITY_AND_REMEDIES` — KoAP, Criminal Code, Civil Code and Labour Code consequence routes.
7. `SECTOR_OVERLAYS` — medicine, finance, telecom, education, public sector, transport, insurance, biometrics and other sectors where special law changes purpose, legal basis, data composition, recipients or retention.

## Required source state machine

`DISCOVERED -> REGISTERED -> PRIMARY_WEB_VERIFIED -> PRIMARY_IMMUTABLE -> ATOMIZED -> EXECUTABLE -> REGRESSION_PROTECTED -> EXPERT_REVIEWED`

A source may remain `AUTHORITATIVE_SECONDARY` when primary bytes are unavailable. No source is promoted by inference.

## Current control anchor

The Roskomnadzor mandatory-requirements list approved on 2025-12-16 contains seven acts for federal supervision over personal-data processing: Federal Law 79-FZ, Federal Law 152-FZ, the Labour Code, Government Decree 211, Government Decree 687, Roskomnadzor Order 140/2025 and Roskomnadzor Order 18/2021. This seven-act list is a **supervisory core**, not the complete implementation universe of a personal-data operator.

## Coverage dimensions

Every source receives at least:

- stable `PDN-SRC-*` identifier;
- regulator/authority;
- legal type and number;
- current/special/historical scope;
- general or sector applicability;
- source/provenance tier;
- repository binding where already modeled;
- atomization state;
- executable/regression state;
- dependencies and supersession notes;
- next evidence action.

## Core decision chain

`ORGANIZATION -> PROCESS -> PURPOSE -> SUBJECT -> DATA -> LEGAL_BASIS -> OPERATION -> SYSTEM/ISPDN -> APPLICABILITY -> REQUIREMENT -> CONTROL -> ROLE -> DEADLINE -> EVIDENCE -> FINDING -> CONSEQUENCE -> REMEDIATION`

## Sector discovery program

The library will be expanded by independent sweeps for at least:

- employment/HR;
- healthcare and medical secrecy;
- finance/banking/payment/AML;
- insurance;
- telecom and communications secrecy;
- education/minors;
- state and municipal services;
- biometrics/EBS;
- transport;
- advertising/marketing;
- archives and statutory retention;
- credit histories;
- KII/GosSOPKA overlap;
- cloud/SaaS/processors and cross-border recipients.

A sector is not marked complete until its discovery query set, regulator catalog, primary acts, amendments, lifecycle and at least one reviewed organization case have passed a red-team replay.

## Measurement

The exact counts in `pdn-master-source-library-v1.yaml` are authoritative for this library. Estimates from chat or memory are forbidden once a source has entered the library.
