---
title: 表和视图
---
本页介绍db数据库文件中包含的所有表和视图。

**表**是用户需要提供的输入，是所有数据的源头。为了确保数据的完整性和一致性，在添加、修改表中的数据时，工具会进行各方面的校验，保证各表的数据不出现冲突和逻辑矛盾。

**视图**是工具计算出的报表，是用户关心的各项统计数据结果。每当任一张表的内容发生了变化，所有视图均会立即自动更新并反映最新的内容，视图的计算不需要手工触发。

有一些视图是面向用户提供报表数据的（比如资产统计），也有一些视图是另一些视图的中间计算结果，用户通常不需要关注（除非对最终的统计结果有疑问想要检查计算过程）。视图描述中对于用户通常不需关注的视图会有注明。

所有名字以check开头的视图都是用于检查数据一致性的。当数据一致时，这些check开头的视图应当不含任何记录。如果发现某个check开头的视图内容不为空，TataruBook会在命令行报告相关的数据错误并提示用户修正。

# 简化的复式记账法

TataruBook遵循[复式记账](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)里“每笔交易都必须有两个账户参与”的要求，但并没有使用专业会计方法中的账户分类法，以及[针对每种类别账户的不同数值变化属性](https://en.wikipedia.org/wiki/Debits_and_credits)。对于普通个人或家庭的记账来说，严格遵循专业会计方法会使记账太过于复杂且难以理解。因此TataruBook用了更简易直观的记账方法，只把所有账户分为两类：

- **内部账户**中的余额为正时表示用户拥有的资产，为负时表示用户对外的负债；
- **外部账户**中的余额表示某一类收入、支出或利息的累计数值，为正数时表示支出，为负数时表示收入或利息。

这样，每笔交易在其涉及的两个账户中的变动数额加起来总是恰好等于$$ 0 $$（在两个账户资产类型相同的情况下）。在任一时刻把所有内部账户的余额加起来，就能得到用户在当时的净资产。

如果你学过专业的会计方法，那么要注意在TataruBook的简化记账方法中，有一些名词与会计专业中的术语含义并不完全相同。比如“资产（Asset）”在TataruBook中是价格不同的商品或者货币，而不是会计公式中所讲的负债加所有者权益。
{: .notice}

TataruBook记账方法的另一个特点是：每笔交易涉及的两个账户可以为不同的资产类型（比如两种不同的货币，或者一个是货币另一个是股票），这样的交易在两个账户上产生的变动数额相加不再等于$$ 0 $$（除非两种资产的价格恰好相等）。当指定某一种资产为**标准资产**后，其他类型的资产都会按照对应价格转换为标准资产来进行投资收益率等数据的计算。

有一些视图的命名会把非标准资产称为“股份（share）”，把标准资产称为“现金（cash）”，要注意这仅仅是为了方便理解所做的类比，并不严格对应现实中的股份和现金。比如：如果用户定义标准资产为人民币，那么他所持有的美元现金会被TataruBook看作类似于“股份”，因为这些美元货币的价格是浮动的，且可能产生以人民币计价的收益或亏损。另一个和现实中股份不同的地方是：非标准资产的数量可以不是整数，比如$$ 0.1 $$美元或$$ 0.001 $$美元在记账中都是允许的。

# 表

## asset_types

资产类别列表，此处**资产**特指**具有独立价格**的商品、实物、所有权等等。某一种货币、某一只股票、某一只有净值或价格的基金都可称为一类资产。你也可以把其他任何具有单位价格的物品定义为资产，比如房产、数字货币等等。

如果你只使用一种货币，且不持有或交易具有独立价格的投资品，那么你的`asset_types`表就只有一条记录：自己使用的货币。

**字段**
- `asset_index`（整数）：自动生成的索引，无需用户输入。
- `asset_name`（字符串）：资产名字，不允许为空。仅用于在视图中展示，不会影响计算。
- `asset_order`（整数）：资产序号，不允许为空。仅用于在视图中展示资产时排序使用（值小的资产排在前面），不会影响计算。如果对排序没有要求，可以把所有资产的`asset_order`都设置为$$ 0 $$。

## standard_asset

标准资产，或者叫**本位币**。所有其他资产都会换算成标准资产来统计市场价值。

**字段**
- `asset_index`（整数）：资产索引，不允许为空，必须是[asset_types表]({{ site.baseurl }}/table_view.html#asset_types)中存在的某个资产索引。

**约束**
- 该表只允许有一条记录。
- [prices表]({{ site.baseurl }}/table_view.html#prices)中任一条记录的`asset_index`不允许等于该表中的`asset_index`，因为标准资产的价格固定为$$ 1 $$。（由[check_standard_prices视图]({{ site.baseurl }}/table_view.html#check_standard_prices)校验）

## accounts

账户列表。**账户**是**具有独立余额和交易记录**的实体。注意一张个人银行卡通常包含多个账户，比如活期账户、投资账户、信用账户等等，在给账户命名的时候应当注意。

账户余额并不一定是正数，当余额为负数时，表示账户中有负债。比如，大多数时候信用卡的余额就是负值，表示用户在这个账户上存在未来需要归还的负债。

账户有两种：**内部账户**和**外部账户**。外部账户的余额并不是用户的资产/负债的一部分，而是用户在某一方面的花费/收入的总额。这是因为，**复式记账法**要求任一笔交易必须发生在两个账户之间，因此对于日常开销或者工资收入这类交易，需要一个虚拟的外部账户作为交易的另一方。利用外部账户可以对用户各种开销/收入进行分类统计。

**字段**
- `account_index`（整数）：自动生成的索引，无需用户输入。
- `account_name`（字符串）：账户名字，不允许为空。仅用于在视图中展示，不会影响计算。
- `asset_index`（整数）：账户对应的资产索引，即这个账户上存放的是哪种资产。不允许为空，必须是[asset_types表]({{ site.baseurl }}/table_view.html#asset_types)中存在的某个资产索引。
- `is_external`（`0`或`1`）：为`0`表示内部账户，为`1`表示外部账户。

## interest_accounts

利息账户列表。利息账户是一类特殊的外部账户（请参考[accounts表]({{ site.baseurl }}/table_view.html#accounts)中对**外部账户**的定义），这个外部账户提供了存款利息、理财收益等等利息收益的来源。注意这里定义的**利息**特指**同一账户**内的余额增加，比如某些理财产品的净值固定为$$ 1 $$，分红体现为份额数变多。具有独立净值或价格的基金和股票的分红不应被视为利息，因为这些分红是以现金形式发放到另一个账户的，基金/股票的数量/份额并没有增加。即使因分红再投资导致份额变多，也不应该视作利息——因为股票/基金在分红的同时，其价格下降了，实际总价值并没有变化。**只有在不影响资产价格前提下的同一账户内资产数量增加才应当视为获得利息**，其他的投资收益都会被视为[股份投资收益]({{ site.baseurl }}/table_view.html#return_on_shares)。

**字段**
- `account_index`（整数）：账户索引，不允许为空，必须是[accounts表]({{ site.baseurl }}/table_view.html#accounts)中存在的某个账户索引。

**约束**
- 所有利息账户都必须为外部账户，即对应[accounts表]({{ site.baseurl }}/table_view.html#accounts)中`is_external`字段为`1`。（由[check_interest_account视图]({{ site.baseurl }}/table_view.html#check_interest_account)校验）

## postings

交易明细。根据[简化的复式记账法]({{ site.baseurl }}/table_view.html#简化的复式记账法)，每一笔交易都可看作资产从一个账户转移到另一个账户。因此该表中每一条记录都包含源账户和目标账户，记录的交易使得源账户的余额变少，目标账户余额变多。对于日常开销或者工资收入这类交易，源账户或目标账户可能是虚拟的外部账户。

只要源账户和目标账户的资产为同一种，则源账户的余额减少量等于目标账户的余额增加量，这避免了两边记账不一致产生的错误。当源账户和目标账户为不同资产（即定价不同）时，需要辅助用[posting_extras表]({{ site.baseurl }}/table_view.html#accounts)来记录目标账户的余额增加数量。

**字段**
- `posting_index`（整数）：自动生成的索引，无需用户输入。
- `trade_date`（字符串）：交易日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。交易时间只精确到天，同一天内发生的交易不区分先后顺序。
- `src_account`（整数）：源账户索引，不允许为空，必须是[accounts表]({{ site.baseurl }}/table_view.html#accounts)中存在的某个账户索引。
- `src_change`（浮点数）：源账户的变动数额，不允许为空。因为源账户的余额总是减少的，该值必须小于等于$$ 0 $$。
- `dst_account`（整数）：目标账户索引，不允许为空，必须是[accounts表]({{ site.baseurl }}/table_view.html#accounts)中存在的某个账户索引。
- `comment`（字符串）：交易备注信息，可以为空。仅用于在视图中展示，不会影响计算。

**约束**
- 一条记录中，`src_account`的值不能等于`dst_account`的值。（由[check_same_account视图]({{ site.baseurl }}/table_view.html#check_same_account)校验）

刚开始记账的用户会面临如何把各个账户的现有余额导入到表中的问题。建议的做法是：建立一个名为“历史结余”的外部账户，对于每个需要导入余额的内部账户，添加一笔从“历史结余”到此内部账户的交易记录。
{: .notice}

## posting_extras

交易明细中目标账户的变动数额，见[postings表]({{ site.baseurl }}/table_view.html#postings)中的相关描述。

**字段**
- `posting_index`（整数）：交易索引，不允许为空，必须是[postings表]({{ site.baseurl }}/table_view.html#postings)中存在的某个交易索引。
- `dst_change`（浮点数）：目标账户的变动数额，不允许为空。因为目标账户的余额总是增加的，该值必须大于等于$$ 0 $$。

**约束**
- 当源账户和目标账户的资产为同一种时，该交易不允许有`posting_extras`记录。此时目标账户的余额增加量等于源账户的余额减少量。（由[check_same_asset视图]({{ site.baseurl }}/table_view.html#check_same_asset)校验）
- 当源账户和目标账户的资产不同时，该交易必须要有`posting_extras`记录指定目标账户的变动数额，即使该次变动数额恰好和源账户相等。（由[check_diff_asset视图]({{ site.baseurl }}/table_view.html#check_diff_asset)校验）

## prices

资产价格，用于在统计总资产时将所有非标准资产换算成[标准资产（本位币）]({{ site.baseurl }}/table_view.html#standard_asset)。注意资产价格与交易明细没有关联，交易明细中某笔买入/卖出资产的价格（即两边账户变动数额之比）可以不等于当天`prices`表中该资产的价格。这是因为`prices`表记录的是当天结束时的价格（即收盘价），它可以不等于交易的实时价格。（见[start_stats视图]({{ site.baseurl }}/table_view.html#start_stats)的示例）

**字段**
- `price_date`（字符串）：价格日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。
- `asset_index`（整数）：资产索引，不允许为空，必须是[asset_types表]({{ site.baseurl }}/table_view.html#asset_types)中存在的某个资产索引。
- `price`（浮点数）：价格数值（即$$ 1 $$份该资产可以换成多少份标准资产），不允许为空。

**约束**
- 标准资产不允许有价格。（由[check_standard_prices视图]({{ site.baseurl }}/table_view.html#check_standard_prices)校验）
- 同一资产在同一天只能有一个价格，即任两条记录的`price_date`和`asset_index`不能都相同。
- 在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)这两天，所有非标准资产都必须有价格，否则总资产无法计算。（由[check_absent_price视图]({{ site.baseurl }}/table_view.html#check_absent_price)校验）
- 非标准资产与外部账户发生了交易的日子必须要有其价格。比如，如果标准资产为人民币，那么当有美元账户产生了消费时，消费当天必须要有美元兑人民币的价格。这是为了能把消费换算成人民币价值进行统计。（由[check_absent_price视图]({{ site.baseurl }}/table_view.html#check_absent_price)校验）

## start_date

统计周期的起始时间点。所有的统计视图都是基于指定的统计周期进行计算的。比如要统计2023年全年的资产变化情况，则`start_date`为`2022-12-31`，`end_date`为`2023-12-31`。注意开始日期当天的交易并不被包含在统计周期内，因为资产计算是以开始日期当天结束时的资产作为起点。

**字段**
- `val`（字符串）：开始日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。

**约束**
- 该表只允许有一条记录。
- 开始日期必须小于结束日期。

## end_date

统计周期的结束时间点。所有的统计视图都是基于指定的统计周期进行计算的。比如要统计2023年全年的资产变化情况，则`start_date`为`2022-12-31`，`end_date`为`2023-12-31`。注意结束日期当天的交易会被包含在统计周期内。

**字段**
- `val`（字符串）：结束日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。

**约束**
- 该表只允许有一条记录。
- 结束日期必须大于开始日期。

# 视图

## single_entries

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

把输入的复式记账交易记录转换为单式记账。每一条[postings表]({{ site.baseurl }}/table_view.html#postings)中的记录都会变成该视图中的两条记录。

**字段**
- `posting_index`：来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`posting_index`。
- `trade_date`：来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`trade_date`。
- `account_index`：来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`src_account`和`dst_account`。
- `amount`：来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`src_change`（并转换）或者[posting_extras表]({{ site.baseurl }}/table_view.html#postings)中的`dst_change`。
- `target`：交易的另一方，来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`src_account`和`dst_account`。
- `comment`：来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`comment`。

## statements

把输入的复式记账交易记录转换为单式记账，并且展示交易的账户关联信息。

**字段**
- 包含[single_entries视图]({{ site.baseurl }}/table_view.html#single_entries)中的所有字段，以及：
- `src_name`、`target_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。
- `is_external`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`is_external`。
- `balance`：从该账户之前的交易数额所推导出的账户余额。注意由于交易记录只精确到天，因此在一天内的实时余额不一定准确。

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
| 2 | 2023-01-07 | 1 | -67.5 | 3 | 背水咖啡厅晚餐 | 萨雷安银行活期 | 1 | 0 | 餐饮消费 | 49932.5 |
| 3 | 2023-01-09 | 1 | -13000.0 | 2 | 购入加隆德股份 | 萨雷安银行活期 | 1 | 0 | 莫古证券_加隆德股份 | 36932.5 |
| 3 | 2023-01-09 | 2 | 260.0 | 1 | 购入加隆德股份 | 莫古证券_加隆德股份 | 2 | 0 | 萨雷安银行活期 | 260.0 |
| 2 | 2023-01-07 | 3 | 67.5 | 1 | 背水咖啡厅晚餐 | 餐饮消费 | 1 | 1 | 萨雷安银行活期 | 67.5 |
| 1 | 2023-01-06 | 4 | -50000.0 | 1 | 领取工资 | 工资 | 1 | 1 | 萨雷安银行活期 | -50000.0 |

说明：`statements`视图比较像通常人们所习惯的单式记账账单。如果只想查看某一个账户的变动记录，可以用其他软件打开db文件并按`account_index`或`src_name`筛选。比如筛选`account_index`为`1`的记录，就能看到`萨雷安银行活期`的所有历史变动和余额变化。

## start_balance

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

在[start_date]({{ site.baseurl }}/table_view.html#start_date)这天结束时，所有内部账户的余额。

**字段**
- `date_val`：来自[start_date表]({{ site.baseurl }}/table_view.html#start_date)中的`val`。
- `account_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `account_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `balance`：通过累加`start_date`及之前所有交易记录计算得到的账户余额。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。

## start_stats

在[start_date]({{ site.baseurl }}/table_view.html#start_date)这天结束时，所有内部账户的余额，以及按当天价格换算成[标准资产]({{ site.baseurl }}/table_view.html#standard_asset)的市场价值。

**字段**
- 包含[start_balance视图]({{ site.baseurl }}/table_view.html#start_balance)中的所有字段，以及：
- `asset_order`：来自[asset_types表]({{ site.baseurl }}/table_view.html#asset_types)中的`asset_order`。
- `asset_name`：来自[asset_types表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_name`。
- `price`：来自[prices表]({{ site.baseurl }}/table_view.html#accounts)中的`price`；如果是标准资产，则值为$$ 1 $$。
- `market_value`：通过$$ \text{price} \times \text{balance} $$计算得到的市场价值。

**示例**

假设在[statements视图]({{ site.baseurl }}/table_view.html#statements)中示例已有表基础上，另外加入表：

`start_date`

| val |
|:-:|
| 2023-1-9 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-1-9 | 2 | 51 |

则`start_stats`视图内容为：

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-01-09 | 1 | 萨雷安银行活期 | 36932.5 | 1 | Gil | 1.0 | 36932.5 |
| 0 | 2023-01-09 | 2 | 莫古证券_加隆德股份 | 260.0 | 2 | 加隆德炼铁厂股份 | 51.0 | 13260.0 |

说明：注意`balance`列的值和`statements`视图中该日期各账户的余额是一致的；外部账户不会在`start_stats`视图里出现。根据`postings`表中购买`加隆德炼铁厂股份`的交易记录可以换算当时交易的价格是$$ 13000 \div 260 = 50 $$，但是`prices`表中`2023-1-9`的价格记录是$$ 51 $$，且账户资产市场价值是根据$$ 51 $$计算的。这个例子展示了实时交易价格可以和收盘价不同。

## diffs

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个账户在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)之间的交易额统计。`start_date`当天的交易不统计，`end_date`当天的交易会统计。

**字段**
- `account_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `account_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `amount`：通过累加`start_date`和`end_date`之间所有交易记录计算得到的交易额统计。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。

## comparison

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个账户在[start_date]({{ site.baseurl }}/table_view.html#start_date)的初始余额，[end_date]({{ site.baseurl }}/table_view.html#end_date)的最终余额，以及两个日期之间的交易额统计。

**字段**
- 包含[diffs视图]({{ site.baseurl }}/table_view.html#diffs)中的`account_index`、`account_name`、`asset_index`字段，以及：
- `start_amount`：来自[start_balance视图]({{ site.baseurl }}/table_view.html#start_balance)中的`balance`。
- `diff`：来自[diffs视图]({{ site.baseurl }}/table_view.html#diffs)中的`amount`；或者，如果一个账户在统计周期内没有变化，则为$$ 0 $$。
- `end_amount`：通过$$ \text{start_amount} + \text{diff} $$计算得到的最终余额。

## end_stats

在[end_date]({{ site.baseurl }}/table_view.html#end_date)这天结束时，所有内部账户的余额，以及按当天价格换算成[标准资产]({{ site.baseurl }}/table_view.html#standard_asset)的市场价值。

注意：[start_date表]({{ site.baseurl }}/table_view.html#start_date)中必须要有一条记录，才能使`end_stats`视图显示正确的内容。
{: .notice--warning}

**字段**
- 除以下字段外，其他字段均与[start_stats视图]({{ site.baseurl }}/table_view.html#start_stats)中的字段相同：
- `balance`：通过累加`end_date`及之前所有交易记录计算得到的账户余额。

**示例**

假设在[statements视图]({{ site.baseurl }}/table_view.html#statements)中示例已有表基础上，另外加入表：

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

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-01-09 | 1 | 萨雷安银行活期 | 36932.5 | 1 | Gil | 1.0 | 36932.5 |
| 0 | 2023-01-09 | 2 | 莫古证券_加隆德股份 | 260.0 | 2 | 加隆德炼铁厂股份 | 51.0 | 13260.0 |

说明：可以看到`end_stats`视图的内容与[start_stats视图]({{ site.baseurl }}/table_view.html#start_stats)几乎一样，仅统计日期为`end_date`这一点有区别。

## external_flows

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个**外部账户**在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)之间的每笔交易，以及当天该资产的价格。`start_date`当天的交易不统计，`end_date`当天的交易会统计。注意外部账户（除利息账户外）实际上代表收入和支出的特定类别。

**字段**
- `trade_date`：来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`trade_date`。
- `asset_order`：来自[asset_types表]({{ site.baseurl }}/table_view.html#asset_types)中的`asset_order`。
- `account_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `account_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `amount`：来自[single_entries表]({{ site.baseurl }}/table_view.html#single_entries)中的`amount`。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。
- `asset_name`：来自[asset_types表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_name`。
- `price`：来自[prices表]({{ site.baseurl }}/table_view.html#accounts)中的`price`；如果是标准资产，则值为`1`。

## income_and_expenses

每个**外部账户**在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)之间的交易额统计，以及换算的总市场价值。`start_date`当天的交易不统计，`end_date`当天的交易会统计。注意外部账户（除利息账户外）实际上代表收入和支出的特定类别。

**字段**
- 包含[external_flows视图]({{ site.baseurl }}/table_view.html#external_flows)中的`asset_order`、`account_index`、`account_name`、`asset_index`、`asset_name`字段，以及：
- `total_amount`：通过累加`start_date`和`end_date`之间该外部账户每笔交易的变动数额得到的交易额统计（未换算成标准资产）。
- `total_value`：把每笔交易的变动数额按当天资产价格换算成标准资产，并累加得到的总市场价值。假设某外部账户一共有$$ n $$笔交易，该资产在每笔交易当天的单位价格分别为$$ p_1 \dots p_n $$，变动数额分别为$$ a_1 \dots a_n $$，则总价值为：$$ \displaystyle\sum_{i=1}^{n} p_ia_i $$。

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

说明：注意外部账户的累计变动数额等于内部账户变动数额的相反数，比如`工资`账户`total_amount`为$$ -50000.0 $$，即表示内部账户共有$$ 50000.0 $$的工资收入。

对于外部账户资产为标准资产（如例子中的`Gil`）的，统计市场价值等于变动数额累加；但是当外部账户资产为非标准资产时（如例子中的`金碟币`），会按交易发生当天的价格依次换算为标准资产再累加。在这个例子中，`金碟消费`的`total_value`计算过程为$$ 30 \times 90 + 100 \times 110 = 13700 $$。

## portfolio_stats

只有一条记录，展示所有账户的组合在周期开始和结束时的净资产、周期内的总收入支出、总投资收益。

**字段**
- `start_value`：期初净资产，从[start_stats表]({{ site.baseurl }}/table_view.html#start_stats)中的`market_value`累加得到。
- `end_value`：期末净资产，从[end_stats表]({{ site.baseurl }}/table_view.html#end_stats)中的`market_value`累加得到。
- `net_outflow`：期间发生的净流出资金额。从[income_and_expenses视图]({{ site.baseurl }}/table_view.html#income_and_expenses)中非[利息账户]({{ site.baseurl }}/table_view.html#interest_accounts)的`total_value`累加得到，注意利息收入不会被记入。如果这期间资金是净流入的，那么这个值为负数。
- `interest`：期间发生的利息收入总计，从[income_and_expenses视图]({{ site.baseurl }}/table_view.html#income_and_expenses)中[利息账户]({{ site.baseurl }}/table_view.html#interest_accounts)的`total_value`累加得到。
- `net_gain`：期间投资产生的总收益（或总亏损），计算方法为$$ \text{end_value} + \text{net_outflow} - \text{start_value} $$。即：除了收入支出产生的净资产变化，其他净资产变动都认为是投资收益（或亏损）。利息收入属于投资收益的一部分。
- `rate_of_return`：使用简单Dietz方法计算的期间投资收益率。

## flow_stats

每个内部账户在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)之间与**外部账户**发生的交易额统计。`start_date`当天的交易不统计，`end_date`当天的交易会统计。注意外部账户（除利息账户外）实际上代表收入和支出的特定类别，因此这个视图可看作是每个内部账户的分类收入支出统计。

注意该视图和[income_and_expenses视图]({{ site.baseurl }}/table_view.html#income_and_expenses)相比有两个区别：
1. `flow_stats`中不同内部账户会分开进行统计，但`income_and_expenses`中不同内部账户和同一外部账户交易的数额会被累加合并；
1. `flow_stats`只展示按相应资产变动数额累加的统计值，但`income_and_expenses`还按照资产价格换算成了标准资产。

**字段**
- `flow_index`：外部账户索引，来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `flow_name`：外部账户名字，来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `account_index`：内部账户索引，来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `account_name`：内部账户名字，来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `amount`：通过累加`start_date`和`end_date`之间每笔交易的变动数额得到的交易额统计（未换算成标准资产）。

**示例**

假设在[income_and_expenses视图]({{ site.baseurl }}/table_view.html#income_and_expenses)中示例已有表基础上，在这两个表中加入额外的记录：

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

每个非标准资产的内部账户与其他账户的每笔交易额换算成标准资产的市场价值。该数据用于计算非标准资产（即投资品）的投资收益率。

如果把非标准资产看成股票，那么这个视图可以理解为每一笔交易的买入成本或者卖出收入。

**字段**
- 包含[single_entries视图]({{ site.baseurl }}/table_view.html#single_entries)中的所有字段，以及：
- `account_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。
- `asset_name`：来自[asset_types表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_name`。
- `asset_order`：来自[asset_types表]({{ site.baseurl }}/table_view.html#asset_types)中的`asset_order`。
- `cash_flow`：该笔交易额换算成标准资产后的市场价值。

## share_stats

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个非标准资产的内部账户（即投资品）的所需最小资金净流入，以及通过交易和持有该投资品获得的净现金（标准资产）增量。请参见最小初始资金法的介绍来理解该视图的数据。

**字段**
- `asset_order`：来自[asset_types表]({{ site.baseurl }}/table_view.html#asset_types)中的`asset_order`。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。
- `asset_name`：来自[asset_types表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_name`。
- `account_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `account_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `min_inflow`：该标准资产（即投资品）在整个周期中所需要的最小资金净流入。如果不需要流入，那么为$$ 0 $$。
- `cash_gained`：交易该标准资产（投资品）获得的净现金（标准资产）增量。

## return_on_shares

每个非标准资产的内部账户（即投资品）在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)之间的投资收益率。`start_date`当天的交易不统计，`end_date`当天的交易会统计。计算收益率采用的是最小初始资金法。

注意：利息收入不会被计入该视图的投资收益率，而是在[interest_rates视图]({{ site.baseurl }}/table_view.html#interest_rates)中展示。如果不希望利息收益被剥离计算，那么可以把利息收入记录为成本为$$ 0 $$的买入操作（类似股份的拆分或送股）。
{: .notice}

**字段**
- `asset_order`：来自[asset_types表]({{ site.baseurl }}/table_view.html#asset_types)中的`asset_order`。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。
- `asset_name`：来自[asset_types表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_name`。
- `account_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `account_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `start_amount`：来自[comparison视图]({{ site.baseurl }}/table_view.html#comparison)中的`start_amount`。
- `start_value`：来自[start_stats视图]({{ site.baseurl }}/table_view.html#start_stats)中的`market_value`，或者$$ 0 $$（如果`start_stats`中没有此账户）。
- `diff`：来自[comparison视图]({{ site.baseurl }}/table_view.html#comparison)中的`diff`。
- `end_amount`：来自[comparison视图]({{ site.baseurl }}/table_view.html#comparison)中的`end_amount`。
- `end_value`：来自[end_stats视图]({{ site.baseurl }}/table_view.html#end_stats)中的`market_value`，或者$$ 0 $$（如果`end_stats`中没有此账户）。
- `cash_gained`：来自[share_stats视图]({{ site.baseurl }}/table_view.html#share_stats)中的`cash_gained`，或者$$ 0 $$（如果`share_stats`中没有此账户）。
- `min_inflow`：来自[share_stats视图]({{ site.baseurl }}/table_view.html#share_stats)中的`min_inflow`，或者$$ 0 $$（如果`share_stats`中没有此账户）。
- `profit`：该非标准资产的投资利润（或亏损），计算方法为$$ \text{cash_gained} + \text{end_value} - \text{start_value} $$。
- `rate_of_return`：使用最小初始资金法计算的该非标准资产的投资收益率。

## interest_stats

这个视图为其他视图计算的中间过程，用户通常不需要关心这个视图。
{: .notice}

每个内部账户在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)之间获得的利息。

**字段**
- `account_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `account_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。
- `amount`：该账户在统计周期内获得的利息（未换算成标准资产）。

## interest_rates

每个内部账户在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)之间获得的利息，平均每日账户资产，以及按照修改的Dietz方法计算出的利率。

该视图只展示有利息收入的内部账户（无论该内部账户是否为标准资产），且展示的收益率仅仅为利息的收益率，并不包含资产价格变动产生的收益。

**字段**
- `account_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_index`。
- `account_name`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`account_name`。
- `asset_index`：来自[accounts表]({{ site.baseurl }}/table_view.html#accounts)中的`asset_index`。
- `avg_balance`：该账户在统计周期内的平均每日余额（未换算成标准资产）。
- `interest`：来自[interest_stats视图]({{ site.baseurl }}/table_view.html#interest_stats)中的`amount`。
- `rate_of_return`：使用修改的Dietz方法计算的投资收益率（即利率）。

## periods_cash_flows

所有账户的组合在统计周期内每天的资金净流入/流出。利息收入作为投资收益，不会被计入资金流入/流出；除利息账户以外的其他外部账户和内部账户之间的交易都会被计入资金流入/流出。在周期的开始，组合的净资产被视作一次净流入；在周期的结束，组合的净资产被视作一次净流出。

该视图为计算内部收益率（IRR）所需要的数据。

**字段**
- `trade_date`：资金净流入/流出的日期。
- `period`：该日期相对于周期的开始日期所经过的天数。
- `cash_flow`：在该日期所有账户的资金净流入/流出，已换算成标准资产。注意根据内部收益率（IRR）的定义，流入为负值，流出为正值，这和通常的定义不一样。

## check_standard_prices

正常情况下这个视图没有记录。如果出现了记录，说明在[prices表]({{ site.baseurl }}/table_view.html#prices)中出现了标准资产的价格，违反了约束。

## check_interest_account

正常情况下这个视图没有记录。如果出现了记录，说明有[利息账户]({{ site.baseurl }}/table_view.html#interest_accounts)是内部账户，违反了约束。

## check_same_account

正常情况下这个视图没有记录。如果出现了记录，说明[postings表]({{ site.baseurl }}/table_view.html#postings)中有`src_account`和`dst_account`相同的记录，违反了约束。

## check_diff_asset

正常情况下这个视图没有记录。如果出现了记录，说明[postings表]({{ site.baseurl }}/table_view.html#postings)中有源账户和目标账户的资产不同，但[posting_extras表]({{ site.baseurl }}/table_view.html#posting_extras)却没有对应记录，违反了约束。

## check_same_asset

正常情况下这个视图没有记录。如果出现了记录，说明[postings表]({{ site.baseurl }}/table_view.html#postings)中有源账户和目标账户的资产相同，但[posting_extras表]({{ site.baseurl }}/table_view.html#posting_extras)却有对应记录，违反了约束。

## check_absent_price

正常情况下这个视图没有记录。如果出现了记录，说明[prices表]({{ site.baseurl }}/table_view.html#prices)中缺少某些资产在某些日期需要被用到的价格，违反了约束。