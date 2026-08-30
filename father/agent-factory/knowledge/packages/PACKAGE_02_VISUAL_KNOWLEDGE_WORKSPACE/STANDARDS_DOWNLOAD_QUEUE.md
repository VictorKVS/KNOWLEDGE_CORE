# FATHER — Standards Download Queue

Status: ACTIVE
Purpose: download and ingest the smallest useful set of current Russian standards that directly governs FATHER product engineering, secure development, architecture, AI, UX, observability and access control.

## Rule

Do not bulk-download obsolete revisions. For every standard store: designation, title, current status, source URL, source SHA-256, publication/effective date, scope, supersedes/superseded-by, local path, extracted text, requirements, relations, applicability and review state.

## P0 — Download first

| ID | Standard | Why FATHER needs it | Primary artifact |
|---|---|---|---|
| STD-RU-001 | ГОСТ Р 71752-2024 — Искусственный интеллект. Техническое задание. Требования к содержанию | baseline structure for AI technical assignment | MASTER_TZ_V1 |
| STD-RU-002 | ГОСТ Р 59194-2020 — Управление требованиями. Основные положения | requirement lifecycle, verification, validation, change control | Requirement Catalog / Traceability |
| STD-RU-003 | ГОСТ Р 57100-2025 — Системная и программная инженерия. Описание архитектуры | architecture descriptions, viewpoints, model kinds | C4/HLD/LLD/Architecture Studio |
| STD-RU-004 | ГОСТ Р 57193-2025 — Системная и программная инженерия. Процессы жизненного цикла систем | lifecycle process backbone | lifecycle gates / project plan |
| STD-RU-005 | ГОСТ Р 72118-2025 — Защита информации. Системы с конструктивной информационной безопасностью. Методология разработки | secure-by-design overlay on architecture and system lifecycle | Security-by-Design Graph |
| STD-RU-006 | ГОСТ Р 56939-2024 — Защита информации. Разработка безопасного программного обеспечения. Общие требования | Secure SDLC; static/dynamic/composition analysis; vulnerability handling | Secure SDLC / DevSecOps gates |
| STD-RU-007 | ГОСТ Р 58412-2019 — Угрозы безопасности информации при разработке ПО | threat model for development environment and software lifecycle | DEV Threat Model |
| STD-RU-008 | ГОСТ Р 59548-2022 — Регистрация событий безопасности | SECURITY_EVENT schema and audit evidence | Security Event Model |
| STD-RU-009 | ГОСТ Р 59547-2021 — Мониторинг информационной безопасности. Общие положения | monitoring levels, sources, monitoring data protection | Security Monitoring / Cases |
| STD-RU-010 | ГОСТ Р 71207-2024 — Статический анализ ПО. Общие требования | SAST process, error classification, analyst/tool requirements | SAST gate / finding workflow |

## P1 — Download after P0

| ID | Standard | Why | Primary artifact |
|---|---|---|---|
| STD-RU-011 | ГОСТ Р ИСО/МЭК 25010-2015 | software/system quality model | NFR / quality gates |
| STD-RU-012 | ГОСТ Р ИСО 9241-210-2016 | human-centred design | Figma UX / usability acceptance |
| STD-RU-013 | ГОСТ Р ИСО/МЭК 42001-2024 | AI management system | AI governance / roles / controls |
| STD-RU-014 | ПНСТ 838-2023/ИСО/МЭК 23053:2022 | description of ML/AI system components | AI system model |
| STD-RU-015 | ГОСТ Р 70262.1-2022 | identification assurance | IAM identity model |
| STD-RU-016 | ГОСТ Р 70262.2-2025 | authentication assurance | IAM authentication model |
| STD-RU-017 | ГОСТ Р 71753-2024 | accounts and access-right lifecycle | entitlement workflow |
| STD-RU-018 | ГОСТ Р 56938-2016 | virtualization security | container/VM deployment security |

## P2 — High assurance / later production

| ID | Standard | Why |
|---|---|---|
| STD-RU-019 | ГОСТ Р 59453.1-2021 | formal access-control model — general principles |
| STD-RU-020 | ГОСТ Р 59453.2-2021 | verification of formal access-control model |
| STD-RU-021 | ГОСТ Р 59453.3-2025 | recommendations for development of formal access-control model |
| STD-RU-022 | ГОСТ Р 59453.4-2025 | verification of access-control implementations from formal model |

## Do not download as current

- ГОСТ Р 56939-2016 — replaced by ГОСТ Р 56939-2024.
- ГОСТ Р 57193-2016 — replaced by ГОСТ Р 57193-2025.
- ГОСТ Р ИСО 9241-210-2012 — replaced by ГОСТ Р ИСО 9241-210-2016.

Old revisions may later be kept only in VERSION_HISTORY for change analysis.

## Suggested local tree

```text
G:\1\OTUS\Библиотека\FATHER_GOLDEN_LIBRARY\00_STANDARDS\
  00_REGISTRY\
  01_SYSTEM_ENGINEERING\
  02_REQUIREMENTS\
  03_ARCHITECTURE\
  04_SECURE_BY_DESIGN\
  05_SECURE_SDLC\
  06_DEV_THREATS\
  07_SECURITY_EVENTS_MONITORING\
  08_IAM_ACCESS_CONTROL\
  09_QUALITY_UX\
  10_AI_GOVERNANCE\
  99_SUPERSEDED\
```

## Knowledge extraction

Each standard follows:

`OFFICIAL SOURCE -> ORIGINAL -> SHA256 -> STRUCTURE -> CLAUSE -> REQUIREMENT -> DEFINITION -> RELATION -> APPLICABILITY -> CONTROL -> TEST -> EVIDENCE -> KB_READY`

No requirement may be promoted without exact clause/source provenance.
