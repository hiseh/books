# Hello World：
```python
from sanic import Sanic
from sanic import response

app = Sanic(__name__)


@app.route("/")
async def test(request):
    return response.text('Hello World')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
```
- Sanic 构建一个Sanic服务的实例
    - name=None 服务名。通常可以用\_\_name\_\_预置变量，如果name为None，则从之前栈中获得module name。
- route() 路由装饰器，注册一个路由
    - uri URL路径
- run() 运行HTTP Server，直到键盘中断或收到终止信号。终止前，会处理完所有的链接。
    - socket 服务器接收socket连接
    - host host地址，如果socket为None，host = host or '127.0.0.1'。0.0.0.0表示本机上所有IPv4地址，也就是不限定本机地址（一般用于多网卡服务器上）。
    - port host端口