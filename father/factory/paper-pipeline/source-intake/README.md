# FATHER Source Intake — A0 canonical entry point

Status: `PRIMARY SOURCE INVENTORY / BEFORE CONTENT PROMOTION`

Purpose: ensure FATHER can use **all relevant materials** without mixing authority, evidence quality, copyright state, freshness or project truth.

The source-intake layer is executed before substantive downstream design work.

## Core rule

```text
find everything
→ identify exact source/version
→ classify authority
→ preserve original
→ record provenance/hash/freshness
→ determine applicability
→ extract atomic items
→ map to artifacts/methods
→ compare conflicts/supersession
→ only then promote knowledge or requirements
```

`Everything is used` does **not** mean `everything is equally authoritative`.

## Source classes

1. `MANDATORY_LAW_REGULATION` — laws, government resolutions, regulator orders and binding contractual/corporate requirements.
2. `STANDARD_METHODICAL` — GOST/ISO/IEC/methodical documents used according to applicability or contractual adoption.
3. `PROJECT_FACT` — actual project sources: repository, code, configuration, telemetry, current documents, test evidence, approved owner decisions.
4. `COURSE_METHOD` — OTUS 01–31 and other educational material; supplies methods/capability ideas, not project truth.
5. `PROFESSIONAL_BOOK` — user-owned books; supplies source-verified professional methods after intake/review.
6. `SCIENTIFIC_PRIMARY` — peer-reviewed papers, standards research, primary technical documentation and benchmark methodology.
7. `VENDOR_PRODUCT_DOC` — official documentation for selected technologies/products.
8. `COMPETITOR_REFERENCE` — Ardoq/IcePanel/KNIME/Node-RED/Camunda/Structurizr/etc.; used for UX/process patterns, not copied as doctrine.
9. `HISTORICAL_SUPERSEDED` — obsolete/replaced versions retained for traceability and migration reasoning.
10. `HYPOTHESIS_NOTE` — idea, recommendation or working assumption not yet promoted.

## Precedence / conflict rule

Default decision precedence:

```text
mandatory applicable requirement
→ authorized project owner decision / contract
→ verified current project fact
→ applicable standard/methodical requirement
→ verified scientific/technical evidence
→ professional/book/course recommendation
→ competitor pattern / hypothesis
```

This is not a universal legal hierarchy; `REGULATORY_APPLICABILITY` remains project-specific and legal/compliance authority is preserved.

## Every source record must contain

- stable `source_id`;
- source class;
- canonical title/designation;
- author/authority/provider;
- version/revision/date;
- effective/superseded/draft state where applicable;
- access location and rights basis;
- original byte identity/hash when bytes are available;
- language/content type;
- project applicability;
- freshness/recheck requirement;
- extraction state;
- atomic-item coverage;
- artifact/method mapping state;
- conflicts/supersession links;
- reviewer/owner;
- promotion status.

## Processing states

`DISCOVERED → IDENTIFIED → ORIGINAL_VERIFIED → PARSED → ATOMIC_EXTRACTED → MAPPED → CONFLICT_CHECKED → DOMAIN_REVIEW → ADMITTED`

Additional states:

`PARTIAL`, `STALE`, `SUPERSEDED`, `REJECTED`, `NOT_APPLICABLE`, `BLOCKED_RIGHTS`, `NEEDS_EXPERT_REVIEW`.

## What we process first

1. existing FATHER canonical registries and policies;
2. actual `OSINT_deepseek` project evidence as a walkthrough project;
3. core lifecycle/architecture/requirements/testing/security standards and regulator overlays;
4. OTUS 01–31 exact lesson source and assignments;
5. user-owned architecture/security/data/AI books;
6. official technology docs needed by selected candidate stack;
7. competitor/reference UX sources;
8. scientific sources required to justify algorithms and eval methodology.

The order above controls **intake**, not authority.

## Output of A0 source-intake

- `MASTER_SOURCE_REGISTRY.yaml`;
- source version/freshness register;
- admitted-source set per FATHER role;
- exact missing-source backlog;
- conflict/supersession register;
- source → atomic item → artifact/method mapping;
- coverage report showing what is actually supported and what remains UNKNOWN.

No Model Zoo or automatic knowledge promotion is authorized at this layer until source identity and authority are known.
