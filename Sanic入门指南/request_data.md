# Request
&emsp;&emsp;当服务端收到HTTP请求时，路由方法会传过来`Request`对象。`Request`对象包含以下属性：
- json JSON正文。
```python
from sanic.response import json

@app.route("/json")
def post_json(request):
    return json({ "received": True, "message": request.json })
```
- args dict，例如请求参数为`?key1=value1&key2=value2`，返回`{'key1': ['value1'], 'key2': ['value2']}`
- raw_args dict，更少封装的dict，很多时候比args还实用。例如请求参数为`?key1=value1&key2=value2`，返回`{'key1': 'value1', 'key2': 'value2'}`
- headers dict，一个大小写无关（一般都是小写）的dict，包含request header。

其它常用属性还包括：ip, port, url, host, path, quary_string