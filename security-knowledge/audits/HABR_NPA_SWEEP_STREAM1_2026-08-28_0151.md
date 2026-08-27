# Habr NPA sweep — Stream 1 — 2026-08-28 01:51 MSK

Scope: systematic pass over Habr 432466 and the project NPA list for federal laws, Presidential acts, Government acts, Roskomnadzor and general personal-data/information regulation.

Method: GitHub is discovery/storage evidence only. Legal identity is checked from document body; currentness and official publication are checked separately. `PATH/METADATA -> BODY_IDENTITY -> COMPLETENESS -> AMENDMENT_CHAIN -> CURRENT`.

## NEW — FULL_TEXT — Presidential Decree 609/2005

Target: Presidential Decree of 30.05.2005 No. 609, approving the Regulation on personal data of Russian Federation state civil servants and maintenance of their personal files.

GitHub candidate:
- repo: `buba1477/multik_bot`
- commit: `e8e0c46feb0d4a7feadafc934920825bed808f7d`
- path: `embendings/Об утверждении Положения о персональных данных.md`
- type: Markdown
- size: `36,246 bytes`
- blob SHA: `4c8b1c63d5cb93a4b22dafa04ebf2a63317b1706`

Body verification: PASS. The body itself states authority/type/date/number/title, contains Decree points 1-5, President signature/date/number, and the attached Regulation. The file says `По состоянию на 09.04.2026` and includes amendments through Presidential Decree 31.12.2025 No. 1009.

Official/currentness evidence: Presidential Decree 31.12.2025 No. 1009 is officially published on 01.01.2026, publication No. `0001202601010001`; it amends Presidential acts including the Regulation under No. 609. No later amendment was established in this pass.

Status: `FULL_TEXT_CURRENT_CANDIDATE / REVISION_INCLUDES_1009_2025 / OFFICIAL_AMENDMENT_CORROBORATED / NON_OFFICIAL_GITHUB_COPY`.

Hard gate remains: do not promote to `VERIFIED_CURRENT` until a complete official lifecycle check confirms no later act after 31.12.2025.

## NEW — FULL_TEXT — Federal Law 79-FZ/2004

Target: Federal Law of 27.07.2004 No. 79-FZ, On the State Civil Service of the Russian Federation. It is directly relevant to the personal-data rules implemented by Decree 609.

Primary GitHub text inspected:
- repo: `buba1477/multik_bot`
- commit: `e8e0c46feb0d4a7feadafc934920825bed808f7d`
- path: `embendings/79-FZ.md`
- type: Markdown
- size: `512,449 bytes`
- blob SHA: `a31396ef3158886bc380db7a1bed01b6ad3c9542`

Body verification: PASS. The body identifies `27.07.2004 N 79-ФЗ`, exact title, chapters/articles and full normative structure. The stored revision reaches amendments through late 2025.

Additional same-act format/processing variants in the same commit:
- `GraphRAG/Docling/79-FZ.md` — 517,034 bytes — blob `46c9adb48eb14a07bcc91f901850293fd3077b9c`
- `GraphRAG/Docling/79-FZ.rtf` — 2,751,014 bytes — blob `c5dd8548b39de201c14fa47120296a34f9da86e7`
- `GraphRAG/Docling/79-ФЗ.pdf` — 1,317,825 bytes — blob `27a488375d40a10746c725601141b2fdcb9e4121`

These are `SAME_ACT_FORMAT_VARIANTS`, not exact duplicates: all blob SHAs differ.

Currentness conflict: current legal systems show 79-FZ in revision 08.03.2026. Federal Law 08.03.2026 No. 52-FZ, officially published under No. `0001202603080008`, changes part 5 of Article 15 of 79-FZ. Therefore the GitHub copy is not current.

Status: `FULL_TEXT / STALE_AFTER_28.12.2025 / MISSING_52-FZ_08.03.2026 / NON_OFFICIAL_GITHUB_COPY`.

## NEW RELATION — 52-FZ/2026 links civil-service and genomic-registration layers

Official Federal Law 08.03.2026 No. 52-FZ amends:
- `79-FZ/2004` — Article 15(5): civil servants become subject to mandatory state fingerprint and genomic registration in cases/order established by federal laws;
- `242-FZ/2008` On State Genomic Registration — expands categories and procedures for mandatory genomic registration.

Relations to store:
- `52-FZ/2026 --AMENDS--> 79-FZ/2004`
- `52-FZ/2026 --AMENDS--> 242-FZ/2008 genomic registration`

Do not confuse this `242-FZ/2008` with the unrelated `242-FZ/2014` localization amendment law.

## BLOCKERS / REJECTS in this pass

No new reliable full GitHub text was confirmed for:
- Federal Law 03.12.2008 No. 242-FZ on state genomic registration;
- Federal Law 08.03.2026 No. 52-FZ (the official text exists, but no independent full GitHub copy was confirmed);
- Presidential Decree No. 188/1997 confidential-information list;
- 247-FZ/2020 mandatory requirements;
- 258-FZ/2020 experimental legal regimes;
- 123-FZ/2020 AI experiment in Moscow;
- 367-FZ/2021 treaty ratification;
- Government Decree 1046/2021, Decree 24/2023, Decree 1154/2025;
- Roskomnadzor Orders 128/2022 and 187/2022.

Search hits for those targets in this pass were secondary notes, references, coursework or unrelated number collisions and remain rejected for the primary normative layer.

## Delta

- new confirmed `FULL_TEXT`: **+2**
- new `CURRENT_CANDIDATE`: **+1** (Decree 609)
- new confirmed `STALE`: **+1** (79-FZ GitHub copy)
- new amendment relations: **+2**
- exact duplicates: **0**
- same-act format variants: **+3** for 79-FZ
