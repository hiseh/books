# 日志
Sanic允许你基于[python3 logging API](https://docs.python.org/3/howto/logging.html)，创建不同级别的log。建议阅读本章之前，先拥有基本的python3 logging知识。
## 快速开始
一个使用默认配置的简单例子：
```py
rom sanic import Sanic

app = Sanic('test')

@app.route('/')
async def test(request):
    return response.text('Hello World!')

if __name__ == "__main__":
  app.run(debug=True, access_log=True)
```
如果想使用自己的日志配置，可以在初始化Sanic应用是，用`logging.config.dictConfig`，或者通过`log_config`参数：
```py
app = Sanic('test', log_config=LOGGING_CONFIG)
```
如果想关闭日志，可以设置access_log=False：
```py
app.run(debug=False, access_log=False)
```
这么配置，会忽略掉request处理时的日志方法，能加快系统运行速度。
## 配置
默认的，`log_config`参数使用`sanic.log.LOGGING_CONFIG_DEFAULTS`字典作为配置。
```py
import logging

log = logging.getLogger(__name__)

LOG_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            # 'class': 'logging.handlers.RotatingFileHandler',
            # 'filename': './log/error.log',
            'level': 'DEBUG',
            'formatter': 'default',
            # 'encoding': 'utf-8'
        },
        'error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'debug',
            'filename': './log/error.log',
            'maxBytes': 1024 * 1024 * 200,
            'backupCount': 5,
            'encoding': 'utf-8'
        },
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s:%(lineno)d | %(message)s',
        },
        'debug': {
            'format': '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d | %(message)s',
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'error'],
            'propagate': True
        },
    }
}
```