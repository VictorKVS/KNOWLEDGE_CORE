# Habr NPA sweep — Stream 1 — 2026-08-28 10:55 MSK

Scope: systemic pass over Habr 432466 and the user NPA list. GitHub copies are treated as non-official until separately verified.

## Delta

- FULL_TEXT: +1
- SAME_ACT_FORMAT_VARIANT: +1
- independent historical/partial mirror: +1
- exact duplicates: 0
- new identity conflicts: 0
- currentness promotion to VERIFIED_CURRENT: 0

## 1. Постановление Правительства РФ от 26.06.1995 № 608 «О сертификации средств защиты информации»

Habr coverage: section «Техническое регулирование. Сертификация средств защиты информации».

### GitHub primary candidate already present in VictorKVS/gpt-agent

Repository: `VictorKVS/gpt-agent`
Commit: `ef8b02c1e0e997e028efc1dd2f3d30dc7e1cdce8`
Path: `дОКУМЕНТЫ ЗАГРУЖАЕМЫЕ В АГЕНТ/Техническое регулирование. Сертификация средств защиты информации/Постановление Правительства РФ от 26.06.1995 N 608 О сертификации средств защиты информации/Постановление Правите.txt`
Type: TXT
Size: `30417` bytes
Blob SHA: `ed96d5870c4b445f31d72b2bab519ff87bbd2fb1`

Identity/body verification:
- internal title: Постановление Правительства РФ от 26 июня 1995 г. N 608 «О сертификации средств защиты информации»;
- contains the Government operative part (`Правительство Российской Федерации постановляет`, points 1–2, signature);
- contains the attached `Положение о сертификации средств защиты информации`;
- amendment chain in copy: 23.04.1996 №509, 29.03.1999 №342, 17.12.2004 №808, 21.04.2010 №266.

Classification: `FULL_TEXT / GARANT_EXPORT / NON_OFFICIAL_GITHUB_COPY / CURRENT_CANDIDATE`.

Companion format variant in same directory:
- PDF, size `110812` bytes, blob `47f49410960576aecb89f9e31a8034dc39168b19`.
- Classification: `SAME_ACT_FORMAT_VARIANT`, not exact duplicate.

### Currentness / official status

Current legal-reference pages still expose PP RF №608 in revision `21.04.2010`; no later amendment was identified in this pass. A 2026 FSTEC order (20.01.2026 №9, official publication no. `0001202604210031`, published 21.04.2026, effective 02.05.2026) amends the FSTEC certification-system regulation built on the certification framework, which is consistent with the continued legal relevance of №608.

However, the primary official publication page for the old 1995 Government act itself was not reliably retrievable during this pass. Therefore do **not** promote to `VERIFIED_CURRENT` yet.

Current blocker: `PRIMARY_OFFICIAL_LIFECYCLE_CONFIRMATION_PENDING`.

## 2. Independent historical mirror — Libertarium

Repository: `Libertarium/libertarium.github.io`
Commit: `fab8b847f5de3a1d7a012bb42dbda57d42303ba9`
Path: `1500997a7.html`
Type: HTML mirror (HTTrack snapshot, 2020)

Body verification:
- correct act/date/number context for PP RF №608;
- contains the attached `Положение о сертификации средств защиты информации`;
- explicitly labels revision only through PP RF 23.04.1996 №509 in the visible normative block;
- parent Government operative clauses are not present as a complete standalone act in the inspected content.

Classification: `SUBSTANTIVE_ATTACHMENT_FULL / PARENT_ACT_PARTIAL / HISTORICAL / NON_OFFICIAL_MIRROR`.

Use: independent corroboration of the attachment text only; reject as the canonical full NPA copy.

## 3. Open blockers carried forward

No new standalone verified GitHub bodies were confirmed in this pass for:
- 247-ФЗ/2020;
- 258-ФЗ/2020;
- 242-ФЗ/03.12.2008 on state genomic registration;
- RKN orders 128/178/179/180/187;
- PP RF 1722/2020 and 336/2022.

## Normalizer rule reinforced

`PARENT_ACT + ATTACHMENT` must be verified as a complete legal object. A page containing a full regulation/appendix but omitting the parent act's operative part is not a FULL_TEXT copy of the whole NPA.
