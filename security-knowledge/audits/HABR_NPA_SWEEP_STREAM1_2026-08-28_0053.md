# Habr NPA sweep — Stream 1 — 2026-08-28 00:53 MSK

Scope: incremental sweep only. Do not treat GitHub copies as official sources. Full-text promotion requires body identity/completeness plus separate lifecycle/currentness verification.

## New reliable candidate

### Government Decree RF 01.11.2012 No. 1119 — PDn IS protection requirements

- repo: `VictorKVS/gpt-agent`
- commit: `ef8b02c1e0e997e028efc1dd2f3d30dc7e1cdce8`
- path: `дОКУМЕНТЫ ЗАГРУЖАЕМЫЕ В АГЕНТ/Постановление Правительства РФ от 1 ноября 2012 г N 1119 Об утверждении требован.pdf`
- type: PDF
- size: 71,553 bytes
- blob: `c0b7b0a57970be9c70a5671daf38dde3058714d0`
- status: `PDF_FULLTEXT_CANDIDATE / NON_OFFICIAL_GITHUB_COPY / BODY_VERIFICATION_PENDING`

Reason: repository metadata provides an exact act-level filename and stable binary. Binary-body visual/text verification could not be completed through the current connector/browser path, therefore this is not promoted to `FULL_TEXT` yet. Independent current web legal references still expose the act under the correct identity `01.11.2012 N 1119` and title. Primary official lifecycle record for the old 2012 publication remains to be resolved before `VERIFIED_CURRENT`.

## New false / secondary candidates

### Roskomnadzor Order 19.06.2025 No. 140 — Namelomax/Anon

- repo: `Namelomax/Anon`
- commit: `79277627343e5df8ed4ab3893e7dad4dda5d42ac`
- path: `anonymizer/ЮРИДИЧЕСКИЕ_ДОКУМЕНТЫ/07_Соответствие_приказу_РКН_140.md`
- type: Markdown
- status: `SECONDARY_COMPLIANCE_ANALYSIS / REJECT_FOR_PRIMARY_KB`

Body explicitly identifies itself as an implementation audit/compliance plan and quotes/selects clauses from Order 140; it is not the normative act. The official publication portal independently confirms Order 140, registration No. 83110, publication No. `0001202508010002` on 01.08.2025.

### Old anonymization material found during Order-140 search

- repo: `LAIR-RCC/InfSecurityRussianNLP`
- commit: `0f072394f0ada37f607bc4a3da2f22fdd5201eae`
- path: `seccoll/1630.txt`
- type: TXT
- status: `COMMENTARY / WRONG_ACT_OLDER_ANONYMIZATION_MATERIAL / REJECT_FOR_PRIMARY_KB`

It is not Roskomnadzor Order 140/2025 and must not be mapped by topic keywords alone.

## New structural conflicts in old corpus

`VictorKVS/gpt-agent/дОКУМЕНТЫ ЗАГРУЖАЕМЫЕ В АГЕНТ/Государственные регуляторы/Роскомнадзор/` contains only one file at the checked commit:

- `Постановление Правительства РФ от 16 марта .pdf`
- type: PDF
- size: 160,639 bytes
- blob: `9b56ca9727c8a9be49fdd5774922a2518b170733`

No Roskomnadzor Orders 128/178/179/180/187/140 are present in that regulator directory. Classification: `REGULATOR_FOLDER_CONTAMINATION / COVERAGE_GAP`. Folder placement cannot be used as authority identity.

The separate `Персональные данные ФЗ 152` directory likewise contains the 152-FZ TXT/PDF plus user-authored checklists/algorithms/lists, but no files named as Orders 178/179/180/187. This confirms the existing rule `folder != legal ontology`.

### Number 140 collision across authorities and dates

The same `gpt-agent` commit contains a distinct binary:

- path: `дОКУМЕНТЫ ЗАГРУЖАЕМЫЕ В АГЕНТ/Постановление Правительства РФ от 9 февраля 2022 г N 140 О единой государственно.pdf`
- type: PDF
- size: 318,368 bytes
- blob: `25cffc2f3d09b9b0702cefb2a634fa2b331dfb9b`

This is named as a **Government Decree** No. 140 dated 09.02.2022, while the target anonymization act is **Roskomnadzor Order** No. 140 dated 19.06.2025. Classification: `AUTHORITY_NUMBER_DATE_COLLISION`. Normalization must match `authority + act_type + date + number + title/body`, never number alone.

## Blockers after this pass

- PP RF No. 1119: binary GitHub candidate now found, but exact body/completeness verification is still pending; official 2012 lifecycle/currentness needs a primary-source record.
- Roskomnadzor Orders 128/178/179/180/187: independent GitHub full texts still not confirmed.
- Roskomnadzor Order 140/2025: official primary identity is confirmed, but GitHub results found in this pass are secondary compliance/research material, not the act itself.
- 247-FZ, 258-FZ, PP RF No. 1722: no new verified full-text GitHub candidate in this pass.

## Delta

- confirmed `FULL_TEXT`: +0
- reliable act-level binary candidate: +1 (PP 1119)
- rejected secondary/wrong candidates: +2
- structural/identity conflicts: +2
- exact duplicates: +0
- CURRENT promotions: +0
