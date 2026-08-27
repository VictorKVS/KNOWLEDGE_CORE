# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass, asdict


@dataclass
class ModelEndpoint:
    server: str
    models_url: str
    chat_url: str
    models: list[str]


ENDPOINTS = [
    ("llama.cpp/common", "http://127.0.0.1:8080/v1/models", "http://127.0.0.1:8080/v1/chat/completions"),
    ("LM Studio", "http://127.0.0.1:1234/v1/models", "http://127.0.0.1:1234/v1/chat/completions"),
    ("OpenAI-compatible 8000", "http://127.0.0.1:8000/v1/models", "http://127.0.0.1:8000/v1/chat/completions"),
    ("OpenAI-compatible 5000", "http://127.0.0.1:5000/v1/models", "http://127.0.0.1:5000/v1/chat/completions"),
    ("Ollama OpenAI compatibility", "http://127.0.0.1:11434/v1/models", "http://127.0.0.1:11434/v1/chat/completions"),
]

TRANSLATOR_PREFS = [
    "qwen2.5-14b-instruct",
    "qwen2.5-14b",
    "qwen2.5",
    "gigachat3-10b",
    "gigachat-20b",
    "gigachat",
    "qwen",
]

REVIEWER_PREFS = [
    "gigachat3-10b",
    "gigachat-20b",
    "gigachat",
    "qwen2.5-14b-instruct",
    "qwen2.5-14b",
    "qwen2.5",
    "qwen",
]


def _get_json(url: str, timeout: float = 2.0) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _model_ids(data: dict) -> list[str]:
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return [str(x.get("id")) for x in data["data"] if isinstance(x, dict) and x.get("id")]
    return []


def discover() -> list[ModelEndpoint]:
    found: list[ModelEndpoint] = []
    for server, models_url, chat_url in ENDPOINTS:
        try:
            data = _get_json(models_url)
            models = _model_ids(data)
            if models:
                found.append(ModelEndpoint(server, models_url, chat_url, models))
        except Exception:
            pass
    return found


def _score(model: str, prefs: list[str]) -> int:
    low = model.lower()
    for idx, pref in enumerate(prefs):
        if pref in low:
            return 1000 - idx * 100
    return 100


def choose(endpoint: ModelEndpoint, prefs: list[str]) -> str:
    return sorted(endpoint.models, key=lambda m: (-_score(m, prefs), m.lower()))[0]


def select_pair(found: list[ModelEndpoint]) -> dict:
    if not found:
        raise RuntimeError("No OpenAI-compatible local model server with a loaded model was detected.")

    # Prefer one server exposing at least two models so translator and reviewer can differ.
    multi = sorted(found, key=lambda e: (-len(e.models), e.server.lower()))
    endpoint = multi[0]
    translator = choose(endpoint, TRANSLATOR_PREFS)

    reviewer_candidates = [m for m in endpoint.models if m != translator] or endpoint.models
    reviewer_endpoint = ModelEndpoint(endpoint.server, endpoint.models_url, endpoint.chat_url, reviewer_candidates)
    reviewer = choose(reviewer_endpoint, REVIEWER_PREFS)

    return {
        "server": endpoint.server,
        "chat_url": endpoint.chat_url,
        "translator_model": translator,
        "reviewer_model": reviewer,
        "same_model": translator == reviewer,
        "all_models_on_server": endpoint.models,
    }


def main() -> int:
    print("FATHER MODEL ZOO")
    print("=" * 72)
    found = discover()
    if not found:
        print("No loaded OpenAI-compatible local models detected.")
        print("Start llama.cpp, LM Studio, Ollama or another compatible server and run again.")
        return 2

    for ep in found:
        print(f"OK  {ep.server}")
        print(f"    chat: {ep.chat_url}")
        print(f"    models: {', '.join(ep.models)}")

    selected = select_pair(found)
    print("\nSELECTED FOR FACTORY")
    print(json.dumps(selected, ensure_ascii=False, indent=2))
    print("\nPowerShell:")
    print(f"$env:FATHER_LLM_BASE_URL='{selected['chat_url']}'")
    print(f"$env:FATHER_TRANSLATOR_MODEL='{selected['translator_model']}'")
    print(f"$env:FATHER_REVIEWER_MODEL='{selected['reviewer_model']}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
