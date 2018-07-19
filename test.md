# 接口使用规范
## 服务商控制台管理
服务商填写接口URL时需要按着实际情况填写所需的调用信息，如请求方式、返回类型、请求参数等，不填表示接口对该项无要求。
URL中如果带参数，需要用{xxx}表示，例如：https://api.example.com/user/{uid}/info。
一个URL中参数个数不限，可以有多个：https://api.example.com/user/{uid}/prod/{pid}/info

应用商店显示时会替换域名为统一的https://api.ebizyun.com。

## 用户调用接口
调用接口时，用户需要自行将URL中的参数替换为真实数据，例如：https://api.ebizyun.com/user/40/info。

此外还需用request行参数形式附上相关token，例如：https://api.ebizyun.com/user/40/info?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtZXRoIjoidGhyIiwiaWF0IjoxNTI5OTkzNDU2LjQ3NSwidXJsIjoiWnZiNTNyTG16WUhtaFU2SFZLRHZ5azVKQjIyZGc3NWVId1JkQ2FuVmRqV2pDSkVvam9WdmdrUnNCNVZqb2UxMCIsImV4cCI6MTUzMDQ5NzA3NywicG8iOiI5ODkyMjY2MjU2IiwidHlwZSI6ImFwaSJ9.Dfl4SOrlUJR_Ro7wxOPCj0VGQpjzF4wjcOVpdcO2mvY

所需参数、方法、header等请依照接口信息填写，如果有其它request行参数，进行utf-8的urlEncode后附在token参数后面即可（参数顺序可随意，不影响调用），例如：
https://api.ebizyun.com/user/40/info?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtZXRoIjoidGhyIiwiaWF0IjoxNTI5OTkzNDU2LjQ3NSwidXJsIjoiWnZiNTNyTG16WUhtaFU2SFZLRHZ5azVKQjIyZGc3NWVId1JkQ2FuVmRqV2pDSkVvam9WdmdrUnNCNVZqb2UxMCIsImV4cCI6MTUzMDQ5NzA3NywicG8iOiI5ODkyMjY2MjU2IiwidHlwZSI6ImFwaSJ9.Dfl4SOrlUJR_Ro7wxOPCj0VGQpjzF4wjcOVpdcO2mvY&field=nickname_icon

## 返回值
API网关返回类型：
|错误原因|状态码<br/>信息|
|:------|:------:|
|未提供token|400|
|token不符合易商云规范|400|
|token已失效|200<br/>token invalid|
|调用次数达到上限|200<br/>order over threshold|
