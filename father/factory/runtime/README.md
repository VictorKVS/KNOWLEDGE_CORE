# FATHER Model Zoo Runtime — MVP

Status: `FIRST EXECUTABLE SLICE`

This package turns the existing FATHER automation contracts into a minimal executable decision pipeline:

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

## What it deliberately does not do yet

- no autonomous final approval;
- no legal applicability or residual-risk acceptance by models;
- no background promotion;
- no provider secrets in repository;
- no database/message broker requirement;
- no claim that an LLM vote is evidence.

## Providers in the first slice

- `fixture` — deterministic tests/demos;
- `ollama` — local `/api/chat`;
- `openai_compatible` — generic `/v1/chat/completions` for local or remote compatible servers.

Provider-specific adapters can be added behind the same interface later.

## Run deterministic demo

From repository root:

```bash
python -m father.factory.runtime run \
  --registry father/factory/runtime/examples/model_registry.fixture.json \
  --request father/factory/runtime/examples/decision_request.json \
  --data-dir data/father_runtime_demo
```

The command writes a decision packet snapshot plus append-only audit JSONL.

## Record human approval

Use the emitted packet path:

```bash
python -m father.factory.runtime approve \
  --packet data/father_runtime_demo/decision_packets/<panel-run-id>.json \
  --approval father/factory/runtime/examples/approval.json \
  --data-dir data/father_runtime_demo
```

The role must match `required_human_authority` in the packet.

## Tests

No third-party test framework is required:

```bash
python -m unittest discover -s tests/runtime -p 'test_*.py' -v
```

Covered in the first slice:

- materiality routing;
- sensitive-data provider filtering;
- four-challenger architecture panel;
- independent judge identity;
- fail-closed invented evidence references;
- mandatory authorized human gate.

## Next runtime layers

1. evidence resolvers for repository/file/clause refs;
2. prompt/version registry and hashable input snapshots;
3. cross-examination round on material dissent;
4. Model Zoo telemetry and adaptive routing;
5. GenAI Quality Gate integration;
6. document pipeline workers (extract/map/conflict/review);
7. FastAPI + web workbench;
8. persistent DB/queue only after runtime load/operability needs are measured.
