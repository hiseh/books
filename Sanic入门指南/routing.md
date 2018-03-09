# 路由
&emsp;&emsp;用户可以通过路由来设置URL与handler之间的关联。一个基本的路由形式如下：
```python
from sanic import response

@app.route("/")
async def test(request):
    return response.text('Hello World')
```
&emsp;&emsp;sanic的handler方法必须用`async`关键字定义为异步方法。
## Request参数
&emsp;&emsp;request路由规则与flask一致，可以使用变量、正则来设置。
```python
from sanic.response import text

# 参数名: tag，可以是任意字符
@app.route('/tag/<tag>')
async def tag_handler(request, tag):
    return text('Tag - {}'.format(tag))

# 参数名: integer_arg，int类型
@app.route('/number/<integer_arg:int>')
async def integer_handler(request, integer_arg):
    return text('Integer - {}'.format(integer_arg))

@app.route('/number/<number_arg:number>')
async def number_handler(request, number_arg):
    return text('Number - {}'.format(number_arg))

# 参数名: name，英文字母
@app.route('/person/<name:[A-z]+>')
async def person_handler(request, name):
    return text('Person - {}'.format(name))

# 参数名: folder_id，英文字母+数字，0~4个字符长度
@app.route('/folder/<folder_id:[A-z0-9]{0,4}>')
async def folder_handler(request, folder_id):
    return text('Folder - {}'.format(folder_id))
```
## HTTP请求类型
&emsp;&emsp;默认请求类型是GET，如果用其它方法，需要单独指定。
```python
from sanic.response import text

# post方法
@app.route('/post', methods=['POST'])
async def post_handler(request):
    return text('POST request - {}'.format(request.json))

# get方法
@app.route('/get')
async def get_handler(request):
    return text('GET request - {}'.format(request.args))
```
&emsp;&emsp;此外，还可以指定host等额外参数。
```python
@app.route('/get', methods=['GET'], host='example.com')
async def get_handler(request):
    return text('GET request - {}'.format(request.args))

# 如果host头不匹配example.com，会自动使用这条路由
@app.route('/get')
async def get_handler(request):
    return text('GET request in default - {}'.format(request.args))
```
## add_route方法
&emsp;&emsp;如上文所示，通常使用`app.route`装饰器来定义路由规则，实际上这个装饰器封装了`app.add_route`方法，所以可以像下面形式添加路由。
```python
from sanic.response import text

# handler方法
async def handler1(request):
    return text('OK')

async def handler2(request, name):
    return text('Folder - {}'.format(name))

async def person_handler2(request, name):
    return text('Person - {}'.format(name))

# 为每个方法添加路由
app.add_route(handler1, '/test')
app.add_route(handler2, '/folder/<name>')
app.add_route(person_handler2, '/person/<name:[A-z]>', methods=['GET'])
```
&emsp;&emsp;这种方式可以在文件中统一管理路由，代码更清晰。
## 使用url_for创建URL
&emsp;&emsp;handler方法内可以使用`url_for`来创建URL。通过引用handler名字来构建，避免在代码中硬编码URL。
```python
@app.route('/')
async def index(request):
    # 生成一个post_handler的url
    url = app.url_for('post_handler', post_id=5)
    # URL是`/posts/5`

    url = app.url_for('post_handler', post_id=5, arg_one='one', arg_two='two')
    # /posts/5?arg_one=one&arg_two=two

    url = app.url_for('post_handler', post_id=5, arg_one=['one', 'two'])
    # /posts/5?arg_one=one&arg_one=two

    return redirect(url)


@app.route('/posts/<post_id>')
async def post_handler(request, post_id):
    return text('Post - {}'.format(post_id))
```
### 特殊参数
- _anchor 锚点
- _method 现在版本还不支持
- _server 域名和端口号
```python
url = app.url_for('post_handler', post_id=5, arg_one='one', _anchor='anchor')
# /posts/5?arg_one=one#anchor


# you can pass all special arguments one time
url = app.url_for('post_handler', post_id=5, arg_one=['one', 'two'], arg_two=2, _anchor='anchor', _server='another_server:8888')
# http://another_server:8888/posts/5?arg_one=one&arg_one=two&arg_two=2#anchor
```