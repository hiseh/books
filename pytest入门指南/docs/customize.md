# 配置
## 初始化：声明rootdir和inifile
*v2.7+*
pytest依赖命令行参数（指定测试文件、路径）和*ini文件*中的定义来为每个测试用例声明统一的`rootdir`。当启动时，`rootdir`和*ini文件*会写入pytest头部。
- 当收集时，会构建node id：每一个以`rootdir`为根起点的测试用例都会获取一个完整路径、类名、函数名和参数列表（如果有的话），并分配一个唯一的node id。
- 使用插件在project/test下的固定位置存储特定运行信息，例如内部[缓存](https://docs.pytest.org/en/latest/cache.html#cache)插件在`rootdir`下创建了`.cache`子目录，来存储跨测试用例运行状态。

强调一下，**`rootdir`不是用来修改`sys.path/PYTHONPATH`和干涉模块导入的**。详情请查看[pytest导入机制和sys.path/PYTHONPATH](https://docs.pytest.org/en/latest/pythonpath.html#pythonpath)

## 内置配置文件选项
### testpaths
*v2.8+*
当从[rootdir](#初始化：声明rootdir和inifile)目录执行pytest时，如果命令行中没有设置具体的目录、文件或test id，那么可以用testpaths来设置一个目录列表，用来提供搜索测试用例。正确的做法是把所有项目测试用例放在一个确定的目录下，好加快用例收集速度并且避免收集到计划外用例。
```py
[pytest]
testpaths = testing doc
```
当从root目录执行pytest时，pytest只会从`testing`和`doc`目录下查找测试用例。
