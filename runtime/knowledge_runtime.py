from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


HEALTH_SCORE = {"GREEN": 1.0, "YELLOW": 0.5, "RED": 0.0, "UNKNOWN": 0.25, "": 0.25}
MATURITY_SCORE = {
    "REUSABLE": 1.0,
    "VERIFIED": 0.9,
    "APPROVED": 0.9,
    "ADOPTED": 0.85,
    "REVIEWED": 0.75,
    "MEASURED": 0.75,
    "TESTED": 0.65,
    "DOCUMENTED": 0.55,
    "DRAFT": 0.25,
    "": 0.25,
}
CRITICAL_CONTEXT = {"workload", "scale", "data_semantics", "trust_boundary", "failure_model"}


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

    @staticmethod
    def _nonempty(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, dict)):
            return bool(value)
        return True

    @staticmethod
    def _flatten_known(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        return {str(k): v for k, v in value.items() if KnowledgeRuntime._nonempty(v)}

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
                str(node.get("id", "")), str(node.get("title", "")),
                " ".join(map(str, node.get("tags", []))), str(node.get("status", "")),
                str(node.get("health", "")),
            ]).lower()
            score = sum(3 if term in str(node.get("id", "")).lower() else 1 for term in terms if term in haystack)
            if terms and score == 0:
                continue
            ranked.append((score, node))
        ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
        return [{**node, "text_score": score} for score, node in ranked[:limit]]

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
        return {"root": record_id, "nodes": [self.by_id[node_id] for node_id in sorted(seen)], "edges": edges}

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

    def _candidate_context(self, record: dict[str, Any]) -> dict[str, dict[str, Any]]:
        context = record.get("context") if isinstance(record.get("context"), dict) else {}
        applicability = record.get("applicability") if isinstance(record.get("applicability"), dict) else {}
        constraints = record.get("constraints") if isinstance(record.get("constraints"), dict) else {}
        runtime = context.get("runtime") if isinstance(context.get("runtime"), dict) else {
            "language": context.get("language"), "version": context.get("runtime_version"), "compiler": context.get("compiler")
        }
        def section(value: Any, scalar_key: str) -> dict[str, Any]:
            if isinstance(value, dict):
                return self._flatten_known(value)
            return {scalar_key: value} if self._nonempty(value) else {}
        return {
            "workload": section(context.get("workload"), "description"),
            "scale": section(context.get("scale"), "description"),
            "runtime": self._flatten_known(runtime),
            "environment": section(context.get("environment"), "os"),
            "data_semantics": self._flatten_known(applicability.get("data_semantics")),
            "trust_boundary": section(context.get("trust_boundary"), "input_trust"),
            "failure_model": self._flatten_known(applicability.get("failure_model")),
            "compatibility": self._flatten_known(applicability.get("compatibility")),
            "operational_constraints": self._flatten_known(constraints.get("operational")),
        }

    def _context_match(self, current: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
        candidate = self._candidate_context(record)
        details: dict[str, Any] = {}
        hard_mismatch = False
        critical_unknown = False
        matched = 0
        comparable = 0
        for dimension, cur_value in current.items():
            cur = self._flatten_known(cur_value)
            cand = candidate.get(dimension, {})
            if not cur:
                continue
            if not cand:
                state = "UNKNOWN"
                notes = ["candidate applicability missing"]
                if dimension in CRITICAL_CONTEXT:
                    critical_unknown = True
            else:
                mismatches = [key for key, value in cur.items() if key in cand and cand[key] != value]
                compared = [key for key in cur if key in cand]
                comparable += len(compared)
                matched += len(compared) - len(mismatches)
                if mismatches:
                    state = "MISMATCH"
                    notes = [f"{key}: current={cur[key]!r}, candidate={cand[key]!r}" for key in mismatches]
                    if dimension in CRITICAL_CONTEXT:
                        hard_mismatch = True
                elif compared:
                    state = "MATCH"
                    notes = [f"matched fields: {', '.join(compared)}"]
                else:
                    state = "UNKNOWN"
                    notes = ["no comparable declared fields"]
                    if dimension in CRITICAL_CONTEXT:
                        critical_unknown = True
            details[dimension] = {"state": state, "notes": notes}
        ratio = 1.0 if not current else (matched / comparable if comparable else 0.5)
        return {
            "score": round(max(0.0, min(1.0, ratio)), 3),
            "hard_context_mismatch": hard_mismatch,
            "critical_context_unknown": critical_unknown,
            "details": details,
        }

    def rank_candidates(self, query: str, *, context: dict[str, Any] | None = None, limit: int = 10) -> list[dict[str, Any]]:
        raw = self.search(query, kinds={"DM", "ADR"}, limit=max(limit * 3, 20))
        max_text = max([item.get("text_score", 0) for item in raw] or [1])
        ranked: list[dict[str, Any]] = []
        for node in raw:
            record = self.get_record(node["id"])
            health = str(node.get("health") or record.get("health") or "UNKNOWN").upper()
            ctx = self._context_match(context or {}, record)
            hard_blocks: list[str] = []
            if health == "RED": hard_blocks.append("health_red")
            if ctx["hard_context_mismatch"]: hard_blocks.append("hard_context_mismatch")
            graph = self.neighborhood(node["id"], depth=2)
            linked_ids = {item["id"] for item in graph["nodes"]}
            con_refs = sorted(ref for ref in linked_ids if ref.startswith("CON-"))
            rq_refs = sorted(ref for ref in linked_ids if ref.startswith("RQ-"))
            open_conflicts = []
            for ref in con_refs:
                try:
                    if str(self.get_record(ref).get("status", "OPEN")).upper() == "OPEN": open_conflicts.append(ref)
                except Exception:
                    open_conflicts.append(ref)
            if open_conflicts:
                hard_blocks.append("open_contradiction")
            semantic = (node.get("text_score", 0) / max_text) if max_text else 0.0
            maturity = MATURITY_SCORE.get(str(record.get("status", "")).upper(), 0.25)
            health_score = HEALTH_SCORE.get(health, 0.25)
            score = round(
                semantic * 20 + ctx["score"] * 25 + health_score * 20 + maturity * 10
                + ctx["score"] * 10 + (5 if not rq_refs else 0) + 5,
                2,
            )
            if rq_refs: score -= 10
            ranked.append({
                "id": node["id"], "title": node.get("title", ""), "health": health,
                "eligible": not hard_blocks, "score": score if not hard_blocks else None,
                "hard_blocks": hard_blocks, "context": ctx,
                "contradiction_refs": con_refs, "open_contradictions": open_conflicts,
                "research_task_refs": rq_refs,
                "dimensions": {
                    "semantic_relevance": round(semantic * 20, 2), "context_match": round(ctx["score"] * 25, 2),
                    "evidence_health": round(health_score * 20, 2), "maturity": round(maturity * 10, 2),
                },
            })
        ranked.sort(key=lambda item: (not item["eligible"], -(item["score"] if item["score"] is not None else -10000), item["id"]))
        return ranked[:limit]

    def build_decision_brief(self, *, query: str, owner_agent: str, context: dict[str, Any] | None = None, limit: int = 5) -> dict[str, Any]:
        candidates = self.rank_candidates(query, context=context or {}, limit=limit)
        eligible = [item for item in candidates if item["eligible"]]
        selected = eligible[0] if eligible else None
        if selected is None:
            route = "RESEARCH" if candidates else "RESEARCH"
        elif selected["health"] != "GREEN" or selected["context"]["critical_context_unknown"] or selected["research_task_refs"]:
            route = "ADAPT"
        else:
            route = "FAST"

        selected_record = self.get_record(selected["id"]) if selected else {}
        graph = self.neighborhood(selected["id"], depth=2) if selected else {"nodes": []}
        linked = sorted(node["id"] for node in graph["nodes"] if node["id"] != (selected or {}).get("id"))
        refs_by_prefix = lambda prefix: [ref for ref in linked if ref.startswith(prefix)]
        rejected = []
        for candidate in candidates:
            if selected and candidate["id"] == selected["id"]:
                continue
            reason = ", ".join(candidate["hard_blocks"]) if candidate["hard_blocks"] else "lower explainable ranking score"
            rejected.append({"candidate_ref": candidate["id"], "disposition": "rejected", "reason": reason})

        return {
            "schema_version": "1.0", "kind": "decision-brief", "status": "GENERATED",
            "problem": {"objective": query, "task_context_ref": ""},
            "context": context or {},
            "recommendation": {
                "summary": selected.get("title") or selected["id"] if selected else "No reusable candidate passed hard filters",
                "decision_ref": selected["id"] if selected else "", "route": route,
                "why_now": "Best eligible candidate after evidence, context and contradiction gates" if selected else "Existing candidates are blocked or absent",
            },
            "alternatives": rejected,
            "reason_chain": {
                "claim_refs": refs_by_prefix("CLM-"), "source_refs": refs_by_prefix("SRC-"),
                "test_refs": refs_by_prefix("TEST-"), "benchmark_refs": refs_by_prefix("BENCH-"),
                "experiment_refs": refs_by_prefix("EXP-"), "outcome_refs": refs_by_prefix("OUT-"),
            },
            "applicability": {
                "matched": selected["context"]["details"] if selected else {},
                "limitations": selected_record.get("limitations", []) if isinstance(selected_record, dict) else [],
            },
            "security": {
                "requirement_refs": refs_by_prefix("SEC-REQ-"), "threat_refs": refs_by_prefix("SEC-THREAT-"),
                "control_refs": refs_by_prefix("SEC-CTRL-"), "mandatory_checks": refs_by_prefix("SEC-CHECK-"),
                "blockers": selected["hard_blocks"] if selected else ["no_eligible_candidate"],
            },
            "implementation_guidance": {"owner_agent": owner_agent, "adaptation_required": [] if route == "FAST" else ["revalidate changed or unknown assumptions"]},
            "verification": {"required_tests": refs_by_prefix("TEST-"), "required_benchmarks": refs_by_prefix("BENCH-"), "required_security_checks": refs_by_prefix("SEC-CHECK-")},
            "unknowns": {"material_unknowns": [], "research_task_refs": selected["research_task_refs"] if selected else []},
            "conflicts": {"contradiction_refs": selected["contradiction_refs"] if selected else [], "unresolved_positions": selected["open_contradictions"] if selected else []},
            "confidence": {
                "level": "HIGH" if selected and selected["health"] == "GREEN" and route == "FAST" else "LIMITED",
                "rationale": "Derived from evidence health, context match and hard filters",
                "evidence_health": selected["health"] if selected else "UNKNOWN",
            },
            "ranking": candidates,
            "provenance": {"generated_by": "knowledge_runtime", "knowledge_index_version": self.index.get("schema_version", "")},
        }
