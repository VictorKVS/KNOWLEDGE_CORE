# Habr NPA sweep — Stream 1 — 2026-08-28 03:56 MSK

Scope: only new findings/blockers from Habr 432466 and the active PDn/information NPA list. GitHub copies are never treated as official by default.

## New blocker — 247-FZ / 31.07.2020
Target identity from Habr: Federal Law No. 247-FZ of 31.07.2020, "On Mandatory Requirements in the Russian Federation". Primary publication identity was independently confirmed on publication.pravo.gov.ru: publication No. 0001202007310002, published 31.07.2020.

GitHub exact-title/date searches did not yield a standalone full-text copy. Returned hits are references inside other legal corpora, Duma-session materials, KOAP-derived documents and other secondary contexts. Status: `OFFICIAL_IDENTITY_VERIFIED / GITHUB_FULL_TEXT_PENDING / CURRENTNESS_PENDING`.

## New conflict — 258-FZ number collision
Habr target: Federal Law No. 258-FZ of 31.07.2020, "On Experimental Legal Regimes in the Sphere of Digital Innovations in the Russian Federation". Primary publication identity: publication No. 0001202007310024, published 31.07.2020.

The same federal-law number is reused in other years for unrelated acts: publication.pravo.gov.ru also has Federal Law No. 258-FZ of 03.07.2016 and Federal Law No. 258-FZ of 29.07.2017 with different titles and subject matter. Therefore `258-FZ` alone is unsafe as an identifier. Required canonical identity key: `act_type + authority + date + number + normalized_title/body_identity`.

GitHub searches for the exact 2020 target currently return mainly references inside 152-FZ copies and legislative-session material, not a standalone verified full text. Status: `NUMBER_COLLISION_CONFIRMED / OFFICIAL_IDENTITY_VERIFIED / GITHUB_FULL_TEXT_PENDING`.

## New blocker — Roskomnadzor Order No. 128 / 05.08.2022
Habr target: Order of Roskomnadzor No. 128 of 05.08.2022, "On approval of the list of foreign states providing adequate protection of the rights of personal data subjects". Primary publication identity independently confirmed: registered 20.09.2022 No. 70152; publication No. 0001202209200008; published 20.09.2022.

Exact-title GitHub search returned only a third-party data-processing specification referencing the order; no standalone full-text copy was confirmed. Status: `OFFICIAL_IDENTITY_VERIFIED / GITHUB_FULL_TEXT_PENDING`.

## New blocker — Roskomnadzor Order No. 187 / 14.11.2022
Habr identifies the target as Order No. 187 of 14.11.2022, "On approval of the procedure and conditions for interaction ... within the registry of personal-data incidents", registered No. 71851. GitHub exact-title search produced an Obsidian PDn-package note and application/privacy-policy mentions, not the normative body. No standalone full text confirmed. Status: `HABR_IDENTITY_CONFIRMED / GITHUB_FULL_TEXT_PENDING / PRIMARY_OFFICIAL_CARD_PENDING`.

## Rejected false candidate — 242-FZ / genomic registration
For the target Federal Law No. 242-FZ of 03.12.2008 "On State Genomic Registration in the Russian Federation", the strongest new GitHub text hit in `Chepenkoroman/duma_analysis`, commit `3875b7e726b2ad4af6f859fba85922360b84bfbe`, path `data/txt_output/508.txt`, is a State Duma plenary-session transcript dated 25.08.2008, not the enacted law. It mentions legislative work but fails body-identity/full-text gates. Status: `PARLIAMENT_TRANSCRIPT / REJECT_FOR_PRIMARY_KB`. The standalone full-text GitHub blocker remains open.

## Delta
- new verified standalone FULL_TEXT: 0
- new official identities confirmed: 3 (247-FZ/2020, 258-FZ/2020, RKN-128/2022)
- new identifier conflicts: 1 (`258-FZ` cross-year collision)
- new false candidates rejected: 1 (Duma transcript for 242-FZ/2008)
- exact duplicates: 0
- blockers kept open: 247-FZ/2020, 258-FZ/2020, 242-FZ/2008, RKN 128/187 full GitHub bodies
