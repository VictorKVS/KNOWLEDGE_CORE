# Document lifecycle flags

Use this stage after document identity/version/representation reconciliation and before final master reconciliation.

## Why three layers

Do not use one flat `status` field for amendment, repeal and replacement.

Keep separately:

1. `lifecycle_state` — whether the document/version is in force now;
2. `version_state` — whether a version is current, historical, future or superseded;
3. `change_flags` + transition relations — what changed it, what it changes, and whether a future change is pending.

## Typical lifecycle states

- `EFFECTIVE`
- `FUTURE_EFFECTIVE`
- `PUBLISHED_NOT_EFFECTIVE`
- `PARTIALLY_EFFECTIVE`
- `SUSPENDED`
- `PARTIALLY_SUSPENDED`
- `REPEALED`
- `PARTIALLY_REPEALED`
- `EXPIRED`
- `DRAFT`
- `UNKNOWN`

## Typical change flags

- `HAS_AMENDMENTS`
- `AMENDMENT_PENDING`
- `HAS_PARTIAL_REPEAL`
- `HAS_REPLACEMENT`
- `REPLACEMENT_PENDING`
- `HAS_SUCCESSOR`
- `HAS_CORRECTION`
- `HAS_EXTENSION`
- `STATUS_REVIEW_REQUIRED`

## Required transition relations

Record directed relations rather than replacing historical records:

- `AMENDS` / `AMENDED_BY`
- `REPEALS` / `REPEALED_BY`
- `PARTIALLY_REPEALS` / `PARTIALLY_REPEALED_BY`
- `REPLACES` / `REPLACED_BY`
- `PARTIALLY_REPLACES` / `PARTIALLY_REPLACED_BY`
- `SUPERSEDES_VERSION` / `SUPERSEDED_BY_VERSION`
- `SUSPENDS` / `SUSPENDED_BY`
- `EXTENDS_VALIDITY` / `VALIDITY_EXTENDED_BY`
- `CORRECTS` / `CORRECTED_BY`

Every transition needs evidence, effective date when proven, checked-at timestamp and scope (`WHOLE_DOCUMENT`, `PARTIAL_DOCUMENT`, `SPECIFIC_PROVISIONS`, `UNKNOWN_SCOPE`).

## UI flags

The UI may derive friendly labels:

- 🟢 `ДЕЙСТВУЕТ`
- 🟡 `ИЗМЕНЯЛСЯ`
- 🔵 `ЕСТЬ БУДУЩЕЕ ИЗМЕНЕНИЕ`
- 🟠 `ЧАСТИЧНО УТРАТИЛ СИЛУ`
- 🔴 `УТРАТИЛ СИЛУ`
- 🟣 `ЕСТЬ ЗАМЕНЯЮЩИЙ ДОКУМЕНТ`
- ⚫ `ПРИОСТАНОВЛЕН`
- ⚪ `СТАТУС НЕ ПОДТВЕРЖДЁН`
- ⚠ `ТРЕБУЕТ ПРОВЕРКИ`

These labels are derived display data, not evidence by themselves.

## Codex instruction

> After library collection, hashing and identity/version resolution, read `.ai/document-lifecycle-state.yaml`. For each normative/versioned document build an evidence-backed lifecycle chain. Assign lifecycle_state separately from version_state and change_flags. Record amendment, repeal, partial repeal, replacement, partial replacement, suspension, validity extension and correction as explicit directed relations with source/target IDs, effective date, scope and evidence refs. Do not mark a whole document repealed when only provisions were repealed. Do not switch the current version because a future amendment/replacement date exists until the required enactment/publication/effective evidence is proven. Preserve every historical version. If evidence conflicts or is incomplete, use UNKNOWN/STATUS_REVIEW_REQUIRED rather than guessing.
