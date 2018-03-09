# Response
使用`sanic.response`模块创建response。
- 文字
```python
from sanic import response


@app.route('/text')
def handle_request(request):
    return response.text('Hello world!')
```
- HTML
```python
from sanic import response


@app.route('/html')
def handle_request(request):
    return response.html('<p>Hello world!</p>')
```
- json
```python
from sanic import response


@app.route('/json')
def handle_request(request):
    return response.json({
        'message': 'Hello world!',
        # header
        headers={'X-Served-By': 'sanic'},
        # status
        status=200})
```
- file 效率不如nginx高
```python
from sanic import response


@app.route('/file')
async def handle_request(request):
    return await response.file('/srv/www/whatever.png')
```
- redirect
```python
from sanic import response


@app.route('/redirect')
def handle_request(request):
    return response.redirect('/json')
```