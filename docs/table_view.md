---
title: 表和视图
---
本页介绍db数据库文件中包含的所有表和视图。

**表**是用户需要提供的输入，是所有数据的源头。为了确保数据的完整性和一致性，在添加、修改表中的数据时，工具会进行各方面的校验，保证各表的数据不出现冲突和逻辑矛盾。

**视图**是工具计算出的报表，是用户关心的各项统计数据结果。每当任一张表的内容有任何更新，所有视图均会立即自动更新并反映最新的内容，视图的计算不需要手工触发。

有一些视图是面向用户提供报表数据的（比如资产统计），也有一些视图是另一些视图的中间计算结果，用户通常不需要关注（除非对最终的统计结果有疑问想要检查计算过程）。在下面的视图描述中，对于用户通常不需关注的视图会专门说明。

所有名字以check开头的视图都是用于检查数据一致性的。当数据一致时，这些check开头的视图应当不包含任何内容。如果发现某个check开头的视图内容不为空，TataruBook会在命令行报告相关的数据错误并提示用户修正。

# 表

## asset_info

资产列表，此处**资产**特指**具有独立价格**的标的。某一种货币、某一只股票、某一只有净值或价格的基金都可称为一个资产。你也可以把其他任何具有单位价格的物品定义为资产，比如房产、数字货币等等。

如果你只使用一种货币，且不持有或交易具有独立价格的投资品（货币基金的净值始终为1，因此不具有独立价格），那么你的`asset_info`表就只有一条记录：自己使用的货币。

**字段**
- `asset_index`（整数）：自动生成的索引，无需用户输入。
- `asset_name`（字符串）：资产名字，不允许为空。仅用于在视图中展示，不会影响计算。
- `asset_category`（整数）：资产类型，不允许为空。仅用于在视图中展示资产时排序使用（值小的资产排在前面），不会影响计算。如果对排序没有要求，可以把所有资产的`asset_category`都设置为`0`。

## standard_asset

标准资产，或者叫**本位币**。所有其他资产都会换算成本位币来统计价值。通常这张表中只应当有一条记录。

**字段**
- `asset_index`（整数）：资产索引，不允许为空，必须是[asset_info表]({{ site.baseurl }}/table_view.html#asset_info)中存在的某个资产索引。

**约束**
- [prices表]({{ site.baseurl }}/table_view.html#prices)中任一条记录的`asset_index`不允许等于该表中的`asset_index`，因为本位币自身的价格固定为`1`。

## account_info

账户列表。**账户**是**具有独立余额和交易记录**的实体。注意一张个人银行卡通常包含多个账户，比如活期账户、投资账户、信用账户等等，在给账户命名的时候应当注意。

账户余额并不一定是正数，因为负债也可以用账户记录。比如，大多数时候信用卡的余额就是负值，表示用户在这个账户上存在未来需要归还的负债。

有一类特殊的账户：**外部账户**，它的余额并不是用户的资产/负债的一部分，而是用户在某一方面的花费/收入的总额。这是因为，**复式记账法**要求任一笔交易必须发生在两个账户之间，因此对于日常开销或者工资收入这类交易，需要一个虚拟的外部账户作为交易的另一方。利用外部账户可以对用户各种开销/收入进行分类统计。（对复式记账法的更多描述可查看[postings表]({{ site.baseurl }}/table_view.html#postings)）

**字段**
- `account_index`（整数）：自动生成的索引，无需用户输入。
- `account_name`（字符串）：账户名字，不允许为空。仅用于在视图中展示，不会影响计算。
- `asset_index`（整数）：账户对应的资产索引，即这个账户上放的是哪种资产。不允许为空，必须是[asset_info表]({{ site.baseurl }}/table_view.html#asset_info)中存在的某个资产索引。
- `is_external`（`0`或`1`）：为`0`表示是普通账户，为`1`表示是外部账户。

## interest_account

利息账户列表。利息账户是一类特殊的外部账户（请参考[account_info表]({{ site.baseurl }}/table_view.html#account_info)中对**外部账户**的定义），这个外部账户提供了存款利息、货币基金收益等等这类利息收益的来源。注意这里定义的**利息**特指**同一账户**内的余额增加，比如货币基金分红体现为份额数变多。除货币基金外，其他类型基金和股票的分红不应被视为利息，因为这些分红是以现金形式发放到另一个账户的，基金/股票的数量/份额并没有增加。即使选择分红再投资导致份额变多，也不应该视作利息——因为股票/基金在分红的同时，其价格下降了，实际总价值并没有变化。**只有在不影响资产价格前提下的同一账户内资产数量增加才应当视为获得利息**，其他的投资收益都会被视为浮动投资收益。

**字段**
- `account_index`（整数）：账户索引，不允许为空，必须是[account_info表]({{ site.baseurl }}/table_view.html#account_info)中存在的某个账户索引。

## postings

交易明细。根据复式记账规则，每一笔交易都是资产从一个账户转移到另一个账户，因此表中每一条记录都会包含源账户和目标账户，交易使得源账户的余额变少，目标账户余额变多。对于日常开销或者工资收入这类交易，源账户或目标账户可能是虚拟的外部账户。

只要源账户和目标账户的资产为同一种，则源账户的余额减少量等于目标账户的余额增加量，这避免了两边记账不一致产生的错误。当源账户和目标账户为不同资产（即定价不同）时，需要辅助用[receiving表]({{ site.baseurl }}/table_view.html#account_info)来记录目标账户的余额增加数量。

**字段**
- `posting_index`（整数）：自动生成的索引，无需用户输入。
- `trade_date`（字符串）：交易日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。交易时间只精确到天，同一天内发生的所有交易不区分先后顺序。
- `src_account`（整数）：源账户索引（在复式记账法中称为**Debit**），不允许为空，必须是[account_info表]({{ site.baseurl }}/table_view.html#account_info)中存在的某个账户索引。
- `src_amount`（浮点数）：源账户的变动数额，不允许为空。因为源账户的余额总是减少的，该值必须小于等于`0`。
- `dst_account`（整数）：目标账户索引（在复式记账法中称为**Credit**），不允许为空，必须是[account_info表]({{ site.baseurl }}/table_view.html#account_info)中存在的某个账户索引。
- `comment`（字符串）：交易备注信息，可以为空。仅用于在视图中展示，不会影响计算。

对新用户来说，会面临如何把现有账户的当前余额导入到表中的问题。建议的做法是：在最早的一天，增加一笔从“历史余额”外部账户到自己对应账户的交易记录。
{: .notice}

## receiving

交易明细中目标账户的变动数额，见[postings表]({{ site.baseurl }}/table_view.html#postings)中的相关描述。

**字段**
- `posting_index`（整数）：交易索引，不允许为空，必须是[postings表]({{ site.baseurl }}/table_view.html#postings)中存在的某个交易索引。
- `dst_amount`（浮点数）：目标账户的变动数额，不允许为空。因为目标账户的余额总是增加的，该值必须大于等于`0`。

**约束**
- 当源账户和目标账户的资产为同一种时，该交易不允许有receiving记录。此时目标账户的余额增加量等于源账户的余额减少量。
- 当源账户和目标账户的资产不同时，该交易必须要有receiving记录指定目标账户的变动数额，即使该次变动数额恰好和源账户相等。

## prices

资产价格，用于统计总资产时将所有其他资产换算成[标准资产（本位币）]({{ site.baseurl }}/table_view.html#standard_asset)。注意资产价格与交易明细没有关联，交易明细中某笔买入/卖出资产的价格（即两边账户变动数额之比）可以不等于当天prices表中的资产价格。这是因为prices表记录的是当天结束时的价格（即收盘价），它可以不等于交易的实时价格。

**字段**
- `price_date`（字符串）：价格日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。
- `asset_index`（整数）：资产索引，不允许为空，必须是[asset_info表]({{ site.baseurl }}/table_view.html#asset_info)中存在的某个资产索引。
- `price`（浮点数）：价格数值（即`1`份该资产可以换成多少份标准资产（本位币）），不允许为空。

**约束**
- 标准资产不允许有价格。
- 同一资产在同一天只能有一个价格，即任两条记录的`price_date`和`asset_index`不能都相同。
- 在[start_date]({{ site.baseurl }}/table_view.html#start_date)和[end_date]({{ site.baseurl }}/table_view.html#end_date)这两天，所有非标准资产都必须有价格，否则总资产无法计算。
- 非标准资产与外部账户发生了交易的日子必须要有价格。比如，如果标准资产为人民币，那么当有美元账户产生了消费时，消费当天必须要有美元兑人民币的价格。这是为了能把消费换算成人民币价值进行统计。

## start_date

统计周期的起始时间点。统计周期用于计算一段时间内的总资产变化、投资收益率等。比如要统计2023年全年的资产变化情况，则`start_date`为`2022-12-31`，`end_date`为`2023-12-31`。注意开始日期当天并不包含在统计周期内，因为资产计算是以开始日期当天结束时的资产作为起点。

**字段**
- `val``（字符串）：开始日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。

**约束**
- 该表只允许有一条记录。
- 开始日期必须小于结束日期。

## end_date

统计周期的结束时间点。统计周期用于计算一段时间内的总资产变化、投资收益率等。比如要统计2023年全年的资产变化情况，则`start_date`为`2022-12-31`，`end_date`为`2023-12-31`。注意结束日期当天也包含在统计周期内。

**字段**
- `val``（字符串）：结束日期，不允许为空，固定为ISO 8601格式：yyyy-mm-dd。

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
- `amount`：来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`src_amount`（并转换）或者[receiving表]({{ site.baseurl }}/table_view.html#postings)中的`dst_amount`。
- `target`：交易的另一方，来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`src_account`和`dst_account`。
- `comment`：来自[postings表]({{ site.baseurl }}/table_view.html#postings)中的`comment`。

## statements

把输入的复式记账交易记录转换为单式记账，并且展示交易的账户关联信息。

**字段**
- 包含[single_entries视图]({{ site.baseurl }}/table_view.html#single_entries)中的所有字段，以及：
- `src_name`、`target_name`：来自[account_info表]({{ site.baseurl }}/table_view.html#account_info)中的`account_name`。
- `asset_index`：来自[account_info表]({{ site.baseurl }}/table_view.html#account_info)中的`asset_index`。
- `is_external`：来自[account_info表]({{ site.baseurl }}/table_view.html#account_info)中的`is_external`。
- `balance`：从该账户之前的交易数额所推导出的账户余额。注意由于交易记录只精确到天，因此在一天内的实时余额不一定准确。

**示例**

假设现有表内容如下：
