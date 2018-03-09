# 配置
任何复杂点的应用，都不允许把配置写在代码里，要根据环境或安装配置，而做不同的设置。
## 基础
Sanic在application对象的`config`属性中管理配置。配置对象就是一个可以通过*.*或字典属性来修改的对象：
```py
app.config.DB_NAME = 'appdb'
app.config.DB_USER = 'appuser'
```
配置对象实际上是一个字典，可以使用`update`方法批量更新配置值。
```py
db_settings = {
    'DB_HOST': 'localhost',
    'DB_NAME': 'appdb',
    'DB_USER': 'appuser'
}
app.config.update(db_settings)
```
通常配置参数都用大写字母。
## 加载配置
有几种发放来加载配置
### 从环境变量读取
任何一个变量如果是`SANIC_`前缀开头，都会被应用成Sanic配置。例如`SANIC_REQUEST_TIMEOUT`会自动被应用加载，并提供给`REQUEST_TIMEOUT`变量。你也可以传递一个其它前缀：
```py
app = Sanic(load_env='MYAPP_')
```
然后，上面的超时配置环境变量会变成`MYAPP_REQUEST_TIMEOUT`：
```py
environ["MYAPP_REQUEST_TIMEOUT"] = "42"
app = Sanic(load_env='MYAPP_')
assert app.config.REQUEST_TIMEOUT == 42
```
如果你想拒绝从环境变量中加载配置，可以把它设成`False`。
```py
app = Sanic(load_env=False)
```
### 从对象读取
如果有非常多配置值，并且它们都有默认值，那么将它们放到一个对象里会更方便管理：
```py
class Config:
    not_for_config = 'should not be used'
    CONFIG_VALUE = 'should be used'

app = Sanic('test_load_from_object')
    app.config.from_object(Config)
    assert app.config.CONFIG_VALUE == 'should be used'
    assert 'not_for_config' not in app.config
```
> 配置变量需要全部是大写
### 从文件中读取
通常我们希望要加载的配置文件不限定为应用的一部分，例如配置文件统一放在一个配置目录下`from_pyfile(/path/to/config_file)`。但是这么做，需要程序内写好配置文件的路径，所以我们可以把配置文件路径写到环境变量中，由Sanic加载。
```py
app = Sanic('myapp')
app.config.from_envvar('MYAPP_SETTINGS')
```
然后我们就可以使用`MYAPP_SETTINGS`环境变量来设置配置文件路径了
```bash
$ MYAPP_SETTINGS=/path/to/config_file python3 myapp.py
```
配置文件是一个正常的Python文件，只有全部为大写字母的变量才会被加载，通常文件内容都是如下所示的键值对。
```py
# config_file
DB_HOST = 'localhost'
DB_NAME = 'appdb'
DB_USER = 'appuser'
```
## 内置变量
目前来说，Sanic有一些预定义的配置变量，我们编写应用时可以覆盖它们

|变量名|默认值|描述|
| ------------- |:-------------:| -----:|
|REQUEST_MAX_SIZE|100000000|request最大长度(bytes)|
|REQUEST_TIMEOUT|60|request超时时间(秒)|
|RESPONSE_TIMEOUT|60|response超时时间|
|KEEP_ALIVE|True|是否维持长链接|
|KEEP_ALIVE_TIMEOUT|5|长链接超时时间(秒)|

关于长链接具体的具体信息，请参见[Wiki](https://en.wikipedia.org/wiki/Keepalive)或自行百度。