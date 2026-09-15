from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class Materiality:
    reversibility: str = "LOW"
    security_impact: str = "NONE"
    legal_privacy_impact: str = "NONE"
    cost_impact: str = "LOW"
    blast_radius: str = "LOCAL"
    external_dependency_impact: str = "NONE"
    uncertainty: str = "LOW"
    architecture_decision: bool = False
    residual_risk_decision: bool = False
    sensitive_external_processing: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Materiality":
        data = data or {}
        aliases = {
            "securityImpact": "security_impact",
            "legalPrivacyImpact": "legal_privacy_impact",
            "costImpact": "cost_impact",
            "blastRadius": "blast_radius",
            "externalDependencyImpact": "external_dependency_impact",
            "architectureDecision": "architecture_decision",
            "residualRiskDecision": "residual_risk_decision",
            "sensitiveExternalProcessing": "sensitive_external_processing",
        }
        normalized = {aliases.get(k, k): v for k, v in data.items()}
        allowed = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in normalized.items() if k in allowed})


@dataclass(slots=True)
class DecisionRequest:
    prompt: str
    capability: str
    lifecycle_stage: str
    data_class: str = "PUBLIC"
    evidence_refs: list[str] = field(default_factory=list)
    materiality: Materiality = field(default_factory=Materiality)
    metadata: dict[str, Any] = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DecisionRequest":
        if not str(data.get("prompt", "")).strip():
            raise ValueError("prompt is required")
        if not str(data.get("capability", "")).strip():
            raise ValueError("capability is required")
        if not str(data.get("lifecycle_stage", data.get("lifecycleStage", ""))).strip():
            raise ValueError("lifecycle_stage is required")
        return cls(
            task_id=str(data.get("task_id", data.get("taskId", uuid4()))),
            prompt=str(data["prompt"]),
            capability=str(data["capability"]),
            lifecycle_stage=str(data.get("lifecycle_stage", data.get("lifecycleStage"))),
            data_class=str(data.get("data_class", data.get("dataClass", "PUBLIC"))).upper(),
            evidence_refs=[str(x) for x in data.get("evidence_refs", data.get("evidenceRefs", []))],
            materiality=Materiality.from_dict(data.get("materiality")),
            metadata=dict(data.get("metadata", {})),
            created_at=str(data.get("created_at", data.get("createdAt", utc_now_iso()))),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ModelRunResult:
    model_id: str
    provider: str
    role: str
    content: str
    parsed: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    error: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DecisionPacket:
    task_id: str
    panel_run_id: str
    profile: str
    lifecycle_stage: str
    capability: str
    data_class: str
    champion: ModelRunResult | None
    challengers: list[ModelRunResult]
    judge: ModelRunResult | None
    evidence_verification: dict[str, Any]
    consensus_state: str
    suggested_gate_outcome: str
    required_human_authority: str
    dissent_register: list[dict[str, Any]] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "panel_run_id": self.panel_run_id,
            "profile": self.profile,
            "lifecycle_stage": self.lifecycle_stage,
            "capability": self.capability,
            "data_class": self.data_class,
            "champion": self.champion.to_dict() if self.champion else None,
            "challengers": [x.to_dict() for x in self.challengers],
            "judge": self.judge.to_dict() if self.judge else None,
            "evidence_verification": self.evidence_verification,
            "consensus_state": self.consensus_state,
            "suggested_gate_outcome": self.suggested_gate_outcome,
            "required_human_authority": self.required_human_authority,
            "dissent_register": self.dissent_register,
            "unknowns": self.unknowns,
            "warnings": self.warnings,
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class ApprovalRecord:
    panel_run_id: str
    task_id: str
    actor_id: str
    actor_role: str
    decision: str
    rationale: str
    evidence_refs: list[str] = field(default_factory=list)
    approval_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
