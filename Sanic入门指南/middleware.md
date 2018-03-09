# 中间件和监听器
中间件是一类特定方法，它们会在服务器收到request之前或之后执行，通常用来定制request和response。此外，Sanic还提供了监听器机制，可以在程序生命周期的不同点运行自己的代码。
## 中间件
有两种类型的中间件：request和response，都由`@app.middleware`装饰器定义，定义时通过字符串参数`request`或`response`来设定类型。Response中间件需要接收request和response作为参数。中间件可以修改传给它的request和response参数，同时不返回。
```python
app = Sanic(__name__)

@app.middleware('response')
async def custom_banner(request, response):
    response.headers["Server"] = "Fake-Server"

@app.middleware('response')
async def prevent_xss(request, response):
    response.headers["x-xss-protection"] = "1; mode=block"

app.run(host="0.0.0.0", port=8000)
```
上述代码实现了两个有序的中间件：
0. **custom_banner**会将HTTP头`Server`键值改为`Fake-Server`
0. **prevent_xss**会将加一个HTTP头，来防止跨域攻击。

如果蓝图中也有中间件，可以看到中间件执行顺序是：
**request** &rarr; **蓝图中request** &rarr; **蓝图视图request** &rarr; **蓝图视图response** &rarr; **蓝图response** &rarr; **response**

### 提前返回
如果蓝图中返回了`HTTPResponse`对象，后续request会停止执行，并返回response。如果这条语句是在用户请求的路由handler前被调用的，那么handler将不会被调用。例如：
```python
@app.middleware('request')
async def halt_request(request):
    return text('I halted the request')

@app.middleware('response')
async def halt_response(request, response):
    return text('I halted the response')
```
## 监听器
如果你想在服务启动/结束执行初始化/清理程序，那么可以使用下述监听器：
- before_server_start
- after_server_start
- before_server_stop
- after_server_stop

监听器可以像普通装饰器一样使用，例如：
```python
@app.listener('before_server_start')
async def before_server_start(app, loop):
    print('\n', before_server_start.__name__, '\n')

@app.listener('after_server_start')
async def after_server_start(app, loop):
    print('\n', after_server_start.__name__, '\n')

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    print('\n', before_server_stop.__name__, '\n')

@app.listener('after_server_stop')
async def after_serfer_stop(app, loop):
    print('\n', after_serfer_stop.__name__, '\n')
```
执行顺序是：
**before_server_start** &rarr; **after_server_start** &rarr; **before_server_stop** &rarr; **after_serfer_stop**

如果你想要在loop启动之后，执行一些后台任务，可以使用Sanic的`add_task`方法。
```python
async def notify_server_started_after_five_seconds():
    await asyncio.sleep(5)
    print('Server successfully started!')

app.add_task(notify_server_started_after_five_seconds())
```