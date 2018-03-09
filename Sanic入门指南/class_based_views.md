# 基于类的视图
基于类的视图就是实现了response行为的Python类，可以响应request请求。它们提供了在同一个入口响应不同的http方法的方式。比如说如果要定义3个不同的hanler方法，每个方法响应一个http方法，这时就可以用基于类的视图实现。
## 定义视图
基于类的视图需要继承`HTTPMethodView`，你可以实现所有http方法。如果某个方法未被实现，则会返回`405: Method not allowed`。可以用`app.add_route`注册视图，第一个参数必须是视图类名调用`as_view`方法，第二个参数是url路径。可以被实现http方法包括： get, post, put, patch, delete。path方法不常见，一般用在有部分修改的资源上。
```py
class TestView(views.HTTPMethodView):
    @staticmethod
    @bp.middleware('request')
    async def print_bp_view_request(request):
        print('blue view request middle')

    @staticmethod
    @bp.middleware('response')
    async def print_bp_view_response(request, response):
        print('blue view response middle')

    async def get(self, request):
        return response.json({'type': 'view class'})

bp.add_route(TestView.as_view(), '/view')
```
实现的http方法可以是同步的，也可以是异步的。
## URL参数
如果需要使用URL参数，参照URL路由章节，在方法定义中包含参数即可。
```py
class NameView(HTTPMethodView):

  def get(self, request, name):
    return text('Hello {}'.format(name))

app.add_route(NameView.as_view(), '/<name>')
```
## 装饰器
如果需要应用装饰器，需要定义`decorators`类变量，它们会在`as_view`方法调用后，应用到类中。
```py
def stupid_decorator(view):
    def decorator(*args, **kwargs):
        results.append(1)
        return view(*args, **kwargs)
    return decorator

class DummyView(HTTPMethodView):
    decorators = [stupid_decorator]

    def get(self, request):
        return text('I am get method')

app.add_route(DummyView.as_view(), '/')
```
## 构建URL
如果希望为HTTPMethodView构建URL，需要将class作为参数传递给`url_for`，例如：
```py
@app.route('/')
def index(request):
    url = app.url_for('SpecialClassView')
    return redirect(url)


class SpecialClassView(HTTPMethodView):
    def get(self, request):
        return text('Hello from the Special Class View!')


app.add_route(SpecialClassView.as_view(), '/special_class_view')
```
## 使用CompositionView
作为`HTTPMethodView`的代替品，可以用`CompositionView`将handler方法移到视图类外面。每个HTTP方法都可以用外部的handler方法接收，然后用`CompositionView.add`添加到视图上。第一个参数是HTTP方法列表，比如`['GET', 'POST']`，第二个参数是handler方法。下面这个例子示范了`CompositionView`的两个使用场景，分别是外部的handler方法和lambda。
```py
from sanic import Sanic
from sanic.views import CompositionView
from sanic.response import text

app = Sanic(__name__)

def get_handler(request):
    return text('I am a get method')

view = CompositionView()
view.add(['GET'], get_handler)
view.add(['POST', 'PUT'], lambda request: text('I am a post/put method'))

app.add_route(view, '/')
```
