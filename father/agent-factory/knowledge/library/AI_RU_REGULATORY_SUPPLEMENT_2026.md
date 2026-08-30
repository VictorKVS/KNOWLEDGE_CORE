# AI RU Regulatory Supplement — 2026

Status: curated supplement to FATHER legal/standards backbone.  
Purpose: reconcile the user-provided historical AI regulatory compilation with current official-source checks.  
Rule: the historical compilation is a candidate source only; no item becomes a binding requirement without official-source/currentness/applicability verification.

## 1. Direct AI legal core — priority P0

| ID | Instrument | Role in FATHER | Verification |
|---|---|---|---|
| AI-LEGAL-001 | Presidential Decree 490 of 10.10.2019, AI development / National AI Strategy to 2030 | strategic root for AI policy and terminology | official publication confirmed |
| AI-LEGAL-002 | Presidential Decree 124 of 15.02.2024 amending Decree 490 and the National AI Strategy | current strategic update; adds trusted AI, generative models, regulation and safety directions | Kremlin/official source confirmed |
| AI-LEGAL-003 | Federal Law 123-FZ of 24.04.2020, Moscow AI special-regulation experiment | direct AI experimental regulation; intersects personal-data law | official publication confirmed |
| AI-LEGAL-004 | Federal Law 258-FZ of 31.07.2020, experimental legal regimes in digital innovation | general EPR legal framework | official publication confirmed |
| AI-LEGAL-005 | Federal Law 331-FZ of 02.07.2021 | supporting amendments connected with 258-FZ | official publication confirmed |
| AI-LEGAL-006 | Federal Law 169-FZ of 08.07.2024 | amendment lineage for 258-FZ | official publication confirmed |
| AI-LEGAL-007 | Federal Law 233-FZ of 08.08.2024 | amendments to 152-FZ and the Moscow AI experiment law 123-FZ | official publication confirmed |
| AI-LEGAL-008 | Federal Law 336-FZ of 31.07.2025 | latest identified amendment lineage for experimental legal regimes | official publication confirmed |
| AI-LEGAL-009 | Ministry of Economic Development Order 725 of 19.11.2024 | registry of IP results created including with AI inside EPR | official publication / registration confirmed |
| AI-LEGAL-010 | Ministry of Economic Development Order 752 of 26.11.2024 | investigation of harm caused by AI solutions in EPR | official publication / registration confirmed |

### Required graph lineage

`DECREE_490_2019 -> AMENDED_BY -> DECREE_124_2024`

`LAW_258_2020 -> AMENDED_BY -> LAW_331_2021 / LAW_169_2024 / LAW_336_2025`

`LAW_123_2020 <-> INTERSECTS -> LAW_152_PDN`

`LAW_123_2020 -> AMENDED_BY -> LAW_233_2024`

`LAW_258_2020 -> IMPLEMENTED_BY -> ORDER_725_2024 / ORDER_752_2024`

## 2. AI strategy requirements that matter to FATHER

Decree 124/2024 is especially relevant because the updated National AI Strategy:
- treats an AI model as software or a software component;
- introduces concepts related to large generative models, datasets and trusted AI;
- calls for trusted AI in areas where harm to national security is possible;
- calls for a comprehensive regulatory framework for AI development/use and safety;
- calls for trusted software for development of safe and functionally effective AI solutions using common open standards;
- explicitly addresses developer access to datasets/industrial data and boundaries of responsibility for large generative models.

These are strategic/policy requirements, not automatically product-level binding controls. They should enter FATHER as `STRATEGIC_REQUIREMENT` and be connected to binding NPA/GOST/control nodes where a legal basis exists.

## 3. High-value AI engineering standards — current status checked

| ID | Standard | Current status | FATHER use |
|---|---|---|---|
| AI-STD-001 | GOST R 71476-2024, Artificial intelligence. Concepts and terminology | ACTIVE | canonical RU AI glossary / ontology seed |
| AI-STD-002 | GOST R 71539-2024 (ISO/IEC 5338:2023), AI system lifecycle processes | ACTIVE from 01.01.2025 | AI-specific lifecycle overlay on 15288/12207 |
| AI-STD-003 | GOST R 71540-2024 (ISO/IEC 5392:2024), reference architecture of knowledge engineering | ACTIVE from 01.01.2025 | core architectural source for FATHER Knowledge Factory |
| AI-STD-004 | PNST 842-2023 (ISO/IEC 25059:2023), quality model for AI systems | ACTIVE PNST | AI quality/NFR/test model; keep type=PNST, not GOST |
| AI-STD-005 | GOST R ISO/IEC 42001-2024 | already in FATHER standard set | AI management system/governance |
| AI-STD-006 | GOST R 71752-2024 | already P0 verified | AI technical specification content |

### Important legacy reconciliation

The historical compilation contains drafts/first editions that must not remain classified as current projects when a final national standard exists. Examples:
- project `AI concepts and terminology` -> GOST R 71476-2024;
- project `AI system lifecycle processes` -> GOST R 71539-2024;
- project `reference architecture of knowledge engineering` -> GOST R 71540-2024;
- project `AI technical specification` -> GOST R 71752-2024 (already verified in FATHER);
- project `AI management system` -> GOST R ISO/IEC 42001-2024 (already in FATHER).

Create relationships `DRAFT_PREDECESSOR_OF` rather than treating both as independent current requirements.

## 4. Additional candidates from historical compilation — verify before promotion

These are relevant but require current official-source verification before use:
- Government Resolution 676 of 06.07.2015 — lifecycle requirements for state information systems;
- Presidential Decree 203 of 09.05.2017 — Information Society Strategy 2017–2030;
- Presidential Decree 646 of 05.12.2016 — Information Security Doctrine;
- Presidential Decree 83 of 02.03.2022 — accelerated development/support of the IT industry;
- Government Resolution 2117 of 15.12.2020 — Center of Competence for ICT Import Substitution;
- sectoral AI standards and industry strategies (healthcare, transport, industry, education) — only activate when a product/domain profile requires them;
- subsidy/grant rules — `SUPPORT_MEASURE`, never architecture/compliance obligations unless the project participates in that program.

## 5. Classification rule for the 777-line historical compilation

Every item must receive one of:
- `BINDING_NPA_CURRENT`
- `BINDING_NPA_SUPERSEDED`
- `STRATEGY_POLICY_CURRENT`
- `PROGRAM_SUPPORT_MEASURE`
- `SECTORAL_PROFILE`
- `STANDARD_CURRENT`
- `PNST_CURRENT`
- `DRAFT_STANDARD_HISTORICAL`
- `REPEALED_HISTORICAL`
- `NEEDS_OFFICIAL_VERIFICATION`

Hard gate: only `BINDING_NPA_CURRENT` may produce legal obligation nodes. Standards produce obligation nodes only after a separate applicability basis is proven.

## 6. Next processing sequence

1. Keep the current Stage-6 pack of 56 local NPA intact.
2. Add the P0 AI legal core above as an enrichment queue.
3. Resolve duplicates by canonical legal identity `(type, issuer, number, date)`, not filename.
4. Verify official publication/currentness/amendment lineage.
5. Parse verified legal sources into atomic norms.
6. Add current AI standards as guidance/engineering requirements with separate legal applicability.
7. Only after the legal/standard backbone is clean, map book knowledge to the same concepts and decisions.

Target crosswalk:

`LEGAL_NORM -> STRATEGIC_REQUIREMENT -> STANDARD_CLAUSE -> ENGINEERING_REQUIREMENT -> ARCHITECTURE -> CONTROL -> TEST -> EVIDENCE`

and

`BOOK_PRINCIPLE -> SUPPORTS / REFINES / ALTERNATIVE_TO -> ENGINEERING_REQUIREMENT / ADR`.
