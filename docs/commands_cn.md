---
title: 命令行手册
sidebar:
  nav: "chinese"
---
本页介绍TataruBook支持的所有命令及选项。

TataruBook有两种[安装方式]({{ site.baseurl }}/index_cn.html#如何下载和安装tatarubook)，与之对应的有两种命令行用法：**Python脚本用法**和**可执行文件用法**。为了简便起见，本页都以可执行文件用法为示例。如果采用的是Python脚本用法，则需要将所有命令开头从`tatarubook`换成`python tatarubook.py`。比如，要创建一个名为`example.db`的数据库文件，需要将`tatarubook init example.db`命令改为`python tatarubook.py init example.db`。

# 通用特性

下面介绍一些和多个命令都有关的特性：

## 字符编码格式

默认设置下，TataruBook使用操作系统默认字符编码格式读写文件。但是注意非英文Windows操作系统的默认字符编码格式不是UTF-8，因此在Windows下读取UTF-8格式的csv文件时，TataruBook可能会遇到解码错误。为了解决这个问题，TataruBook在用其他格式解码失败时，会再尝试使用UTF-8解码一次。

如果想要TataruBook使用其他的字符编码格式读写文件，可以在相关命令中使用`--encoding`选项指定字符编码格式，支持的编码格式列表见[这里](https://docs.python.org/3/library/codecs.html#standard-encodings)。

## 自动生成的索引字段

有一些字段的值是在插入时自动生成的，比如[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表的`account_index`，[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表的`posting_index`等等。当用[insert]({{ site.baseurl }}/commands_cn.html#insert)命令插入这些表的记录时，这些字段的值应当填写为`NULL`；用[import]({{ site.baseurl }}/commands_cn.html#import)命令导入记录时，这个字段对应单元格的内容应当为空。这样，TataruBook会自动找到一个与其他记录不同的新索引值填入这个字段。

## 日期的输入格式

在输入日期时，TataruBook要求一个日期包含且仅包含年、月、日三个成员，且成员排列顺序依次为年、月、日。成员之间可以用`/`、`-`、`.`三种字符中的任一种分隔，但是分隔符必须一致。年必须是4位数字，月和日可以是1位或2位数字，可以有或者没有前导0。

年、月、日之间也可以没有分隔符，但没有分隔符时整个日期必须是8位数字，形式为`yyyymmdd`。

以下日期格式都是合法的：`2023/5/3`、`2023-5-3`、`2023.5.3`、`2023-05-03`、`2023/5/03`、`20230503`。

以下日期格式都是不合法的：`2023-5/3`（分隔符不一致）、`23-05-03`（年不是4位数字）、`2023053`（没有分隔符但不是8位数字）。

## 根据名字查找索引

当一张表的某条记录引用另一张表的某条记录时，根据数据库的设计原则，引用的是记录的**索引（index）**。但是人工输入索引是比较麻烦且容易出错的。举个例子：如果[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表的内容如下：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | 萨雷安银行活期 | 1 | 0 |
| 2 | 餐饮消费 | 1 | 1 |

现在想在[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表中插入一条记录，表示从`萨雷安银行活期`账户产生了一笔`餐饮消费`的记录，这条记录事实上是这样的：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-07 | 1 | -67.5 | 2 | 背水咖啡厅晚餐 |

但是，手工编写这条记录时，需要查找到`萨雷安银行活期`的`account_index`为`1`，并填写到`src_account`字段中；查找到`餐饮消费`的`account_index`为`2`，并填写到`dst_account`字段中。这个查找过程很麻烦——尤其当`accounts`表有几十条以上的记录时。

为了解决这个问题，TataruBook允许在某些需要填写索引的地方填写**名字**。比如要插入上面这条`postings`表的记录，可以在csv文件中写成这样（如果你不明白为什么`posting_index`下面的单元格是空的，见[自动生成的索引字段]({{ site.baseurl }}/commands_cn.html#自动生成的索引字段)）：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-01-07 | 萨雷安银行活期 | -67.5 | 餐饮消费 | 背水咖啡厅晚餐 |

然后用[import]({{ site.baseurl }}/commands_cn.html#import)命令导入。TataruBook会自动查找`accounts`表中哪条记录的`account_name`为`萨雷安银行活期`，哪条记录的`account_name`为`餐饮消费`，并把这两条记录的`account_index`填到对应的字段。

不光[import]({{ site.baseurl }}/commands_cn.html#import)命令支持这个功能，[insert]({{ site.baseurl }}/commands_cn.html#insert)命令也支持这个功能。上面的这条记录也可以直接用一条命令插入：

~~~
tatarubook insert example.db postings NULL 2023-01-07 萨雷安银行活期 -67.5 餐饮消费 背水咖啡厅晚餐
~~~

TataruBook根据名字查找索引的具体规则如下：

1. 首先把字段内容看成是**索引**，如果该索引对应的记录存在，那么直接用这个索引值不做转换。例如：如果存在一条记录的索引是`666`，那么输入的`666`会被直接解释为索引——即使其他记录中存在**名字**是`666`的，也会被忽略。
1. 如果该索引对应的记录不存在，那么查找名字**等于或者包含**字段内容的**唯一**记录。如果找到了，把字段内容转换为这条记录的索引。这个过程如上面使用[import]({{ site.baseurl }}/commands_cn.html#import)和[insert]({{ site.baseurl }}/commands_cn.html#insert)命令的例子所示。
1. 如果没有记录的名字等于或者包含该字段内容，或者找出的记录不止一条，那么执行失败并报错。例如：如果存在两条`accounts`表记录的名字分别为`萨雷安银行活期`和`萨雷安养老金`，那么当查找字段内容为`萨雷安`时会报错，因为TataruBook无法确定对应的是哪个索引。

下面列出了支持填写名字而不是索引的所有字段，以及在自动查找该索引时涉及到的相关表和字段：

| 表 | 字段 | 引用的表 | 查找名字 | 转换后的索引 |
|:-:|:-:|:-:|:-:|:-:|
| postings | src_account | accounts | account_name | account_index |
| postings | dst_account | accounts | account_name | account_index |
| interest_accounts | account_index | accounts | account_name | account_index |
| accounts | asset_index | asset_types | asset_name | asset_index |
| prices | asset_index | asset_types | asset_name | asset_index |
| standard_asset | asset_index | asset_types | asset_name | asset_index |

强烈建议在插入记录的时候，填写名字而不是索引。这种做法可大大减少填写出错的可能性。
{: .notice}

## 自动插入关联表的记录

[posting_extras]({{ site.baseurl }}/tables_and_views_cn.html#posting_extras)表的记录几乎总是和[postings]({{ site.baseurl }}/tables_and_views_cn.html#postings)表的相应记录同时被插入的——因为它们描述的是同一条交易记录。因此在添加交易记录时，需要先插入`postings`表的记录，然后查询刚刚插入的记录的`posting_index`，然后编辑`posting_extras`表的记录写入这个`posting_index`，最后再插入`posting_extras`表的记录。

这个过程显然很麻烦。为了简化交易记录的插入，TataruBook支持**自动插入关联表的记录**功能。当插入`postings`表的记录时，如果在末尾多写一个字段，TataruBook即认为这是要关联插入`posting_extras`表，这个多出的字段是`posting_extras`表的`dst_change`字段的值。

举例：用[import]({{ site.baseurl }}/commands_cn.html#import)命令导入下面这样的csv文件内容，会同时在`postings`表和`posting_extras`表各插入一条记录，且两条记录的`posting_index`相同。（如果你不明白为什么`src_account`和`dst_account`的值不是数字，参见[根据名字查找索引]({{ site.baseurl }}/tables_and_views_cn.html#根据名字查找索引)功能；如果不明白为什么`posting_index`下面的单元格是空的，见[自动生成的索引字段]({{ site.baseurl }}/commands_cn.html#自动生成的索引字段)）

| posting_index | trade_date | src_account | src_change | dst_account | comment | dst_change |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-05-22 | 萨雷安银行活期 | -10000 | 加隆德炼铁厂股份 | 买入股票 | 500 |

[insert]({{ site.baseurl }}/commands_cn.html#insert)命令也支持这个功能，用下面这条命令可达到一样的效果：

~~~
tatarubook insert example.db postings NULL 2023-05-22 萨雷安银行活期 -10000 加隆德炼铁厂股份 买入股票 500
~~~

注意`dst_change`字段一定要放在末尾。TataruBook只根据位置来识别字段，不关心csv文件标题行的内容。

[accounts]({{ site.baseurl }}/tables_and_views_cn.html#accounts)表也支持关联插入功能：如果要插入的`accounts`表记录对应的`asset_types`表记录也需要插入，那么可以用一次[import]({{ site.baseurl }}/commands_cn.html#import)命令操作完成，使用的csv文件内容如下：

| account_index | account_name | asset_index | is_external | asset_name | asset_order |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 莫古证券_加隆德股份 | | 0 | 加隆德炼铁厂股份 | 0 |

这种场景常见于买入新的基金/股票品种时，需要同时添加新的资产类型和新的账户。

# 命令使用方法

## help

使用`-h`或`--help`参数时，会给出命令帮助信息。分两种情况：

1. 没有子命令时（比如输入`tatarubook -h`），会列出所有其他命令的简要功能说明。
1. 有子命令时（比如输入`tatarubook insert -h`），会提示对应子命令的详细用法。

## init

创建并初始化一个空的db文件。

**命令格式**：

~~~
tatarubook init [-h] db_file
~~~

**参数**：
- `db_file`：db文件名，可带路径。如果该文件已存在，不会执行任何操作，只打印错误信息。如果路径和文件名中有空格，需要在这个参数两侧加上引号。

## check

检查db文件中的数据是否符合一致性约束。

**v1.1版本新增功能**：检查db文件中所有的表、索引、视图定义与当前版本是否一致。
{: .notice}

**命令格式**：

~~~
tatarubook check [-h] db_file
~~~

**参数**：
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。

数据一致性约束分为两种：

1. 强制性约束：如果不满足，那么修改操作会立即失败，数据会马上回滚。一般来说，字段值类型/范围约束、外键有效性都是强制性约束。由于强制性约束已经由底层数据库保证，在正常情况下不可能被违反，所以`check`命令不会检查强制性约束。
1. 警示性约束：如果不满足，数据仍然允许修改，但是会提示需要修复。这种约束大多通过特定的`check`视图来检查，比如要求特定日期特定资产需要有价格信息。`check`命令只检查警示性约束。

想了解数据一致性约束包含哪些检查，可以查看[表和视图]({{ site.baseurl }}/tables_and_views_cn.html)中的说明。

由于数据一致性对很多报表的正确性都有影响，因此TataruBook在执行了任何修改db文件的操作后，都会自动运行一次数据一致性检查并报告结果。
{: .notice}

## export

把指定表/视图或者所有表/视图的内容导出到csv文件。

**命令格式**：

~~~
tatarubook export [-h] [--table TABLE] [--encoding ENCODING] db_file
~~~

**参数**：
- `--table TABLE`（可选）：指定名字为`TABLE`的表或视图。如果没有这个参数，导出所有的表和视图。
- `--encoding ENCODING`（可选）：指定字符编码。见[字符编码格式]({{ site.baseurl }}/commands_cn.html#字符编码格式)中的说明。
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。

生成文件名的规则：对应表/视图的名字加上`.csv`后缀。如果遇到某个文件已经存在，则会**跳过**这个文件，但仍会导出其他没有冲突的文件（如果存在的话）。

## insert

插入指定表的一条记录（通常是一条，除非触发[自动插入关联表的记录]({{ site.baseurl }}/commands_cn.html#自动插入关联表的记录)功能）。

**命令格式**：

~~~
tatarubook insert [-h] db_file table values
~~~

**参数**：
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。
- `table`：表名。
- `values`：所有字段的值，字段之间以空格分隔。如果某个字段中含有空格，需要用引号括起来。

插入操作有一些特殊的处理，见[通用特性]({{ site.baseurl }}/commands_cn.html#通用特性)中的说明。

## import

使用csv文件批量导入（新增）指定表的一批记录，表中已经存在的记录不受影响。

**命令格式**：

~~~
tatarubook import [-h] [--table TABLE] [--encoding ENCODING] db_file csv_file
~~~

**参数**：
- `--table TABLE`（可选）：指定名字为`TABLE`的表。如果没有这个参数，则根据`csv_file`的文件名判断导入哪个表。
- `--encoding ENCODING`（可选）：指定字符编码。见[字符编码格式]({{ site.baseurl }}/commands_cn.html#字符编码格式)中的说明。
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。
- `csv_file`：csv文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。

TataruBook会自动判断csv文件有没有标题行，判断方式是：如果csv的第一行所有列都不是数字，那么就认为是标题行。注意：TataruBook只判断并跳过标题行，不会根据标题行的内容来调整字段顺序。字段顺序必须和表定义一致。

如果在插入某条记录时处理失败，那么TataruBook会执行**回滚**，整个db文件会被还原到执行这条`import`命令之前的状态，即使csv文件中其他记录可以插入成功，也不会被插入。

导入操作有一些特殊的处理，见[通用特性]({{ site.baseurl }}/commands_cn.html#通用特性)中的说明。

## overwrite

把指定表的所有内容删除，然后插入一条记录。这个命令只适用于仅含一个字段的表：[start_date]({{ site.baseurl }}/tables_and_views_cn.html#start_date)、[end_date]({{ site.baseurl }}/tables_and_views_cn.html#end_date)、[standard_asset]({{ site.baseurl }}/tables_and_views_cn.html#standard_asset)。

**命令格式**：

~~~
tatarubook overwrite [-h] db_file table content
~~~

**参数**：
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。
- `table`：表名，必须是`start_date`、`end_date`、`standard_asset`之一。
- `content`：插入的唯一一条记录的唯一字段的内容。

这个命令可看作是对仅含一个值的表的快捷修改方式。

## delete

删除指定表指定索引的一条记录。

**命令格式**：

~~~
tatarubook delete [-h] db_file table values
~~~

**参数**：
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。
- `table`：表名。
- `values`：指定的索引值。如果索引包含了多个字段，字段之间以空格分隔。如果某个字段中含有空格，需要用引号括起来。

注意`delete`命令输入的`values`只含索引字段的值，不要输入所有字段。

当删除`postings`表的记录时，如果有与之对应的`posting_extras`表记录，那么`posting_extras`表中的这条记录也会被一并删除。

## prune

删除指定表中由csv文件给出的一个或多个索引对应的一批记录。

**命令格式**：

~~~
tatarubook prune [-h] [--table TABLE] [--encoding ENCODING] db_file csv_file
~~~

**参数**：
- `--table TABLE`（可选）：指定名字为`TABLE`的表。如果没有这个参数，则根据`csv_file`的文件名判断操作哪个表。
- `--encoding ENCODING`（可选）：指定字符编码。见[字符编码格式]({{ site.baseurl }}/commands_cn.html#字符编码格式)中的说明。
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。
- `csv_file`：csv文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。

TataruBook会自动判断csv文件有没有标题行，判断方式是：如果csv的第一行所有列都不是数字，那么就认为是标题行。注意：TataruBook只判断并跳过标题行，不会根据标题行的内容来调整索引字段的顺序。索引字段的顺序必须和表定义一致。

注意csv文件中每一行只含索引字段的值，不要包含其他的字段。

当删除`postings`表的记录时，如果有与之对应的`posting_extras`表记录，那么`posting_extras`表中的这条记录也会被一并删除。

如果在删除某个索引时处理失败，那么TataruBook会执行**回滚**，整个db文件会被还原到执行这条`prune`命令之前的状态，即使csv文件中其他索引可以删除成功，也不会被删除。

## execsql

执行自定义的SQL命令。

**命令格式**：

~~~
tatarubook execsql [-h] db_file cmd
~~~

**参数**：
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。
- `cmd`：SQL命令字符串，需要在这个参数两侧加上引号。

TataruBook不对SQL命令进行任何检查和约束，执行自定义的SQL命令所造成的后果由用户自己负责。如果SQL命令修改了表/视图的定义，可能导致这个db文件以后无法再被TataruBook正确处理。

由于TataruBook没有查询命令，如果想在命令行直接查询某个表/视图的内容（而不是导出到csv文件），可以使用`execsql`命令来完成。比如，下面这条命令可以查询`statements`视图的内容：

~~~
tatarubook execsql example.db "select * from statements"
~~~

## upgrade

这是v1.1版本新增的命令。
{: .notice}

尝试将db文件中所有的表、索引、视图定义修改为与当前版本一致。

**命令格式**：

~~~
tatarubook upgrade [-h] db_file
~~~

**参数**：
- `db_file`：db文件名，可带路径。如果路径和文件名中有空格，需要在这个参数两侧加上引号。

通常db文件的表、索引、视图定义与当前版本不一致是由于TataruBook软件升级导致的。如果TataruBook软件和db文件的表、索引、视图定义不一致，可能在操作时出现无法预知的错误。建议每次TataruBook升级以后，先用`upgrade`命令修改db文件与当前版本一致。

如果db文件中存在表、索引的定义在当前TataruBook中不存在，或者与TataruBook中的定义不一致，则`upgrade`命令会拒绝升级并报告错误。因为如果删除或者修改这些表、索引定义，可能会造成用户数据丢失。通常TataruBook软件升级时只会修改视图的定义而不会修改表、索引的定义。

强烈建议在使用`upgrade`命令之前备份db文件。
{: .notice--warning}