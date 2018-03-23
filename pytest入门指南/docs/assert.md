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
## 高级断言检查