---
title: 表和视图
sidebar:
  nav: "chinese"
---
本页介绍db文件中包含的所有表和视图。

**表**包含了用户提供的财务数据，它是所有报表的数据源头。为了确保数据的完整性和一致性，在添加、修改、删除表中的数据时，TataruBook会进行各方面的校验，保证数据之间不出现冲突和逻辑矛盾。

**视图**是使用表中的数据计算出的报表，包含净资产、分类收入支出、投资收益率等各种统计数据。每当任一张表中的数据发生了变化，所有视图均会立即重新计算并更新。通常来说视图更新的速度非常快，用户往往感知不到延迟。视图的更新不需要手工触发。

有一些视图是面向用户提供的报表，也有一些视图是供另一些视图使用的中间计算结果，用户通常不需要关注这些中间结果视图。但是，如果用户对某些报表数据有疑惑，想要检查计算过程，可以查看这些中间结果视图。另外，对于自己编写SQL查询的高级用户，中间结果视图可能也是有用的。

所有名字以`check`开头的视图都是用于检查数据一致性的。当数据一致时，这些`check`开头的视图应当不含任何记录。如果TataruBook发现某个`check`开头的视图内容不为空，则会在命令行报告相关的数据错误并提示用户修正。

# 简化的复式记账法

![记账数据架构]({{ site.baseurl }}/assets/images/architecture.png)

TataruBook遵循[复式记账](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)里“每笔交易都必须有两个账户参与”的要求，但并没有使用专业会计方法中的账户分类法，以及[每种账户约定的正负号](https://en.wikipedia.org/wiki/Debits_and_credits)。对于普通个人或家庭的记账来说，严格遵循专业会计方法会使记账太过于复杂且难以理解。因此TataruBook用了更简单直观的记账方法，只把所有账户分为两类：

- **内部账户**中的某笔变动数额为正表示财产变多，为负表示财产变少；余额为正时表示拥有财产，为负时表示对外负债。
- **外部账户**中的某笔变动数额为正表示支出，为负表示收入或利息。

这样，每笔交易在其涉及的两个账户中的变动数额加起来总是恰好等于$$ 0 $$（当两个账户包含相同的资产时）。在任一时刻把所有内部账户的余额相加，就能得到当时的净资产。

如果你学过专业的会计方法，那么要注意在TataruBook的简化的复式记账法中，有一些名词与会计专业中的术语含义并不完全相同。比如**资产（Asset）**在TataruBook中指的是一种货币或者一种具有单位价格的可交易所有权，而不是会计公式中的**负债**加**所有者权益**。
{: .notice}

在TataruBook使用的记账方法中，每笔交易涉及的两个账户可以包含不同的资产（比如两种不同的货币，或者一个是货币另一个是股票），这样的交易在两个账户上产生的变动数额相加不再等于$$ 0 $$（除非两种资产的单位价格恰好相等）。TataruBook要求指定某一种资产为**标准资产**，其他资产都会按照（某个时间）对应的单位价格转换为标准资产来进行计算。

在某些视图的名字里，非标准资产可能被称为**股份（share）**，标准资产可能被称为**现金（cash）**，要注意这仅仅是为了方便理解所做的类比，并不严格对应现实中的股份和现金。举个例子：如果用户定义标准资产为人民币，那么他所持有的美元现金会被TataruBook看作“股份”，因为美元的价格是浮动的，持有的美元现金在以人民币计价时可能产生收益或亏损。资产的数量可以不是整数，比如$$ 0.1 $$美元或$$ 0.001 $$美元在记账中都是允许的。

# 表

## asset_types

资产类型列表。在TataruBook中，一种**资产**是具有**独立单位价格**的一类实体，如某一种货币、某一只股票、某一只有单位净值的基金等等。

如果你只使用一种货币，也不持有或交易其他投资品或商品，那么你的`asset_types`表就只有一条记录：自己使用的货币。

**字段**
- `asset_index`（整数）：自动生成的索引，无需用户输入。
- `asset_name`（字符串）：资产名字，不允许为空。仅用于在视图中展示，不会影响计算。
- `asset_order`（整数）：资产序号，不允许为空。仅用于在视图中展示资产时排序使用（序号小的资产排在前面），不会影响计算。如果对排序没有要求，可以把所有资产的`asset_order`都设置为$$ 0 $$。

## standard_asset

标准资产，作为记账**本位币**。所有其他资产都会换算成标准资产来统计市场价值。

**字段**
- `asset_index`（整数）：资产索引，不允许为空，必须是[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中存在的某个资产索引。

**约束**
- 该表只允许有一条记录。
- [prices]({{ site.baseurl }}/tables_and_views_cn.html#prices)表中任一条记录的`asset_index`不允许等于该表中的`asset_index`，因为标准资产的价格固定为$$ 1 $$。（由[check_standard_prices]({{ site.baseurl }}/tables_and_views_cn.html#check_standard_prices)视图校验）

## accounts

账户列表。**账户**是**具有独立余额**的实体。注意一张个人银行卡通常包含多个账户，比如活期账户、投资账户、信用账户等等，在给账户命名的时候应当注意。

一个账户的余额所使用的单位由它包含的资产定义。比如，如果账户包含的资产是货币，那么账户余额是货币的金额；如果账户包含的资产是某只股票，那么账户余额是股份的数量。

账户余额并不一定是正值，当余额为负值时，表示账户中有负债。比如，大多数时候信用卡的余额就是负值，表示用户在这个账户上存在未来需要归还的负债。

账户有两种：**内部账户**和**外部账户**，见[简化的复式记账法]({{ site.baseurl }}/tables_and_views_cn.html#简化的复式记账法)。一个外部账户表示一类收入/支出，用户通过定义外部账户可自定义如何对收入/支出进行分类统计。

**字段**
- `account_index`（整数）：自动生成的索引，无需用户输入。
- `account_name`（字符串）：账户名字，不允许为空。仅用于在视图中展示，不会影响计算。
- `asset_index`（整数）：账户包含的资产的索引。不允许为空，必须是[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中存在的某个资产索引。
- `is_external`（`0`或`1`）：为`0`表示内部账户，为`1`表示外部账户。

## interest_accounts

利息账户列表。**利息账户**是一类特殊的**外部账户**，这些外部账户提供存款利息、理财收益等利息收益。

当利息账户与内部账户之间产生了交易，TataruBook认为该内部账户产生了利息收入，并计算相关的**利率**。计算时，TataruBook认为该内部账户的**平均每日余额**是利率的分母。见[interest_rates]({{ site.baseurl }}/tables_and_views_cn.html#interest_rates)视图。

为了不让利率数据失真，基金/股票的分红不应该来自利息账户（除非是价格始终为$$ 1 $$，且分红体现为份额增加的货币基金）。因为这些分红是以现金形式发放到另一个内部账户，而不是基金/股票本身所在的内部账户。要了解基金/股票的分红、拆分用什么方式记录，可见[return_on_shares]({{ site.baseurl }}/tables_and_views_cn.html#return_on_shares)视图中的例子。

**字段**
- `account_index`（整数）：账户索引，不允许为空，必须是[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中存在的某个账户索引。

**约束**
- 所有利息账户都必须为外部账户，即对应[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中`is_external`字段为`1`。（由[check_interest_account]({{ site.baseurl }}/tables_and_views_cn.html#check_interest_account)视图校验）

## postings

交易明细列表。根据[简化的复式记账法]({{ site.baseurl }}/tables_and_views_cn.html#简化的复式记账法)，每一笔交易都可看作价值从一个账户转移到另一个账户的过程。因此该列表中每一条交易明细记录都包含**源账户**和**目标账户**，交易使得源账户的余额变少，目标账户余额变多。

只要源账户和目标账户包含相同资产，则目标账户的变动数额等于源账户的变动数额的相反数，即两者相加等于$$ 0 $$。这种情况下，只需要输入源账户的变动数额，目标账户的变动数额会被自动计算出来。当源账户和目标账户包含不同资产时，需要辅助用[posting_extras]({{ site.baseurl }}/tables_and_views_cn.html#posting_extras)表记录这笔交易中目标账户的变动数额。

**字段**
- `posting_index`（整数）：自动生成的索引，无需用户输入。通常，后输入的记录的索引比先输入的大。
- `trade_date`（字符串）：交易日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。对于同一天内发生的交易，按照`posting_index`确定先后顺序，索引小的在前，大的在后。
- `src_account`（整数）：源账户索引，不允许为空，必须是[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中存在的某个账户索引。
- `src_change`（浮点数）：源账户的变动数额，不允许为空。该值必须小于等于$$ 0 $$。
- `dst_account`（整数）：目标账户索引，不允许为空，必须是[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中存在的某个账户索引。
- `comment`（字符串）：交易备注信息，可以为空。仅用于在视图中展示，不会影响计算。

**约束**
- 一条记录中，`src_account`的值不能等于`dst_account`的值。（由[check_same_account]({{ site.baseurl }}/tables_and_views_cn.html#check_same_account)视图校验）
- 一条记录中，源账户和目标账户不能都是外部账户。（由[check_both_external]({{ site.baseurl }}/tables_and_views_cn.html#check_both_external)视图校验）（v1.1新增）
- 一条记录中，源账户或者目标账户是外部账户时，该外部账户要么包含标准资产，要么和另一个账户包含相同资产。（由[check_external_asset]({{ site.baseurl }}/tables_and_views_cn.html#check_external_asset)视图校验）（v1.1新增）

刚开始记账的用户可能会疑惑如何把各个账户的现有余额导入到db文件中。建议的做法是：建立一个名为`历史结余`的外部账户，并对每个需要导入余额的内部账户，添加一笔从`历史结余`到该内部账户的交易记录。
{: .notice}

## posting_extras

当源账户和目标账户包含不同资产时，交易明细中目标账户的变动数额，见[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的相关描述。

**字段**
- `posting_index`（整数）：交易索引，不允许为空，必须是[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中存在的某个索引。
- `dst_change`（浮点数）：目标账户的变动数额，不允许为空。该值必须大于等于$$ 0 $$。

**约束**
- 当源账户和目标账户包含相同资产时，该交易不允许有`posting_extras`记录，此时目标账户的变动数额等于源账户的变动数额的相反数。（由[check_same_asset]({{ site.baseurl }}/tables_and_views_cn.html#check_same_asset)视图校验）
- 当源账户和目标账户包含不同资产时，该交易必须要有`posting_extras`记录指定目标账户的变动数额。（由[check_diff_asset]({{ site.baseurl }}/tables_and_views_cn.html#check_diff_asset)视图校验）

## prices

资产的单位价格，用于在需要时将非标准资产换算成[标准资产]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)（记账本位币）。一种资产在每一天最多只能有一个价格，该价格视为该资产在这天结束时的价格。对于股票这类有日内价格变动的资产，其资产价格是一天的收盘价。因此，如果在某一天的交易明细中买入或卖出了某种资产，那么，该笔交易中的实际交易价格（实时价）可以不等于当天`prices`表中该资产的价格（收盘价）。（见[start_stats]({{ site.baseurl }}/tables_and_views_cn.html#start_stats)视图的示例）

**字段**
- `price_date`（字符串）：日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。
- `asset_index`（整数）：资产索引，不允许为空，必须是[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中存在的某个资产索引。
- `price`（浮点数）：单位价格（即$$ 1 $$份该资产等于多少份标准资产），不允许为空。

**约束**
- 标准资产不允许有价格。（由[check_standard_prices]({{ site.baseurl }}/tables_and_views_cn.html#check_standard_prices)视图校验）
- 同一资产在同一天只能有一个价格，即任两条记录的`price_date`和`asset_index`不能都相同。
- 在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)这两天，所有非标准资产都必须有价格。（由[check_absent_price]({{ site.baseurl }}/tables_and_views_cn.html#check_absent_price)视图校验）
- 如果两个含有非标准资产的账户发生了交易（无论是内部账户还是外部账户），该（一种或两种）非标准资产在交易当天必须要有价格。比如：如果美元是非标准资产，那么当使用美元买入美国股票时，交易当天必须要有美元的价格和该股票的价格（注意是以标准资产计价的价格）。这是因为在对这两个账户计算投资收益率时，它们在交易当天都有一次资金流入或流出，需要计算流入/流出的价值。（由[check_absent_price]({{ site.baseurl }}/tables_and_views_cn.html#check_absent_price)视图校验）

## start_date

统计开始日期，作为一些视图的统计周期的起始时间点。注意开始日期当天的交易并不被包含在统计周期内，统计周期是以开始日期当天结束时作为起点。比如要对2023年全年的财务数据进行统计分析，则`start_date`为`2022-12-31`，`end_date`为`2023-12-31`。

**字段**
- `val`（字符串）：开始日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。

**约束**
- 该表只允许有一条记录。
- 开始日期必须小于结束日期。

## end_date

统计结束日期，作为一些视图的统计周期的结束时间点。注意结束日期当天的交易会被包含在统计周期内。比如要对2023年全年的财务数据进行统计分析，则`start_date`为`2022-12-31`，`end_date`为`2023-12-31`。

**字段**
- `val`（字符串）：结束日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。

**约束**
- 该表只允许有一条记录。
- 结束日期必须大于开始日期。

# 视图

## single_entries

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

把输入的复式记账交易记录转换为单式记账展示。每一条[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的记录都会变成该视图中的两条记录。

**字段**
- `posting_index`：来自[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的`posting_index`。
- `trade_date`：来自[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的`trade_date`。
- `account_index`：来自[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的`src_account`或`dst_account`。
- `amount`：该账户该笔交易的变动数额，来自[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的`src_change`（或者其相反数），或者[posting_extras]({{ site.baseurl }}/tables_and_views_cn.html#posting_extras)表中的`dst_change`。
- `target`：该交易的另一方账户，来自[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的`src_account`或`dst_account`。
- `comment`：来自[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的`comment`。

## statements

把输入的复式记账交易记录转换为单式记账展示，并且展示账户相关信息。

**字段**
- 包含[single_entries]({{ site.baseurl }}/tables_and_views_cn.html#single_entries)视图中的所有字段，以及：
- `src_name`、`target_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。
- `is_external`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`is_external`。
- `balance`：这笔交易发生后的账户余额（根据之前的所有交易记录推导出）。对于外部账户来说，余额的相反数代表历史上该类收入/支出的总和。

**示例**

假设现有表内容如下：

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | 加隆德炼铁厂股份 | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | 萨雷安银行活期 | 1 | 0 |
| 2 | 莫古证券_加隆德股份 | 2 | 0 |
| 3 | 餐饮消费 | 1 | 1 |
| 4 | 工资 | 1 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-06 | 4 | -50000.0 | 1 | 领取工资 |
| 2 | 2023-01-07 | 1 | -67.5 | 3 | 背水咖啡厅晚餐 |
| 3 | 2023-01-09 | 1 | -13000.0 | 2 | 购入加隆德股份 |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 3 | 260.0 |

则`statements`视图内容为：

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-06 | 1 | 50000.0 | 4 | 领取工资 | 萨雷安银行活期 | 1 | 0 | 工资 | 50000.0 |
| 1 | 2023-01-06 | 4 | -50000.0 | 1 | 领取工资 | 工资 | 1 | 1 | 萨雷安银行活期 | -50000.0 |
| 2 | 2023-01-07 | 1 | -67.5 | 3 | 背水咖啡厅晚餐 | 萨雷安银行活期 | 1 | 0 | 餐饮消费 | 49932.5 |
| 2 | 2023-01-07 | 3 | 67.5 | 1 | 背水咖啡厅晚餐 | 餐饮消费 | 1 | 1 | 萨雷安银行活期 | 67.5 |
| 3 | 2023-01-09 | 1 | -13000.0 | 2 | 购入加隆德股份 | 萨雷安银行活期 | 1 | 0 | 莫古证券_加隆德股份 | 36932.5 |
| 3 | 2023-01-09 | 2 | 260.0 | 1 | 购入加隆德股份 | 莫古证券_加隆德股份 | 2 | 0 | 萨雷安银行活期 | 260.0 |

说明：`statements`视图比较像通常人们所习惯的单式记账账单。如果只想查看某一个账户的变动记录，可以用其他软件打开db文件并按`account_index`或`src_name`筛选。比如筛选`account_index`为`1`的记录，就能看到`萨雷安银行活期`的所有历史交易和余额变化。

## start_balance

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)这天结束时，所有余额不为$$ 0 $$的内部账户的余额。

**字段**
- `date_val`：来自[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)表中的`val`。
- `account_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `account_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `balance`：通过累加`start_date`及之前所有交易记录的变动数额得到的账户余额。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。

## start_values

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)这天结束时，所有余额不为$$ 0 $$的内部账户的余额，以及按当天价格换算成[标准资产]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)的市场价值。

**字段**
- 包含[start_balance]({{ site.baseurl }}/tables_and_views_cn.html#start_balance)视图中的所有字段，以及：
- `price`：来自[prices]({{ site.baseurl }}/tables_and_views_cn.html#prices)表中的`price`；如果是标准资产，则值为$$ 1 $$。
- `market_value`：通过$$ \text{price} \times \text{balance} $$计算得到的市场价值。

## start_stats

在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)这天结束时，所有余额不为$$ 0 $$的内部账户的余额，按当天价格换算成[标准资产]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)的市场价值，以及每个账户的价值占总价值的比例。

**字段**
- 包含[start_values]({{ site.baseurl }}/tables_and_views_cn.html#start_values)视图中的所有字段，以及：
- `asset_order`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_order`。
- `asset_name`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_name`。
- `proportion`：这个账户的价值占所有账户价值总和的比例。

**示例**

假设在[statements]({{ site.baseurl }}/tables_and_views_cn.html#statements)视图中示例已有表基础上，另外加入表：

`start_date`

| val |
|:-:|
| 2023-1-9 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-1-9 | 2 | 51 |

则`start_stats`视图内容为：

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-01-09 | 1 | 萨雷安银行活期 | 36932.5 | 1 | Gil | 1.0 | 36932.5 | 0.7358 |
| 0 | 2023-01-09 | 2 | 莫古证券_加隆德股份 | 260.0 | 2 | 加隆德炼铁厂股份 | 51.0 | 13260.0 | 0.2642 |

说明：注意`balance`列的值和`statements`视图中该日期各账户的余额是一致的；外部账户不会在`start_stats`视图里出现。根据`postings`表中购买`加隆德炼铁厂股份`的交易记录可以换算当时交易的价格是$$ 13000 \div 260 = 50 $$，但是`prices`表中`2023-1-9`的价格记录是$$ 51 $$，且市场价值是根据$$ 51 $$计算的。这个例子展示了实时交易价格可以和收盘价不同。

## start_assets

在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)这天结束时，每一种资产的数量，按当天价格换算成[标准资产]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)的市场价值，以及每种资产的价值占总价值的比例。

**字段**
- `asset_order`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_order`。
- `date_val`：来自[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)表中的`val`。
- `asset_index`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_index`。
- `asset_name`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_name`。
- `amount`：通过累加包含这种资产的所有账户的余额得到的资产数量。
- `price`：来自[prices]({{ site.baseurl }}/tables_and_views_cn.html#prices)表中的`price`；如果是标准资产，则值为$$ 1 $$。
- `total_value`：通过$$ \text{price} \times \text{amount} $$计算得到的市场价值。
- `proportion`：这种资产的价值占所有资产价值总和的比例。

## diffs

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个账户在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间的变动数额统计。`start_date`当天的交易不统计，`end_date`当天的交易会统计。

**字段**
- `account_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `account_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `amount`：通过累加`start_date`和`end_date`之间所有交易记录的变动数额得到的变动数额统计值。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。

## comparison

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个账户在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)的期初余额，[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)的期末余额，以及两个日期之间的变动数额统计。

**字段**
- 包含[diffs]({{ site.baseurl }}/tables_and_views_cn.html#diffs)视图中的`account_index`、`account_name`、`asset_index`字段，以及：
- `start_amount`：来自[start_balance]({{ site.baseurl }}/tables_and_views_cn.html#start_balance)视图中的`balance`。
- `diff`：来自[diffs]({{ site.baseurl }}/tables_and_views_cn.html#diffs)视图中的`amount`；或者，如果账户余额在统计周期内没有变化，则为$$ 0 $$。
- `end_amount`：通过$$ \text{start_amount} + \text{diff} $$计算得到的期末余额。

## end_values

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

在[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)这天结束时，所有余额不为$$ 0 $$的内部账户的余额，以及按当天价格换算成[标准资产]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)的市场价值。

**字段**
- 所有字段均与[start_values]({{ site.baseurl }}/tables_and_views_cn.html#start_values)视图中的字段相同，只是统计时间点变为[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)这天结束时。

## end_stats

在[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)这天结束时，所有余额不为$$ 0 $$的内部账户的余额，按当天价格换算成[标准资产]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)的市场价值，以及每个账户的价值占总价值的比例。。

注意：[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)表和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)表必须各有一条记录，才能使`end_stats`视图显示正确的内容。
{: .notice--warning}

**字段**
- 所有字段均与[start_stats]({{ site.baseurl }}/tables_and_views_cn.html#start_stats)视图中的字段相同，只是统计时间点变为[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)这天结束时。

**示例**

假设在[statements]({{ site.baseurl }}/tables_and_views_cn.html#statements)视图中示例已有表基础上，另外加入表：

`start_date`

| val |
|:-:|
| 2023-1-5 |

`end_date`

| val |
|:-:|
| 2023-1-9 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-1-9 | 2 | 51 |

则`end_stats`视图内容为：

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-01-09 | 1 | 萨雷安银行活期 | 36932.5 | 1 | Gil | 1.0 | 36932.5 | 0.7358 |
| 0 | 2023-01-09 | 2 | 莫古证券_加隆德股份 | 260.0 | 2 | 加隆德炼铁厂股份 | 51.0 | 13260.0 | 0.2642 |

说明：可以看到`end_stats`视图的内容与[start_stats]({{ site.baseurl }}/tables_and_views_cn.html#start_stats)视图几乎一样，仅统计日期为`end_date`这一点有区别。

## end_assets

在[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)这天结束时，每一种资产的数量，按当天价格换算成[标准资产]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)的市场价值，每种资产的价值占总价值的比例。

注意：[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)表和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)表必须各有一条记录，才能使`end_assets`视图显示正确的内容。
{: .notice--warning}

**字段**
- 所有字段均与[start_assets]({{ site.baseurl }}/tables_and_views_cn.html#start_assets)视图中的字段相同，只是统计时间点变为[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)这天结束时。

## external_flows

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个**外部账户**在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间的每笔交易，以及交易当天该资产的价格。`start_date`当天的交易不统计，`end_date`当天的交易会统计。注意每个外部账户（除利息账户外）代表收入和支出的特定类别。

虽然视图名字是**外部资金流**，但和[收益率计算方法]({{ site.baseurl }}/rate_of_return_cn.html)中对**外部资金流**的定义不同的是，该视图包含了利息交易。
{: .notice}

**字段**
- `trade_date`：来自[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中的`trade_date`。
- `asset_order`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_order`。
- `account_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `account_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `amount`：来自[single_entries]({{ site.baseurl }}/tables_and_views_cn.html#single_entries)表中的`amount`。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。
- `asset_name`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_name`。
- `price`：来自[prices]({{ site.baseurl }}/tables_and_views_cn.html#prices)表中的`price`；如果是标准资产，则值为`1`。

## income_and_expenses

每个**外部账户**在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间的交易记录的变动数额统计，以及换算的总市场价值。`start_date`当天的交易不统计，`end_date`当天的交易会统计。注意外部账户（除利息账户外）代表收入和支出的特定类别，因此这个视图可看作在统计周期内对收入、支出、利息的分类统计。

**字段**
- 包含[external_flows]({{ site.baseurl }}/tables_and_views_cn.html#external_flows)视图中的`asset_order`、`account_index`、`account_name`、`asset_index`、`asset_name`字段，以及：
- `total_amount`：通过累加`start_date`和`end_date`之间该外部账户所有交易记录的变动数额得到的交易额统计（未换算成标准资产）。
- `total_value`：把每笔交易的变动数额按当天资产价格换算成标准资产，并累加得到的总市场价值。假设某外部账户一共有$$ n $$笔交易，每笔交易变动数额分别为$$ a_1 \dots a_n $$，该账户包含的资产在每笔交易当天的单位价格分别为$$ p_1 \dots p_n $$，则总价值为：$$ \displaystyle\sum_{i=1}^{n} p_ia_i $$。

**示例**

假设现有表内容如下：

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | 金碟币 | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | 萨雷安银行活期 | 1 | 0 |
| 2 | 金碟钱包 | 2 | 0 |
| 3 | 工资 | 1 | 1 |
| 4 | 金碟消费 | 2 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-02-06 | 3 | -50000.0 | 1 | 领取工资 |
| 2 | 2023-02-07 | 1 | -30000.0 | 2 | 购买金碟币 |
| 3 | 2023-02-12 | 2 | -30.0 | 4 | 游戏娱乐 |
| 4 | 2023-02-15 | 2 | -100.0 | 4 | 购买饰品 |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 2 | 300.0 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-02-12 | 2 | 90.0 |
| 2023-02-15 | 2 | 110.0 |

则`income_and_expenses`视图内容为：

| asset_order | account_index | account_name | total_amount | asset_index | asset_name | total_value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 3 | 工资 | -50000.0 | 1 | Gil | -50000.0 |
| 0 | 4 | 金碟消费 | 130.0 | 2 | 金碟币 | 13700.0 |

说明：注意外部账户的变动数额等于内部账户变动数额的相反数，比如`工资`账户`total_amount`为$$ -50000.0 $$，代表内部账户共有$$ 50000.0 $$的工资收入。

对于外部账户包含的资产为标准资产（如例子中的`Gil`）的，统计市场价值等于变动数额累加；但是当外部账户包含的资产为非标准资产时（如例子中的`金碟币`），会按交易发生当天的价格依次换算为标准资产再累加。在这个例子中，`金碟消费`的`total_value`计算过程为$$ 30 \times 90 + 100 \times 110 = 13700 $$。

## portfolio_stats

只有一条记录：把所有内部账户的集合看作一个**投资组合**，展示该投资组合在统计周期开始和结束时的净资产、统计周期内的总收入支出、总投资收益。

**字段**
- `start_value`：期初净资产，从[start_values]({{ site.baseurl }}/tables_and_views_cn.html#start_values)视图中的`market_value`累加得到。
- `end_value`：期末净资产，从[end_values]({{ site.baseurl }}/tables_and_views_cn.html#end_values)视图中的`market_value`累加得到。
- `net_outflow`：统计周期内的净流出资金额。从[income_and_expenses]({{ site.baseurl }}/tables_and_views_cn.html#income_and_expenses)视图中非[利息账户]({{ site.baseurl }}/tables_and_views_cn.html#interest_accounts)的`total_value`累加得到。注意利息不属于资金流入或流出。如果统计周期内资金是净流入的，那么这个值为负值。
- `interest`：统计周期内发生的利息收入总计，从[income_and_expenses]({{ site.baseurl }}/tables_and_views_cn.html#income_and_expenses)视图中[利息账户]({{ site.baseurl }}/tables_and_views_cn.html#interest_accounts)的`total_value`累加得到。
- `net_gain`：统计周期内投资产生的总收益（或总亏损），计算方法为$$ \text{end_value} + \text{net_outflow} - \text{start_value} $$。即：除了收入支出产生的净资产变化，其他净资产变动都认为是投资收益（或亏损）。利息收入属于投资收益的一部分。
- `rate_of_return`：使用[简单Dietz方法]({{ site.baseurl }}/rate_of_return_cn.html#简单dietz方法)计算的投资收益率。

## flow_stats

每个内部账户在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间与**外部账户**发生的交易额统计。`start_date`当天的交易不统计，`end_date`当天的交易会统计。注意外部账户（除利息账户外）代表收入和支出的特定类别，因此这个视图可看作在统计周期内按每个内部账户分别进行的对收入、支出、利息的分类统计。

注意该视图和[income_and_expenses]({{ site.baseurl }}/tables_and_views_cn.html#income_and_expenses)视图相比有两个区别：
1. `flow_stats`中不同内部账户会分开进行统计，但`income_and_expenses`中不同内部账户和同一外部账户交易的数额会被累加合并；
1. `flow_stats`只展示按相应资产变动数额累加的统计值，但`income_and_expenses`还按照资产价格换算成了标准资产。

**字段**
- `flow_index`：外部账户索引，来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `flow_name`：外部账户名字，来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `account_index`：内部账户索引，来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `account_name`：内部账户名字，来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `amount`：通过累加`start_date`和`end_date`之间该内部账户与该外部账户所有交易记录的变动数额得到的交易额统计（未换算成标准资产）。

**示例**

假设在[income_and_expenses]({{ site.baseurl }}/tables_and_views_cn.html#income_and_expenses)视图中示例已有表基础上，在这两个表中加入额外的记录：

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 5 | 萨雷安个人养老金 | 1 | 0 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 2023-02-06 | 3 | -10000.0 | 5 | 随工资发放养老金 |

则`flow_stats`视图内容为：

| flow_index | flow_name | account_index | account_name | amount |
|:-:|:-:|:-:|:-:|:-:|
| 3 | 工资 | 1 | 萨雷安银行活期 | -50000.0 |
| 3 | 工资 | 5 | 萨雷安个人养老金 | -10000.0 |
| 4 | 金碟消费 | 2 | 金碟钱包 | 130.0 |

说明：`工资`对于两个不同内部账户分别进行了统计，相比之下`income_and_expenses`视图只会显示一条`工资`记录（所有内部账户累加到一起）。此外，`金碟消费`统计的是以`金碟币`为单位的数量，而不是标准资产`Gil`。

## share_trades

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个包含非标准资产的内部账户在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间与其他账户的每笔交易额换算成标准资产的市场价值。该数据用于计算非标准资产的投资收益率。

如果把非标准资产看成股票，那么这个视图可以理解为每一笔交易的买入成本或卖出收入。

**字段**
- 包含[single_entries]({{ site.baseurl }}/tables_and_views_cn.html#single_entries)视图中的所有字段，以及：
- `account_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。
- `asset_name`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_name`。
- `asset_order`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_order`。
- `cash_flow`：该笔交易的变动数额按照当天价格换算成标准资产后的市场价值。

## share_stats

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个包含非标准资产的内部账户在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间的所需最小资金净流入，以及通过交易和持有该内部账户中的资产获得的净现金（以标准资产计价）增量。请参见[最小初始资金法]({{ site.baseurl }}/rate_of_return_cn.html#最小初始资金法)的介绍来理解该视图的数据。

**字段**
- `asset_order`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_order`。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。
- `asset_name`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_name`。
- `account_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `account_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `min_inflow`：该非标准资产在统计周期内所需要的最小资金净流入。如果不需要流入，那么为$$ 0 $$。
- `cash_gained`：交易该非标准资产获得的净现金（标准资产）增量。

## return_on_shares

每个包含非标准资产的内部账户在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间，以标准资产计算市场价值得到的投资收益率。`start_date`当天的交易不统计，`end_date`当天的交易会统计。计算收益率采用的是[最小初始资金法]({{ site.baseurl }}/rate_of_return_cn.html#最小初始资金法)。

**字段**
- `asset_order`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_order`。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。
- `asset_name`：来自[asset_types]({{ site.baseurl }}/tables_and_views_cn.html#asset_types)表中的`asset_name`。
- `account_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `account_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `start_amount`：期初余额。来自[comparison]({{ site.baseurl }}/tables_and_views_cn.html#comparison)视图中的`start_amount`。
- `start_value`：期初市场价值。来自[start_values]({{ site.baseurl }}/tables_and_views_cn.html#start_values)视图中的`market_value`，或者$$ 0 $$（如果`start_values`中没有此账户）。
- `diff`：期间变动数额。来自[comparison]({{ site.baseurl }}/tables_and_views_cn.html#comparison)视图中的`diff`。
- `end_amount`：期末余额。来自[comparison]({{ site.baseurl }}/tables_and_views_cn.html#comparison)视图中的`end_amount`。
- `end_value`：期末市场价值。来自[end_values]({{ site.baseurl }}/tables_and_views_cn.html#end_values)视图中的`market_value`，或者$$ 0 $$（如果`end_values`中没有此账户）。
- `cash_gained`：已实现收益。来自[share_stats]({{ site.baseurl }}/tables_and_views_cn.html#share_stats)视图中的`cash_gained`，或者$$ 0 $$（如果`share_stats`中没有此账户）。
- `min_inflow`：最小资金净流入。来自[share_stats]({{ site.baseurl }}/tables_and_views_cn.html#share_stats)视图中的`min_inflow`，或者$$ 0 $$（如果`share_stats`中没有此账户）。
- `profit`：该账户的投资利润（或亏损），计算方法为$$ \text{cash_gained} + \text{end_value} - \text{start_value} $$。
- `rate_of_return`：使用[最小初始资金法]({{ site.baseurl }}/rate_of_return_cn.html#最小初始资金法)计算的该账户的投资收益率。

**示例1**

假设现有表内容如下：

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | 加隆德炼铁厂股份 | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | 萨雷安银行活期 | 1 | 0 |
| 2 | 莫古证券_加隆德股份 | 2 | 0 |
| 3 | Gil历史结余 | 1 | 1 |
| 4 | 加隆德股份历史结余 | 2 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022-12-31 | 3 | -10000.0 | 1 | Gil历史结余 |
| 2 | 2022-12-31 | 4 | -10.0 | 2 | 股份历史结余 |
| 3 | 2023-02-08 | 1 | -60.0 | 2 | 买入股份 |
| 4 | 2023-03-08 | 2 | -6.0 | 1 | 卖出股份 |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 3 | 5.0 |
| 4 | 90.0 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2022-12-31 | 2 | 10.0 |
| 2023-06-30 | 2 | 11.0 |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-06-30 |

则`return_on_shares`视图内容为：

| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2 | 加隆德炼铁厂股份 | 2 | 莫古证券_加隆德股份 | 10.0 | 100.0 | -1.0 | 9.0 | 99.0 | 30.0 | 60.0 | 29.0 | 0.18125 |

说明：这个例子与[最小初始资金法]({{ site.baseurl }}/rate_of_return_cn.html#最小初始资金法)中的**举例1**非常像，只是资金流入流出的时间间隔不一样，所以计算出的收益率和那个例子是相同的。注意`prices`表中只需要提供统计周期开始和结束时的价格就行了，不需要提供每笔交易发生时的价格，因为交易本身已经体现了价格信息。

**示例2**

假设现有表内容如下：

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | 金碟币 | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | 金碟钱包 | 2 | 0 |
| 2 | 金碟币历史结余 | 2 | 1 |
| 3 | 金碟币利息 | 2 | 1 |

`interest_accounts`

| account_index |
|:-:|
| 3 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022-12-31 | 2 | -1000.0 | 1 | 金碟币历史结余 |
| 2 | 2023-06-21 | 3 | -10.0 | 1 | 利息 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2022-12-31 | 2 | 10.0 |
| 2023-06-21 | 2 | 11.0 |
| 2023-06-30 | 2 | 12.0 |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-06-30 |

则`return_on_shares`视图内容为：

| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2 | 金碟币 | 1 | 金碟钱包 | 1000.0 | 10000.0 | 10.0 | 1010.0 | 12120.0 | 0 | 0 | 2120.0 | 0.212 |

说明：`金碟币`是非标准资产，同时也有利息收益。这种情况下，`return_on_shares`视图计算的是包括利息收益在内的整体收益。单独的利息收益会被展示在[interest_rates]({{ site.baseurl }}/tables_and_views_cn.html#interest_rates)视图中。记得将利息账户添加到`interest_accounts`表。本例中，如果`interest_accounts`表中的记录不存在，结果会有很大差别。

## interest_stats

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个有利息收入的内部账户在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间获得的利息。

**字段**
- `account_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `account_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。
- `amount`：该账户在统计周期内获得的利息（未换算成标准资产）。

## interest_rates

每个有利息收入的内部账户在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间获得的利息、平均每日余额，以及按照[改良的Dietz方法]({{ site.baseurl }}/rate_of_return_cn.html#改良的dietz方法)计算出的**利率**（投资收益率）。

该视图展示的收益率仅仅为利息部分的收益率，并不包含资产价格变动产生的收益。

**字段**
- `account_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_index`。
- `account_name`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`account_name`。
- `asset_index`：来自[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表中的`asset_index`。
- `avg_balance`：该账户在统计周期内的平均每日余额（未换算成标准资产）。
- `interest`：来自[interest_stats]({{ site.baseurl }}/tables_and_views_cn.html#interest_stats)视图中的`amount`。
- `rate_of_return`：使用[改良的Dietz方法]({{ site.baseurl }}/rate_of_return_cn.html#改良的dietz方法)计算的投资收益率（即利率）。

**示例**

假设现有表内容如下：

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | 萨雷安银行活期 | 1 | 0 |
| 2 | 工资 | 1 | 1 |
| 3 | 消费 | 1 | 1 |
| 4 | Gil利息 | 1 | 1 |

`interest_accounts`

| account_index |
|:-:|
| 4 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-03-31 | 2 | -10000.0 | 1 | 领取工资 |
| 2 | 2023-09-30 | 1 | -10000.0 | 3 | 大件消费 |
| 3 | 2023-12-21 | 4 | -100.0 | 1 | 利息 |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-12-31 |

则`interest_rates`视图内容为：

| account_index | account_name | asset_index | avg_balance | interest | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 萨雷安银行活期 | 1 | 5016.44 | 100.0 | 0.02 |

说明：利率计算方法见[改良的Dietz方法]({{ site.baseurl }}/rate_of_return_cn.html#改良的dietz方法)。注意`interest_rates`表计算的利率是以这个账户包含的资产进行的，不会换算成标准资产，因此资产价格的变化不会体现在利率中。如果想查看包含资产价格变化的整体收益率，见[return_on_shares]({{ site.baseurl }}/tables_and_views_cn.html#return_on_shares)视图。

## periods_cash_flows

把所有内部账户的集合看作一个**投资组合**，展示该投资组合在[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)和[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)之间每天的资金净流入/流出。`start_date`当天的资金流不统计，`end_date`当天的资金流会统计。利息收入作为投资收益，不会被计入资金流入/流出；除利息账户以外的其他外部账户和内部账户之间的交易都会被计入资金流入/流出。在周期的开始，投资组合的净资产被视作一次净流入；在周期的结束，投资组合的净资产被视作一次净流出。

该视图为计算[内部收益率（IRR）]({{ site.baseurl }}/rate_of_return_cn.html#内部收益率irr)所需要的数据。

**字段**
- `trade_date`：资金净流入/流出的日期。
- `period`：该日期相对于周期的开始日期所经过的天数。
- `cash_flow`：在该日期的资金净流入/流出，已换算成标准资产。注意根据[内部收益率（IRR）]({{ site.baseurl }}/rate_of_return_cn.html#内部收益率irr)的定义，流入为负值，流出为正值，这和通常的定义不一样。

## check_standard_prices

正常情况下这个视图没有记录。如果出现了记录，说明在[prices]({{ site.baseurl }}/tables_and_views_cn.html#prices)表中出现了标准资产的价格，违反了约束。

## check_interest_account

正常情况下这个视图没有记录。如果出现了记录，说明有[利息账户]({{ site.baseurl }}/tables_and_views_cn.html#interest_accounts)是内部账户，违反了约束。

## check_same_account

正常情况下这个视图没有记录。如果出现了记录，说明[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中有`src_account`和`dst_account`相同的记录，违反了约束。

## check_both_external

这是v1.1版本新增的视图。
{: .notice}

正常情况下这个视图没有记录。如果出现了记录，说明[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中有`src_account`和`dst_account`同时都是外部账户，违反了约束。

## check_diff_asset

正常情况下这个视图没有记录。如果出现了记录，说明[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中有源账户和目标账户包含不同资产，但[posting_extras]({{ site.baseurl }}/tables_and_views_cn.html#posting_extras)表却没有对应记录，违反了约束。

## check_same_asset

正常情况下这个视图没有记录。如果出现了记录，说明[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中有源账户和目标账户包含相同资产，但[posting_extras]({{ site.baseurl }}/tables_and_views_cn.html#posting_extras)表却有对应记录，违反了约束。

## check_external_asset

这是v1.1版本新增的视图。
{: .notice}

正常情况下这个视图没有记录。如果出现了记录，说明[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中有些记录的源账户或者目标账户是外部账户，且该外部账户既不包含标准资产，也没有和另一个账户包含相同资产，违反了约束。

## check_absent_price

正常情况下这个视图没有记录。如果出现了记录，说明[prices]({{ site.baseurl }}/tables_and_views_cn.html#prices)表中缺少某些资产在某些日期需要被用到的价格，违反了约束。