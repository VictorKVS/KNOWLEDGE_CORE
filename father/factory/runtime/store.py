from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ApprovalRecord, DecisionPacket, utc_now_iso


class RuntimeStore:
    def __init__(self, root: str | Path = "data/father_runtime") -> None:
        self.root = Path(root)
        self.packet_dir = self.root / "decision_packets"
        self.audit_file = self.root / "audit.jsonl"
        self.approval_file = self.root / "approvals.jsonl"
        self.packet_dir.mkdir(parents=True, exist_ok=True)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_packet(self, packet: DecisionPacket) -> Path:
        path = self.packet_dir / f"{packet.panel_run_id}.json"
        path.write_text(json.dumps(packet.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        self.audit("DECISION_PACKET_CREATED", packet.panel_run_id, {"task_id": packet.task_id, "profile": packet.profile})
        return path

    def append_approval(self, approval: ApprovalRecord) -> None:
        self._append_jsonl(self.approval_file, approval.to_dict())
        self.audit("HUMAN_DECISION_RECORDED", approval.panel_run_id, approval.to_dict())

    def audit(self, event_type: str, object_id: str, payload: dict[str, Any]) -> None:
        self._append_jsonl(
            self.audit_file,
            {"event_type": event_type, "object_id": object_id, "payload": payload, "created_at": utc_now_iso()},
        )

    @staticmethod
    def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
