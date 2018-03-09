# 异常
Sanic可以自动地在handler中抛出异常，异常信息会作为它的第一个参数，包含`response`的状态码。
## 抛出异常
使用Python自带的`raise`或者`exceptions.abort()`都可以抛出异常
```python
from sanic.exceptions import ServerError

@app.route('/killme')
def i_am_ready_to_die(request):
    raise ServerError("Something bad happened", status_code=500)

@app.route('/youshallnotpass')
def no_no(request):
        abort(401)
        # 直接返回，后续代码不会再被执行
        text("OK")
```
`about()`封装了`raise`，会抛出一个基于`SanicException`的异常，除非特别指定，否则返回HTTP状态码对应的标准信息（在`response.STATUS_CODES`中设置）。
## 自定义异常
使用`@app.exception`装饰器，可以覆盖默认的异常处理程序。这个装饰器内置了异常列表作为参数，可以通过`SanicException`捕获它们。被装饰的方法必须有`Request`和`Exception`两个对象作为参数。
```python
from sanic.response import text
from sanic.exceptions import NotFound

@app.exception(NotFound)
def ignore_404s(request, exception):
    return text("Yep, I totally found the page: {}".format(request.url))
```
## 常用的异常
- `NotFound` 404
- `ServerError` 500

完整的异常列表可参见`sanic.exceptions`