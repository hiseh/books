# 断言
## 使用*assert*判断状态
可以在`pytest`中使用标准的Python`assert`断言来检查结果和异常。例如下面代码可以检查函数返回值：
```py
def f():
    return 3

def test_function():
    assert f() == 4
```
如果断言检查失败，`pytest`会输出函数真正的返回值。
```sh
$ pytest -q test_sample.py::test_answer
F                                                                        [100%]
=================================== FAILURES ===================================
_________________________________ test_answer __________________________________

    def test_answer():
>       assert func(3) == 4
E       assert 3 == 4
E        +  where 3 = func(3)

test_sample.py:10: AssertionError
1 failed in 0.05 seconds
```
`pytest`可以显示出调用、属性、比较、一元和二元运算符的结果值。请参照[pytest的失败报告Demo](https://docs.pytest.org/en/latest/example/reportingdemo.html#tbreportdemo)。我们完全可以用符合Python规范的方式编写pytest，还不会损失检查信息，方便吧。如果断言中有表达式，方便我们检查一些特殊信息：
```py
def test_special_answer():
    assert func(4) % 2 == 1
```
详细信息请查看[高级断言检查](#高级断言检查)
## 检查预期的异常
我们可以用`pytest.raises`作为上下文管理，来检查抛出的异常：
```py
def func_exce(x):
    if x & 1 != 0:
        raise TypeError
    return 0

def test_1_TypeError():
    with pytest.raises(TypeError):
        func_exce(1)

def test_0_TypeError():
    with pytest.raises(TypeError):
        func_exce(0)
```
第一条测试能通过，而第二条测试会报告`Failed: DID NOT RAISE <class 'TypeError'>`，符合我们的预期。此外，我们还可以获取运行中生成的异常信息：
```py
def test_recursion_depth():
    with  pytest.raises(RuntimeError) as e:
        def f():
            f()
        f()
    assert 'maximum recursion' in str(e.value)
```
`e`是`ExceptionInfo`实例，封装了运行中抛出的异常信息，主要用它三个属性：`.type`，`.value`和`.traceback`。
*v3.0+*

pytest可以用`message`参数定制异常信息, ：
```py
>>> with raises(ValueError, message="预期的ValueError"):
...    pass
... Failed: 预期的ValueError
```
此外，还可以将raises作为参数传递给`pytest.mark.xfail`装饰器，用来检查更具体的测试失败方式，而不是抛出任何异常。它更像描述**应该**发生的异常。
```py
@pytest.mark.xfail(raises=IndexError)
def test_f():
    f()
```
```sh
h$ pytest -q test_sample.py::test_f
F                                                                        [100%]
=================================== FAILURES ===================================
____________________________________ test_f ____________________________________

    @pytest.mark.xfail(raises=IndexError)
    def test_f():
>       f()

test_sample.py:28:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    def f():
>       raise SystemExit(1)
E       SystemExit: 1v

test_sample.py:5: SystemExit
1 failed in 0.05 seconds
```
`pytest.raises`更适合用来测试自家代码主动抛出的异常，而用`@pytest.mark.xfail`装饰检查函数，更方便记录未修复的bug或依赖代码中的bug。
在上下文管理中用`match`可以通过正则表达式检查异常描述信息是否匹配我们的预期（类似Python官方`unittest`库中的`TestCase.assertRaisesRegexp`方法）：
```py
def special_func():
    raise ValueError("异常信息：123")

def test_match():
    with pytest.raises(ValueError, match=r'.*123$'):
        special_func()
```
```sh
$ pytest -q test_sample.py::test_match
.                                                                        [100%]
1 passed in 0.01 seconds
```
`match`参数调用的正则表达式规则与`re.search`一致。
## 检查预期的警告
*v2.8+*

通过[`pytest.warns`](https://docs.pytest.org/en/latest/warnings.html#warns)检查代码中抛出的特定警告信息。
## 编写上下文敏感的比较
*v2.0+*

作比较时，`pytest`可以提供丰富的上下文敏感信息，比如；
```py
def test_set_comparison():
    set1 = set("1308")
    set2 = set("8035")
    assert set1 == set2
```
运行一下：
```sh
$ pytest -q test_sample.py::test_set_comparison
F                                                                        [100%]
=================================== FAILURES ===================================
_____________________________ test_set_comparison ______________________________

    def test_set_comparison():
        set1 = set("1308")
        set2 = set("8035")
>       assert set1 == set2
E       AssertionError: assert {'0', '1', '3', '8'} == {'0', '3', '5', '8'}
E         Extra items in the left set:
E         '1'
E         Extra items in the right set:
E         '5'
E         Full diff:
E         - {'1', '3', '0', '8'}
E         ?   ^...
E
E         ...Full output truncated (3 lines hidden), use '-vv' to show

test_sample.py:55: AssertionError
1 failed in 0.04 seconds
```
结果中说明了所有比较实例：
- 比较字符串：显示不同的内容
- 比较列表：第一个不同的索引
- 比较字典：不同的实体
更多实例请查看[Demo](https://docs.pytest.org/en/latest/example/reportingdemo.html#tbreportdemo)。
## 定义自己的比较判断
实现`pytest_assertrepr_compare`
>**pytest_assertrepr_compare(config, op, left, right)**
><br/>返回失败的断言表达式说明<br/>
>如果没有自定义说明返回*None*，否则返回字符串列表。字符串列表可以包含多行文字，不过返回时换行符会被去掉。此外第一行会缩进显示，因此建议第一行显示摘要文字。<br/>
> **参数：** config (_pytest.config.Config) – pytest配置对象

下面是一个实例，在[configtest.py](https://docs.pytest.org/en/latest/fixture.html#conftest-py)中增加一个钩子，比较Foo对象时提供额外的比较信息。
```py
class Foo(object):
    def __init__(self, val):
        self.val = val

    def __eq__(self, other):
        return self.val == other.val

def test_compare():
    f1 = Foo(1)
    f2 = Foo(2)
    assert f1 == f2
```
如果不实用自定义的比较判断，测试结果如下：
```sh
$ pytest -q test_foocompare.py
F                                                                        [100%]
=================================== FAILURES ===================================
_________________________________ test_compare _________________________________

    def test_compare():
        f1 = Foo(1)
        f2 = Foo(2)
>       assert f1 == f2
E       assert <test_foocompare.Foo object at 0x1054e0198> == <test_foocompare.Foo object at 0x1054e0278>

test_foocompare.py:11: AssertionError
1 failed in 0.04 seconds
```
增加自定义的configtest.py文件：
```py
from test_foocompare import Foo
def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, Foo) and isinstance(right, Foo) and op == "==":
        return ['比较 Foo 实例:',
                '   值: %s != %s' % (left.val, right.val)]
```
再次执行测试，结果如下：
```sh
$ pytest -q test_foocompare.py
F                                                                        [100%]
=================================== FAILURES ===================================
_________________________________ test_compare _________________________________

    def test_compare():
        f1 = Foo(1)
        f2 = Foo(2)
>       assert f1 == f2
E       assert 比较 Foo 实例:
E            值: 1 != 2

test_foocompare.py:11: AssertionError
1 failed in 0.04 seconds
```
## 高级断言检查
*v2.1+*

