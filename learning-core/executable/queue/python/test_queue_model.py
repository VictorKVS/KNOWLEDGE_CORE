import pytest

from queue_model import BoundedQueue, QueueFull


def test_fifo_and_capacity() -> None:
    q = BoundedQueue(2)
    q.put("a")
    q.put("b")
    assert q.get() == "a"
    assert q.get() == "b"


def test_backpressure_rejects_unbounded_growth() -> None:
    q = BoundedQueue(1)
    q.put("a")
    with pytest.raises(QueueFull):
        q.put("b")
    assert len(q) == 1
