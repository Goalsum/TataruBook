![](https://raw.githubusercontent.com/Goalsum/TataruBook/main/docs/assets/images/overview.png)

# TataruBook

TataruBook is a bookkeeping software for individuals or families, which is able to record daily income and expenditure as well as investment transactions in an unlimited number of accounts, supporting any variety of currencies, stocks, funds, futures, and other asset types customized by the user, and generating a variety of statistical reports based on the raw data, such as: the status of assets in all accounts on a specified date; categorized statistics of income and expenditure within a specified period; the overall return on investment, contribution of each investment, interest gains and so on.

TataruBook has the following features:

- **Flexible and customizable**: TataruBook's data model does not depend on any specific currency, asset type, income and expenditure type, and users can use it to record any physical and virtual assets. In addition to common assets such as cash, stocks, funds, futures, etc., TataruBook can even be used to record transactions related to real estate, digital currencies, personal loans, etc., and all of them can be converted to the specified home currency in the report. This makes TataruBook ideal for managing the overall asset position of an individual or family.
- **Data accuracy and reliability**: TataruBook adopts **double-entry bookkeeping**, which inherently avoids the problem of data inconsistency when transferring money between different accounts, and also uses a lot of checking rules to ensure the consistency and completeness of the data. TataruBook operates the data in a transactional form, and rolls back the data as soon as an error is detected during batch processing, avoiding data anomalies caused by operational errors. TataruBook allows users to verify the calculation process of each report by presenting the intermediate calculation process in views. Users can verify the correctness of data from multiple perspectives.
- **Open and extensible**: All data and reports in TataruBook are stored in db files in the **SQLite** format, one of the most widely used database formats in the world, and supported by a wide range of software. Users can not only manipulate db files with TataruBook, but also use other graphical interface software such as **DB Browser for SQLite** to view and edit their data. Users can also write their own SQL query statements to generate reports that are not provided by TataruBook, or write scripts to batch process data (almost all major programming languages have libraries that support the operation of SQLite data files). All data and reports of TataruBook can be exported to CSV files and edited in Excel, which makes it easy to convert data and interoperate between different software.
- **Easy to use**: TataruBook has a detailed documentation, all the tables, views, fields, commands are explained in the documentation. The documentation also provides quick start tutorials and rich examples to help new users learn how to use TataruBook. TataruBook has a number of auxiliary features that allow users to enter data in a more intuitive way, avoiding the tediousness of manually manipulating data in SQLite tables.
- **High performance**: Although TataruBook is written in Python, all reports are implemented as SQLite views, so most of the calculations are done by the SQLite engine. The SQLite engine is a mature open source software written in C and optimized for many years, so performance is fully guaranteed. TataruBook makes full use of window functions and other features to optimize the query steps when generating reports using SQL query statements, ensuring that all views can be calculated with O(n) time complexity. On the typical data scale of an individual or a family, users will hardly feel the delay caused by the computation of the report.
- **Privacy and security**: TataruBook is **free** and **open source** software, process data locally, **never connects to the internet**. All bookkeeping data and reports are stored in a db file controlled by the user, separated from the TataruBook program. TataruBook relies only on the standard libraries of the Python language and the SQLite engine, both of which are mature open-source software that has been widely used. Therefore, users can have full confidence that their privacy will not be compromised and their data will not be tampered with.

**TataruBook's documentation**: [https://goalsum.github.io/TataruBook/](https://goalsum.github.io/TataruBook/)

**About the name**: **Tataru Taru** (Japanese: **タタル・タル**) is a female Lalafell NPC in the online game **Final Fantasy XIV**, developed by Square Enix. She is the money manager for the Scions of the Seventh Dawn. Tataru is not skilled in combat, but is gifted in finances, with bookkeeping being one of her main interests.

TataruBook是一款面向个人或家庭的记账软件，它能够记录不限数量的账户中的日常收支和投资交易，支持任意多种货币、股票、基金、期货以及其他由用户定制的资产类型，并能根据原始数据生成多种统计报表，如：指定日期的所有账户资产状况；指定周期内的收支分类统计；指定周期内的整体投资收益、各个品种的投资收益、利息收益等等。

TataruBook拥有以下特点：

- **灵活、可定制**：TataruBook的数据模型不依赖任何特定的货币、资产类型、收支类型，用户可用它记录任何实物资产和虚拟资产。除了常见的现金、股票、基金、期货等资产外，TataruBook甚至可用来记录不动产、数字货币、个人借贷等相关交易，而且所有的资产都能在报表中换算为指定的本位币。这使TataruBook非常适合用于管理个人或家庭的整体资产状况。
- **数据准确、可靠**：TataruBook采用**复式记账法**，从根源上避免了不同账户间转账时数据不一致的问题，同时还使用了很多校验规则来保证数据的一致性和完整性。TataruBook以事务的形式操作数据，在批量处理时一旦发现错误会立刻回滚，避免因操作失误导致的数据异常。TataruBook允许用户通过视图核查每项报表数据的计算过程，将中间计算过程透明呈现。用户可以从多种角度验证数据的正确性。
- **开放、可扩展**：TataruBook的所有数据和报表都保存在**SQLite**格式的db文件中。SQLite是世界上使用最为广泛的数据库格式之一，有众多的软件支持这种格式。用户不光可以用TataruBook操作db文件，还可以使用**DB Browser for SQLite**等其他图形界面软件来查看和编辑自己的数据。用户还可以自己编写SQL查询语句来生成TataruBook中没有的报表，或者编写脚本来批量处理数据（几乎所有主流编程语言都有库能支持操作SQLite数据文件）。TataruBook的所有数据和报表都可以导出成csv文件并用Excel编辑，可方便的在不同软件间进行数据转换和互通。
- **易用**：TataruBook拥有详尽的文档，所有表、视图的字段，所有操作命令在文档中都有解释。文档中还提供了快速入门教程和丰富的例子来帮助新用户学习如何使用TataruBook。TataruBook有一些辅助特性让用户能用更直观的方式录入数据，避免手工在SQLite表中操作数据的繁琐。
- **高性能**：虽然TataruBook是用Python语言编写的，但所有报表都是以SQLite视图的方式实现的，所以主要计算都由SQLite的数据引擎完成。而SQLite引擎是采用C语言编写且经过多年优化的成熟开源软件，性能有充分保证。TataruBook在使用SQL查询语句生成报表时，充分利用窗口函数等特性优化查询步骤，确保所有视图都能以O(n)的时间复杂度完成计算。在个人或家庭的典型数据规模上，用户几乎不会感觉到报表的计算带来的延迟。
- **隐私安全**：TataruBook是**免费**、**开源**的软件，所有处理都在本地进行，**不联网**，不需要用户注册账号。所有记账数据及报表都保存在由用户自己控制的db文件中，和TataruBook程序分离。TataruBook只依赖Python语言的标准库和SQLite引擎，而它们都是已被广泛使用的成熟开源软件。因此，用户可充分相信自己的隐私不会被泄露，数据不会被篡改。

**TataruBook的文档**：[https://goalsum.github.io/TataruBook/](https://goalsum.github.io/TataruBook/index_cn.html)

**关于名字**：**Tataru Taru**（中文名：**塔塔露·塔露**、日文名：**タタル・タル**）是由Square Enix公司开发的网络游戏《**最终幻想14**》中的一个拉拉菲尔族女性NPC，拂晓血盟组织的资金管理人。她并不擅长战斗，但是在财务方面天赋卓绝，算账是她的主要兴趣之一。
