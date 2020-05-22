# 几种生成分布式ID的方式

外甥的游戏服务端要做成分布式部署，因此在多台服务器都各自生成业务ID的情况下，如何设计好分布式ID是第一个要解决的问题。首先设计系统前，定义好约束条件：

**必须满足的条件**

1. 唯一性：这没什么可说的，分布式ID的核心需求，必须满足。

**优先满足的条件**

2. 高性能和高可用：都上分布式架构了，高性能和高可用怎么也得提一下。
3. 业务相关：ID应该尽量与业务相关，否则还需维护一套ID和业务的关联关系，增加系统复杂性和出错概率。

定下了目标，我们依次分析下常见的几种ID生成方式。

## UUID

UUID是一种非常常见的唯一标识格式，在[RFC 4122](https://tools.ietf.org/html/rfc4122)中定义了v1，v3，v4和v5四个版本（v2很少被用到）具体的规范，期中我们最常用的是v4版本。通常可以用下面的标准选择具体版本：

- 如果只是需要生成一个唯一ID,可以使用v1或v4。
- v1基于时间戳和MAC地址,这些ID有一定的规律，会暴露我们的MAC地址。
- v4是完全伪随机的，但重复概率非常低，不用考虑重复的可能。
- 如果希望用相同的参数生成相同的UUID,可以使用V3或V5。这两个都是基于HASH算法，一个MD5，一个SHA-1。理论上v3兼容性更好，效率更高，v5算法更先进些。

UUID优点非常多，比如唯一性好（理论上可重复，实际概率非常低），性能高，实现简单。但是也有3个缺点，使得它不适合用在当前业务场合。

1. UUID非常长，用16进制表示需要32个字母。如果存到数据库的话，再加上索引，要占用不少空间存储，总的下来速度也会降低。
2. UUID太随机了，如果用它做主键，建了聚簇索引后，基本上每次插入都需要移动页位置，非常影响插入效率。
3. UUID与业务无关，一个是不能从ID本身解析到任何业务信息，另外就是还要维护一套ID和业务的对应关系，不方便扩展及管理。

## 基于现有数据库的序列形式

无论是MySQL，PostgreSQL这类关系型数据库，还是MongoDB，Redis之类的非关系数据库都提供了生成序列ID的机制。关系型数据库因为要维护B-tree，所以效率不会太高，当大并发写入时会给数据库带来一定压力。另外通常在网络拓扑中，关系型数据库都部署在最后一层，没必要为了生成个ID而把请求发送到最后一层。

## 雪花（Snowflake）算法

雪花算法（Snowflake）是Twitter发明的分布式项目ID生成算法，开源后被很多系统借鉴，现在已经是一个事实上的分布ID标准算法。这是Twitter官方[项目地址](https://developer.twitter.com/ja/docs/basics/twitter-ids)。

这张图片表示地非常清楚，雪花算法就是拼数字的算法，特别容易理解。

![snowflake](https://pic1.zhimg.com/80/v2-89659f2e11fdbdacd672a26b7be42068_1440w.jpg)

1. 首先雪花ID是个`long int`型，一般都用正数表示，所以第一位肯定都是**0**，不用多做考虑。
1. 第二部分是时间戳，Twitter推荐用 *当前时间 - 固定开始时间* 的方式实现，这么做可以满足更大时间范围的需求，41位bit，够用69年了。 *0x1FFFFFFFFFF / (1000 * 60 * 60 * 24 * 365) ≈ 69年*  
1. 第三部分是机器ID，一共10位，最大就是0x3FF，算上0一共有1024个数字。这部分比较简单，机子少时直接写死，甚至为了精确控制，用进程/线程编号都可以。
1. 最后一部分是12位的序列号，最大是0xFFF，共有4096个数字。因为这部分比较短，如果单机并发超过4096 * 1000后，100%会出现重复序列号，此时最好的办法是加服务器，不用都紧着一台生成序列号。

各部分生成好后拼在一起就完成了,当然生产环境必须加上检查，防止数字溢出和重复。以下是demo代码：

```py
# Python
@dataclass
class SnowFlake:
    _last_stamp: int = -1
    _start: int = int(datetime(year=2020, month=1, day=1, tzinfo=timezone.utc).timestamp() * 1000)

    @property
    def _timestamp(self):
        # 生成第二部分
        now = int(datetime.utcnow().timestamp() * 1000)
        if now < self._last_stamp:
            raise RuntimeError
        self._last_stamp = now
        return now - self._start

    @property
    def _serial(self):
        # 生成第四部分
        return random.randint(0, 4095)

    def gen_id(self, mach_id: int) -> int:
        # 生成ID
        if 0 <= mach_id <= 0x3FF:
            return (self._timestamp << 22) | (mach_id << 12) | self._serial
        else:
            raise RuntimeError


sf = SnowFlake()
```

```c
/*
 * C逻辑与Python完全一致。
 * C99标准库里时间函数不够丰富，像生成毫秒级时间戳，操作UTC时区之类的都要自己实现，所以我们可以用*nix的time库。
**/
...
    struct tm start = {.tm_year = 2020 - 1900, .tm_mday = 1};
    timegm(&start) * 1000;
...
    struct timeval tv;
    gettimeofday(&tv, NULL);
...
```

要注意有些语言是没有`long int`类型的。比如JavaScript和lua，它们用`double`存储高精度数字，`double`整数部分只有53位。这种情况下可以用拼字符串的方式生成ID或传输。如果实在想操作数字，lua里可以用luajit，把C数据类型封装进来。

```lua
local ffi = require("ffi")

local lua_var = ffi.new("int64_t", 一个long int数字)
```

## UidGenerator

[UidGenerator](https://github.com/baidu/uid-generator/blob/master/README.zh_cn.md)是百度基于SnowFlake发展出来ID生成器。UidGenerator以组件形式工作在应用项目中, 支持自定义workerId位数和初始化策略, 从而适用于docker等虚拟化环境下实例自动重启、漂移等场景。 在实现上, UidGenerator通过借用未来时间来解决sequence天然存在的并发限制; 采用RingBuffer来缓存已生成的UID, 并行化UID的生产和消费, 同时对CacheLine补齐，避免了由RingBuffer带来的硬件级「伪共享」问题. 最终单机QPS可达600万。

如果用UidGenerator默认的WorkerID分配器，需要在启动阶段通过数据库进行管理。

## Leaf

[Leaf](https://github.com/Meituan-Dianping/Leaf/blob/master/README_CN.md)最早期需求是各个业务线的订单ID生成需求。在美团早期，有的业务直接通过DB自增的方式生成ID，有的业务通过redis缓存来生成ID，也有的业务直接用UUID这种方式来生成ID。以上的方式各自有各自的问题，因此我们决定实现一套分布式ID生成服务来满足需求。具体Leaf 设计文档见： leaf 美团分布式ID生成服务

目前Leaf覆盖了美团点评公司内部金融、餐饮、外卖、酒店旅游、猫眼电影等众多业务线。在4C8G VM基础上，通过公司RPC方式调用，QPS压测结果近5w/s，TP999 1ms。

Leaf 提供两种生成的ID的方式（号段模式和snowflake模式），你可以同时开启两种方式，也可以指定开启某种方式（默认两种方式为关闭状态）。

## Tinyid
[Tinyid](https://github.com/didi/tinyid/wiki)
是用Java开发的一款分布式id生成系统，基于数据库号段算法实现，关于这个算法可以参考美团leaf或者tinyid原理介绍。Tinyid扩展了[Leaf](##Leaf)算法，支持了多db(master)，同时提供了java-client(sdk)使id生成本地化，获得了更好的性能与可用性。Tinyid在滴滴客服部门使用，均通过tinyid-client方式接入，每天生成亿级别的id。

综合比较下来，还是雪花算法最容易实现，也完全能满足初中学生的项目要求，最终决定就它了。
