---
title: 总体介绍
---
这是TataruBook的帮助文档。

# TataruBook是什么？

TataruBook是一个使用[简化的复式记账法]({{ site.baseurl }}/tables_and_views.html#简化的复式记账法)的、基于SQL表和视图的、以命令行方式执行的、面向个人或家庭的记账和理财收益计算工具软件。该工具可辅助用户把资产、账户、交易明细等数据输入[db文件]({{ site.baseurl }}/index.html#什么是db文件)，并计算出净资产、分类收入支出、投资收益率等各种统计数据。

# 如何下载和安装TataruBook？

有2种方式：

1. （推荐）首先安装[Python 3.8或以上版本](https://www.python.org/downloads/)，然后从[Github仓库](https://github.com/Goalsum/TataruBook)或者[Gitee仓库](https://gitee.com/goalsum/tatarubook)上下载`tatarubook.py`脚本，之后使用`python tatarubook.py`运行该脚本即可。这种方式可用于任何能够支持Python的操作系统。
1. 从[Github发布页面](https://github.com/Goalsum/TataruBook/releases)或者[Gitee发布页面](https://gitee.com/goalsum/tatarubook/releases)下载`tatarubook.zip`包，解压缩到任何一个文件夹，然后运行其中的`tatarubook.exe`程序。这种方式不需要安装Python，但是只适用于Windows 10或以上版本的Windows操作系统。

第一种方式是推荐的，因为采用这种方式的`tatarubook.py`运行脚本直接使用运行环境中最新的Python解释器、SQLite等依赖库，占用的磁盘空间极小。如果用第二种方式，则Python解释器、SQLite以及其他依赖的Python库都会被下载并占用磁盘空间，但好处是如果运行环境中这些库缺失或者有问题，不会影响TataruBook软件的运行。

**注意：**采用第二种方式安装软件后，`tatarubook.exe`程序运行时需要依赖压缩包中的其他文件。因此，请确保在同一目录解压`tatarubook.zip`中的所有文件，且保持压缩包里的目录结构。
{: .notice--warning}

# 如何使用TataruBook进行记账？

你需要先了解一些概念：

TataruBook只是一个程序（严格地说，是一个Python脚本），它自身并不包含任何财务数据，所有的数据都被保存在**db文件**中，db文件是由用户命名且后缀名为`.db`的文件。TataruBook可以对命令行中指定的db文件进行操作。

## 什么是db文件？

db文件是保存了财务数据和相关报表的文件。每个db文件都是[SQLite格式](https://sqlite.com/)的数据库文件，可以使用任何支持SQLite文件格式的软件进行查看和修改。

如果使用其他软件来查看和修改TataruBook生成的db文件，请确保这些软件支持SQLite的一些新特性（如STRICT属性）。例如：若要使用[DB Browser for SQLite](https://sqlitebrowser.org/)来打开db文件，则必须用`DB Browser for SQLite`的[nightly版本](https://nightlies.sqlitebrowser.org/latest/)才能支持STRICT属性。
{: .notice}

**注意：**使用其他软件修改db文件时，只能添加、删除、修改记录，不可修改表和视图的定义！否则，TataruBook将无法保证以后还能正确操作这个db文件。
{: .notice--warning}

通常来说，一个用户或家庭/组织的所有历史财务数据都放在同一个db文件中。db文件中有一些报表会把该db文件中所有的内部账户看作一个**投资组合（portfolio）**，并展示这个投资组合的净资产、收益率和资金流入流出情况。因此，希望参与统计的账户数据都应当放在同一个db文件中，TataruBook不支持跨db文件进行计算。

有些用户习惯于按时间周期分割财务数据，比如把每一年的财务数据放在一个独立的db文件中。使用TataruBook时没有必要做这种分割，因为TataruBook支持展示任意历史时间段（精确到天）的财务报表。把所有历史财务数据存放在一个db文件中可以保持连贯而准确的财务记录，省去新建db文件时需要导入每个账户历史余额的麻烦。

## 我该从哪儿开始？

对于第一次使用TataruBook的用户，推荐阅读[快速入门]({{ site.baseurl }}/quick_start.html)。这篇教程通过由浅入深的使用案例帮助新用户快速掌握TataruBook的主要用法。

[表和视图]({{ site.baseurl }}/tables_and_views.html)介绍了db文件中所有的表和视图，以及它们之间的关系。当你对某些表或视图的字段有疑问时，可参阅此文档。

[命令行手册]({{ site.baseurl }}/commands.html)介绍了TataruBook的所有命令用法和注意事项。

如果你觉得db文件中的现有视图还不能满足自己，并且你知道如何使用SQL语言，那么，你可以使用其他支持SQLite格式的软件（需确保这些软件支持SQLite的一些新特性）来打开db文件，并自己编写SQL语句对数据进行查询和编辑（但是不要修改已有表和视图的定义）。

对于投资者来说，投资收益率是倍受关注的。TataruBook中有多个视图从各个角度呈现投资收益率。[收益率计算方法]({{ site.baseurl }}/rate_of_return.html)中详细介绍了各种收益率的计算方法，以及其在TataruBook的视图中是如何被使用的。

# 如何反馈问题和需求？

请在[Github仓库](https://github.com/Goalsum/TataruBook)或者[Gitee仓库](https://gitee.com/goalsum/tatarubook)上提交issue，我会查看并进行回复。
