from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum, auto


class Status(Enum):
    DRAFT = auto()
    APPROVED = auto()
    PUBLISHED = auto()
    ARCHIVED = auto()


class InvalidTransition(ValueError):
    pass


@dataclass(frozen=True)
class Document:
    status: Status = Status.DRAFT


_ALLOWED: dict[Status, set[Status]] = {
    Status.DRAFT: {Status.APPROVED},
    Status.APPROVED: {Status.DRAFT, Status.PUBLISHED},
    Status.PUBLISHED: {Status.ARCHIVED},
    Status.ARCHIVED: set(),
}


def transition(document: Document, target: Status) -> Document:
    if target not in _ALLOWED[document.status]:
        raise InvalidTransition(f"{document.status.name} -> {target.name}")
    return replace(document, status=target)
