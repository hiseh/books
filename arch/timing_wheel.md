<!--
 * @Author: Hiseh
 * @Date: 2020-05-06 10:43:05
 * @LastEditors: Hiseh
 * @LastEditTime: 2020-05-18 22:15:14
 * @Description: 时间轮定时器
 -->
# 用时间轮实现一个高精度定时器
[返回首页](../README.md)<br/>
五一和外甥聊天时得知小家伙正在学开发游戏，而且还是实时战斗类的游戏，我当时随口提了一句，说这类游戏对时效性要求比较高，通常系统自带的定时器精度不够，需要自己实现一个。最近有时间，把实现方式整理一下写出来。一般来说，定时任务有两种形式：

1. 约定某个时间点执行。
1. 约定一段时间后执行。

这两种方式逻辑上是互通的，第一种完全可以用第二种形式表示成从当前时间延迟一段时间后执行，所以我们通常用第二种方式管理定时任务。

## 轮询方式
很多库用不同的方式实现了定时器功能，比如libevent，用I/O非阻塞机制的空余时间做轮询：先定一个基础频率（假设10ms），然后每隔这个频率去检查一次是否有超时的事件。
```py
def update_events(timeout = 10):
    result = selector.select(timeout)
    ...
    update_timer(time.time())

def update_timer (current):
'''
检查需要唤醒的时钟，并调用回调任务
'''
    # 最简单的遍历方式
    # libevent为了避免每次都要检查所有节点，还维护了一个有序堆（最小堆），如果第一个节点超时，则删除并检查下一个节点，否则返回本次检查结果。
    for timer in available_timers:
         while current >= timer.expires:
             timer.callback(current)
             timer.expires += timer.period

while True:
    WAIT_MILLISEC = 10
    update_events(WAIT_MILLISEC)
```
这种方式逻辑上直观易理解，但不适用于数据量大并且超时周期不固定的场合。目前更主流的方式还是Linux Kernel的时间轮算法，该算法可以保证唤醒时钟的时间是个常数，下面就是一个简单的时间轮定时器实现方式。
## 时间轮
所谓时间轮其实就是一个存储了多个时间格的环形队列，一个时间轮结构如图所示：![单一时间轮](https://www.ibm.com/developerworks/aix/library/au-lowertime/fig1.gif)<br/>每个时间格代表当前时间轮的基本时间跨度，用*tickMs*表示。所有任务按着超时时间，依次存放在对应的时间格中。时间轮包含的时间格数量或者说时间轮长度用*wheelSize*表示，因此时间轮总跨度就是*tickMs* x *wheelSize*，用*interval*表示。此外时间轮通常还用一个指针表示当前时间以及用来区分到期和未到期任务，一般用*currentTime*表示，因为时间轮最小的时间跨度是*tickMs*，所以*currentTime*一定是*tickMs*的整倍数。一般用*currentTime*将时间轮划分为到期部分和未到期两部分，*currentTime*当前指向的时间格属于到期部分，此时间格所对应的所有任务都需要做超时处理。为了保证时间轮精度，需要定一个很小的TickMs，此时如果整个定时器时间跨度较长，又会造成时间轮长度过长。比如游戏中设定每隔1ms检查一次子弹轨迹，一枚手雷扔出后要5秒才会爆炸，那么*TickMs*最大是1ms，则整个时间轮至少需要`5000 ÷ 1 = 5000`个格子，最后会造成大量占用内存的情况。所以我们通常用多阶时间轮来满足高精度和长跨度清醒，如图所示（图片来自[朱小厮的博客](https://blog.csdn.net/u013256816/article/details/80697456)）：![多阶时间轮](https://img-blog.csdn.net/20180614194206760?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3UwMTMyNTY4MTY=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

设最低一层时间轮的*tickMs*为1ms，*wheelSize*为20，*interval*为20ms，并且高阶时间轮的*tickMs*为低阶时间轮的*interval*，所有时间轮的*wheelSize*都是固定的20个。初始指针*c<sub>1</sub>* = 0，同时插入一个超时时间为2ms的任务*t<sub>1</sub>*，自然*t<sub>1</sub>*会插入到第一层的第二个时间格*tw_a<sub>2</sub>*中。当*c<sub>1</sub>*指向*tw_a<sub>2</sub>*时，*t<sub>1</sub>*任务会过期。如果此时又来一个超时时间为8ms的任务*t<sub>2</sub>*，那么*t<sub>2</sub>*需要在当前时间基础上延迟8ms过期，所以*t<sub>2</sub>*会插入到*tw_a<sub>10</sub>*处。以上都是在同阶时间轮内操作，很好处理，如果*c<sub>1</sub>* = 10的时候，来了个超时时间是350ms的任务*t<sub>3</sub>*，该如何处理呢？

显然此时第一层时间轮*tw_a*是没法满足了，我们看看第二层时间轮*tw_b*。*tw_b*的*tickMs*为*tw_a*的*interval*，即20ms。每一层时间轮的*wheelSize*是固定的，都是20，那么*tw_b*的*interval* = 400ms，完全可以存下*t<sub>3</sub>*。此时*c<sub>1</sub>* = 10，所以*tw_a*还剩 20 - 10 = 10ms，*tw_b*中需要寻找延迟时间是340ms的格子即可，最终*t<sub>3</sub>*存入*tw_b<sub>17</sub>*。

需要注意的是，越高阶时间轮*tickMs*粒度越大，以*tw_b<sub>1</sub>*为例，可能一个格子里既存了超时时间为20ms，又存了超时时间为39ms的任务，显然我们不能同时超时处理这两个任务，此处我们还需要做个任务降级的机制。当*tw_a*转完一圈时（*c<sub>1</sub>*是*interval<sub>1</sub>*的整倍数），需要提取出*tw_b<sub>1</sub>*中所有任务，将其超时时间减去*c<sub>1</sub>*后，重新分配给*tw_a*。也就是说，只有*tw_a*中的任务才会真正被执行，高阶时间轮的任务仅仅在备场等待。
```c
/*
 * 任务和时间轮结构体
 * 因为一个时间格要存储多个任务，所以时间格可以用链表形式存储。
 * LIST_HEAD和LIST_ENTRY是*nix标准库里宏定义，定义了一个list
**/
typedef void (*ttimer_func_t)(struct ttimer_ref *, void *);
typedef struct ttimer_ref {
    // 私有成员 
    LIST_ENTRY(ttimer_ref) entry;
    time_t remaining;

    ttimer_func_t func;
    void *arg;
    bool scheduled;
} ttimer_ref_t

typedef struct {
    unsigned hand;
    LIST_HEAD(, ttimer_ref) bucket[WHEEL_BUCKETS];
} twheel_t
```
```c
/*
 * 创建时间轮
**/
ttimer_t *ttimer_create(time_t maxtimeout, time_t now) {
    unsigned len, levels = 0;
    ttimer_t *timer;

    while (maxtimeout > 0) {
        maxtimeout = DIV_BY_BUCKETS(maxtimeout);
        levels++;
    }
    levels = levels ? MIN(levels, WHEEL_MAX_LEVELS) : WHEEL_MAX_LEVELS;
    len = offsetof(ttimer_t, wheel[levels]);

    if ((timer = calloc(1, len)) == NULL) {
        return NULL;
    }
    timer->levels = levels;
    timer->lastrun = now;
    return timer;
}
```
```c
/*
 * 启动时间轮组
 * 因为单台部署，所以时间就用本地时间，如果考虑时区问题，建议用UTC。
 * 尽量不要用系统时间计算时间戳，推荐用CPU时钟结合程序启动的时间计算，避免因为系统改时间造成超时计算错误。
 *
**/
void ttimer_start(ttimer_t *timer, ttimer_ref_t *ent, time_t timeout) {
    unsigned level, r, multiplier;
    twheel_t *wheel;

    ASSERT(timeout > 0);
    ASSERT(!ent->scheduled);
    ASSERT(ent->func != NULL);

    level = 0;
    ent->remaining = 0;
    multiplier = 1;

    /*
     * 可以用epoll/queue非阻塞机制循环检查，也可以用事件驱动（比如python自带的asyncio.new_event_loop事件循环策略），当然最直白的用
     * while(1) { sleep(xxx)}
     * 死循环也没问题。
     * 无论哪种方式，都会阻塞当前线程，所以要在新线程中跑任务。
    **/
next:
    wheel = &timer->wheel[level];
    r = MOD_BY_BUCKETS(wheel->hand + timeout);
    timeout = DIV_BY_BUCKETS(wheel->hand + timeout);

    // 切换到高阶时间轮
    if (__predict_false(timeout > 0)) {
        ent->remaining += (r * multiplier);
        multiplier *= WHEEL_BUCKETS;
        level++;

        if (__predict_true(level < WHEEL_MAX_LEVELS)) {
            goto next;
        }

        // 最高阶只能添加全部剩余时间
        ent->remaining += multiplier * (timeout - 1);
        level--;
    }

    // 时间轮入口
    wheel = &timer->wheel[level];
    LIST_INSERT_HEAD(&wheel->bucket[r], ent, entry);
    ent->scheduled = true;
}
```
生产级代码请参照韦易笑写的代码👍🏻

[itimer.h](https://raw.githubusercontent.com/skywind3000/AsyncNet/master/system/itimer.h)<br/>
[itimer.c](https://raw.githubusercontent.com/skywind3000/AsyncNet/master/system/itimer.c)
