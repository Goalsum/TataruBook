---
title: Introduction
---
This is the documentation for TataruBook.

# What is TataruBook?

TataruBook is an individual or family-oriented bookkeeping and financial income calculation tool using [simplified double-entry bookkeeping]({{ site.baseurl }}/tables_and_views.html#simplified-double-entry-bookkeeping), based on SQL tables and views, and executed from the command-line. The tool assists users in entering data such as assets, accounts, and transaction details into a [DB file]({{ site.baseurl }}/index.html#what-is-a-db-file) and calculates various statistics such as net worth, categorized income and expenses, and ROI.

# How to download and install TataruBook?

TataruBook can be used either as an executable program or as a Python script. The two corresponding download and installation approaches are as follows:

## Executable program in Windows 10 or higher version of Windows

Download `tatarubook.zip` package from the [Github release page](https://github.com/Goalsum/TataruBook/releases) or [Gitee release page](https://gitee.com/goalsum/tatarubook/releases), extract it to any folder, and run the `install.bat` script to install (you may be asked to grant administrator privileges during the installation process). Once the installation is complete, you can use the features of TataruBook via the right-click context menu in File Explorer.

The `install.bat` will only modify the registry to add the context menu items, it will not add files to any system directory. If you move the location of the TataruBook program folder, you will need to re-run `install.bat`. By running `uninstall.bat` you can remove all the added context menu items.
{: .notice}

**NOTICE:** The `tatarubook.exe` file in the zip file is for command-line invocation only, do not try to double-click on it to run this file directly. TataruBook depends on several other files to run, so be sure to unzip all of the files in `tatarubook.zip` in the same directory, and keep the directory structure as is.
{: .notice--warning}

## Python script

If you have Python 3.8 or higher version installed on your system, then you can also download the `tatarubook.py` source file from the [Github repository](https://github.com/Goalsum/TataruBook) or [Gitee repository](https://gitee.com/goalsum/tatarubook), and then run `tatarubook.py` script with the Python interpreter to use TataruBook's bookkeeping functions.

This approach only requires downloading a very small script file, needs neither unzipping nor installation, and can be run on any operating system. But by this approach TataruBook can only be used through command-line. The first approach is recommended for those using Windows 10 or higher version to gain the convenience of context menu operations.

# How to use TataruBook for bookkeeping?

You need to understand some concepts first:

TataruBook is just a program, it doesn't contain any financial data itself, all the data is stored in **DB files**, which are files named by the user and have the suffix `.db`. TataruBook can operate on the DB file specified on the command-line.

## What is a DB file?

A DB file is a file that holds financial data and related reports. Each DB file is a [SQLite format](https://sqlite.com/) database file that can be viewed and modified using any software that supports the SQLite file format.

**NOTICE:** When using other software to modify the DB file, you can only add, delete, and modify records, you cannot modify the table and view definitions! Otherwise, TataruBook will not be able to guarantee that it will be able to operate this DB file correctly in the future.
{: .notice--warning}

Typically, all the historical financial data of a user or family/organization is placed in the same DB file. DB file has some reports that will consider all the internal accounts in that DB file as a **portfolio** and show the net worth, rate of return, and inflows and outflows of that portfolio. Therefore, it is expected that the account data involved in the statistics should all be in the same DB file. TataruBook does not support calculations across DB files.

Some users are accustomed to splitting financial data by time period, such as putting each year's financial data in a separate DB file. There is no need to do this when using TataruBook, because TataruBook supports displaying financial statements for any specified time period (down to the day). Storing all historical financial data in a single DB file maintains a consistent and accurate financial record and eliminates the need to carry forward balances for each account when creating a new DB file.

## Where do I start?

For first time users of TataruBook, we recommend reading [quick start]({{ site.baseurl }}/quick_start.html). This tutorial helps new users to quickly grasp the main usage of TataruBook by going from simple to deep use cases.

[Tables and views]({{ site.baseurl }}/tables_and_views.html) describes all the tables and views in the DB file and how they are related to each other. When you have questions about certain table or view fields, refer to this document.

[User manual]({{ site.baseurl }}/commands.html) describes all the command usage and notes of TataruBook.

If you feel that the existing views in the DB file are not enough for you and you know how to use the SQL language, you can use other software that supports the SQLite format (make sure that they support some of the new features of SQLite) to open the DB file and write your own SQL statements to query and edit the data (but do not modify the definitions of the existing tables and views).

For investors, the return on investment is of great interest, and TataruBook has several views that present the return on investment from various perspectives. [Rate of return]({{ site.baseurl }}/rate_of_return.html) describes in detail how the various rates of return are calculated and how they are used in TataruBook's views.

How to improve the efficiency of importing external data is a key challenge in actual bookkeeping, [Data importing guide]({{ site.baseurl }}/importing_data.html) gives efficient data processing and importing s for reference.

# How do I give feedback on issues and requirements?

Please submit an issue on [Github repository](https://github.com/Goalsum/TataruBook) or [Gitee repository](https://gitee.com/goalsum/tatarubook) and I'll check it out and respond.
