# Домашнее задание — Многоуровневое проектирование: C4 -> Sequence -> OpenAPI

Кейс: `FATHER Knowledge Factory / Research Graph`.

## 1. C2 Container Diagram

Обязательные контейнеры:
- Frontend;
- Backend API;
- AI / Evidence Service;
- Vector DB;
- SQL DB.

Дополнительно показаны Original Store, Review/Promotion Service, Trace/Audit Store и LLM Endpoint, потому что они следуют из требований FR-001/003/009/010 и не могут быть спрятаны без потери архитектурной ответственности.

Артефакт: `diagrams/c2-containers.mmd`.
Structurizr source: `structurizr/workspace.dsl`, view `C2`.

## 2. C3 Component Diagram — AI / Evidence Service

Компоненты:
- Recommendation Controller;
- Policy Guard;
- RAG Manager;
- Evidence Retriever;
- Prompt Template Factory;
- LLM Client;
- Citation Validator;
- Knowledge Projector;
- Audit Emitter.

Артефакт: `diagrams/c3-ai-evidence-service.mmd`.
Structurizr source: `structurizr/workspace.dsl`, view `C3-AI`.

## 3. Sequence Diagram — Пользователь запрашивает рекомендацию

Сценарий:
`Analyst -> Frontend -> Backend -> Recommendation Controller -> Policy Guard -> RAG Manager -> Vector DB/Evidence Retriever -> Prompt Template Factory -> LLM Client -> Citation Validator -> Knowledge Projector -> Audit Emitter -> Backend -> Frontend`.

Артефакт: `diagrams/sequence-get-recommendation.mmd`.

## 4. API Spec

Internal Backend-to-AI endpoint:

`POST /get_recommendation`

Формат: OpenAPI 3.1 YAML.

Артефакт: `api/openapi.yaml`.

Request содержит `request_id`, `trace_id`, `project_id`, `question`, `role`, retrieval options.
Response содержит `status`, answer, claims, citations, warnings, audit metadata и тот же `trace_id`.

## 5. Согласованность представлений

Правила:
- имена контейнеров C2 используются без переименования на C3/Sequence;
- Sequence вызывает только существующие контейнеры/компоненты;
- операция Sequence существует в OpenAPI;
- `trace_id` проходит Backend -> AI Service -> downstream calls;
- claim без подтверждённого evidence не получает verified/KB_READY статус.

## 6. Трассировка требований

- FR-001/002 -> ingestion/original/document pipeline;
- FR-003 -> Evidence Retriever + canonical evidence storage;
- FR-004 -> review path;
- FR-005 -> graph/role projection;
- FR-006 -> Backend/report surface;
- FR-007 -> versioning/original store;
- FR-008 -> storage boundaries;
- FR-009 -> Audit Emitter/Trace Store;
- FR-010 -> Review/Promotion Service;
- FR-011 -> Knowledge Projector/role_views;
- FR-012 -> typed graph relation `CONTRADICTS`.

## 7. Что сдавать

Для задания достаточно приложить ссылки на:
1. Structurizr DSL / Mermaid C2;
2. Mermaid C3;
3. Mermaid Sequence;
4. OpenAPI YAML.

Все четыре артефакта находятся в этом package и версионируются вместе с Product/Analytics/Architecture документами.
