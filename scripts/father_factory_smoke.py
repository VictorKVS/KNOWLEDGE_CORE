# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from father_model_zoo import discover, select_pair

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "father" / "agent-factory" / "translation" / "fixtures" / "architecture_security_smoke_en.txt"
FACTORY = REPO_ROOT / "scripts" / "father_translation_factory.py"
OUTPUT = Path(r"G:\1\FATHER_TRANSLATION_FACTORY")
SMOKE_DIR = OUTPUT / "smoke"
INVENTORY = SMOKE_DIR / "smoke_inventory.csv"


def write_inventory() -> None:
    SMOKE_DIR.mkdir(parents=True, exist_ok=True)
    with INVENTORY.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["full_path", "filename", "category"], delimiter=";")
        writer.writeheader()
        writer.writerow({
            "full_path": str(FIXTURE),
            "filename": "architecture_security_smoke_en.txt",
            "category": "architecture security software engineering",
        })


def main() -> int:
    print("=" * 72)
    print("FATHER FACTORY SMOKE — MODEL ZOO -> EN TEXT -> TRANSLATION FACTORY")
    print("=" * 72)

    if not FIXTURE.exists():
        raise FileNotFoundError(f"Smoke fixture not found: {FIXTURE}")
    if not FACTORY.exists():
        raise FileNotFoundError(f"Translation factory not found: {FACTORY}")

    found = discover()
    if not found:
        print("No loaded OpenAI-compatible local model server detected.")
        print("Run PROBE_FATHER_LOCAL_LLM.cmd after starting a local model server.")
        return 2

    selected = select_pair(found)
    print("Selected local model configuration:")
    print(json.dumps(selected, ensure_ascii=False, indent=2))

    write_inventory()

    env = os.environ.copy()
    env["FATHER_LLM_BASE_URL"] = selected["chat_url"]
    env["FATHER_TRANSLATOR_MODEL"] = selected["translator_model"]
    env["FATHER_REVIEWER_MODEL"] = selected["reviewer_model"]
    env["FATHER_TRANSLATION_QA"] = "1"
    # Smoke run intentionally uses one inference worker to avoid overloading a 12 GB GPU.
    env["FATHER_TRANSLATION_WORKERS"] = "1"
    env["FATHER_TRANSLATION_CHUNK_CHARS"] = "5000"

    print("\nRunning short English text through the real factory...")
    cmd = [
        sys.executable,
        str(FACTORY),
        "--mode", "run",
        "--inventory", str(INVENTORY),
        "--output", str(OUTPUT),
        "--max-books", "1",
        "--max-chunks", "1",
        "--workers", "1",
    ]
    rc = subprocess.call(cmd, env=env, cwd=str(REPO_ROOT))
    if rc != 0:
        print(f"Factory smoke failed with ExitCode={rc}")
        return rc

    print("\nSMOKE SUCCESS")
    print(f"Fixture: {FIXTURE}")
    print(f"Output root: {OUTPUT}")
    print("Open the newest translated/<book_id>/bilingual.md and summary.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
