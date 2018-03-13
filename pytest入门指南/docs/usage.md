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
##遇到第一个（第N个）失败后停止
遇到第一个（第N个）失败后停止测试：
```sh
pytest -x            # 遇到第一个失败后停止
pytest --maxfail=2    # 遇到2个失败后停止
```