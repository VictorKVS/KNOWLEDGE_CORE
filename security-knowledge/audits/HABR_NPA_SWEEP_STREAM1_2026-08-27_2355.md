# Habr NPA sweep — Stream 1 — 2026-08-27 23:55 MSK

Scope: only new confirmed findings/conflicts from the continuing sweep of Habr 432466 and the general NPA list.

## 1. 210-FZ — full text found, but not current after 04.08.2026

Target from Habr: Federal Law of 27.07.2010 No. 210-FZ "On the Organization of Provision of State and Municipal Services".

GitHub candidate:
- repo: `SergSi/EXPERT`
- commit: `7b6cc83b69d251a1ff53c4d6dc15c5b854e8961e`
- path: `NORMATIVE/210-ФЗ.txt`
- size: `234681` bytes
- type: `TXT`
- blob: `a3503f31cfa216452fcffeaab6e7fbd940d1806e`

Body verification:
- starts with Chapter 1 / Article 1 and the correct subject matter (state and municipal services);
- contains the electronic-services/e-signature provisions used by the Habr section;
- reaches Article 30, Presidential signature, `27 July 2010`, `N 210-FZ`;
- GARANT export footer: `01.05.2026`, 71/71 pages.

Freshness:
- the file includes amendments through at least 29.12.2025 and changes effective in 2026;
- current consolidation is already revised on 04.08.2026;
- later acts of 04.08.2026 include No. 285-FZ (changes Art. 10 and Art. 21) and No. 312-FZ (changes Art. 21.3), therefore the GitHub export is no longer current.

Status: `FULL_TEXT / GARANT_EXPORT_2026-05-01 / STALE_AFTER_2026-08-04 / NON_OFFICIAL_GITHUB_COPY`.

Primary official publication card for the latest two 04.08.2026 amendments was not resolved by the current search index; keep `LATEST_PRIMARY_OFFICIAL_CARD=PENDING` and do not promote to CURRENT.

## 2. 218-FZ filename collision — wrong act for the Habr target

Habr target: Federal Law of 30.12.2004 No. 218-FZ "On Credit Histories".

Found file:
- repo: `SergSi/EXPERT`
- commit: `7b6cc83b69d251a1ff53c4d6dc15c5b854e8961e`
- path: `NORMATIVE/218-ФЗ.txt`
- size: `957272` bytes
- type: `TXT`
- blob: `95fd60969971831cfd6cf17fc988568c44b2aa67`

Body verification shows that this is NOT the 2004 credit-history law. Article 1 regulates state registration of rights to immovable property and EGRN. The official legal identity matching that body is Federal Law of 13.07.2015 No. 218-FZ "On State Registration of Real Estate".

Status: `ACT_NUMBER_COLLISION / WRONG_TARGET_FOR_HABR_218 / DO_NOT_MATCH_BY_NUMBER_ONLY`.

This is a concrete regression fixture for the normalizer: `act_number` alone is not a stable identity; use at minimum `(act_type, date, number, title/body identity)`.

## 3. 248-FZ — full general-control law found, but one revision behind

Additional general-control candidate relevant to the inspection/control layer:
- repo: `SergSi/EXPERT`
- commit: `7b6cc83b69d251a1ff53c4d6dc15c5b854e8961e`
- path: `NORMATIVE/248-ФЗ .txt`
- size: `359341` bytes
- type: `TXT`
- blob: `7a3a920b76f13adfb6bd3813faee78bb74004c37`

Body verification:
- Article 1 defines state/municipal control;
- the text contains KII/TZI licensing-control exclusions in Article 2;
- reaches Chapter 19, Article 98 "Procedure for entry into force", so it is full text rather than notes;
- contains amendments through 29.12.2025 (No. 567-FZ).

Official identity: Federal Law of 31.07.2020 No. 248-FZ "On State Control (Supervision) and Municipal Control in the Russian Federation"; original official publication number `0001202007310018`, published 31.07.2020.

Freshness: current consolidation is revised 17.04.2026. Federal Law No. 101-FZ of 17.04.2026 subsequently amended 248-FZ and was officially published 17.04.2026 under publication number `0001202604170013`; this amendment is absent from the GitHub file.

Status: `FULL_TEXT / STALE_BEFORE_101-FZ_2026 / NON_OFFICIAL_GITHUB_COPY`.

## Delta

- new confirmed FULL_TEXT: `2` (210-FZ, 248-FZ);
- new identity/number collision: `1` (218-FZ 2004 target vs 218-FZ 2015 body);
- new exact duplicates: `0`;
- CURRENT promotions: `0`.
