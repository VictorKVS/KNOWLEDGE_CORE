from __future__ import annotations

import argparse
import json
from pathlib import Path

from .approval import ApprovalGate
from .models import ApprovalRecord, DecisionPacket, DecisionRequest, ModelRunResult
from .panel import DecisionPanel
from .registry import ModelRegistry
from .store import RuntimeStore


def main() -> None:
    parser = argparse.ArgumentParser(description="FATHER Model Zoo runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run one decision panel")
    run.add_argument("--registry", required=True)
    run.add_argument("--request", required=True)
    run.add_argument("--data-dir", default="data/father_runtime")

    approve = sub.add_parser("approve", help="record authorized human decision")
    approve.add_argument("--packet", required=True)
    approve.add_argument("--approval", required=True)
    approve.add_argument("--data-dir", default="data/father_runtime")

    args = parser.parse_args()
    store = RuntimeStore(args.data_dir)

    if args.command == "run":
        registry = ModelRegistry.load_json(args.registry)
        request = DecisionRequest.from_dict(json.loads(Path(args.request).read_text(encoding="utf-8")))
        packet = DecisionPanel(registry, store).run(request)
        print(json.dumps(packet.to_dict(), ensure_ascii=False, indent=2))
        return

    packet = _packet_from_dict(json.loads(Path(args.packet).read_text(encoding="utf-8")))
    approval_data = json.loads(Path(args.approval).read_text(encoding="utf-8"))
    approval = ApprovalRecord(
        panel_run_id=packet.panel_run_id,
        task_id=packet.task_id,
        actor_id=str(approval_data["actor_id"]),
        actor_role=str(approval_data["actor_role"]),
        decision=str(approval_data["decision"]),
        rationale=str(approval_data["rationale"]),
        evidence_refs=[str(x) for x in approval_data.get("evidence_refs", [])],
    )
    final = ApprovalGate(store).record(packet, approval)
    print(json.dumps({"approval": approval.to_dict(), "final_gate_outcome": final}, ensure_ascii=False, indent=2))


def _run_result(data: dict | None) -> ModelRunResult | None:
    if not data:
        return None
    return ModelRunResult(**data)


def _packet_from_dict(data: dict) -> DecisionPacket:
    return DecisionPacket(
        task_id=data["task_id"],
        panel_run_id=data["panel_run_id"],
        profile=data["profile"],
        lifecycle_stage=data["lifecycle_stage"],
        capability=data["capability"],
        data_class=data["data_class"],
        champion=_run_result(data.get("champion")),
        challengers=[_run_result(x) for x in data.get("challengers", []) if x],
        judge=_run_result(data.get("judge")),
        evidence_verification=data.get("evidence_verification", {}),
        consensus_state=data.get("consensus_state", "INSUFFICIENT_EVIDENCE"),
        suggested_gate_outcome=data.get("suggested_gate_outcome", "BLOCKED"),
        required_human_authority=data["required_human_authority"],
        dissent_register=data.get("dissent_register", []),
        unknowns=data.get("unknowns", []),
        warnings=data.get("warnings", []),
        created_at=data.get("created_at", ""),
    )


if __name__ == "__main__":
    main()
