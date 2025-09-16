import pytest

from cognitive_core.app.services import dot, solve_linear_2x2


def test_dot_ok():
    assert dot([1, 2, 3], [4, 5, 6]) == 32.0


def test_dot_len_mismatch():
    with pytest.raises(ValueError):
        dot([1, 2], [1])


def test_solve2x2():
    x, y = solve_linear_2x2(1, 2, 3, 4, 5, 6)
    assert round(x, 6) == -4.0
    assert round(y, 6) == 4.5
