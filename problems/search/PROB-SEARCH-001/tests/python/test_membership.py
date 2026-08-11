from solution import linear_contains, binary_contains, hash_contains


def check_all(values, target, expected):
    assert linear_contains(values, target) is expected
    assert binary_contains(sorted(values), target) is expected
    assert hash_contains(set(values), target) is expected


def test_nominal_present():
    check_all([1, 3, 5, 7, 9], 7, True)


def test_nominal_absent():
    check_all([1, 3, 5, 7, 9], 4, False)


def test_empty():
    check_all([], 1, False)


def test_single_present():
    check_all([42], 42, True)


def test_duplicates():
    check_all([2, 2, 2, 3], 2, True)


def test_negative_values():
    check_all([-5, -1, 0, 4], -1, True)
