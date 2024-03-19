---
title: 文档使用说明
---
这是TataruBook的帮助文档。

# TataruBook是什么？

TataruBook是一个使用复式记账方式的、基于SQL表和视图的、以命令行方式执行的、面向个人或家庭的记账和理财收益计算工具。用户把资产、账户、明细等数据输入工具后，工具可计算出总资产、各项开支统计、投资收益率等各种数据。

# 如何下载和安装TataruBook？

有2种方式：

1. （推荐）首先安装[Python 3.8或以上版本](https://www.python.org/downloads/)，然后从[Github仓库](https://github.com/Goalsum/TataruBook)上下载tatarubook.py文件，之后使用`python tatarubook.py`运行该脚本即可。这种方式可用于任何安装了Python的操作系统。
1. 从[发布页面](https://github.com/Goalsum/TataruBook/releases)下载tatarubook.zip包，解压缩到任何一个文件夹，然后运行其中的tatarubook.exe程序。这种方式不需要安装Python，但是只适用于Windows 10或以上版本的Windows操作系统。

第一种方式是推荐的，因为采用这种方式的tatarubook.py运行脚本直接使用系统中最新的Python解释器、SQLite等依赖库，占用的磁盘空间极小。如果用第二种方式，则Python解释器、SQLite以及其他依赖的Python库都会被下载并占用磁盘空间，但好处是如果系统中这些库缺失或者有问题，不会影响tatarubook软件的运行。

**注意：**采用第二种方式使用软件时，切勿修改、删除或移动tatarubook.zip包解压后所在目录中的任何一个文件（包括除tatarubook.exe以外的文件），这些文件都是程序运行所需要依赖的。
{: .notice--warning}

# 如何使用TataruBook进行记账？

你需要先了解一些概念：

TataruBook只是一个程序（严格的说，是一个Python脚本），它自身并不包含任何财务数据，所有的数据都被保存在由用户管理的xxx.db文件中（文件名由用户自己指定）。TataruBook可以对用户指定的xxx.db文件进行操作，且TataruBook的大多数命令都需要指定一个db文件名作为参数。

## 什么是db文件？

db文件是保存了用户记账数据的文件。每个db文件都是SQLite格式的数据库文件，可以使用任何支持SQLite数据文件格式的软件进行查看和修改。

如果使用其他软件来打开TataruBook生成的db文件，请确保这些软件支持SQLite的一些新特性（如STRICT表）。例如：若要使用[DB Browser for SQLite](https://sqlitebrowser.org/)来打开db文件，则必须用它的[nightly版本](https://nightlies.sqlitebrowser.org/latest/)才能支持STRICT表。
{: .notice}

**注意：**使用其他软件（非TataruBook）修改db文件时，只能添加、删除、修改记录，不可修改表和视图的定义！否则，TataruBook将无法保证正确操作这个db文件。
{: .notice--warning}

## 我该从哪儿开始？

在开始上手使用TataruBook之前，我推荐你先阅读[表和视图]({{ site.baseurl }}/table_view.html)文档。这篇文档介绍了db文件中所有的表和视图，以及它们之间的关系。你需要先对几个基本的表有所了解，才能正确的输入记账数据。

如果你觉得自己对需要用到的表结构已经理解得差不多了，那么可以阅读[命令行手册]({{ site.baseurl }}/commands.html)文档，并使用其中的命令来操作自己的数据库文件。

对于已经充分理解了db文件中的表和视图，并且会使用SQL语言的高级用户，你可以使用除TataruBook之外的其他软件来打开db文件，自己编写SQL语句进行任意查询和编辑（但是切记不要修改表和视图的定义）。

# 如何反馈问题和需求？

请在[Github仓库](https://github.com/Goalsum/TataruBook)上提交issue，我会查看并进行回复。
