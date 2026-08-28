# Habr NPA sweep — Stream 1 — 2026-08-28 08:56 MSK

Scope: new deltas only. GitHub copies are not treated as official sources. Body identity, completeness, currentness and official publication are separate gates.

## 1. Minцифры Order 22.09.2020 No. 486 — FULL_TEXT found

Target identity: Приказ Министерства цифрового развития, связи и массовых коммуникаций Российской Федерации от 22.09.2020 № 486 «Об утверждении классификатора программ для электронных вычислительных машин и баз данных».

GitHub candidate:
- repo: `VictorKVS/gpt-agent`
- commit/ref: `ef8b02c1e0e997e028efc1dd2f3d30dc7e1cdce8`
- path: `дОКУМЕНТЫ ЗАГРУЖАЕМЫЕ В АГЕНТ/Техническое регулирование/Приказ Минкомсвязи России от 22.09.2020 N 486 Об утверждении классификатора программ для электронных вычислительных машин и баз данных/22(1)_1.txt`
- type: TXT
- size: 113,440 bytes
- blob: `6f5f3accfea2be5e0f5339a7e1d34284beb1ef1f`

Body verification: PASS. The body independently states Ministry, date 22 September 2020, No. 486, exact title, operative clauses 1–3, Minister M.I. Shadaev, Ministry of Justice registration 29.10.2020 No. 60646, and includes the attached classifier rather than only a title/summary. The copy records amendments dated 26.04.2022, 22.12.2022 and 04.12.2023 and explicitly contains the classifier revision effective 22.03.2024 under Minцифры Order No. 1041 of 04.12.2023. GARANT export marker: 26.11.2024.

Same-act binary variant in the same directory:
- PDF: `Приказ Министерства цифрового развития связи и массовых коммуникаций РФ от 22 се (1).pdf`
- size: 227,025 bytes
- blob: `332bc67143c083dec94c814a41f0422625041556`
- classification: `SAME_ACT_FORMAT_VARIANT`; the TXT is the body-verified machine-readable candidate.

Primary official verification:
- original Order No. 486: official publication No. `0001202010290057`, published 29.10.2020; registration No. 60646;
- amendment Order Minцифры 04.12.2023 No. 1041: registration 11.03.2024 No. 77464, official publication No. `0001202403110026`, published 11.03.2024.

No later official amendment was established in this pass by exact searches, but absence was not proven exhaustively. Status: `FULL_TEXT / REVISION_INCLUDES_1041_2023_EFFECTIVE_2024 / NON_OFFICIAL_GARANT_EXPORT / CURRENT_CANDIDATE / OFFICIAL_ORIGINAL_AND_KNOWN_AMENDMENT_VERIFIED`.

## 2. PP RF 30.12.2016 No. 1567 — FULL_TEXT plus exact duplicate set

Target identity: Постановление Правительства Российской Федерации от 30.12.2016 № 1567 «О порядке стандартизации в отношении оборонной продукции ... иной информации ограниченного доступа ...».

GitHub source:
- repo: `VictorKVS/gpt-agent`
- commit/ref: `ef8b02c1e0e997e028efc1dd2f3d30dc7e1cdce8`
- directory: `дОКУМЕНТЫ ЗАГРУЖАЕМЫЕ В АГЕНТ/Техническое регулирование/Постановление Правительства РФ от 30.12.2016 N 1567 О порядке стандартизации в отношении оборонной продукции/`

Three TXT paths are byte-identical:
- `Постановление Правительства Р.txt`
- `Постановление Правительства Р (1).txt`
- `Постановление Правительства Р (2).txt`
- each size: 190,614 bytes
- each blob: `9f9ddb48e1e92c6f9417305ae5dc9373b2400192`

This is one canonical text plus two redundant exact copies, not three legal documents. A PDF format variant also exists:
- `Постановление Правительства Р.pdf`
- size: 188,287 bytes
- blob: `0f8445d5f79e8bd699485dff39a67453fc713c44`

Body verification: PASS. The text independently contains the Government resolution identity, date 30.12.2016, No. 1567, exact long title, operative clauses, attached regulations and the entry-into-force clause. It records amendments dated 25.11.2020 and 12.03.2024; in particular it states that PP RF 12.03.2024 No. 295 changed several clauses with effect from 23.03.2024. GARANT export marker: 26.11.2024. This is `FULL_TEXT`, not a mention or summary.

Primary-official gate: exact searches of `publication.pravo.gov.ru` / Government sources did not resolve a primary page for the original No. 1567 or amendment No. 295 in this pass. Therefore no official/current promotion is made from GitHub or secondary legal-system status.

Status: `FULL_TEXT / GARANT_EXPORT_2024 / NON_OFFICIAL_GITHUB_COPY / EXACT_DUPLICATE_TXT_X3 / PDF_FORMAT_VARIANT / PRIMARY_OFFICIAL_LIFECYCLE_PENDING`.

Regression rule: before ingestion, deduplicate by content/blob hash before considering filename or folder path; identical bodies with suffixes `(1)` / `(2)` are aliases, not versions.

## Delta

- new body-verified FULL_TEXT acts: 2;
- exact-duplicate set: 1 (`PP 1567`, 3 identical TXT files = 2 redundant physical copies);
- same-act PDF format variants: 2 acts have PDF companions in the checked directories (for No. 486 one PDF is confirmed; for No. 1567 one PDF is confirmed);
- new official primary identity/publication verified: Order No. 486 and amendment No. 1041;
- new primary-official blocker: PP No. 1567 lifecycle page not resolved in this pass;
- no new standalone verified GitHub bodies found in rechecks for 247-FZ/2020, 258-FZ/2020, Roskomnadzor No. 178 and PP No. 1722/2020.
