# 蓝图
蓝图概念来自**Flask**，意思是可在应用中，用来做子路由的对象。相对于前面章节讲到的增加路由方式，蓝图也定义了类似的方法，但采用插件方式更易于扩展。在大型应用中，蓝图尤其有用，能方便地把服务解耦成各自独立的模块。
## 第一个蓝图
下面示范了一个简单的蓝图，注册了访问`/`路由的handler。假设蓝图文件为`my_blueprint.py`，后面需要`import`到主应用中。
```python
from sanic import response, Blueprint

bp = Blueprint('my_blueprint')

@bp.route('/')
async def bp_root(request):
    return response.json({'my': 'blueprint'})
```
## 注册蓝图
蓝图需要注册到主程序中。
```python
from sanic import Sanic
import my_blueprint

app = Sanic(__name__)
app.blueprint(my_blueprint.bp)

app.run(host='0.0.0.0', port=8000, debug=True)
```
## 使用蓝图
使用方式如同前面章节描述的主应用实例，一样的方式添加中间件，添加路由。
### 中间件
同样可以注册全局中间件。
```python
@bp.middleware('request')
async def print_bp_request(request):
    print('blue request middle')

@bp.middleware('response')
async def print_bp_reponse(request, response):
    print('blue response middle')
```
也可以注册视图内的中间件（详见[视图](./class_based_views.md)）
```python
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
### 异常
蓝图内可以定义自己的异常。
```python
@bp.exception(NotFound)
def ignore_404s(request, exception):
    return text("Yep, I totally found the page: {}".format(request.url))
```
### 开始和结束
蓝图也可以像主应用一样使用监听器。如果运行在多进程模式下，会在某个进城创建后触发该事件。可用的事件如下，事件触发方式与主应用一致：
- before_server_start
- after_server_start
- before_server_stop
- after_server_stop
```python
bp = Blueprint('my_blueprint')

@bp.listener('before_server_start')
async def setup_connection(app, loop):
    global database
    database = mysql.connect(host='127.0.0.1'...)

@bp.listener('after_server_stop')
async def close_connection(app, loop):
    await database.close()
```
### 用例：API变换
蓝图可以方便地实现API变换，比如一个蓝图指向`/v1/<routes>`，另一个指向`/v2/<routes>`。当蓝图创建时，可以使用`url_prefix`参数，用来指名当前蓝图下所有路由的前缀。这个特性可以用来实现API变换。
```python
from sanic import response, Blueprint

blueprint_v1 = Blueprint('v1', url_prefix='/v1')
blueprint_v2 = Blueprint('v2', url_prefix='/v2')

@blueprint_v1.route('/')
async def api_v1_root(request):
    return response.text('Welcome to version 1 of our documentation')

@blueprint_v2.route('/')
async def api_v2_root(request):
    return response.text('Welcome to version 2 of our documentation')
```
当在应用中注册蓝图后，`/v1`和`/v2`路由会分别指向特定的蓝图，可以用来给不同的子站点应用对应的API。
```python
# main.py
from sanic import Sanic
from blueprints import blueprint_v1, blueprint_v2

app = Sanic(__name__)
app.blueprint(blueprint_v1, url_prefix='/v1')
app.blueprint(blueprint_v2, url_prefix='/v2')

app.run(host='0.0.0.0', port=8000, debug=True)
````
如果main.py的注册程序和my_blurprint.py初始化中都有url_prefix参数，那么main的会覆盖掉Blueprint初始化的设定。app.py源码中也可以证明
```python
def blueprint(self, blueprint, **options):
        if blueprint.name in self.blueprints:
            assert self.blueprints[blueprint.name] is blueprint, \
                'A blueprint with the name "%s" is already registered.  ' \
                'Blueprint names must be unique.' % \
                (blueprint.name,)
        else:
            self.blueprints[blueprint.name] = blueprint
            self._blueprint_order.append(blueprint)
        # 覆盖掉blurprint实例的设定
        blueprint.register(self, options)
```
### 用`url_for`创建URL
如果需要在蓝图中创建路由，记得端点格式是`<blueprint_name>.<handler_name>`，例如：
```python
@blueprint_v1.route('/')
async def root(request):
    url = request.app.url_for('v1.post_handler', post_id=5) # --> '/v1/post/5'
    return redirect(url)

@blueprint_v1.route('/post/<post_id>')
async def post_handler(request, post_id):
    return text('Post {} in Blueprint V1'.format(post_id))
```