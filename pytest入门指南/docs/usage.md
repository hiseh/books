# 常规用法
## 通过python -m pytest调用
*v2.0+*

可以通过命令行中Python命令调用测试：
```sh
python -m pytest [...]
``
上面调用方式基本与命令行中执行`pytest [...]`等价，区别仅仅是通过`python`调用，而将当前目录加到`sys.path`。
```
## 可能的结束编码
运行`pytest`会得到六种可能的结束编码。

- **Exit code 0**  所有测试都被收集到，并且全部运行通过
- **Exit code 1**  所有测试都被收集到，全部运行，但某些测试未通过
- **Exit code 2**  用户终止测试
- **Exit code 3**  当执行测试时发生内部错误
- **Exit code 4**  pytest命令行调用错误
- **Exit code 5**  未收集到测试
## 获得帮助信息
```sh
pytest --version   # 显示pytest版本信息和来源
pytest --fixtures  # 显示可用的内置函数参数
pytest -h | --help # 显示命令行帮助和配置操作
```
## 遇到第一个（第N个）失败后停止
遇到第一个（第N个）失败后停止测试：
```sh
pytest -x            # 遇到第一个失败后停止
pytest --maxfail=2    # 遇到2个失败后停止
```
## 选择执行测试
pytest支持多种命令行方式，选择执行测试。
### 运行指定模块内的测试
```sh
pytest test_mod.py
``` 
### 运行指定目录下的测试
```sh
pytest testing/
```
### 通过关键字筛选测试
```sh
pytest -k 'TestClass and not two'
```
上述命令将会执行包含"TestClass"关键字的测试，同时不包含"two"关键字。关键字可以是文件名、类名和函数名。例如上面例子，pytest会执行`TestClass.test_one`，而不会执行`TestClass.test_two`
### 通过node id运行测试
每个收集到的测试都会被分配一个`nodeid`，`nodeid`包含模块文件名、类名、函数名以及参数名，中间用`::`分隔。
通过模块、类名和方法名运行指定的测试：
```sh
pytest test_class.py::TestClass::test_two
```
### 通过标记运行测试
```sh
pytest -m slow
```
上述命令将运行所有`@pytest.mark.slow decorator`装饰器的测试。更多信息请参见[标记](https://docs.pytest.org/en/latest/mark.html#mark)
### 通过包运行测试
```sh
pytest --pyargs pkg.testing
```
上述命令将导入`pkg.testing`包，并从它文件系统位置发现和运行测试。
## 修改Python的追溯打印
修改追溯打印的例子：
```sh
pytest --showlocals # 在追溯中打印本地变量
pytest -l           # 显示本地变量（快捷方式）

pytest --tb=auto    # （默认）第一和最后一项的信息为'long'类型，其他项为'short'。
pytest --tb=long    # 打印全面详细的追溯信息。
pytest --tb=short   # 与long相反。
pytest --tb=line    # 每条失败信息打印一行
pytest --tb=native  # Python标准格式
pytest --tb=no      # 全部不打印
```
`--full-trace`会打印非常长的信息（比`--tb=long`还长）。它也会确保打印时可被键盘终止（Ctrl + c），这点在遇到超长信息是很有用。默认的，pytest不会输出任何追溯信息（因为pytest会触发键盘终止），只有手工打开打印追溯信息选项后，才能使用这个功能。
## 失败时调用PDB（Python Debugger）
Python自带一个内置的调试器，叫PDB。通过命令行参数，`pytest`可以让失败测试直接进入PDB。
```sh
pytest --pdb
```
上述命令会在每次失败时调用PDB。不过通常我们调试代码时，多只关注第一次失败信息，可以用下面命令：
```sh
pytest -x --pdb   # 第一次失败时进入PDB，然后停止测试。
pytest --pdb --maxfail=3  # 遇到3个失败时进入PDB。
```
> 所有失败信息都存储在`sys.last_value`，`sys.last_type`和`sys.last_traceback`中。实际使用中，可以用任何debug工具分析期中数据，也可以手工读取：
```py
>>> import sys
>>> sys.last_traceback.tb_lineno
42
>>> sys.last_value
AssertionError('assert result == "ok"',)
```
## 设置断点
可以使用Python自带的pdb库设置断点：
```py
import pdb
pdb.set_trace()
```
具体使用方式请参见[PDB](http://docs.python.org/library/pdb.html)文档。针对pytest，只需了解
- 其它测试中的输出捕获不会影响当前测试
- 之前任何测试的输入，如果已被捕获，都将照常处理
- 当前测试之后的输出不会被捕获，而是直接发送到`sys.stdout`中。
## 根据测试执行时间排序
列出最慢的N个测试：
```sh
pytest --durations=N
```
## 创建JUnitXML格式的文件
*v3.1+*

用下列调用方式，创建能被[Jenkins](http://jenkins-ci.org/)等持续集成服务读取的结果文件：
```sh
pytest --junitxml=path
```
`path`参数为结果文件的文件名。也可以在配置文件的`junit_suite_name`中直接设置根测试组件名：
```ini
[pytest]
junit_suite_name = my_suite
```
### record_xml_property
*v2.8+*

使用`record_xml_property`特性记录测试额外信息。
```py
def test_function(record_xml_property):
    record_xml_property("example_key", 1)
    assert 0
```
可以将扩展属性`example_key="1"`加到生成的`testcase`元素中。
```xml
<testcase classname="test_function" file="test_function.py" line="0" name="test_function" time="0.0009">
  <properties>
    <property name="example_key" value="1" />
  </properties>
</testcase>
```
### record_xml_attribute
*v3.4+*

使用`record_xml_attribute`可以向`testcase`元素增加新的xml属性，也可以覆盖已存在值。
```py
def test_function(record_xml_attribute):
    record_xml_attribute("assertions", "REQ-1234")
    record_xml_attribute("classname", "custom_classname")
    print('hello world')
    assert True
```
不像`record_xml_property`，上面代码不会增加子元素，而是增加一个属性：`assertions="REQ-1234"`，并且用`classname=custom_classname`覆盖掉默认的`classname`。
```xml
<testcase classname="custom_classname" file="test_function.py" line="0" name="test_function" time="0.003" assertions="REQ-1234">
    <system-out>
        hello world
    </system-out>
</testcase>
```
## Python代码中调用pytest
*v2.0+*

直接在Python中调用pytest：
```py
pytest.main()
```
效果与命令行调用一致，只不过不会抛出`SystemExit`，而是返回结束代码。也可以传递参数：
```py
pytest.main(['-x', 'mytestdir'])
```