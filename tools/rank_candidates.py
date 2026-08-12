from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HEALTH_SCORE = {"GREEN": 1.0, "YELLOW": 0.5, "RED": 0.0, "": 0.25, "UNKNOWN": 0.25}
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

WEIGHTS = {
    "semantic_relevance": 20,
    "context_match": 25,
    "evidence_health": 20,
    "maturity": 10,
    "applicability": 10,
    "successful_outcomes": 10,
    "freshness": 5,
}

PENALTIES = {
    "open_noncritical_contradiction": 20,
    "evidence_gap": 10,
    "stale_dependency": 15,
    "context_unknown": 8,
    "medium_confidence_claim": 5,
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def candidate_score(candidate: dict[str, Any]) -> dict[str, Any]:
    hard_blocks = list(candidate.get("hard_blocks") or [])
    if str(candidate.get("health", "")).upper() == "RED" and "health_red" not in hard_blocks:
        hard_blocks.append("health_red")
    if candidate.get("hard_context_mismatch") is True and "hard_context_mismatch" not in hard_blocks:
        hard_blocks.append("hard_context_mismatch")

    semantic = normalize(candidate.get("semantic_relevance", 0))
    context = normalize(candidate.get("context_match", 0))
    health = HEALTH_SCORE.get(str(candidate.get("health", "UNKNOWN")).upper(), 0.25)
    maturity = MATURITY_SCORE.get(str(candidate.get("maturity") or candidate.get("status") or "").upper(), 0.25)
    applicability = normalize(candidate.get("applicability_match", context))
    outcomes = normalize(candidate.get("successful_outcomes", 0))
    freshness = normalize(candidate.get("freshness", 0.5))

    dimensions = {
        "semantic_relevance": semantic * WEIGHTS["semantic_relevance"],
        "context_match": context * WEIGHTS["context_match"],
        "evidence_health": health * WEIGHTS["evidence_health"],
        "maturity": maturity * WEIGHTS["maturity"],
        "applicability": applicability * WEIGHTS["applicability"],
        "successful_outcomes": outcomes * WEIGHTS["successful_outcomes"],
        "freshness": freshness * WEIGHTS["freshness"],
    }

    penalties = {}
    flags = set(candidate.get("flags") or [])
    for name, amount in PENALTIES.items():
        if name in flags:
            penalties[name] = amount

    raw_score = round(sum(dimensions.values()) - sum(penalties.values()), 2)
    eligible = not hard_blocks
    return {
        "id": candidate.get("id", ""),
        "eligible": eligible,
        "score": raw_score if eligible else None,
        "hard_blocks": hard_blocks,
        "dimensions": {k: round(v, 2) for k, v in dimensions.items()},
        "penalties": penalties,
        "explanation": candidate.get("explanation", ""),
        "source": candidate,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank engineering knowledge candidates with explainable factors")
    parser.add_argument("input", type=Path, help="JSON list of candidate feature objects")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    data = load(args.input)
    candidates = data if isinstance(data, list) else data.get("candidates", [])
    ranked = [candidate_score(item) for item in candidates if isinstance(item, dict)]
    ranked.sort(key=lambda item: (not item["eligible"], -(item["score"] or -10_000), item["id"]))
    result = ranked[: args.limit]
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
