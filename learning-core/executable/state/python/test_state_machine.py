import pytest

from state_machine import Document, InvalidTransition, Status, transition


def test_valid_lifecycle() -> None:
    doc = transition(Document(), Status.APPROVED)
    doc = transition(doc, Status.PUBLISHED)
    doc = transition(doc, Status.ARCHIVED)
    assert doc.status is Status.ARCHIVED


def test_rejected_transition_preserves_original_state() -> None:
    original = Document()
    with pytest.raises(InvalidTransition):
        transition(original, Status.PUBLISHED)
    assert original.status is Status.DRAFT


def test_approved_can_return_to_draft() -> None:
    doc = transition(Document(), Status.APPROVED)
    assert transition(doc, Status.DRAFT).status is Status.DRAFT
