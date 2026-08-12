from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RuntimeConfig:
    root: Path = Path(".")
    index_path: Path = Path("generated/knowledge-index.json")


class KnowledgeRuntime:
    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self.config = config or RuntimeConfig()
        self.root = self.config.root.resolve()
        self.index = self._load_index(self.root / self.config.index_path)
        self.by_id = {node["id"]: node for node in self.index.get("nodes", [])}
        self.reverse_refs: dict[str, list[str]] = {}
        for edge in self.index.get("edges", []):
            self.reverse_refs.setdefault(edge["to"], []).append(edge["from"])

    @staticmethod
    def _load_index(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def get_record(self, record_id: str) -> dict[str, Any]:
        node = self.by_id.get(record_id)
        if not node:
            raise KeyError(f"unknown record id: {record_id}")
        path = self.root / node["path"]
        with path.open("r", encoding="utf-8") as fh:
            record = yaml.safe_load(fh)
        if not isinstance(record, dict):
            raise ValueError(f"canonical record is not an object: {record_id}")
        return record

    def search(self, query: str, *, kinds: set[str] | None = None, limit: int = 10) -> list[dict[str, Any]]:
        terms = [term.lower() for term in query.split() if term.strip()]
        kinds = {kind.upper() for kind in (kinds or set())}
        ranked: list[tuple[int, dict[str, Any]]] = []
        for node in self.index.get("nodes", []):
            if kinds and str(node.get("kind", "")).upper() not in kinds:
                continue
            haystack = " ".join([
                str(node.get("id", "")),
                str(node.get("title", "")),
                " ".join(map(str, node.get("tags", []))),
                str(node.get("status", "")),
                str(node.get("health", "")),
            ]).lower()
            score = sum(3 if term in str(node.get("id", "")).lower() else 1 for term in terms if term in haystack)
            if terms and score == 0:
                continue
            ranked.append((score, node))
        ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
        return [{**node, "score": score} for score, node in ranked[:limit]]

    def neighborhood(self, record_id: str, *, depth: int = 1) -> dict[str, Any]:
        if record_id not in self.by_id:
            raise KeyError(f"unknown record id: {record_id}")
        seen = {record_id}
        frontier = {record_id}
        edges: list[dict[str, str]] = []
        for _ in range(max(depth, 0)):
            next_frontier: set[str] = set()
            for current in frontier:
                node = self.by_id[current]
                for target in node.get("refs", []):
                    edges.append({"from": current, "to": target})
                    if target in self.by_id and target not in seen:
                        seen.add(target)
                        next_frontier.add(target)
                for source in self.reverse_refs.get(current, []):
                    edges.append({"from": source, "to": current})
                    if source in self.by_id and source not in seen:
                        seen.add(source)
                        next_frontier.add(source)
            frontier = next_frontier
        return {
            "root": record_id,
            "nodes": [self.by_id[node_id] for node_id in sorted(seen)],
            "edges": edges,
        }

    def impacts(self, record_id: str) -> list[str]:
        if record_id not in self.by_id:
            raise KeyError(f"unknown record id: {record_id}")
        seen: set[str] = set()
        frontier = [record_id]
        while frontier:
            current = frontier.pop()
            for downstream in self.reverse_refs.get(current, []):
                if downstream not in seen:
                    seen.add(downstream)
                    frontier.append(downstream)
        return sorted(seen)

    def build_decision_brief(self, *, query: str, owner_agent: str, limit: int = 5) -> dict[str, Any]:
        candidates = self.search(query, kinds={"DM", "ADR"}, limit=limit)
        selected = candidates[0] if candidates else None
        selected_health = str(selected.get("health", "UNKNOWN")).upper() if selected else "UNKNOWN"
        if selected is None:
            route = "RESEARCH"
        elif selected_health == "RED":
            route = "BLOCKED"
        elif selected_health == "YELLOW":
            route = "ADAPT"
        else:
            route = "FAST"

        refs = [candidate["id"] for candidate in candidates]
        return {
            "schema_version": "1.0",
            "kind": "decision-brief",
            "status": "GENERATED",
            "problem": {"objective": query, "task_context_ref": ""},
            "recommendation": {
                "summary": selected.get("title", selected["id"]) if selected else "No reusable candidate found",
                "decision_ref": selected["id"] if selected else "",
                "route": route,
                "why_now": "Top indexed candidate after hard runtime availability checks" if selected else "No candidate available",
            },
            "alternatives": [
                {"candidate_ref": candidate["id"], "disposition": "fallback", "reason": "Lower-ranked indexed candidate"}
                for candidate in candidates[1:]
            ],
            "reason_chain": {"candidate_refs": refs},
            "implementation_guidance": {"owner_agent": owner_agent},
            "confidence": {"level": "unknown", "evidence_health": selected_health},
            "provenance": {"generated_by": "knowledge_runtime"},
        }
