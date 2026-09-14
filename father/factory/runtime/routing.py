from __future__ import annotations

from dataclasses import dataclass

from .models import Materiality


@dataclass(frozen=True, slots=True)
class PanelPlan:
    profile: str
    challenger_count: int
    needs_judge: bool
    needs_model_evidence_verifier: bool


class MaterialityRouter:
    ROUTINE = "ROUTINE_DOCUMENT_REVIEW"
    MATERIAL = "MATERIAL_ENGINEERING_DECISION"
    ARCHITECTURE = "ARCHITECTURE_CTO_CHALLENGE"
    HIGH_RISK = "HIGH_RISK_SECURITY_LEGAL"

    def route(self, m: Materiality) -> PanelPlan:
        sec = m.security_impact.upper()
        legal = m.legal_privacy_impact.upper()
        if sec == "CRITICAL" or legal in {"HIGH", "CRITICAL"} or m.residual_risk_decision or m.sensitive_external_processing:
            return PanelPlan(self.HIGH_RISK, 3, True, True)
        if (
            m.architecture_decision
            or m.reversibility.upper() == "HIGH"
            or m.blast_radius.upper() in {"SYSTEM_WIDE", "EXTERNAL"}
            or m.external_dependency_impact.upper() == "HARD_LOCK_IN"
            or m.cost_impact.upper() == "HIGH"
        ):
            return PanelPlan(self.ARCHITECTURE, 4, True, True)
        if (
            m.reversibility.upper() == "MEDIUM"
            or m.blast_radius.upper() == "MULTI_COMPONENT"
            or m.external_dependency_impact.upper() == "MATERIAL"
            or m.uncertainty.upper() == "HIGH"
            or m.cost_impact.upper() == "MEDIUM"
            or sec in {"MEDIUM", "HIGH"}
            or legal == "MEDIUM"
        ):
            return PanelPlan(self.MATERIAL, 2, True, True)
        return PanelPlan(self.ROUTINE, 0, False, False)
