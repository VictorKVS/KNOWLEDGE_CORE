import pytest

from validation import Registration, parse_registration


def test_valid_payload_is_normalized() -> None:
    assert parse_registration({"username": "  Ada  ", "age": 36}) == Registration("Ada", 36)


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"username": "Ada", "age": True},
        {"username": "", "age": 36},
        {"username": "Ada", "age": -1},
        {"username": "Ada", "age": 131},
        {"username": "Ada", "age": 36, "admin": True},
    ],
)
def test_invalid_payloads_are_rejected(payload: object) -> None:
    with pytest.raises(ValueError):
        parse_registration(payload)
