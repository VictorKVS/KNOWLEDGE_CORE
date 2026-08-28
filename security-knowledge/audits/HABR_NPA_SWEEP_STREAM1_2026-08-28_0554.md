# Habr NPA sweep — Stream 1 — 2026-08-28 05:54 MSK

Delta-only audit. Prior confirmed findings are not repeated.

## New confirmed conflict — 40-FZ / Federal Security Service

Target act:
- Federal Law of 03.04.1995 No. 40-FZ «О федеральной службе безопасности».
- Official identity is separately confirmed by the President of Russia document bank (`kremlin.ru/acts/bank/7696`).
- A later official federal act, 23-FZ of 28.02.2025, amends the 1995 40-FZ, so currentness must be resolved from the official lifecycle/consolidated text rather than inferred from any GitHub copy.

GitHub candidate inspected:
- repo: `illua0607/advokat`
- commit: `4ff36b4068dea5b76f5605d51626cd4c9f72987b`
- path: `laws/ФЗ О Федеральной Службе Безопасности.txt`
- size: `32130` bytes
- type: TXT
- blob: `aecd32d4088d267576e40b48dd48186d46c7f689`

Body verification result: REJECT.

Although the filename and opening title mimic the federal act, the body repeatedly replaces the Russian Federation with a fictional/role-play jurisdiction «Южный округ», including formulations such as «безопасности Южного округа», «Президентом Южного округа», «Конституция Южного округа» and «субъектам Южного округа». It therefore is not the Russian federal statute and must never be admitted as primary legal evidence.

Classification:
`ADAPTED_OR_ROLEPLAY_TEXT / IDENTITY_MIMIC / BODY_CONTRADICTS_TARGET / REJECT_FOR_PRIMARY_KB`

Normalizer regression rule added conceptually:
`TITLE_OR_FILENAME_MATCH != LEGAL_IDENTITY`.
For high-risk legal ingestion, body-level jurisdiction/issuer/date/number/title checks must precede admission, and strong mismatches must quarantine the whole candidate.

## Additional rejected hit

A broad search for 99-FZ «О лицензировании отдельных видов деятельности» returned `krikyn/Strong-Paraphrase-Generation-2020`, commit `3d5b6f4fd0d4b4f96ed6bdd91b7000d3d80fc901`, `download/v1/7564.txt`. Body inspection shows a news article about proposed bookmaker/tote amendments, not a legal act. Status: `NEWS_ARTICLE / MENTION_ONLY / REJECT_FOR_PRIMARY_KB`.

## Checked open blockers — no new standalone verified body this pass

No new standalone verified GitHub full text was confirmed in this pass for:
- 247-FZ/31.07.2020;
- 258-FZ/31.07.2020;
- 242-FZ/03.12.2008 on state genomic registration;
- Presidential Decree No. 188/06.03.1997;
- Roskomnadzor orders 128/178/179/180/187;
- Government Resolution No. 538/24.04.2025;
- 99-FZ/04.05.2011.

## Delta counters

- NEW_FULL_TEXT: 0
- NEW_RELIABLE_BINARY_CANDIDATE: 0
- NEW_CONFIRMED_CONFLICTS: 1
- NEW_REJECTED_FALSE_CANDIDATES: 2
- NEW_EXACT_DUPLICATES: 0
- CURRENT_PROMOTIONS: 0
