# Habr NPA sweep — Stream 1 — 2026-08-28 07:56 MSK

Scope: new deltas only. GitHub copies are not treated as official sources. Body identity, completeness, currentness and official publication are separate gates.

## 1. PP RF 08.05.2025 No. 612 — FULL_TEXT found

Target identity: Постановление Правительства Российской Федерации от 08.05.2025 № 612 «О внесении изменений в некоторые акты Правительства Российской Федерации».

GitHub candidate:
- repo: `Gevork23/dissertacia_project`
- commit/ref: `8b48b17c22f269b55b2903b408459e863d8fe61f`
- path: `regression/ruslawod_pairs/pair_0018/new.txt`
- type: TXT
- size: 4,520 bytes
- blob: `9d95f6cbcecedb56280302349a6fc31c97ce133f`

Body verification: PASS. The body independently states Government of the Russian Federation, resolution, date 8 May 2025, No. 612, exact title, operative clauses and signature. It amends PP RF No. 2467 of 31.12.2020 and PP RF No. 488 of 12.04.2025. This is a complete short amending act, not a summary or mention.

Status: `FULL_TEXT / NON_OFFICIAL_GITHUB_COPY / ORIGINAL_2025_TEXT / CURRENT_REVISION_NOT_MATCHED`.

Currentness: the act was later amended by PP RF No. 1670 of 27.10.2025 according to current legal-system cards, so the GitHub text must not be promoted as CURRENT without incorporating/checking that revision.

Official publication: secondary legal-system metadata identifies official publication as `pravo.gov.ru` on 16.05.2025, publication No. `0001202505160028`. Direct retrieval of the primary publication page timed out in this run, therefore `PRIMARY_OFFICIAL_FETCH_PENDING` remains set; no official-status promotion is made from GitHub.

## 2. Number collision regression fixture: PP RF No. 612/2020 vs No. 612/2025

Same repository and commit contain:
- path: `regression/ruslawod_pairs/pair_0018/old.txt`
- type: TXT
- size: 6,779 bytes
- blob: `0ed144c304f00843554e2bda0af7ad9e71033789`

Its body is a different act: Постановление Правительства РФ от 30.04.2020 № 612, also titled «О внесении изменений в некоторые акты Правительства Российской Федерации», focused on metrology/agency powers.

Status: `NUMBER_AND_GENERIC_TITLE_COLLISION_CONFIRMED`.

Regression rule: even `act_type + authority + number + generic title` is insufficient. Canonical identity must include at minimum `authority + act_type + exact date + number + normalized title/body fingerprint`.

## 3. Government Order 20.05.2023 No. 1315-r — reliable PDF candidate, body pending

Target: Распоряжение Правительства Российской Федерации от 20.05.2023 № 1315-р «Об утверждении Концепции технологического развития на период до 2030 года».

GitHub candidate:
- repo: `VictorKVS/gpt-agent`
- commit/ref: `ef8b02c1e0e997e028efc1dd2f3d30dc7e1cdce8`
- directory: `дОКУМЕНТЫ ЗАГРУЖАЕМЫЕ В АГЕНТ/Стратегические документы/Распоряжение Правительства РФ от 20.05.2023 N 1315-р Об утверждении Концепции технологического развития на период до 2030 года/По отрослям`
- file: `Распоряжение.pdf`
- type: PDF
- size: 315,995 bytes
- blob: `9b168ea40dcc5d9fb8ce213f099f87398abc4650`

The repository path strongly matches the target act, but binary body extraction through the GitHub connector failed; therefore completeness and internal date/number/title have NOT been verified. Status: `PDF_ACT_LEVEL_CANDIDATE / BODY_VERIFICATION_PENDING / NON_OFFICIAL_GITHUB_COPY`.

Primary official identity: official publication portal identifies order 20.05.2023 No. 1315-r, publication No. `0001202305250050`, published 25.05.2023. The Government of Russia official document page currently displays the act in the revision of order 21.10.2024 No. 2963-r.

Status: `OFFICIAL_IDENTITY_VERIFIED / OFFICIAL_CURRENT_REVISION_21.10.2024 / GITHUB_REVISION_UNKNOWN`.

## Delta counters

- new verified GitHub FULL_TEXT: +1
- new act-level PDF candidate: +1
- new number/title collision: +1
- new exact duplicates: 0
- GitHub copies promoted to CURRENT: 0

## Gates retained

- `GITHUB_COPY != OFFICIAL_SOURCE`
- `PATH_MATCH != BODY_IDENTITY`
- `NUMBER != IDENTITY`
- `GENERIC_TITLE + NUMBER != IDENTITY`
- `FULL_TEXT != CURRENT`
- currentness requires a separate official lifecycle check.
