# Habr NPA sweep — stream 1 — 2026-08-27

Scope: federal laws, Presidential acts, Government acts, Roskomnadzor and common PDn/information acts.

## Newly confirmed findings

### 59-FZ — citizen appeals
- Act: Federal Law of 02.05.2006 No. 59-FZ "On the Procedure for Considering Appeals of Citizens of the Russian Federation".
- GitHub repo: `SergSi/EXPERT`
- Commit/ref: `7b6cc83b69d251a1ff53c4d6dc15c5b854e8961e`
- Path: `NORMATIVE/59-ФЗ.txt`
- Blob SHA: `7f3dc4b756254e8f76bcafe46972eaff04f9c250`
- Size: `31,726` bytes
- Type: TXT, GARANT export.
- Completeness: full body through Article 18 and presidential signature block; footer identifies the act as 02.05.2006 No. 59-FZ.
- Export date embedded in file: 01.05.2026.
- Currentness evidence in body: amendments through Federal Law No. 547-FZ of 28.12.2024; current legal-reference sources also show revision 28.12.2024.
- Official amendment publication: Federal Law No. 547-FZ, publication No. `0001202412280052`, 28.12.2024.
- Status: `FULL_TEXT_CURRENT_CANDIDATE / GARANT_EXPORT / NON_OFFICIAL_GITHUB_COPY`.

### Constitution of the Russian Federation — stronger current candidate than previously found stale copies
- GitHub repo: `SergSi/EXPERT`
- Commit/ref: `7b6cc83b69d251a1ff53c4d6dc15c5b854e8961e`
- Path: `NORMATIVE/Конституция РФ.txt`
- Blob SHA: `a3a46dc01145a717b1c8d9aae08206c72b1a0a24`
- Size: `152,832` bytes
- Type: TXT, GARANT export.
- Completeness/currentness indicators: contains Article 67.1 introduced in 2020; contains 2025 GARANT annotations; export footer dated 01.05.2026.
- Official baseline: Constitution text published 06.10.2022, publication No. `0001202210060013`; Presidential Decree No. 710 of 05.10.2022 ordered publication of the text with changes.
- Status: `FULL_TEXT_CURRENT_CANDIDATE / GARANT_EXPORT / NON_OFFICIAL_GITHUB_COPY`.
- Action: preferred replacement candidate for earlier stale 2014/pre-2020 GitHub copies.

## Rejected candidates / blockers

### Government Resolution No. 1119
- Candidate: `brainalytics/brainalytics.github.io`, commit `c2d76d8e1234173f99c5af257e5739d840efb536`, path `docs/gost/pp-1119.html`.
- Body contains only heading, `TBD`, and a pravo.gov.ru link.
- Status: `STUB_ONLY / LINK_ONLY / REJECT_FOR_PRIMARY_KB`.
- Blocker remains: no independently verified full GitHub copy confirmed in this pass.

### Federal Law No. 187-FZ
- Candidate: `ale88andr/obs-vault`, commit `c11b4d292870c9b7e6c8277b08610ae68fc7f4bd`, path `InfoSec/Законодотельство ИБ/ФЗ 187.md`.
- Body is analyst notes/checklist and starts with a link to `[[ФЗ187.pdf]]`; it is not the statutory text.
- Status: `SECONDARY_ANALYSIS / LINK_TO_PDF / REJECT_FOR_PRIMARY_KB`.

### Roskomnadzor Order No. 178
- Candidate: `Nataly369264/compliance152`, commit `a233c538aa1252b0407470786a339e5fc98353b6`, path `knowledge_base/templates/harm_assessment.md`.
- Body is a harm-assessment template merely citing Order No. 178.
- Status: `TEMPLATE / MENTION_ONLY / REJECT_FOR_PRIMARY_KB`.

## Gate reinforced
A GitHub hit counts as primary-source candidate only after `BODY_IDENTITY + COMPLETENESS + CURRENTNESS` checks. References, templates, checklists and pages linking to an official act stay outside the normative source layer.
