---
title: 命令行手册
---
本页介绍工具支持的所有命令及选项。

TataruBook命令行有[两种用法]({{ site.baseurl }}/index.html#如何下载和安装tatarubook)，为了简便起见，本页都以可执行文件用法为示例。如果采用的是Python脚本用法，则需要将所有命令开头从`tatarubook`换成`python tatarubook.py`。比如，创建一个名为`example.db`的数据库文件，需要将`tatarubook init example.db`命令改为`python tatarubook.py init example.db`。

# 通用特性

下面介绍一些和多个命令都有关的特性：

## 字符编码格式

默认设置下，TataruBook使用操作系统默认字符编码格式读写文件。但是注意非英文Windows操作系统的默认字符编码格式不是UTF-8，因此在Windows下读取UTF-8格式的csv文件时，TataruBook可能会遇到解码错误。为了解决这个问题，TataruBook在用其他格式解码失败时，会再尝试使用UTF-8解码一次。

如果想要TataruBook使用其他的字符编码格式读写文件，可以在相关命令中使用`--encoding`选项指定字符编码格式。

## 根据名字查找索引

当一张表的某条记录引用另一张表的某条记录时，根据数据库的设计原则，引用的是记录的**索引（index）**。但是人工输入索引是比较麻烦且容易出错的。举个例子：如果[accounts表]({{ site.baseurl }}/tables_and_views.html#accounts)的内容如下：

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | 萨雷安银行活期 | 1 | 0 |
| 2 | 餐饮消费 | 1 | 1 |

现在想在[postings表]({{ site.baseurl }}/tables_and_views.html#postings)中插入一条记录，表示从`萨雷安银行活期`账户产生了一笔`餐饮消费`的记录，这条记录事实上是这样：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-07 | 1 | -67.5 | 2 | 背水咖啡厅晚餐 |

但是，手工编写这条记录时，需要查找到`萨雷安银行活期`的`account_index`为`1`，并填写到`src_account`字段中；查找到`餐饮消费`的`account_index`为`2`，并填写到`dst_account`字段中。这个查找过程是很麻烦的——尤其当`accounts`表有几十条以上的记录时。

为了解决这个问题，TataruBook允许在某些需要填写索引的地方直接填写名字。比如要插入上面这条`postings`表的记录，可以在csv文件中写成这样：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-01-07 | 萨雷安银行活期 | -67.5 | 餐饮消费 | 背水咖啡厅晚餐 |

然后用import命令导入。TataruBook会自动去查找`accounts`表中哪条记录的`account_name`为`萨雷安银行活期`，哪条记录的`account_name`为`餐饮消费`，并把这两条记录的`account_index`填到对应的地方。

不光import命令支持这个功能，insert命令也支持这个功能。上面的这条记录也可以直接用一条命令插入：

`tatarubook insert example.db postings NULL 2023-01-07 萨雷安银行活期 -67.5 餐饮消费 背水咖啡厅晚餐`

TataruBook对于支持的字段，根据名字查找索引的具体规则如下：

1. 首先把字段内容看成是**索引**，如果该索引对应的记录存在，那么直接用这个索引值不做转换。即：如果存在一条记录的索引是`666`，那么输入的`666`会被直接解释为索引——即使其他记录中存在**名字**是`666`的，也会被忽略。
1. 如果该索引对应的记录不存在，那么查找名字**等于或者包含**字段内容的唯一记录。如果找到了，把字段内容转换为这条记录的索引。这个过程如上面例子所示。
1. 如果没有记录的名字等于或者包含该字段内容，或者找出的记录不止一条，那么执行失败并报错。举例：如果存在两条`accounts`表记录的名字分别为`萨雷安银行活期`和`萨雷安养老金`，那么当查找字段内容为`萨雷安`时会报错，因为TataruBook无法确定对应的是哪个索引。

下面列出了支持根据名字查找索引功能的所有字段：

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

# 命令使用方法