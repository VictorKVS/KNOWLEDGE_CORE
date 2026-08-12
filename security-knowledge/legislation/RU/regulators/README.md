# Russian regulator and sector layers

This directory separates core information-security regulators from sector and functional regulators.

## Core security regulators

- FSTEK — technical information protection, GIS/ISPDn/ASU TP/CII requirements within its competence.
- FSB — cryptographic protection, GosSOPKA/NKTsKI and CII-related requirements within its competence.
- ROSKOMNADZOR — personal-data supervision, notifications, registries, inspections and related requirements.

## Sector and functional regulators

Sector rules are not treated as universal security obligations. They are connected through organization-profile applicability.

Planned layers include, where relevant:

- ROSPOTREBNADZOR
- MINZDRAV
- MINTSIFRY
- BANK_OF_RUSSIA
- MCHS
- ROSTEKHNADZOR
- MINTRANS
- MINENERGO
- other competent authorities discovered through regulatory dependencies.

## Design rule

A sector document enters the security architecture only through a traceable chain:

`ORGANIZATION FACT -> APPLICABILITY RULE -> NORMATIVE REQUIREMENT -> SECURITY/PROCESS IMPACT -> CONTROL -> EVIDENCE`

The graph must distinguish:

1. direct information-security requirements;
2. sector operating requirements that create security constraints;
3. legal/process requirements that affect architecture, data flows, retention, access, availability or evidence;
4. recommendations and non-binding guidance.

This prevents both under-coverage and the opposite error of applying every regulator to every organization.
