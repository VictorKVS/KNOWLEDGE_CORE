from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any, Protocol

from .models import ModelRunResult
from .registry import ModelSpec


class ModelAdapter(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        ...


class FixtureAdapter:
    def __init__(self, spec: ModelSpec) -> None:
        self.spec = spec

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.spec.options.get("response")
        if response is None:
            response = {"model": self.spec.model_id, "status": "fixture", "unknowns": []}
        return response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)


class OpenAICompatibleAdapter:
    """Minimal /v1/chat/completions adapter for compatible local or remote servers."""

    def __init__(self, spec: ModelSpec) -> None:
        if not spec.endpoint:
            raise ValueError(f"endpoint is required for {spec.model_id}")
        self.spec = spec

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        endpoint = self.spec.endpoint.rstrip("/") + "/chat/completions"
        body = {
            "model": self.spec.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.spec.options.get("temperature", 0.1),
        }
        headers = {"Content-Type": "application/json"}
        if self.spec.api_key_env:
            key = os.getenv(self.spec.api_key_env)
            if not key:
                raise RuntimeError(f"missing API key env: {self.spec.api_key_env}")
            headers["Authorization"] = f"Bearer {key}"
        payload = _post_json(endpoint, body, headers, self.spec.timeout_seconds)
        try:
            return str(payload["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"unexpected OpenAI-compatible response from {self.spec.model_id}") from exc


class OllamaAdapter:
    def __init__(self, spec: ModelSpec) -> None:
        self.spec = spec
        self.endpoint = (spec.endpoint or "http://127.0.0.1:11434").rstrip("/")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        body = {
            "model": self.spec.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": self.spec.options.get("ollama_options", {}),
        }
        payload = _post_json(self.endpoint + "/api/chat", body, {"Content-Type": "application/json"}, self.spec.timeout_seconds)
        try:
            return str(payload["message"]["content"])
        except (KeyError, TypeError) as exc:
            raise RuntimeError(f"unexpected Ollama response from {self.spec.model_id}") from exc


class AdapterFactory:
    def create(self, spec: ModelSpec) -> ModelAdapter:
        provider = spec.provider.lower()
        if provider == "fixture":
            return FixtureAdapter(spec)
        if provider == "openai_compatible":
            return OpenAICompatibleAdapter(spec)
        if provider == "ollama":
            return OllamaAdapter(spec)
        raise ValueError(f"unsupported provider: {spec.provider}")


def run_model(spec: ModelSpec, role: str, system_prompt: str, user_prompt: str, factory: AdapterFactory) -> ModelRunResult:
    started = time.perf_counter()
    try:
        content = factory.create(spec).generate(system_prompt, user_prompt)
        parsed = parse_json_object(content)
        error = None
    except Exception as exc:
        content = ""
        parsed = {}
        error = f"{type(exc).__name__}: {exc}"
    duration_ms = int((time.perf_counter() - started) * 1000)
    return ModelRunResult(
        model_id=spec.model_id,
        provider=spec.provider,
        role=role,
        content=content,
        parsed=parsed,
        duration_ms=duration_ms,
        error=error,
    )


def parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.S | re.I)
    if fenced:
        text = fenced.group(1).strip()
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {"value": value}
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                value = json.loads(text[start : end + 1])
                return value if isinstance(value, dict) else {"value": value}
            except json.JSONDecodeError:
                pass
        return {"unparsed_text": text}


def _post_json(url: str, body: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
