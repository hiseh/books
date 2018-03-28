import pytest


def f():
    raise SystemExit(1)


def func(x):
    return x


def func_exce(x):
    if x & 1 != 0:
        raise TypeError
    return 0


def test_answer():
    assert func(3) == 4


def test_mytest():
    with pytest.raises(SystemExit):
        f()

@pytest.mark.xfail(raises=IndexError)
def test_f():
    f()

def test_special_answer():
    assert func(4) % 2 == 0


def test_1_TypeError():
    with pytest.raises(TypeError):
        func_exce(1)

def test_recursion_depth():
    with  pytest.raises(RuntimeError) as e:
        def f():
            f()
        f()
    assert 'maximum recursion' in str(e.value)

def special_func():
    raise ValueError("异常信息：123")

def test_match():
    with pytest.raises(ValueError, match=r'.*123$'):
        special_func()

def test_set_comparison():
    set1 = set("1308")
    set2 = set("8035")
    assert set1 == set2