# 开始使用
pytest is a framework that makes building simple and scalable tests easy. Tests are expressive and readable—no boilerplate code required. Get started in minutes with a small unit test or complex functional test for your application or library.
pytest能够创建简单和可伸缩的测试应用框架，而不是单纯的套用模板代码。阅读本章后，你花几分钟时间就能为你的应用或代码库创建好一个小单元测试或复合功能测试。
## 安装pytest
0. 在命令行中执行一下命令：
```sh
pip install -U pytest
```
0. 检查安装版本
```sh
$ pytest --version
This is pytest version 3.x.y, imported from $PYTHON_PREFIX/lib/python3.5/site-packages/pytest.py
```
## 创建第一个测试
四行代码就可以创建一个简单测试函数。
```py
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5
```
就这么简单，下面可以执行这个测试函数。
```sh
$ pytest
============================= test session starts ==============================
platform darwin -- Python 3.x.y, pytest-3.x.y, py-1.x.y, pluggy-0.x.y
rootdir: $REGENDOC_TMPDIR, inifile:
collected 1 item

test_sample.py F                                                         [100%]

=================================== FAILURES ===================================
_________________________________ test_answer __________________________________

    def test_answer():
>       assert func(3) == 5
E       assert 4 == 5
E        +  where 4 = func(3)

test_sample.py:5: AssertionError
=========================== 1 failed in 0.04 seconds ===========================
```
因为`func(3)`并没有返回`5`，所以pytest返回了一个失败报告。
> **注意：**
> 你可以使用`assert`声明来证明测试预期。pytest的“高级断言检查”功能，可以智能地返回断言表达式的中间值，避免你阅读太多无用的unittest遗留方法。
## 执行多条测试
`pytest`会执行当前目录和子目录下所有名为*test_\*.py*或*_test.py*的文件。更规范的说明，请参见[标准测试发现规则](./goodpractices.md)。
## 断言预期内的异常抛出
使用`raises`来帮助断言代码抛出异常。
```py
import pytest
def f():
    raise SystemExit(1)

def test_mytest():
    with pytest.raises(SystemExit):
        f()
```
使用“安静”报告模式执行测试函数：
```sh
pytest -q
.                                                                        [100%]
1 passed in 0.01 seconds
```
## 把多条测试集合到类中
一旦写了多条测试，我们会很自然地想把它们集成到类中。用pytest很容易创建一个包含多条测试的类。
```py
class TestClass:
    def test_one(self):
        x = 'this'
        assert 'h' in x

    def test_two(self):
        x = 'hello'
        assert hasattr(x, 'check')
```
`pytest`根据[标准测试发现规则](./goodpractices.md)收集测试用例，所以它会找到所有带`test_`前缀的函数。剩下不需要任何子类。我们可以简单地通过文件名参数运行测试模型。
```sh
$ pytest -q test_class.py
.F                                                                       [100%]
=================================== FAILURES ===================================
______________________________ TestClass.test_two ______________________________

self = <test_class.TestClass object at 0x10550f048>

    def test_two(self):
        x = 'hello'
>       assert hasattr(x, 'check')
E       AssertionError: assert False
E        +  where False = hasattr('hello', 'check')

test_class.py:8: AssertionError
1 failed, 1 passed in 0.05 seconds
```
第一个测试成功，第二个失败。很容易根据断言的中间值判断失败原因。
## 为功能测试获取唯一的临时目录
`pytest`通过[内置的固定/函数参数]来获得特定资源，比如唯一临时目录。
```py
def test_needsfiles(tmpdir):
    print (tmpdir)
    assert 0
```
测试函数执行前，`pytest`将调用工厂模式创建相关资源，上述代码是创建一个每次执行都唯一的临时目录，随后测试函数打印`tmpdir`签名。
```py
$ pytest -q test_tmpdir.py
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________________ test_needsfiles ________________________________

tmpdir = local('PYTEST_TMPDIR/test_needsfiles0')

    def test_needsfiles(tmpdir):
        print (tmpdir)
>       assert 0
E       assert 0

test_tmpdir.py:3: AssertionError
----------------------------- Captured stdout call -----------------------------
PYTEST_TMPDIR/test_needsfiles0
1 failed in 0.04 seconds
```
更多tmpdir信息，请参见[临时目录和文件](https://docs.pytest.org/en/latest/tmpdir.html#tmpdir-handling)。
执行`pytest --fixtures`查看所有内置和可定制的[pytest 组件](https://docs.pytest.org/en/latest/fixture.html#fixtures)
