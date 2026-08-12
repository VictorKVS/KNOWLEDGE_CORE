from idempotent_message import ConsumerState, handle


def test_duplicate_message_does_not_repeat_side_effect() -> None:
    state = ConsumerState()
    assert handle(state, "m1", 10) is True
    assert handle(state, "m1", 10) is False
    assert state.total == 10


def test_distinct_messages_are_applied() -> None:
    state = ConsumerState()
    handle(state, "m1", 10)
    handle(state, "m2", 5)
    assert state.total == 15
