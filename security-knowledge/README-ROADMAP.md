# Security Knowledge — corpus roadmap

The project is a jurisdiction-aware evidence graph for regulatory compliance, security architecture, threat modelling, audit and pentest planning.

## Corpus layers

### 1. Russian mandatory regulation
Federal laws, codes, presidential decrees, Government decrees, FSTEK, FSB, Roskomnadzor and sector/functional regulators including Rospotrebnadzor, Minzdrav, Mintsifry, Bank of Russia, EMERCOM, Rostekhnadzor and others selected by organization applicability.

### 2. GOST and Russian standards
Priority families include GOST R ISO/IEC 27001, 27002, 27005; 15408 family; GOST R 57580.1/57580.2; conformity assessment, risk management, incident management, continuity, secure software development, cryptography, testing and information protection standards.

### 3. International standards
ISO/IEC 27000 family; ISO 22301; ISO 31000; ISO/IEC 15408/Common Criteria; ISO/IEC 27017, 27018, 27701, 27035, 27036, 27034, 27032 and relevant related families.

### 4. Foreign and international regulation — separate jurisdiction layer
GDPR; NIS2; DORA; EU Cybersecurity Act; Cyber Resilience Act; AI Act security-relevant provisions; ePrivacy; Convention 108/108+ and applicable international treaties. These nodes are never silently mixed with Russian obligations. Applicability is jurisdiction-driven.

### 5. Frameworks and best practices
NIST CSF; NIST SP 800-53, 800-30, 800-61, 800-115, 800-218 SSDF; CIS Controls; CIS Benchmarks; CSA CCM; PCI DSS; SWIFT CSCF and sector frameworks. Framework status must not be automatically weighted as law.

### 6. Threat, weakness and vulnerability knowledge
FSTEK BDU; CWE; CVE; NVD; CVSS; CAPEC; MITRE ATT&CK; MITRE D3FEND; CISA KEV; EPSS. This is a technical knowledge layer linked to assets, threat scenarios, weaknesses, controls and checks.

### 7. Application Security
OWASP Top 10; OWASP API Security Top 10; ASVS; MASVS; WSTG; MASTG/MSTG historical naming where relevant; SAMM; Cheat Sheet Series; CWE Top 25 and other verifiable sources.

### 8. Pentest methodology
PTES; NIST SP 800-115; OWASP WSTG; OSSTMM and other methodologies. Maintain authorization, scope, rules of engagement, evidence, severity, remediation and retest as first-class nodes. Build a project-specific evidence-backed TOP-100 checks only after source mapping.

### 9. Vendor and platform hardening
Official security guides and configuration baselines for Microsoft, Linux distributions, Kubernetes, Docker, PostgreSQL, nginx, Apache, Cisco, MikroTik, VMware, cloud platforms and other products actually present in an organization profile.

## Cross-layer graph

`SOURCE -> ATOMIC REQUIREMENT/GUIDANCE -> APPLICABILITY -> UNIFIED CONTROL -> THREAT/WEAKNESS -> SEC-CHECK -> EVIDENCE -> GAP/RISK -> ARCHITECTURE OPTION -> ROADMAP`

## Core quality rules

1. Source text and source version remain authoritative.
2. Every VERIFIED node must be traceable to a source locator.
3. Jurisdictions are evaluated before requirements are merged for implementation planning.
4. Deduplication reduces implementation burden, not legal obligations.
5. Legal force, technical evidence strength and implementation priority are separate weights.
6. Threat intelligence and vulnerability feeds are versioned and time-sensitive.
7. Vendor guidance is selected only after product/platform facts are known.
8. Pentest checks require explicit authorization/scope semantics and must retain evidence/retest lineage.
9. Change monitoring must produce reviewable change sets before altering verified graph semantics or weights.
