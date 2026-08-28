# Habr NPA sweep — Stream 1 — 2026-08-28 04:53 MSK

Scope: only new confirmed findings, false positives, conflicts and blockers from Habr 432466 and the active PDn/information NPA list. GitHub copies are never treated as official by default.

## New full-text mirror — 152-FZ / 27.07.2006
Repository: `ZharovVsevolod/law_rag`
Commit: `7b09c203c212033c36d0a5ce3bc15891ccb0643a`

Variants:
- `data/docs/152/clean.md` — 243,048 bytes — Markdown — blob `477d4be5e4defa0675cc2a1c8813df3f220e2056`.
- `data/docs/152/parsed.md` — 237,277 bytes — Markdown — blob `e13d6d618aa3f8c42040c4987b0a71e166f60204`.
- `data/docs/152/original.pdf` — 953,211 bytes — PDF — blob `ac8a925cfa53f21119e32f7bebcfe54bfa29f8c0`.

`clean.md` contains the normative body, not only a table of contents: internal identity is `27.07.2006 N 152-FZ`, title `О персональных данных`, State Duma/Soviet Federation adoption data, article text and final Article 25. The copy states ConsultantPlus revision `08.08.2024`, saved 03.05.2025.

Primary official freshness check: Federal Law No. 23-FZ of 28.02.2025 expressly amends Federal Law `О персональных данных` (official publication No. `0001202502280034`, 28.02.2025). Therefore this GitHub copy is provably stale.

Status: `FULL_TEXT / SAME_ACT_PROCESSING_VARIANTS / STALE_BEFORE_23-FZ_2025 / NON_OFFICIAL_GITHUB_COPY`.

## New full-text mirror — 149-FZ / 27.07.2006
Repository: `ZharovVsevolod/law_rag`
Commit: `7b09c203c212033c36d0a5ce3bc15891ccb0643a`

Variants:
- `data/docs/149/clean.md` — 592,800 bytes — Markdown — blob `8e30edd4dce281e2fb9261c390e310539d2898c1`.
- `data/docs/149/parsed.md` — 579,777 bytes — Markdown — blob `4b4149528be5c3b2f3b89356f12681b486e6b762`.
- `data/docs/149/original.pdf` — 2,116,591 bytes — PDF — blob `b2b78b25effade606dfa9dafc7f31b94b341dc72`.

`clean.md` contains actual normative body and independently verifies internal identity: `27.07.2006 N 149-FZ`, title `Об информации, информационных технологиях и о защите информации`, adoption data and article text. It declares ConsultantPlus revision `23.11.2024`, saved 22.03.2025.

Primary official freshness check: Federal Law No. 569-FZ of 29.12.2025 expressly amends Federal Law `Об информации, информационных технологиях и о защите информации` (official publication No. `0001202512290057`, 29.12.2025). Therefore this GitHub copy is provably stale.

Status: `FULL_TEXT / SAME_ACT_PROCESSING_VARIANTS / STALE_BEFORE_569-FZ_2025 / NON_OFFICIAL_GITHUB_COPY`.

## New corpus-quality conflict — IvanchikIvanov/ZkonRf
Repository: `IvanchikIvanov/ZkonRf`
Commit: `2ed96981f48397751ce05f735315b3b82302802c`.

Several files are named like complete laws and carry recent amendment lists, but body inspection shows ConsultantPlus page/search snapshots: correct identity metadata, amendment list, chapter/article titles, then `Открыть полный текст документа` and site navigation — not the normative article bodies.

Confirmed examples:
- `data/codexes/ru/zpp_152_fz_personal_data.txt` — 10,697 bytes — TXT — blob `ddfa59e91a0c632babc331b3b5e4b09797977bda`.
- `data/codexes/ru/zpp_149_fz_information.txt` — 17,045 bytes — TXT — blob `c09be1642dc5f566530b9b952e6c63e96bbdbedf`.
- `data/codexes/ru/zpp_161_fz_payment_system.txt` — 15,025 bytes — TXT — blob `b7e522fda6d4df37a8bcac2dde87139f56728e45`.
- `data/codexes/ru/zpp_184_fz_tech_reg.txt` — 17,632 bytes — TXT — blob `9a0b3427d7d75ef583d00e4f7a8f4a40c7478117`.

Status: `TOC/SEARCH_SNAPSHOT / IDENTITY_METADATA_PRESENT / REJECT_FOR_PRIMARY_KB`.
New normalizer rule: `RECENT_AMENDMENT_LIST != FULL_TEXT` and `ARTICLE_TITLES != ARTICLE_BODIES`.

## Rejected false candidate — Roskomnadzor Order No. 180
Repository: `1homeboyjimmy/pitchy`
Commit: `0ed93171bbca96c2175d117879cc133798224cd3`
Path: `sample_docs/legal_and_taxes/rkn_instruction.txt`
Size: 76,652 bytes
Type: TXT
Blob: `37db041dee1b9a8da2ad79b22281226ef04056c0`

The file is a 2025 user instruction for filling the Roskomnadzor electronic notification form. It references Order No. 180 and explains portal workflow, but is not the order itself and does not contain the normative forms as the act body.

Primary official identity separately confirmed: Roskomnadzor Order of 28.10.2022 No. 180, registered 15.12.2022 No. 71532, official publication No. `0001202212150022` dated 15.12.2022.

Status: `SECONDARY_OPERATIONAL_GUIDE / MENTION_ONLY / REJECT_FOR_PRIMARY_KB`.

## Blockers rechecked without new standalone full text
No new verified standalone GitHub body was found in this pass for: 247-FZ/2020, 258-FZ/2020, 242-FZ/2008 genomic registration, Roskomnadzor Orders 128/178/179/180/187, PP 1046/2021, PP 2526/2022, PP 6/2023, PP 24/2023, PP 1154/2025, PP 1722/2020 and PP 336/2022. Returned hits remain mentions, checklists, portal instructions, summaries, amendments or other acts.

## Delta
- newly confirmed full-text mirrors: 2 acts (`149-FZ`, `152-FZ`), both stale and non-official;
- associated processing/format variants recorded: 6 files total across the two acts; no exact blob duplicates among them;
- deceptive TOC/search snapshots rejected: 4 files in `IvanchikIvanov/ZkonRf`;
- false RKN-180 candidate rejected: 1 operational guide;
- newly closed act-coverage blockers: 0;
- exact duplicates newly confirmed: 0.
