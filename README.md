# TataruBook

TataruBook是一款面向个人或家庭的记账软件，其使用简洁而灵活的数据模型，能够记录不限数量的账户中的资产和负债，以及在各个账户中产生的日常收支和投资交易。TataruBook支持任意多种货币、股票、基金、期货以及其他由用户定制的任何资产类型，并能根据原始数据计算多种统计报表，如：指定日期的所有账户资产状况；指定周期内的收支分类统计；指定周期内的整体投资收益、各个品种的投资收益、利息收益等等。

TataruBook还拥有以下特点：

- **数据准确、可靠**：TataruBook采用**复式记账法**，从根源上避免了不同账户间转账时数据不一致的问题，还应用了很多校验规则来保证数据的一致性和完整性。TataruBook以事务形式录入数据，一旦发现错误会立刻回滚，保证数据总是处于一致状态。TataruBook允许用户通过视图核查每项报表数据的计算过程，使得数据的中间计算过程都能透明呈现，最大程度打消对数据正确性的担忧。
- **开放可扩展**：TataruBook的所有数据和报表都保存在**SQLite**格式的db文件中。SQLite是世界上应用最为广泛的数据库格式之一，被众多的软件支持。用户不光可以用TataruBook操作db文件，还可以使用**DB Browser for SQLite**等其他图形界面软件来查看和编辑自己的数据，甚至可以使用多种编程语言开发数据处理脚本。TataruBook的所有数据和报表都可以导出成csv文件并用Excel编辑，实现各种工具间的数据互通和转换。
- **易用**：TataruBook拥有详尽的文档，所有表、视图的字段和每条命令在文档中都有解释。文档中还提供了快速入门教程和丰富的例子来帮助新用户学习如何使用。在录入数据时，TataruBook的辅助特性让用户能用更直观的方式描述记录，避免了手工在SQLite表中操作数据的繁琐和易错。
- **高性能**：虽然TataruBook是用Python语言编写的，但由于所有报表都是以SQLite视图的方式实现的，所以主要计算都由SQLite的数据引擎完成。SQLite引擎是采用C语言编写且经过多年优化的成熟软件，性能有充分保证。TataruBook在设计报表使用的SQL查询语句时，充分利用窗口函数等特性精心优化查询步骤，确保所有视图都能以O(n)的时间复杂度完成计算。对于个人或家庭的典型数据规模，用户几乎不会感觉到报表的计算带来的延迟。
- **隐私安全**：TataruBook是**免费**、**开源**的软件，全程只在本地运行，**不联网**，不需要用户注册账号。所有记账数据都保存在由用户自己控制的db文件中，和TataruBook程序分离。TataruBook软件运行只依赖Python语言的标准库和SQLite引擎，这些被依赖的软件全部是已被广泛使用的成熟开源软件。因此，用户可充分相信自己的隐私不会被泄露，数据不会被窥视或篡改。

**TataruBook的文档**：[https://goalsum.github.io/TataruBook/](https://goalsum.github.io/TataruBook/)

**关于名字**：**Tataru Taru**（中文名：**塔塔露·塔露**、日文名：**タタル・タル**）是由SQUAR ENIX公司开发的网络游戏《**最终幻想14**》中的一个拉拉菲尔族女性NPC。她并不擅长战斗，但是在财务方面天赋卓绝。作为拂晓血盟组织的资金管理人，算账是她的主要兴趣之一。
