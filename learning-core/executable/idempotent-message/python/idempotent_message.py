from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConsumerState:
    processed_ids: set[str] = field(default_factory=set)
    total: int = 0


def handle(state: ConsumerState, message_id: str, amount: int) -> bool:
    if not message_id:
        raise ValueError("message_id is required")
    if message_id in state.processed_ids:
        return False
    state.total += amount
    state.processed_ids.add(message_id)
    return True
