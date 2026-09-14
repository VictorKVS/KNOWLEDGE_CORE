# FATHER Paper Pipeline — Review Checklist

Status: `REVIEW REQUIRED BEFORE AUTOMATION RESUME`

Цель checklist — проверить не красоту схемы, а **полноту алгоритма принятия и передачи инженерной информации**.

## 1. Источники и authority

- [ ] Для каждого класса источника определён authority/priority.
- [ ] Нормативные источники отделены от профессиональных рекомендаций.
- [ ] Применимость overlay определяется по фактам проекта, а не «на всякий случай».
- [ ] Superseded/retired источники не используются как текущая норма.
- [ ] Для автоматизируемого normative blocker существует точная `source → clause → requirement` трасса.
- [ ] Книжная идея не становится правилом без source verification и independent review.

## 2. Полнота стадий A0–A16

Для каждой стадии:

- [ ] понятна цель;
- [ ] перечислены обязательные входные данные;
- [ ] перечислены выходные канонические артефакты;
- [ ] понятны методы обработки;
- [ ] назначен accountable owner;
- [ ] назначены reviewers;
- [ ] определён exit gate;
- [ ] определены valid `UNKNOWN/GAP/CONFLICTED/NOT_APPLICABLE` состояния;
- [ ] определён возврат на предыдущую стадию при дефекте входа;
- [ ] downstream не использует неподтверждённый candidate как факт.

## 3. Документы и data dependencies

- [ ] Каждый material artifact имеет входные artifact/data refs.
- [ ] Нет circular dependency, скрывающей missing source.
- [ ] Brownfield source может заполнять несколько artifact fields без создания дублей.
- [ ] Один artifact может иметь несколько представлений без нескольких источников истины.
- [ ] Version/supersession сохраняются.
- [ ] Owner-confirmed meaning отделён от LLM reconstruction.

## 4. Requirements / Architecture separation

- [ ] Product problem не подменён заранее выбранной технологией.
- [ ] System model формируется до architecture option selection.
- [ ] Threat Model v0 существует до architecture choice.
- [ ] Requirements/NFR имеют measure/verification intent или явный baseline gap.
- [ ] Architecture starts only after upstream gates.
- [ ] Architecture produces multiple options where decision is material.
- [ ] Accepted architecture has evidence, trade-offs, risk and revisit triggers.
- [ ] Detailed design does not silently alter target architecture/requirements.

## 5. Security / Legal / Data

- [ ] Security starts after Product and remains continuous.
- [ ] Legal applicability final decision belongs to Legal/Compliance.
- [ ] Data classification/use/retention final decision belongs to Data Owner.
- [ ] Security Engineer cannot accept residual risk unless separately designated Risk Owner.
- [ ] Threat → security driver → requirement → control → test → evidence trace is possible.
- [ ] AI external processing is gated by approved data policy.

## 6. Verification / Release / Operation

- [ ] Requirement → test coverage is bidirectional.
- [ ] Security and GenAI quality tests are distinct but traceable to same baseline.
- [ ] Load/performance evidence validates sizing assumptions.
- [ ] Release manifest identifies exact build/config/data/model/prompt/index versions where applicable.
- [ ] Rollback/migration evidence exists before Production Ready.
- [ ] SLO/observability are derived from NFR and critical journeys.
- [ ] Incidents/cost/drift create lifecycle feedback, not isolated reports.

## 7. Evolution and retirement

- [ ] Technology radar is evidence-driven, not trend-driven.
- [ ] Architecture Health Review has explicit triggers.
- [ ] New regulation/business/load/cost/incident reopens smallest necessary lifecycle stage.
- [ ] Old ADR is superseded, not rewritten.
- [ ] API lifecycle/deprecation is explicit when external consumers exist.
- [ ] Retirement covers data, access, providers, consumers and archive evidence.

## 8. OTUS 1–31 crosswalk

- [ ] Every lesson has one or more FATHER stageRefs.
- [ ] Later lessons are invoked earlier when NFR/applicability requires them.
- [ ] Course example technology is not automatically production technology.
- [ ] G1–G7 are learning milestones, not substitutes for FATHER gates.

## 9. Model Zoo / LLM future automation

- [ ] Each future LLM use has a bounded input/output contract.
- [ ] Model-generated facts require resolvable evidence refs.
- [ ] Model Zoo is an analysis/review mechanism, not a lifecycle stage.
- [ ] Full zoo is used only by materiality rule.
- [ ] Blind challengers preserve independent dissent.
- [ ] Human/domain authority remains final where required.
- [ ] Automation fail-closes on missing owner/evidence/policy.
- [ ] Runtime remains frozen until activation prerequisites pass.

## 10. Mandatory paper walkthrough scenarios

Before automation resume, manually walk through:

1. **Greenfield ordinary web/service system** — sparse initial documentation.
2. **Brownfield system** — code/API/docs already exist and conflict in places.
3. **AI/RAG system** — external LLM + retrieved untrusted content + eval dataset.
4. **Regulated data case** — applicability/Data Owner decisions required.
5. **Material architecture dispute** — two viable options and unresolved trade-off.
6. **Incident-driven change** — SLO/security incident reopens design.
7. **Retirement** — consumers, data retention and access revocation.

For every walkthrough record:

`input → stage → artifact change → owner/reviewer → gate → rework/forward → evidence refs`.

## Acceptance

Paper Pipeline can be promoted from `CANDIDATE` only when the walkthroughs show that no material decision requires an undocumented data dependency, hidden authority decision, or unmapped rework path.
