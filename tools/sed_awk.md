# SED & AWK 介绍

我们运维团队因为经常要分析和格式化日志文件，但又不习惯命令行下的处理工具，所以处理效率实在不高。为了帮助大家提高工作效率，我从自己使用经验出发，整理了两个强大的命令行流处理工具 **SED** 和 **AWK** 简单实用方法，希望能有帮助。

## SED

SED诞生自unix早期，由unix发明人编写，可以说是根正苗红的大佬级工具。SED全名是*stream editor*，也就是流编辑器，从名字上也能看出来这个编辑器处理文本的方式是边读边处理，一次处理一行内容。可以理解，当年机子内存那么小，一下把文本都读进去，直接卡死啥也甭想干了。SED本身逻辑非常简单，能玩出花样的地方就是正则部分，所以一定要先学会正则，再来学SED。本文不会介绍正则基础知识，也不打算系统性地讲解SED（主要是可讲的东西太多了），如果想系统性学习，可以参考[SED手册](http://www.gnu.org/software/sed/manual/sed.html)，这是GNU版的，还有一个BSD版的也比较流行，这两款在语法上有些差异。

### Hello World

通常Hello World是从陌生到熟悉的关键一步，这里简单地演示下如何替换文本文字，帮大家熟悉SED风格。
我们先准备一段测试文本:

```bash
$ cat test.txt
2020-5-25 200 client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome
2020-5-25 200 client's name is firefox
2020-5-25 200 client's name is w3m
```

然后把其中的client改成browser。

```bash
sed "s/client/browser/g" test.txt
```

非常符合*nix风格，很好理解：`s`表示替换命令，第一个`/***/`表示要匹配的自负，第二个`/***/`表示把匹配替换成什么，`g`表示一行上的替换所有的匹配。script也可以用单引号`'`，但要注意，无法用转义字符表示单引号，例如。

```bash
sed "s/client's/my/g" test.txt
```

来个实际的例子，比如说我们要统计某个目录下的文件类型，可以这么操作：

```bash
find / -type f | sed 's/.*\.//' | sort -u
```

上面的操作仅仅在终端打印了结果，但并没有改变文件内容，如果想保存结果，可以用重定向

```bash
sed "s/client/browser/g" test.txt > result.txt
```

或直接修改原始文件

```bash
sed -i "s/client/browser/g" test.txt
```

SED使用标准正则，想了解详细正则规范，可以参照[SED帮助](http://www.gnu.org/software/sed/manual/sed.html#Regular-Expressions-Overview)。继续举例子，比如我们想要在每行开头加点东西，可以这么做。

```bash
$ sed "s/^/- /g" test.txt
- 2020-5-25 200 client's name is ie
- 2020-5-25 200 client's name is safari
- 2020-5-25 200 client's name is chrome
- 2020-5-25 200 client's name is firefox
- 2020-5-25 200 client's name is w3m
```

### 限定范围

有时我们不需要全文替换，可以在sed里限定好范围，比如只给第3行结尾加上省略号：

```bash
$ sed "3s/$/ .../g" test.txt
2020-5-25 200 client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome ...
2020-5-25 200 client's name is firefox
2020-5-25 200 client's name is w3m
```

只替换第3~4行的文本：

```bash
$ sed "3,4s/client's/my/g" test.txt
2020-5-25 200 client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 my name is chrome
2020-5-25 200 my name is firefox
2020-5-25 200 client's name is w3m
```

把每行第2个i改为I：

```bash
$ sed "s/i/I/2" test.txt
2020-5-25 200 client's name Is ie
2020-5-25 200 client's name Is safari
2020-5-25 200 client's name Is chrome
2020-5-25 200 client's name Is firefox
2020-5-25 200 client's name Is w3m
```

把第一行的第3个及以后的0替换成*：

```bash
$ sed '1s/0/*/3g' test.txt
2020-5-25 2** client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome
2020-5-25 200 client's name is firefox
2020-5-25 200 client's name is w3m
```

### 组合匹配

如果我们需要一次替换多个模式，可试试组合匹配，比如每行第2个i改为I，同时把第一行的第3个及以后的0替换成*：

```bash
$ sed "s/i/I/2; 1s/0/*/3g" test.txt
2020-5-25 2** client's name Is ie
2020-5-25 200 client's name Is safari
2020-5-25 200 client's name Is chrome
2020-5-25 200 client's name Is firefox
2020-5-25 200 client's name Is w3m
```

以上命令等价于：

```bash
$ sed -e "s/i/I/2" -e "1s/0/*/3g" test.txt
2020-5-25 2** client's name Is ie
2020-5-25 200 client's name Is safari
2020-5-25 200 client's name Is chrome
2020-5-25 200 client's name Is firefox
2020-5-25 200 client's name Is w3m
```

### 提取变量

比如我们想用[]括起来client的名字，可以使用`&`当作被匹配的变量：

```bash
$ sed 's/\<\w*\>$/[&]/g' test.txt
2020-5-25 200 client's name is [ie]
2020-5-25 200 client's name is [safari]
2020-5-25 200 client's name is [chrome]
2020-5-25 200 client's name is [firefox]
2020-5-25 200 client's name is [w3m]
```

如果想提取出来所有client的名字，可以用`()`匹配，用`\` + 数字获取第N对`()`的匹配结果：

```bash
$ sed 's/.*\(\<\w*\>$\)/\1/g' test.txt
ie
safari
chrome
firefox
w3m
```

注意，括号必须用`\`转义，否则sed无法找到匹配内容，报`invalid reference`错误。

### 常用参数

- **a和i**

类似vim中的a和i，sed里是操作行的

```bash
# 在第一行前插入一行
$ sed '1i Insert a line.' test.txt
Insert a line.
2020-5-25 200 client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome
2020-5-25 200 client's name is firefox
2020-5-25 200 client's name is w3m

# 在firefox所在行后追加一行
$ sed '/firefox/a Insert a line.' test.txt
2020-5-25 200 client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome
2020-5-25 200 client's name is firefox
Insert a line.
2020-5-25 200 client's name is w3m
```

- **c**

类似vim中的c命令，sed中可以替换匹配到的行。

```bash
# 替换firefox所在行
$ sed '/firefox/c The replaced line.' test.txt
2020-5-25 200 client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome
The replaced line.
2020-5-25 200 client's name is w3m
```

- **d**

类似vim中的d命令，sed中可以删除匹配到的行。

```bash
# 删除firefox所在行
$ sed '/firefox/d' test.txt
2020-5-25 200 client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome
2020-5-25 200 client's name is w3m
```

- **p**

输出匹配到的行。

```bash
# 输出firefox所在的行
$ sed -n '/firefox/p' test.txt
2020-5-25 200 client's name is firefox
```

注意，这里我们加了个`-n`参数，保证只输出被选中的行，否则sed会输出所有处理过的内容，比如：

```bash
$ sed '/firefox/p' test.txt
2020-5-25 200 client's name is ie
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome
2020-5-25 200 client's name is firefox
2020-5-25 200 client's name is firefox
2020-5-25 200 client's name is w3m
```

输出从safari到firefox的行：

```bash
$ sed -n '/safari/,/firefox/p' test.txt
2020-5-25 200 client's name is safari
2020-5-25 200 client's name is chrome
2020-5-25 200 client's name is firefox
```

### 扩展理解

首先sed的命令脚本格式都是这样的： `[address[,address]]function`。所谓`function`就是参数后面的一个字母命令。

#### Addresses

address可以是个十进制数字，也可以是一个模式，可以用逗号分隔表示两个address区间。

1. 对于像`addr1,addr2`这种形式的地址匹配，如果addr1匹配，则匹配成功，**开关**打开，在该行上执行命令，此时不管addr2是否匹配，即使addr2在addr1这一行之前。

1. 接下来读入下一行，看addr2是否匹配，如果addr2在addr1之前，则不匹配，不执行命令，关闭**开关**。如果addr2匹配，则执行命令，同样开关**关闭**。如果addr2在addr1之后，则一直处理到匹配为止，换句话说，如果addr2一直不匹配，则开关一直不关闭，因此会持续执行命令到最后一行。

#### Pattern Space & Hold Space

sed处理时，会把当前处理的行存储在临时缓冲区中，称为**模式空间**（pattern space），接着用sed命令处理缓冲区中的内容，处理完成后，把缓冲区的内容打印到标准输出，最后清空缓冲区继续处理下一行，这样不断重复直到文件末尾。而**保持空间**（hold space）则是sed中的另外一个缓冲区，此缓冲区不会自动清空，但也不会主动把内容打印到标准输出中。而是需要以下sed命令进行处理：

- g：将hold space中的内容拷贝到pattern space中，原来pattern space里的内容清除
- G：将hold space中的内容append到pattern space\n后
- h：将pattern space中的内容拷贝到hold space中，原来的hold space里的内容被清除
- H：将pattern space中的内容append到hold space\n后
- x：交换pattern space和hold space的内容

一个使用hold space常见的例子就是如何反序输出文件内容，例如我们有个文件内容如下：

```bash
$ cat tt.txt
1
2
3
```

可以用这个命令反序输出文件内容：

```bash
$ sed '1!G;h;$!d' tt.txt
3
2
1
```

利用反复拷贝和覆盖pattern space及hold space的方式实现反序文件内容，最后把结果拷贝到pattern space中，让sed自动输出。流程图来自[酷壳](https://coolshell.cn)<br/>![流程图](https://coolshell.cn/wp-content/uploads/2013/02/sed_demo.jpg)<br/>蓝色为pattern space，绿色为hold space。


## AWK

AWK是一种文本处理和模式匹配语言，它比SED晚几年诞生，基本和C是同时代的产物，并且它的三位作者之一Brian Kernighan，即是unix的发明人之一，也是第一本C语言教程的编写者，所以awk语法风格非常类似C语言。AWK擅长于处理数据库和表型数据，如从多个数据集中提取一些列、建立报表或分析数据。事实上，AWK适合于编写短小的、一次性程序，以执行一些灵活的文本处理，而使用其他的语言则可能成本较高。另外，作为一种功能强大的工具，AWK常常在命令行中使用或与管道一起使用。

AWK问世以来发展出多个版本，现如今我们常用的GAWK（GNU AWK），它的特点是：

- 没有预定义的内存限制。
- 可以使用特殊文件支持来访问标准的*NIX流。
- 可以使用Lint检查。
- 默认使用扩展的正则表达式。
- 支持无限制的行长度和连续使用反斜杠字符。
- 包含一些TCP/IP网络函数。

无论哪个版本的AWK，都是按行读取文件/标准输入流内容。

### Hello&nbsp;&nbsp;World

了解基本概念后，当然是动手尝试了。例如我们`netstat -antpl > netstat.txt`生成一个测试文件，想要获取协议（第一列）和本地地址（第四列）的内容，操作方式如下：

```bash
$ awk '{print $1, $4}' netstat.txt
Active (servers
Proto Local
tcp 0.0.0.0:9003
tcp 172.24.36.24:6379
tcp 0.0.0.0:9004
tcp 0.0.0.0:13004
tcp 0.0.0.0:9005
tcp 127.0.0.1:13005
tcp 0.0.0.0:9006
tcp 0.0.0.0:13006
tcp 0.0.0.0:9999
tcp 0.0.0.0:9007
tcp 0.0.0.0:80
tcp 0.0.0.0:9008
tcp 0.0.0.0:22
tcp 0.0.0.0:443
tcp 127.0.0.1:32000
tcp 0.0.0.0:9001
tcp 0.0.0.0:9002
...
```

首先看第一行是怎么回事？看下文件，原来第一行不符合awk获取列的定义，可以用刚学的sed命令瞅一眼：

```bash
$ sed -n '1p' netstat.txt
Active Internet connections (servers and established)
```

这里我们可以结合sed，只处理从地二行开始的内容：

```bash
$ sed -n '2,$p' netstat.txt | awk '{print $1, $4}'
Proto Local
tcp 0.0.0.0:9003
tcp 172.24.36.24:6379
tcp 0.0.0.0:9004
tcp 0.0.0.0:13004
tcp 0.0.0.0:9005
tcp 127.0.0.1:13005
tcp 0.0.0.0:9006
tcp 0.0.0.0:13006
tcp 0.0.0.0:9999
tcp 0.0.0.0:9007
tcp 0.0.0.0:80
tcp 0.0.0.0:9008
tcp 0.0.0.0:22
tcp 0.0.0.0:443
tcp 127.0.0.1:32000
tcp 0.0.0.0:9001
tcp 0.0.0.0:9002
...
```

发现还是有问题，第四列应该是*Local Address*，怎么这里只剩下*Local*了？原来AWK默认分隔符是空格，它没法区分列内空格还是列间空格。我们可以用sed先把列内空格替换成别的字符，然后再调用AWK：

```bash
$ sed -n '2,$p' netstat.txt| sed '1s/^\(\<\w\+\)\s\+\(\<\w\+\-\w\+\)\s\+\(\<\w\+\-\w\+\)\s\+\(\<\w\+\)\s\(\w\+\).*/\1 \2 \3 \4-\5/g' | awk '{printf "%-8s\t%-18s\n", $1, $4}'
Proto   	Local-Address
tcp     	0.0.0.0:9003
tcp     	172.24.36.24:6379
tcp     	0.0.0.0:9004
tcp     	0.0.0.0:13004
tcp     	0.0.0.0:9005
tcp     	127.0.0.1:13005
tcp     	0.0.0.0:9006
tcp     	0.0.0.0:13006
tcp     	0.0.0.0:9999
tcp     	0.0.0.0:9007
tcp     	0.0.0.0:80
tcp     	0.0.0.0:9008
tcp     	0.0.0.0:22
tcp     	0.0.0.0:443
tcp     	127.0.0.1:32000
tcp     	0.0.0.0:9001
tcp     	0.0.0.0:9002
...
```

大括号里面就是AWK语句。须注意，大括号只能被单引号包含。其中的$1..$n表示第几例。 *$0表示整行*

前面说了AWK语法非常类似C，其中许多特性，包括控制语句和字符串函数，如`printf`和`sprintf`，基本上都是相同的，比如格式化输出:

```bash
$ sed -n '2,$p' netstat.txt | awk '{printf "%-8s\t%-18s\n", $1, $4}' | more
Proto   	Local
tcp     	0.0.0.0:9003
tcp     	172.24.36.24:6379
tcp     	0.0.0.0:9004
tcp     	0.0.0.0:13004
tcp     	0.0.0.0:9005
tcp     	127.0.0.1:13005
tcp     	0.0.0.0:9006
tcp     	0.0.0.0:13006
tcp     	0.0.0.0:9999
tcp     	0.0.0.0:9007
tcp     	0.0.0.0:80
tcp     	0.0.0.0:9008
tcp     	0.0.0.0:22
tcp     	0.0.0.0:443
tcp     	127.0.0.1:32000
tcp     	0.0.0.0:9001
tcp     	0.0.0.0:9002
...
```

### 过滤记录

AWK更常当过滤器来使用，比如要提取出所有网络发送队列不为0，并且状态为ESTABLISHED的记录。

```bash
$ awk '$3!=0 && $6=="ESTABLISHED" ' netstat.txt
tcp        0     36 172.24.36.24:22         36.112.91.242:65397     ESTABLISHED 12709/sshd: root@pt
```

通常可以再加上表头一起打印，更清晰些：

```bash
$ awk '$3!=0 && $6=="ESTABLISHED" || NR==2' netstat.txt
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0     36 172.24.36.24:22         36.112.91.242:65397     ESTABLISHED 12709/sshd: root@pt
```

`NR`是AWK的内置变量，表示从开始记录的行号，因为netstat.txt中表格从第二行开始，所以筛选条件是`NR==2`。最后做点格式化输出：

```bash
$ awk '$3!=0 && $6=="ESTABLISHED" || NR==2 {printf "%-8s\t%-10s\n", $3, $6}' netstat.txt
Send-Q  	Foreign
36      	ESTABLISHED
```

### 内置变量

前面用`NR`来筛选特定的行，AWK有很多内置变量，我们常用的有：

|变量|描述|
|--------:|----------:|
|$0|当前记录（这个变量中存放着整个行的内容）。|
|$1 ~ $n|当前记录的第n个字段，字段间由FS分隔。|
|FS|输入字段分隔符，默认是空格或Tab。|
|NF|当前记录中的字段个数，就是有多少列。|
|NR|已经读出的记录数，就是行号，从1开始，如果有多个文件话，这个值也是不断累加中。|
|FNR|当前记录数，与NR不同的是，这个值会是各个文件自己的行号。|
|RS|输入的记录分隔符，默认为换行符。|
|OFS|输出字段分隔符，默认也是空格。|
|ORS|输出的记录分隔符，默认为换行符。|
|FILENAME|当前输入文件的名字。|
|IGNORECASE|当 IGNORECASE 设置为非空值，GAWK 将忽略模式匹配中的大小写。|

举个例子说明，比如说我们要输出行号：

```bash
$ awk '$3!=0 && $6=="ESTABLISHED" || NR==2 {printf "%d\t%-8s\t%-10s\n", NR, $3, $6}' netstat.txt
2	Send-Q  	Foreign
66	36      	ESTABLISHED
```

### 制定分隔符

AWK默认用空格做分隔符，但是有些场景下我们要用其它符号做分隔符，比如如果处理/etc/passwd文件时：

```bash
$ awk  'BEGIN{FS=":"} {print $1,$3,$6}' /etc/passwd
root 0 /root
bin 1 /bin
daemon 2 /sbin
adm 3 /var/adm
lp 4 /var/spool/lpd
sync 5 /sbin
shutdown 6 /sbin
halt 7 /sbin
mail 8 /var/spool/mail
operator 11 /root
games 12 /usr/games
ftp 14 /var/ftp
nobody 99 /
systemd-network 192 /
dbus 81 /
sshd 74 /var/empty/sshd
```

`BEGIN`表达式用来给AWK程序赋予初始状态，同理还有个`END`表达式，用来执行一些收尾工作。上述命令也等价于：

```bash
awk  -F: '{print $1,$3,$6}' /etc/passwd
```

如果要指定多个分隔符，可以数组表示：`FS=[:;]`。

`BEGIN`中可以放多条语句，用`;`分隔即可，比如我们设定输出分隔符为`\t`：

```bash
$ awk 'BEGIN{FS=":"; OFS="\t"} {print $1,$3,$6}' /etc/passwd
root	0	/root
bin	1	/bin
daemon	2	/sbin
adm	3	/var/adm
lp	4	/var/spool/lpd
sync	5	/sbin
shutdown	6	/sbin
halt	7	/sbin
mail	8	/var/spool/mail
operator	11	/root
games	12	/usr/games
ftp	14	/var/ftp
nobody	99	/
systemd-network	192	/
dbus	81	/
sshd	74	/var/empty/sshd
```

上面语句等价于

```bash
awk -F: 'OFS="\t" {print $1,$3,$6}' /etc/passwd
```

### 字符串匹配

AWK（GAWK）的匹配机制类似egrep，把规则用`//`括起来，比如说我们想匹配有*java*字样的行：

```bash
awk ' /java/ {print $4,$5,$7}' OFS="\t" netstat.txt
0.0.0.0:9003	0.0.0.0:*	17362/java
0.0.0.0:9004	0.0.0.0:*	9432/java
0.0.0.0:13004	0.0.0.0:*	4982/java
0.0.0.0:9005	0.0.0.0:*	21614/java
127.0.0.1:13005	0.0.0.0:*	4982/java
0.0.0.0:9006	0.0.0.0:*	17485/java
0.0.0.0:13006	0.0.0.0:*	4982/java
0.0.0.0:9007	0.0.0.0:*	17547/java
0.0.0.0:9008	0.0.0.0:*	12472/java
127.0.0.1:32000	0.0.0.0:*	11740/java
0.0.0.0:9001	0.0.0.0:*	24855/java
0.0.0.0:9002	0.0.0.0:*	2787/java
127.0.0.1:31000	127.0.0.1:32000	11740/java
172.24.36.24:13006	194.61.54.237:63544	4982/java
172.24.36.24:36218	172.24.36.24:3306	9432/java
172.24.36.24:60274	172.24.36.24:3306	21614/java
172.24.36.24:60414	172.24.36.24:3306	17547/java
172.24.36.24:60396	172.24.36.24:3306	17362/java
...
```

如果想精确匹配某一列内容，可以用`$n`变量：

```bash
$ awk '$7 ~ /java/ {print $4,$5,$7}' OFS="\t" netstat.txt
0.0.0.0:9003	0.0.0.0:*	17362/java
0.0.0.0:9004	0.0.0.0:*	9432/java
0.0.0.0:13004	0.0.0.0:*	4982/java
0.0.0.0:9005	0.0.0.0:*	21614/java
127.0.0.1:13005	0.0.0.0:*	4982/java
0.0.0.0:9006	0.0.0.0:*	17485/java
0.0.0.0:13006	0.0.0.0:*	4982/java
0.0.0.0:9007	0.0.0.0:*	17547/java
0.0.0.0:9008	0.0.0.0:*	12472/java
127.0.0.1:32000	0.0.0.0:*	11740/java
0.0.0.0:9001	0.0.0.0:*	24855/java
0.0.0.0:9002	0.0.0.0:*	2787/java
127.0.0.1:31000	127.0.0.1:32000	11740/java
172.24.36.24:13006	194.61.54.237:63544	4982/java
172.24.36.24:36218	172.24.36.24:3306	9432/java
```

### 基础语法
`~`是AWK的运算符，用来进行ERE（extended regular expression）匹配的。下面是AWK表达式优先级的一个排序表，基本和C语言一致：

|语法|功能（🄲表示同C语言）|结果类型|运算方向|
|----:|----:|----:|
|( expr )|组合运算|同expr结果|N/A|
|$expr|引用列|String|N/A|
|++ lvalue|🄲|Numeric|N/A|
|-- lvalue|🄲|Numeric|N/A|
|lvalue ++|🄲|Numeric|N/A|
|lvalue --|🄲|Numeric|N/A|
|expr ^ expr|指数运算|Numeric|←|
|! expr|🄲|Numeric|N/A|
|+ expr|🄲|Numeric|N/A|
|- expr|🄲|Numeric|N/A|
|expr \* expr|🄲|Numeric|→|
|expr / expr|🄲|Numeric|→|
|expr % expr|🄲|Numeric|→|
|expr + expr|🄲|Numeric|→|
|expr - expr|🄲|Numeric|→|
|expr expr|拼接字符串|String|→|
|expr < expr|🄲|Numeric|None|
|expr <= expr|🄲|Numeric|None|
|expr != expr|🄲|Numeric|None|
|expr == expr|🄲|Numeric|None|
|expr > expr|🄲|Numeric|None|
|expr >= expr|🄲|Numeric|None|
|expr ~ expr|正则匹配|Numeric|None|
|expr !~ expr|正则不匹配|Numeric|None|
|expr in array|数组成员|Numeric|→|
|( index ) in array|多维数组成员|Numeric|→|
|expr && expr|🄲|Numeric|→|
|expr || expr|🄲|Numeric|→|
|expr1 ? expr2 : expr3|🄲|选中的expr2或者expr3|←|
|lvalue ^= expr|指数运算+赋值|Numeric|←|
|lvalue %= expr|🄲|Numeric|←|
|lvalue *= expr|🄲|Numeric|←|
|lvalue /= expr|🄲|Numeric|←|
|lvalue += expr|🄲|Numeric|←|
|lvalue -= expr|🄲|Numeric|←|
|lvalue = expr|🄲|expr类型|←|

掌握AWK基础语法后，我们可以让它变得更灵活些了，比如按着状态保存netstat结果：

```bash
$ awk 'NR!=2 {if($6 ~ /TIME|ESTABLISHED/) print > "1.txt";
else if($6 ~/LISTEN/) print > "2.txt";
else print > "3.txt";}' netstat.txt
```

还可以灵活统计文件大小，比如我们要统计所有pdf文件大小总和有多少MB：

```bash
$ find ./ -name '*.pdf' -exec du -ks {} \; | awk '{total=total+$1;} END {print total/1024;}'
98527
```

还可以统计每个用户的进程占了多少MB内存：

```bash
$ ps aux | awk 'NR!=1{a[$1]+=$6;} END {for(i in a) print i ", " a[i]/1024"MB";}'
java_dev, 5263.68MB
dbus, 0.8125MB
polkitd, 7.03125MB
nobody, 88.1875MB
mysql, 756.59MB
ntp, 1.09766MB
root, 844.199MB
```

### 再说BEGIN和END

前面简单用到了BEGIN和END两个特殊模式。每个BEGIN模式只会执行一次，它表示在读取第一个输入和命令行任务完成前。每个END模式也是只会被执行一次，它表示读取最后一个输入之后。BEGIN和END不能联合其它模式使用。AWK里允许使用多个BEGIN和END，它们执行时就按程序中的顺序进行。写AWK程序时，END和BEGIN前后顺序不影响END和BEGIN触发条件，END甚至可以写在BEGIN之前。举个例子说明，假如我们有个学生成绩表：

```bash
$ cat score.txt
2143 张二楞 78 84 77
2321 王铁蛋 66 78 85
2122 刘大头 88 77 71
2537 李小花 87 97 95
2415 赵有财 90 77 62
```

因为这里的AWK代码比较长，再直接写在命令行里执行会变得既不方便，也难以调试，所以单独写个AWK脚本，然后用`-f`命令执行它。我们的AWK脚本如下：

```bash
$ cat cal.awk
#!/bin/awk -f

BEGIN {
    math = 0
    english = 0
    computer = 0
    printf "NO.       姓名     数学     英语     语文    总计\n"
    printf "-------------------------------------------------\n"
}

{
    math+=$3
    english+=$4
    words+=$5
    printf "%-6s %-6s %4d %8d %8d %8d\n", $1, $2, $3, $4, $5, $3+$4+$5
}

END {
    printf "-------------------------------------------------\n"
    printf "  TOTAL:%10d %8d %8d \n", math, english, words
    printf "AVERAGE:%10.2f %8.2f %8.2f\n", math/NR, english/NR, words/NR
}
```

可以用`awk -f`命令执行，另外因为我们awk脚本第一行写了执行命令，所以也可以先给cal.awk赋予可执行权限（`chmod +x cal.awk`），然后像直接运行可执行文件一样执行它。执行结果如下：

```bash
$ ./cal.awk score.txt
NO.       姓名     数学     英语     语文    总计
-------------------------------------------------
张二楞    2143     78       84       77      239
王铁蛋    2321     66       78       85      229
刘大头    2122     88       77       71      236
李小花    2537     87       97       95      279
赵有财    2415     90       77       62      229
-------------------------------------------------
  TOTAL:       409      413      390
AVERAGE:     81.80    82.60    78.00
```

## 总结

很多网上资料说SED是按行处理，AWK是按列处理，但根据我的经验，它们两个都是按行读取内容，也都可以做成按行/列输出结果，行列并不是本质区别。我认为SED的优势是正则，AWK的优势在格式化。如果我们需要通过**区域选择+正则筛选**挑选内容，需要**增删改查**处理数据，那么优先考虑用**SED**。如果我们的工作模式是**预处理→逐行处理→收尾工作**，同时需要**格式化**输出结果，请优选考虑**AWK**。很多时候我们结合着用这两款工具，用好*uix的管道和重定向，灵活组合使用各类工具，才能最终方便我们工作。
