# Handler装饰器
Sanic的handler就是简单的Python方法，可以像Flask一样应用装饰器。典型的应用场景是用在handler代码运行前/后运行自己的代码。装饰器方法必须用`async`定义
```py
from functools import wraps

def decorate_handler(method):
    @wraps(method)
    async def _deco(request, *args, **kwargs):
        print('\ndecorator\n')
        response = await method(request, *args, **kwargs)
        return response
    return _deco

@app.route('/tag/<tag:[0-9]+>', methods=frozenset({'GET'}))
@decorate_handler
async def handler1(request, tag):
    return response.json({'tag': tag})
```