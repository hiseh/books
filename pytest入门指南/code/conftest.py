from test_foocompare import Foo
def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, Foo) and isinstance(right, Foo) and op == "==":
        return ['比较 Foo 实例:',
                '   值: %s != %s' % (left.val, right.val)]