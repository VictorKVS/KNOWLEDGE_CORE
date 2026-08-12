from __future__ import annotations

import json
from pathlib import Path

import yaml

from knowledge_runtime import KnowledgeRuntime, RuntimeConfig


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def make_runtime(tmp_path: Path) -> KnowledgeRuntime:
    write_yaml(tmp_path / "decisions" / "adr.yaml", {"id": "ADR-TEST-001", "title": "Use bounded queue", "status": "verified", "health": "GREEN", "refs": ["CLM-TEST-001"]})
    write_yaml(tmp_path / "claims" / "claim.yaml", {"id": "CLM-TEST-001", "title": "Bounded queues expose overload", "status": "verified", "health": "GREEN"})
    index = {
        "nodes": [
            {"id": "ADR-TEST-001", "kind": "ADR", "path": "decisions/adr.yaml", "title": "Use bounded queue", "status": "verified", "health": "GREEN", "tags": ["queue", "backpressure"], "refs": ["CLM-TEST-001"]},
            {"id": "CLM-TEST-001", "kind": "CLM", "path": "claims/claim.yaml", "title": "Bounded queues expose overload", "status": "verified", "health": "GREEN", "tags": ["queue"], "refs": []},
        ],
        "edges": [{"from": "ADR-TEST-001", "to": "CLM-TEST-001"}],
    }
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "knowledge-index.json").write_text(json.dumps(index), encoding="utf-8")
    return KnowledgeRuntime(RuntimeConfig(root=tmp_path, index_path=Path("generated/knowledge-index.json")))


def test_get_record(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    assert runtime.get_record("ADR-TEST-001")["title"] == "Use bounded queue"


def test_search(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    result = runtime.search("queue", kinds={"ADR"})
    assert result[0]["id"] == "ADR-TEST-001"


def test_neighborhood_and_impacts(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    graph = runtime.neighborhood("ADR-TEST-001", depth=1)
    assert {node["id"] for node in graph["nodes"]} == {"ADR-TEST-001", "CLM-TEST-001"}
    assert runtime.impacts("CLM-TEST-001") == ["ADR-TEST-001"]


def test_brief_routes_green_to_fast(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    brief = runtime.build_decision_brief(query="queue", owner_agent="programming_agent")
    assert brief["recommendation"]["decision_ref"] == "ADR-TEST-001"
    assert brief["recommendation"]["route"] == "FAST"
