from __future__ import annotations

from .models import ApprovalRecord, DecisionPacket
from .store import RuntimeStore


_ALLOWED_DECISIONS = {
    "APPROVE",
    "APPROVE_WITH_CONDITIONS",
    "REQUEST_MORE_EVIDENCE",
    "REWORK",
    "REJECT",
    "DEFER",
}


class ApprovalGate:
    def __init__(self, store: RuntimeStore) -> None:
        self.store = store

    def record(self, packet: DecisionPacket, approval: ApprovalRecord) -> str:
        if approval.decision not in _ALLOWED_DECISIONS:
            raise ValueError(f"unsupported human decision: {approval.decision}")
        if approval.panel_run_id != packet.panel_run_id or approval.task_id != packet.task_id:
            raise ValueError("approval does not belong to this decision packet")
        if approval.actor_role != packet.required_human_authority:
            raise PermissionError(
                f"actor_role={approval.actor_role} cannot finalize packet requiring {packet.required_human_authority}"
            )
        if not approval.rationale.strip():
            raise ValueError("human rationale is required")
        self.store.append_approval(approval)
        if approval.decision == "APPROVE":
            return "PASS"
        if approval.decision == "APPROVE_WITH_CONDITIONS":
            return "CONDITIONAL_PASS"
        if approval.decision in {"REQUEST_MORE_EVIDENCE", "REWORK", "DEFER"}:
            return "BLOCKED"
        return "REJECTED"
