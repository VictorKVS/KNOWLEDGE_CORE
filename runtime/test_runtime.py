from __future__ import annotations

import json
from pathlib import Path

import yaml

from knowledge_runtime import KnowledgeRuntime, RuntimeConfig


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def make_runtime(tmp_path: Path) -> KnowledgeRuntime:
    write_yaml(tmp_path / "decisions" / "adr.yaml", {
        "id": "ADR-TEST-001", "title": "Use bounded queue", "status": "verified", "health": "GREEN",
        "context": {"workload": {"shape": "bursty"}, "trust_boundary": {"input_trust": "internal"}},
        "refs": ["CLM-TEST-001", "TEST-TEST-001"],
    })
    write_yaml(tmp_path / "decisions" / "red.yaml", {
        "id": "ADR-TEST-RED", "title": "Use bounded queue old", "status": "verified", "health": "RED",
        "context": {"workload": {"shape": "bursty"}},
    })
    write_yaml(tmp_path / "claims" / "claim.yaml", {"id": "CLM-TEST-001", "title": "Bounded queues expose overload", "status": "verified", "health": "GREEN"})
    write_yaml(tmp_path / "tests" / "test.yaml", {"id": "TEST-TEST-001", "title": "Queue overload contract", "status": "tested", "health": "GREEN"})
    index = {
        "schema_version": "1.0",
        "nodes": [
            {"id": "ADR-TEST-001", "kind": "ADR", "path": "decisions/adr.yaml", "title": "Use bounded queue", "status": "verified", "health": "GREEN", "tags": ["queue", "backpressure"], "refs": ["CLM-TEST-001", "TEST-TEST-001"]},
            {"id": "ADR-TEST-RED", "kind": "ADR", "path": "decisions/red.yaml", "title": "Use bounded queue old", "status": "verified", "health": "RED", "tags": ["queue", "backpressure"], "refs": []},
            {"id": "CLM-TEST-001", "kind": "CLM", "path": "claims/claim.yaml", "title": "Bounded queues expose overload", "status": "verified", "health": "GREEN", "tags": ["queue"], "refs": []},
            {"id": "TEST-TEST-001", "kind": "TEST", "path": "tests/test.yaml", "title": "Queue overload contract", "status": "tested", "health": "GREEN", "tags": ["queue"], "refs": []},
        ],
        "edges": [
            {"from": "ADR-TEST-001", "to": "CLM-TEST-001"},
            {"from": "ADR-TEST-001", "to": "TEST-TEST-001"},
        ],
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
    assert {item["id"] for item in result} == {"ADR-TEST-001", "ADR-TEST-RED"}


def test_neighborhood_and_impacts(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    graph = runtime.neighborhood("ADR-TEST-001", depth=1)
    assert {node["id"] for node in graph["nodes"]} == {"ADR-TEST-001", "CLM-TEST-001", "TEST-TEST-001"}
    assert runtime.impacts("CLM-TEST-001") == ["ADR-TEST-001"]


def test_red_candidate_is_hard_blocked(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    ranked = runtime.rank_candidates("queue", context={"workload": {"shape": "bursty"}})
    red = next(item for item in ranked if item["id"] == "ADR-TEST-RED")
    assert red["eligible"] is False
    assert "health_red" in red["hard_blocks"]


def test_brief_routes_matching_green_to_fast(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    brief = runtime.build_decision_brief(
        query="queue", owner_agent="programming_agent",
        context={"workload": {"shape": "bursty"}, "trust_boundary": {"input_trust": "internal"}},
    )
    assert brief["recommendation"]["decision_ref"] == "ADR-TEST-001"
    assert brief["recommendation"]["route"] == "FAST"
    assert brief["reason_chain"]["claim_refs"] == ["CLM-TEST-001"]
    assert brief["verification"]["required_tests"] == ["TEST-TEST-001"]


def test_hard_context_mismatch_blocks_candidate(tmp_path: Path) -> None:
    runtime = make_runtime(tmp_path)
    brief = runtime.build_decision_brief(
        query="queue", owner_agent="programming_agent",
        context={"workload": {"shape": "bursty"}, "trust_boundary": {"input_trust": "external"}},
    )
    assert brief["recommendation"]["decision_ref"] == ""
    assert brief["recommendation"]["route"] == "RESEARCH"
    assert any("hard_context_mismatch" in item["hard_blocks"] for item in brief["ranking"])
