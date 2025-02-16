---
title: 快速入门
sidebar:
  nav: "chinese"
---
本页是为刚开始使用TataruBook的人提供的上手教程。此教程通过一个连贯的使用案例来由浅入深的展示TataruBook的常用功能。

# 初始化DB文件

首先下载和安装TataruBook，如果你还不知道如何下载和安装，见[这里]({{ site.baseurl }}/index_cn.html#如何下载和安装tatarubook)。本文假设你使用第一种方式在Windows系统中安装了TataruBook。

安装完成后，打开文件资源管理器，在一个目录中的空白处点右键，选择`TataruBook create DB file`（注意Windows 11会默认隐藏一部分快捷菜单项，你需要先指定显示所有的菜单项）。然后会出现一个窗口要求输入DB文件名：

~~~
Input DB filename to create with(for example: financial.db):
~~~

你可以输入任何自己喜欢的文件名，但是文件名必须以`.db`结尾。在这个例子中，我们输入`accounting.db`并回车，该目录中会多出一个`accounting.db`文件，这就是保存记账数据的**DB文件**。

还有另一种方法也可以创建一个DB文件：打开操作系统的命令行终端，切换到TataruBook程序所在的目录，然后执行命令：

~~~
tatarubook init accounting.db
~~~

这个操作同样会创建`accounting.db`文件。实际上，在使用TataruBook的快捷菜单功能时，TataruBook会自动将快捷菜单指令转换为对应的命令行来执行。因此，每个快捷菜单操作和对应的命令行操作是等价的。

接下来，为了记账，需要先添加一种货币类型。添加货币类型需要修改[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表。为了修改表内容，需要先了解表有哪些字段。我们推荐先使用`export`功能导出这张表再进行修改。

在刚才创建的`accounting.db`文件上点右键，选择`TataruBook export`子菜单下的`asset_types`：

![DB文件的快捷菜单]({{ site.baseurl }}/assets/images/context_menu.png)

弹出的窗口会提示创建了`asset_types.csv`文件。关闭弹出的窗口，使用Excel打开`asset_types.csv`文件，你会看到一个仅包含表头的空表：

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
||||

然后可以在表中添加内容。`asset_index`字段是自动生成的索引，在添加内容时这一列应该为空。`asset_name`字段表示资产（货币）的名字，在这个例子中我们填入`Gil`。`asset_order`字段表示用于排序的资产序号，我们暂时不关心它，先随便填个值`0`。填好后的表格内容如下：

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
|| Gil | 0 |

TataruBook文档中的很多例子借用了《最终幻想14》游戏里的背景设定。在《最终幻想14》中，主要货币为`Gil`，所以本文用这种货币来示例。在实际记账的时候，你可以使用任何货币名字，如人民币、美元、日元等等。
{: .notice}

接下来选中整个表格的内容，按`Ctrl+C`组合键复制到剪贴板，再在`accounting.db`文件上点右键，选择`TataruBook paste`子菜单下的`asset_types`。新添加的这一行就会被插入到`accounting.db`文件里的`asset_types`表中。

实际上，你可以复制表格中的任意一行或多行，再使用`paste`命令将其插入到DB文件中。如果复制的内容含了表头，`paste`命令会自动识别出来并跳过表头。
{: .notice}

刚才的命令执行后，弹出窗口的内容中包含一些奇怪的信息：

~~~
Integrity check after paste:
start_date should contain exactly 1 row but 0 row(s) are found.
end_date should contain exactly 1 row but 0 row(s) are found.
standard_asset should contain exactly 1 row but 0 row(s) are found.
~~~

这是TataruBook进行**数据一致性检查**后报告的问题。TataruBook包含很多分析财务状况的**视图**，其中不少视图需要特定的数据存在才能进行计算。因此，如果TataruBook发现缺失了需要的数据，就会进行提示。通常通过信息文本就足以理解它所报告的问题是什么。

让我们逐个解决提示信息中的问题：

首先把唯一的货币`Gil`设置为记账**本位币**，解决[standard_asset]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)表中需要有一条记录的问题：把刚才表格里包含`Gil`的单元格复制，然后在`accounting.db`文件上点右键，选择`TataruBook paste`子菜单下的`standard_asset`，设置本位币为`Gil`。

在TataruBook的实际数据中，引用资产时使用的都是`asset_index`字段的值而不是`asset_name`字段的值——因为`asset_name`字段并不是表的主键，有可能存在重名的资产。但是，用户输入`asset_index`字段的值并不方便，因此TataruBook允许用户在需要输入`asset_index`字段值的地方输入`asset_name`字段的值，只要根据输入的值可以唯一确定一种资产，那么TataruBook会在内部自动将其转换为对应的`asset_index`字段的值。
{: .notice}

然后设置**统计周期**的开始时间和结束时间，解决[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)表和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)表中各需要有一条记录的问题：在任何能编辑文本的地方输入`2022-12-31`并复制，然后在`accounting.db`文件上点右键，选择`TataruBook paste`子菜单下的`start_date`，设置统计周期的开始时间。用同样的方法设置统计周期的结束时间为`2023-12-31`。

注意：统计周期的起点是`start_date`那天的**结束**时刻，所以如果希望统计2023年一整年的数据，不要把`start_date`写成`2023-1-1`，否则统计时将会漏掉`2023-1-1`这一天的数据。

TataruBook中绝大多数视图的内容都是由[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)表和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)表所定义的统计周期决定的。比如，[start_stats]({{ site.baseurl }}/tables_and_views_cn.html#start_stats)视图展示`start_date`这天结束时的账户余额和价值；[end_stats]({{ site.baseurl }}/tables_and_views_cn.html#end_stats)视图展示`end_date`这天结束时的账户余额和价值；投资收益率相关视图展示统计周期内的收益情况，等等。通过修改`start_date`和`end_date`，可以修改统计周期来观察指定的某段历史时期的财务状况。
{: .notice}

现在数据一致性的问题都解决了。在最后一次`paste`操作弹出的窗口中，TataruBook报告：

~~~
Integrity check after overwrite:
Everything is fine, no integrity breach found.
~~~

TataruBook在每次修改数据操作之后都会自动进行数据一致性检查。你也可以在任何时候手动进行检查：在快捷菜单中选择`TataruBook check`即可。

# 开始记账

让我们先添加一个银行账户：在`accounting.db`文件上点右键，选择`TataruBook export`子菜单下的`accounts`，打开生成的`accounts.csv`文件，添加一行内容：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| 萨雷安银行活期 | Gil | 0 |

然后复制整张表（或者复制这一行），在`accounting.db`文件上点右键，选择`TataruBook paste`子菜单下的`accounts`，完成内容的插入。

在DB文件中任一张表中插入内容的过程均与此类似，因此后续不再赘述插入操作过程。

插入的这一行表示账户的名字是`萨雷安银行活期`，对应的资产（货币）是`Gil`，最后一个字段的值为`0`表示该账户为**内部账户**。

你可能会疑惑“内部账户”是什么？——这个问题的答案很快就会出现。

假设在开始记账前，`萨雷安银行活期`账户里面的余额不为$$ 0 $$，现在我们希望把这笔余额输入TataruBook。但是，TataruBook使用[复式记账法]({{ site.baseurl }}/tables_and_views_cn.html#简化的复式记账法)，**要向某个账户增加资产，一定要有另一个账户减少等量的资产**。为了满足这个要求，我们再在[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中添加一个名为`历史结余`的**外部账户**（注意这一次`is_external`字段值为`1`）：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| 历史结余 | Gil | 1 |

插入这行内容后，就可以从`历史结余`账户向`萨雷安银行活期`账户转移资产了。向[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表插入内容来添加交易记录：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
|| 2022-12-31 | 历史结余 | -5000 | 萨雷安银行活期 | 初始余额 |

插入执行完后，TataruBook认为在`2022-12-31`这天，`历史结余`账户中减少了$$ 5000 $$Gil，`萨雷安银行活期`账户中增加了$$ 5000 $$Gil。因此，`萨雷安银行活期`账户在`2022-12-31`这天结束时有了$$ 5000 $$Gil的余额。

接下来我们要记录餐饮消费，先向[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表添加一个名为`餐饮费`的外部账户：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| 餐饮费 | Gil | 1 |

然后，向[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表添加两笔消费：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
|| 2023-1-5 | 萨雷安银行活期 | -20 | 餐饮费 | 旅店早餐 |
|| 2023-1-7 | 萨雷安银行活期 | -45 | 餐饮费 | 背水咖啡厅晚餐 |

执行完成后，在`accounting.db`文件上点右键，选择`TataruBook export`子菜单下的`statements`，导出[statements]({{ site.baseurl }}/tables_and_views_cn.html#statements)视图。用Excel打开目录中出现的`statements.csv`文件，看到的内容如下：

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022/12/31 | 1 | 5000 | 2 | 初始余额 | 萨雷安银行活期 | 1 | 0 | 历史结余 | 5000 |
| 1 | 2022/12/31 | 2 | -5000 | 1 | 初始余额 | 历史结余 | 1 | 1 | 萨雷安银行活期 | -5000 |
| 2 | 2023/1/5 | 1 | -20 | 3 | 旅店早餐 | 萨雷安银行活期 | 1 | 0 | 餐饮费 | 4980 |
| 2 | 2023/1/5 | 3 | 20 | 1 | 旅店早餐 | 餐饮费 | 1 | 1 | 萨雷安银行活期 | 20 |
| 3 | 2023/1/7 | 1 | -45 | 3 | 背水咖啡厅晚餐 | 萨雷安银行活期 | 1 | 0 | 餐饮费 | 4935 |
| 3 | 2023/1/7 | 3 | 45 | 1 | 背水咖啡厅晚餐 | 餐饮费 | 1 | 1 | 萨雷安银行活期 | 65 |

这些数据和我们平时常见的交易明细账单类似。使用Excel对`src_name`进行筛选，可以以不同视角来观察：当筛选内部账户`萨雷安银行活期`时，看到的是该账户按时间排列的交易记录和余额；当按照外部账户`餐饮费`筛选时，看到的是所有以`餐饮费`的名义发生的交易。所以，**外部账户是对收支的分类**。在TataruBook中，你可以用任何自己喜欢的方式来分类统计收入和支出——只要添加对应的外部账户即可。

# 批量导入数据

在前面的基础上，我们继续输入更多记账数据。先向[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表添加一些内部账户和外部账户：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| 萨雷安银行信用卡 | Gil | 0 |
|| 购物 | Gil | 1 |
|| 房租 | Gil | 1 |
|| 工资 | Gil | 1 |

然后，向[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表添加一批交易记录：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-2-10 | 工资 | -8000 | 萨雷安银行活期 | 月工资 |
| | 2023-2-13 | 萨雷安银行信用卡 | -190 | 购物 | 买衣服 |
| | 2023-2-26 | 萨雷安银行信用卡 | -140 | 购物 | 买生活用品 |
| | 2023-3-2 | 萨雷安银行信用卡 | -9000 | 房租 | 半年租金 |
| | 2023-3-10 | 工资 | -8000 | 萨雷安银行活期 | 月工资 |
| | 2023-3-10 | 萨雷安银行信用卡 | -43 | 餐饮费 | 背水咖啡厅午餐 |
| | 2023-3-20 | 萨雷安银行活期 | -9300 | 萨雷安银行信用卡 | 还信用卡 |

在实际记账时，输入的数据常常来自银行、券商等机构提供的交易明细记录。由于TataruBook对插入的数据有很多校验，在批量插入时可能会遇到某条记录插入失败。这种情况下会触发**回滚**——把DB文件恢复到整条命令执行之前的状态。然后，用户可以修改表格内容中的错误，并重新插入。自动回滚的特性让用户不需要担心插入大量数据时出现部分插入成功而使DB文件的状态难以确定。
{: .notice}

现在我们想看看收支的分类统计。先导出[income_and_expenses]({{ site.baseurl }}/tables_and_views_cn.html#income_and_expenses)视图，看到的内容如下：

| asset_order | account_index | account_name | total_amount | asset_index | asset_name | total_value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 3 | 餐饮费 | 108.0 | 1 | Gil | 108.0 |
| 0 | 5 | 购物 | 330.0 | 1 | Gil | 330.0 |
| 0 | 6 | 房租 | 9000.0 | 1 | Gil | 9000.0 |
| 0 | 7 | 工资 | -16000.0 | 1 | Gil | -16000.0 |

这些数据展示了统计周期内每一类收支的统计结果。注意：由于外部账户的交易数额是内部账户的相反数，所以这些数据中正值表示开支，负值表示收入。

[income_and_expenses]({{ site.baseurl }}/tables_and_views_cn.html#income_and_expenses)视图展示的是所有内部账户在某类收支上的交易额之和。如果想看细分到每个内部账户的统计数据，可以查看[flow_stats]({{ site.baseurl }}/tables_and_views_cn.html#flow_stats)视图：

| flow_index | flow_name | account_index | account_name | amount |
|:-:|:-:|:-:|:-:|:-:|
| 3 | 餐饮费 | 1 | 萨雷安银行活期 | 65.0 |
| 3 | 餐饮费 | 4 | 萨雷安银行信用卡 | 43.0 |
| 5 | 购物 | 4 | 萨雷安银行信用卡 | 330.0 |
| 6 | 房租 | 4 | 萨雷安银行信用卡 | 9000.0 |
| 7 | 工资 | 1 | 萨雷安银行活期 | -16000.0 |

在[flow_stats]({{ site.baseurl }}/tables_and_views_cn.html#flow_stats)视图中，可以看到`萨雷安银行活期`和`萨雷安银行信用卡`两个内部账户分别产生了多少`餐饮费`。

如果想知道经过这些交易后，每个内部账户最后的余额是多少，可以查看[end_stats]({{ site.baseurl }}/tables_and_views_cn.html#end_stats)视图：

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023/12/31 | 1 | 萨雷安银行活期 | 11635.0 | 1 | Gil | 1.0 | 11635.0 | 1.006 |
| 0 | 2023/12/31 | 4 | 萨雷安银行信用卡 | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.006 |

注意信用卡的余额是负值——这是大多数信用卡账户的常态。

TataruBook不允许直接输入账户余额（之前输入初始余额的操作其实录入的是一笔交易），所有账户的余额都是根据交易记录自动计算出来的。在记账时，通过核对TataruBook展示的余额和实际账户余额是否一致，可以有效的校验输入的数据是否完整、准确。
{: .notice}

# 利息收益

银行账户上的资金往往有利息收益。为了记录利息，先向[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表加入表示利息的外部账户：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| Gil利息 | Gil | 1 |

如果有多种不同货币在使用，需要按不同货币来设立不同外部账户。利息账户的名字叫`Gil利息`是出于这个准备：如果以后增加了其他货币，其他货币的利息对应的外部账户可以和`Gil利息`区分开。当然，如果你只使用一种货币，则不需要考虑这些。
{: .notice}

TataruBook可以计算每个账户的实际利率。要使用这个功能，需要向[interest_accounts]({{ site.baseurl }}/tables_and_views_cn.html#interest_accounts)表加入刚才的利息账户：

| interest_accounts |
|:-:|
| Gil利息 |

现在可以向[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表添加利息收入了：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-3-30 | Gil利息 | -30 | 萨雷安银行活期 | 账户结息 |
| | 2023-6-30 | Gil利息 | -35 | 萨雷安银行活期 | 账户结息 |

然后，通过导出[interest_rates]({{ site.baseurl }}/tables_and_views_cn.html#interest_rates)视图可以查看以当前数据计算出的账户利率：

| account_index | account_name | asset_index | avg_balance | interest | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 萨雷安银行活期 | 1 | 11278.38 | 65.0 | 0.00576 |

这些数据表示：统计周期内`萨雷安银行活期`的平均每日账户余额是$$ 11278.38 $$Gil，利率大约是$$ 0.576\% $$。如果想知道详细的计算过程，可参考[改良的Dietz方法]({{ site.baseurl }}/rate_of_return_cn.html#改良的dietz方法)。

检查每个账户的利率有助于避免记账中的错误——如果计算出的利率不合理，那表明记账数据可能存在差错。
{: .notice}

# 股票投资

要记录股票投资，首先需要添加某只股票的**资产**。对TataruBook来说，股票和货币并没有本质的区别，它们都是特定的资产。因此，向[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中添加股票资产的方法和添加一种货币一样：

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
|| 加隆德炼铁厂股份 | 1 |

我们把最后一个字段`asset_order`的值写为`1`，这样在[end_stats]({{ site.baseurl }}/tables_and_views_cn.html#end_stats)等视图中，股票资产会排在货币资产的后面。如果你不关心各个视图中资产排列的顺序，可以把所有资产的`asset_order`都设置为`0`。

接下来添加持有这只股票的内部账户。TataruBook允许多个内部账户持有同一只股票，但是我们现在暂时只用向[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表添加一个股票账户：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| 莫古证券_加隆德股份 | 加隆德炼铁厂股份 | 0 |

TataruBook中的股票交易只不过是内部账户之间的资产转移。但是现在出现一个问题：之前的每笔交易中，源账户（即转出账户）减少的数额总是等于目标账户（即转入账户）增加的数额。所以记录交易时，我们只用写一个数字，TataruBook就会同时完成源账户和目标账户的余额变更。但是现在，现金和股票账户包含的资产不同：现金账户中的余额是货币的数量，而股票账户中的余额是股份的数量。所以交易中现金账户的变动数额并不等于股票账户的变动数额的相反数（除非股价恰好为$$ 1 $$）。

为了解决这个问题，TataruBook规定：**当一笔交易记录中两个账户包含的资产不同时，必须同时提供源账户和目标账户的变动数额**。体现到数据上，就是向[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表插入的这行数据的结尾要多出一列，这一列中的数字表示目标账户的变动数额：

| posting_index | trade_date | src_account | src_change | dst_account | comment ||
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-7-3 | 萨雷安银行活期 | -2000 | 莫古证券_加隆德股份 | 买入股票 | 200 |

最后一列中的$$ 200 $$表示该笔交易购入了$$ 200 $$股。由于这一列在导出[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表时是不存在的，你需要自己记住这多出来的一列的含义。你也可以手工编辑表头，在最后一列的第一行写上`dst_change`来明确这列数据的含义。TataruBook在处理插入的数据时，不关心表头的内容。

添加交易时不需要提供实时交易价格，因为两个账户的变动数额已经反映了当时的交易价格。如果希望记录交易的手续费/佣金/税，那么可以添加对应的外部账户，并把一笔交易拆分为多笔录入。

添加这笔交易后，TataruBook又报告数据一致性问题：

~~~
Integrity check after insertion:
These (date, asset) pairs need price info in calculation:
(2, '加隆德炼铁厂股份', 1, '2023-12-31')
~~~

这是因为在计算净资产时需要知道其他资产换算为本位币的价值，所以需要输入特定日期的股价。我们向[prices]({{ site.baseurl }}/tables_and_views_cn.html#prices)表添加记录来满足这个要求：

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-12-31 | 加隆德炼铁厂股份 | 12 |

现在可以通过[end_stats]({{ site.baseurl }}/tables_and_views_cn.html#end_stats)视图来查看在[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)日期的所有账户余额和市场价值：

如果你一直是按这个教程操作的，那么现在当前目录下已经有一个`end_stats.csv`文件了（因为之前导出过）。在这种情况下，你要先把已有的`end_stats.csv`文件删除，然后再执行`export`命令。否则，`export`执行时会报告失败，且`end_stats.csv`文件的内容不会变化——因为TataruBook要避免意外的损坏已有文件。
{: .notice--warning}

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | 萨雷安银行活期 | 9700.0 | 1 | Gil | 1.0 | 9700.0 | 0.8065 |
| 0 | 2023-12-31 | 4 | 萨雷安银行信用卡 | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.0061 |
| 1 | 2023-12-31 | 9 | 莫古证券_加隆德股份 | 200.0 | 2 | 加隆德炼铁厂股份 | 12.0 | 2400.0 | 0.1996 |

# 投资收益率

除了股票以外，基金、债券、商品、期货等其他资产的交易记录方式也是类似的。我们向[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表添加一种基金资产：

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
|| 艾欧泽亚100指数基金 | 1 |

再向[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表添加相应账户：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| 莫古证券_艾欧泽亚100 | 艾欧泽亚100指数基金 | 0 |

这只基金有多次交易，有申购也有赎回，我们向[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表插入以下交易记录：

| posting_index | trade_date | src_account | src_change | dst_account | comment | dst_change |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023/8/2 | 萨雷安银行活期 | -3000 | 莫古证券_艾欧泽亚100 | 基金申购 | 1500 |
| | 2023/8/21 | 萨雷安银行活期 | -1000 | 莫古证券_艾欧泽亚100 | 基金申购 | 450 |
| | 2023/9/12 | 莫古证券_艾欧泽亚100 | -1000 | 萨雷安银行活期 | 基金赎回 | 2500 |
| | 2023/9/30 | 萨雷安银行活期 | -1200 | 莫古证券_艾欧泽亚100 | 基金申购 | 630 |

为了更清楚的示意每行最后一个字段，表头中增加了`dst_change`列。但实际上TataruBook插入数据时并不关心表头的内容，只要按照要求的顺序填写每个字段的值即可。
{: .notice}

和之前一样，向[prices]({{ site.baseurl }}/tables_and_views_cn.html#prices)表添加`艾欧泽亚100指数基金`在[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)日期的价格信息：

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-12-31 | 艾欧泽亚100指数基金 | 2.35 |

完成后，通过[end_stats]({{ site.baseurl }}/tables_and_views_cn.html#end_stats)视图查看在[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)日期的所有账户余额和市场价值：（如果`end_stats.csv`文件已存在，先删除它再执行`export`命令）

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | 萨雷安银行活期 | 7000.0 | 1 | Gil | 1.0 | 7000.0 | 0.5368 |
| 0 | 2023-12-31 | 4 | 萨雷安银行信用卡 | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.0056 |
| 1 | 2023-12-31 | 9 | 莫古证券_加隆德股份 | 200.0 | 2 | 加隆德炼铁厂股份 | 12.0 | 2400.0 | 0.1840 |
| 1 | 2023-12-31 | 10 | 莫古证券_艾欧泽亚100 | 1580.0 | 3 | 艾欧泽亚100指数基金 | 2.35 | 3713.0 | 0.2847 |

除了按账户展示价值外，还可以通过[end_assets]({{ site.baseurl }}/tables_and_views_cn.html#end_assets)视图来查看每种资产的数量和价值：

| asset_order | date_val | asset_index | asset_name | amount | price | total_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | Gil | 6927.0 | 1.0 | 6927.0 | 0.5312 |
| 1 | 2023-12-31 | 2 | 加隆德炼铁厂股份 | 200.0 | 12.0 | 2400.0 | 0.1840 |
| 1 | 2023-12-31 | 3 | 艾欧泽亚100指数基金 | 1580.0 | 2.35 | 3713.0 | 0.2847 |

虽然最终的价值计算出来了，但对于投资者来说，还关心这只基金通过这些买卖交易，整体的收益如何。通过[return_on_shares]({{ site.baseurl }}/tables_and_views_cn.html#return_on_shares)视图可以查看每个包含投资品的账户的收益情况（TataruBook把所有不是本位币的资产都看作投资品）：

| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2 | 加隆德炼铁厂股份 | 9 | 莫古证券_加隆德股份 | 0 | 0 | 200.0 | 200.0 | 2400.0 | -2000.0 | 2000.0 | 400.0 | 0.2 |
| 1 | 3 | 艾欧泽亚100指数基金 | 10 | 莫古证券_艾欧泽亚100 | 0 | 0 | 1580.0 | 1580.0 | 3713.0 | -2700.0 | 4000.0 | 1013.0 | 0.25325 |

这些数据显示：`莫古证券_加隆德股份`账户的投资收益是$$ 400 $$Gil，收益率是$$ 20\% $$；`莫古证券_艾欧泽亚100`账户的投资收益是$$ 1013.0 $$Gil，收益率是$$ 25.325\% $$。如果想知道详细的计算过程，可参考[最小初始资金法]({{ site.baseurl }}/rate_of_return_cn.html#最小初始资金法)。

TataruBook还会把所有内部账户的集合看作是一个**投资组合**，并计算这个组合整体的收益率，结果显示在[portfolio_stats]({{ site.baseurl }}/tables_and_views_cn.html#portfolio_stats)视图中：

| start_value | end_value | net_outflow | interest | net_gain | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5000.0 | 13040.0 | -6562.0 | -65.0 | 1478.0 | 0.178 |

这些数据显示：所有内部账户在统计周期内投资收益总计为$$ 1478 $$Gil，收益率为$$ 17.8\% $$。注意投资收益中包含利息。如果想知道详细的计算过程，可参考[简单Dietz方法]({{ site.baseurl }}/rate_of_return_cn.html#简单dietz方法)。

TataruBook通常用于记录个人或者家庭的所有资产，因此[portfolio_stats]({{ site.baseurl }}/tables_and_views_cn.html#portfolio_stats)视图的信息很重要，它展示了个人或家庭在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)日期结束时的净资产，以及这两个日期之间的净收支和投资收益情况。
{: .notice}

# 用图形界面软件查看DB文件

TataruBook程序本身没有提供图形界面，但是包含所有表和视图的DB文件是**SQLite格式**文件，任何支持SQLite格式的软件都可查看DB文件中的表和视图（前提是该软件支持SQLite的新特性）。以开源免费的[DB Browser for SQLite](https://sqlitebrowser.org/)软件作为例子来演示：首先下载安装`DB Browser for SQLite`的[nightly版本](https://nightlies.sqlitebrowser.org/latest)（只有nightly版本才支持SQLite的新特性），然后运行`DB Browser for SQLite`，最后点击`打开数据库`按钮并选择`accounting.db`文件，就可以查看DB文件里表和视图的数据了。

![DB Browser for SQLite界面]({{ site.baseurl }}/assets/images/statements_cn.png)

你还可以用这些软件来编辑DB文件中的数据，但是只有TataruBook在插入数据时会进行完善的一致性校验。所以如果用别的软件编辑DB文件，最好再用`TataruBook check`命令做一次检查。如果你会使用SQL语言，还可以自己编写SQL命令来开发TataruBook没有提供的数据分析功能。
{: .notice}