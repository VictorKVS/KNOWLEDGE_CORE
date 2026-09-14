from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ModelSpec:
    model_id: str
    provider: str
    model: str
    roles: set[str]
    capabilities: set[str] = field(default_factory=lambda: {"*"})
    allowed_data_classes: set[str] = field(default_factory=lambda: {"PUBLIC"})
    endpoint: str | None = None
    api_key_env: str | None = None
    enabled: bool = True
    timeout_seconds: int = 60
    options: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelSpec":
        return cls(
            model_id=str(data["model_id"]),
            provider=str(data["provider"]),
            model=str(data.get("model", data["model_id"])),
            roles={str(x).upper() for x in data.get("roles", [])},
            capabilities={str(x) for x in data.get("capabilities", ["*"])},
            allowed_data_classes={str(x).upper() for x in data.get("allowed_data_classes", ["PUBLIC"])},
            endpoint=_expand_env(data.get("endpoint")),
            api_key_env=data.get("api_key_env"),
            enabled=bool(data.get("enabled", True)),
            timeout_seconds=int(data.get("timeout_seconds", 60)),
            options=dict(data.get("options", {})),
        )

    def supports(self, role: str, capability: str, data_class: str) -> bool:
        role = role.upper()
        return (
            self.enabled
            and role in self.roles
            and ("*" in self.capabilities or capability in self.capabilities)
            and data_class.upper() in self.allowed_data_classes
        )


class ModelRegistry:
    def __init__(self, models: list[ModelSpec]) -> None:
        self.models = models

    @classmethod
    def load_json(cls, path: str | Path) -> "ModelRegistry":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        models = [ModelSpec.from_dict(item) for item in data.get("models", [])]
        if not models:
            raise ValueError("model registry contains no models")
        return cls(models)

    def candidates(self, role: str, capability: str, data_class: str) -> list[ModelSpec]:
        return [m for m in self.models if m.supports(role, capability, data_class)]

    def select_one(
        self,
        role: str,
        capability: str,
        data_class: str,
        exclude_ids: set[str] | None = None,
        exclude_providers: set[str] | None = None,
    ) -> ModelSpec:
        exclude_ids = exclude_ids or set()
        exclude_providers = exclude_providers or set()
        candidates = [m for m in self.candidates(role, capability, data_class) if m.model_id not in exclude_ids]
        preferred = [m for m in candidates if m.provider not in exclude_providers]
        chosen = preferred or candidates
        if not chosen:
            raise LookupError(f"no enabled model for role={role} capability={capability} data_class={data_class}")
        return chosen[0]

    def select_many(
        self,
        role: str,
        capability: str,
        data_class: str,
        count: int,
        exclude_ids: set[str] | None = None,
    ) -> list[ModelSpec]:
        exclude_ids = set(exclude_ids or set())
        result: list[ModelSpec] = []
        for spec in self.candidates(role, capability, data_class):
            if spec.model_id in exclude_ids:
                continue
            result.append(spec)
            exclude_ids.add(spec.model_id)
            if len(result) >= count:
                break
        return result


def _expand_env(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if value.startswith("${") and value.endswith("}"):
        return os.getenv(value[2:-1])
    return value
