from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Check:
    name: str
    passed: bool
    evidence: str


def exists_nonempty(root: Path, path: str) -> Check:
    target = root / path
    passed = target.is_file() and target.stat().st_size > 80
    return Check(path, passed, "present and non-empty" if passed else "missing or placeholder-sized")


def any_files(root: Path, pattern: str, name: str) -> Check:
    found = [p for p in root.glob(pattern) if p.is_file() and p.stat().st_size > 0]
    return Check(name, bool(found), f"{len(found)} matching file(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evidence-based repository premium gate")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json", dest="json_path", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    dimensions: dict[str, list[Check]] = {
        "architecture": [
            exists_nonempty(root, "ARCHITECTURE.md"),
            any_files(root, ".ai/*.yaml", "machine-readable architecture policies"),
            any_files(root, "templates/*.yaml", "canonical record templates"),
        ],
        "documentation": [
            exists_nonempty(root, "README.md"),
            exists_nonempty(root, "ROADMAP.md"),
            exists_nonempty(root, "CONTRIBUTING.md"),
        ],
        "code_quality": [
            any_files(root, "tools/*.py", "tooling"),
            any_files(root, "runtime/*.py", "runtime code"),
            any_files(root, "**/test_*.py", "Python tests"),
        ],
        "tests_ci": [
            any_files(root, ".github/workflows/*.yml", "CI workflows"),
            any_files(root, "tools/validate_*.py", "validators"),
            any_files(root, "**/test_*.py", "automated tests"),
        ],
        "security": [
            exists_nonempty(root, "SECURITY.md"),
            any_files(root, ".ai/*security*.yaml", "security policies"),
            any_files(root, "security-core/**/*.yaml", "security canonical records"),
        ],
        "evidence": [
            any_files(root, "sources/**/*.yaml", "sources"),
            any_files(root, "claims/**/*.yaml", "claims"),
            any_files(root, "decisions/**/*.yaml", "decisions"),
        ],
        "agent_readability": [
            exists_nonempty(root, ".ai/agent-query-api-contract.yaml"),
            any_files(root, "templates/*.yaml", "machine-readable templates"),
            exists_nonempty(root, "tools/build_knowledge_index.py"),
        ],
        "visual_consistency": [
            exists_nonempty(root, "PREMIUM_REPOSITORY_STANDARD.md"),
            exists_nonempty(root, "README.md"),
        ],
    }

    weights = {
        "architecture": 15, "documentation": 15, "code_quality": 15, "tests_ci": 15,
        "security": 15, "evidence": 15, "agent_readability": 5, "visual_consistency": 5,
    }
    scores = {
        name: round(100 * sum(c.passed for c in checks) / len(checks), 1)
        for name, checks in dimensions.items()
    }
    total = round(sum(scores[name] * weights[name] / 100 for name in scores), 1)
    critical = {"architecture", "documentation", "code_quality", "tests_ci", "security", "evidence"}
    premium = total >= 90 and all(scores[name] >= 90 for name in critical)

    report = {
        "score": total,
        "premium": premium,
        "dimensions": scores,
        "checks": {name: [asdict(c) for c in checks] for name, checks in dimensions.items()},
        "note": "Structural score only; qualitative review remains required for claims, design and visual quality.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
