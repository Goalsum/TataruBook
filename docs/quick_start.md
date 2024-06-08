---
title: 快速入门
---
这是为刚开始使用TataruBook的人准备的上手教程。这个教程将通过由浅入深的使用案例来展示TataruBook的一些常用功能。

# 初始化db文件

首先下载和安装TataruBook，如果你还不知道如何下载和安装，见[这里]({{ site.baseurl }}/index.html#如何下载和安装tatarubook)。

为了方便起见，本教程假设使用了第二种安装方式（可执行文件方式）。如果使用的是第一种安装方式（Python脚本方式），需要把本教程中所有命令开头的`tatarubook`换成`python tatarubook.py`。比如，创建db文件的命令从`tatarubook init accounting.db`改为`python tatarubook.py init accounting.db`。

安装好之后，打开操作系统的命令行终端，切换到TataruBook程序所在的目录，然后执行命令：

~~~
tatarubook init accounting.db
~~~

该目录下会多出一个`accounting.db`文件，这就是保存我们的记账数据的db文件。

接下来，用命令添加一种货币类型：

~~~
tatarubook insert accounting.db asset_types NULL Gil 0
~~~

这条命令向[asset_types表]({{ site.baseurl }}/tables_and_views.html#asset_types)中插入一条记录。这条记录包含3个字段：`NULL`表示`asset_index`字段由系统自动生成（唯一索引）；`Gil`表示资产（货币）的名字；`0`表示资产序号，当资产多的时候会用它排序。

TataruBook的大多例子会借用《最终幻想14》游戏里的背景设定来举例。在游戏里通用的货币为`Gil`，所以本教程用它作为主要货币。当然，在实际记账的时候，你可以使用任何想要的货币：人民币、美元、日元……都可以。

这条命令执行后会显示一些奇怪的信息：

~~~
Integrity check after insertion:
start_date should contain exactly 1 row but 0 row(s) are found.
end_date should contain exactly 1 row but 0 row(s) are found.
standard_asset should contain exactly 1 row but 0 row(s) are found.
~~~

这是TataruBook在进行**数据一致性检查**。对于很多报表的计算来说，有些数据信息是必须存在的。但是当前这些数据还没有输入，所以会产生这些提示信息。如果不解决这些问题，以后每次修改数据都会提示这些信息。

让我们逐个解决：

首先把唯一的货币`Gil`设置为记账本位币：

~~~
tatarubook overwrite accounting.db standard_asset Gil
~~~

然后设置**统计周期**的开始时间和结束时间：

~~~
tatarubook overwrite accounting.db start_date 2022-12-31
tatarubook overwrite accounting.db end_date 2023-12-31
~~~

注意：统计周期是从`start_date`那天的**结束**时开始的，所以如果希望统计2023年一整年的数据，不要写成`2023-1-1`，否则将会漏掉第一天的数据。

现在看起来数据一致性的问题解决了，TataruBook报告：

~~~
Integrity check after overwrite:
Everything is fine, no integrity breach found.
~~~

实际上，统计周期可以在以后随时进行修改。当你拥有了几年的记账数据后，你可以修改[start_date]({{ site.baseurl }}/tables_and_views.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views.html#end_date)表来观察任何一段历史时期的财务状况。

# 开始记账

先添加一个银行账户：

~~~
tatarubook insert accounting.db accounts NULL 萨雷安银行活期 Gil 0
~~~

这表示账户的名字是`萨雷安银行活期`，对应的资产类型（货币）是`Gil`，最后的`0`表示该账户为**内部账户**。

你可能会奇怪内部账户是什么？——很快你就知道了。假设在记账前，`萨雷安银行活期`账户里面已经有一笔余额了，现在我们希望把这笔余额的数据输入到TataruBook。但是TataruBook使用[复式记账]({{ site.baseurl }}/tables_and_views.html#简化的复式记账法)，**要向某个账户增加资产，一定要有某个账户等量的减少资产**。为了满足这个要求，我们添加一个名为`历史结余`的**外部账户**（注意最后一个字段值为`1`）：

~~~
tatarubook insert accounting.db accounts NULL 历史结余 Gil 1
~~~

然后就可以从`历史结余`账户向`萨雷安银行活期`账户转移资产了。下面这条命令给`萨雷安银行活期`账户注入$$ 5000 $$Gil的余额：

~~~
tatarubook insert accounting.db postings NULL 2022-12-31 历史结余 -5000 萨雷安银行活期 初始余额
~~~

所以，内部账户是用户真正拥有的资产，而外部账户仅仅是个形式？——不仅仅如此。接下来我们要记录餐饮消费，先添加一个`餐饮费`外部账户：

~~~
tatarubook insert accounting.db accounts NULL 餐饮费 Gil 1
~~~

然后，添加两笔消费：

~~~
tatarubook insert accounting.db postings NULL 2023-1-5 萨雷安银行活期 -20 餐饮费 旅店早餐
tatarubook insert accounting.db postings NULL 2023-1-7 萨雷安银行活期 -45 餐饮费 背水咖啡厅晚餐
~~~

现在，使用[export命令]({{ site.baseurl }}/commands.html#export)导出[statements视图]({{ site.baseurl }}/tables_and_views.html#statements)：

~~~
tatarubook export accounting.db --table statements
~~~

目录中出现了`statements.csv`文件，用Excel打开它，看到内容如下：

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022-12-31 | 1 | 5000.0 | 2 | 初始余额 | 萨雷安银行活期 | 1 | 0 | 历史结余 | 5000.0 |
| 2 | 2023-01-05 | 1 | -20.0 | 3 | 旅店早餐 | 萨雷安银行活期 | 1 | 0 | 餐饮费 | 4980.0 |
| 3 | 2023-01-07 | 1 | -45.0 | 3 | 背水咖啡厅晚餐 | 萨雷安银行活期 | 1 | 0 | 餐饮费 | 4935.0 |
| 1 | 2022-12-31 | 2 | -5000.0 | 1 | 初始余额 | 历史结余 | 1 | 1 | 萨雷安银行活期,-5000.0 |
| 2 | 2023-01-05 | 3 | 20.0 | 1 | 旅店早餐 | 餐饮费 | 1 | 1 | 萨雷安银行活期 | 20.0 |
| 3 | 2023-01-07 | 3 | 45.0 | 1 | 背水咖啡厅晚餐 | 餐饮费 | 1 | 1 | 萨雷安银行活期 | 65.0 |

使用Excel，既可以按内部账户筛选查看，也可以按外部账户筛选查看。当按照外部账户`餐饮费`筛选时，可以观察内部账户和`餐饮费`之间的所有交易，也就是所有的餐饮费用情况。所以，**外部账户实际上是对收支的分类**。TataruBook的外部账户是由用户自己添加的，所以你可以用任何自己喜欢的方式来分类统计收入和支出。

# 分类收支

# 利息

# 股票投资