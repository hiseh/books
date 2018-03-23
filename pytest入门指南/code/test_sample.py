import pytest


def f():
    raise SystemExit(1)


def func(x):
    return x


def test_answer():
    assert func(3) == 4


def test_mytest():
    with pytest.raises(SystemExit):
        f()


def test_special_answer():
    assert func(4) % 2 == 0
