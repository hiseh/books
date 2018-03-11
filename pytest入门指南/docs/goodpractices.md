# 集成练习
## Python测试发现规则归纳
`pytest`遵守以下标准测试用例发现规则：
- 如果没有没有在参数中声明起始路径，那么pytest会从[testpath](./customize.md#testpaths)（如果配置了）或当前目录开始收集测试用例。命令行参数可以混合任何目录、文件或者node id。
- 除非声明了[norecursedirs](https://docs.pytest.org/en/latest/customize.html#confval-norecursedirs)，否则都会在目录中递归查找。
- 在那些目录中，查找`test_*.py`和`*_test.py`，导入它们的[测试包名](https://docs.pytest.org/en/latest/goodpractices.html#test-package-name)。
- 从找到的文件中，收集它们的测试用例：
  - 类外所有`test_`前缀的测试函数或方法。
  - `Test`前缀的测试类（不包括`__init__`方法）中，`test_`前缀的测试函数或方法。

例如如何定制化自己的测试用例发现：[改变标准（Python）测试用例发现](https://docs.pytest.org/en/latest/example/pythoncollection.html)。Python模块中，`pytest`也会发现继承[unittest.TestCase](https://docs.pytest.org/en/latest/unittest.html#unittest-testcase)实现的标准测试类。