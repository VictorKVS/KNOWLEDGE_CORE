# -*- coding: utf-8 -*-
import json
import urllib.error
import urllib.request

OPENAI_ENDPOINTS = [
    ("llama.cpp/common", "http://127.0.0.1:8080/v1/models", "http://127.0.0.1:8080/v1/chat/completions"),
    ("LM Studio", "http://127.0.0.1:1234/v1/models", "http://127.0.0.1:1234/v1/chat/completions"),
    ("OpenAI-compatible 8000", "http://127.0.0.1:8000/v1/models", "http://127.0.0.1:8000/v1/chat/completions"),
    ("OpenAI-compatible 5000", "http://127.0.0.1:5000/v1/models", "http://127.0.0.1:5000/v1/chat/completions"),
]


def get_json(url, timeout=2):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def model_ids(data):
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return [str(x.get("id")) for x in data["data"] if isinstance(x, dict) and x.get("id")]
    return []


def main():
    print("FATHER LOCAL MODEL PROBE")
    print("=" * 72)
    found = 0
    for name, models_url, chat_url in OPENAI_ENDPOINTS:
        try:
            data = get_json(models_url)
            models = model_ids(data)
            found += 1
            print(f"OK  {name}")
            print(f"    chat:   {chat_url}")
            print(f"    models: {', '.join(models) if models else '(server answered; model list not parsed)'}")
            if models:
                print("    PowerShell:")
                print(f"    $env:FATHER_LLM_BASE_URL='{chat_url}'")
                print(f"    $env:FATHER_TRANSLATOR_MODEL='{models[0]}'")
                print(f"    $env:FATHER_REVIEWER_MODEL='{models[0]}'")
        except Exception:
            pass

    try:
        data = get_json("http://127.0.0.1:11434/api/tags")
        models = [x.get("name") for x in data.get("models", []) if isinstance(x, dict) and x.get("name")]
        found += 1
        print("OK  Ollama detected")
        print(f"    models: {', '.join(models) if models else '(none)'}")
        print("    Note: M1 translator currently expects an OpenAI-compatible chat endpoint.")
    except Exception:
        pass

    if not found:
        print("No supported local model server detected on common localhost ports.")
        print("Start llama.cpp/LM Studio OpenAI-compatible server, then run this probe again.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
