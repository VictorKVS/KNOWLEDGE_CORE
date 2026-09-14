# FATHER Model Zoo Runtime — MVP

Status: `EXECUTABLE BASELINE / FEATURE DEVELOPMENT FROZEN FOR PAPER PIPELINE REVIEW`

The existing runtime baseline remains reproducible and CI-tested, but lifecycle/authority expansion is frozen by:

`father/factory/paper-pipeline/AUTOMATION_ACTIVATION_GATE.yaml`

Current executable pipeline:

```text
DecisionRequest
  → MaterialityRouter
  → Champion
  → Blind Challengers
  → deterministic EvidenceVerifier
  → Independent Judge
  → DecisionPacket
  → authorized Human Approval
  → Gate outcome
```

## Freeze rule

Until the canonical A0–A16 paper pipeline passes manual review/walkthroughs, runtime work is limited to behavior-preserving bug fixes, tests, documentation and deterministic fixture reproduction.

Do **not** add:

- new lifecycle routing semantics;
- autonomous final approval;
- legal applicability decisions by models;
- residual-risk acceptance by models;
- product-scope authority for models;
- Production release authority for models;
- silent candidate → verified promotion.

## What it deliberately does not do

- no autonomous final approval;
- no legal applicability or residual-risk acceptance by models;
- no background promotion;
- no provider secrets in repository;
- no database/message broker requirement;
- no claim that an LLM vote is evidence.

## Providers in the preserved first slice

- `fixture` — deterministic tests/demos;
- `ollama` — local `/api/chat`;
- `openai_compatible` — generic `/v1/chat/completions` for local or remote compatible servers.

## Run deterministic demo

```bash
python -m father.factory.runtime run \
  --registry father/factory/runtime/examples/model_registry.fixture.json \
  --request father/factory/runtime/examples/decision_request.json \
  --data-dir data/father_runtime_demo
```

## Record human approval

```bash
python -m father.factory.runtime approve \
  --packet data/father_runtime_demo/decision_packets/<panel-run-id>.json \
  --approval father/factory/runtime/examples/approval.json \
  --data-dir data/father_runtime_demo
```

The role must match `required_human_authority`.

## Tests

```bash
python -m unittest discover -s tests/runtime -p 'test_*.py' -v
```

The baseline was CI-verified on Python 3.11 and 3.12, including the deterministic fixture end-to-end demo.

Covered:

- materiality routing;
- sensitive-data provider filtering;
- four-challenger architecture panel;
- independent judge identity;
- fail-closed invented evidence references;
- mandatory authorized human gate.

## Resume backlog — intentionally frozen

After Paper Pipeline activation prerequisites pass:

1. evidence resolvers for repository/file/clause refs;
2. prompt/version registry and hashable input snapshots;
3. cross-examination on material dissent;
4. Model Zoo telemetry/adaptive routing;
5. GenAI Quality Gate binding;
6. document workers (extract/map/conflict/review);
7. FastAPI/web workbench;
8. DB/queue only after measured runtime need.
