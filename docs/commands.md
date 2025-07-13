---
title: User Manual
---
This page describes all the commands supported by TataruBook.

# Command-line and context menu

TataruBook is a command-line based program, but can be invoked by right-click context menu items in Windows 10 or higher version. Each context menu item is just an encapsulation of a specific command: when you right-click a DB file and select a context menu item, TataruBook automatically invokes the corresponding command-line and fills in parameters such as file name, table name, and so on. Therefore, if you want to see the explanation of an item in the context menu, just check the corresponding command's explanation.

The following is a list of commands that can be invoked from the context menu. Commands outside the list can only be invoked from the command-line.

| Trigger Method | Context Menu Item | Corresponding Command |
|:-:|:-:|:-:|
| Right-click on the background of a folder's content | TataruBook create DB file | [init]({{ site.baseurl }}/commands.html#init) |
| Right-click on a DB file | TataruBook check | [check]({{ site.baseurl }}/commands.html#check) |
| Right-click on a DB file | TataruBook export table | [export]({{ site.baseurl }}/commands.html#export) |
| Right-click on a DB file | TataruBook export view | [export]({{ site.baseurl }}/commands.html#export) |
| Right-click on a DB file | TataruBook paste | [paste]({{ site.baseurl }}/commands.html#paste) |
| Right-click on a DB file | TataruBook upgrade | [upgrade]({{ site.baseurl }}/commands.html#upgrade) |

Windows 11 will hide some context menu items by default, you need to specify to show all menu items if you can't find some ones.
{: .notice}

There are two [installation approaches]({{ site.baseurl }}/index.html#how-to-download-and-install-tatarubook) for TataruBook, which correspond to two command-line usages: **Python script usage** and **executable file usage**. For the sake of simplicity, executable file usage is used in examples on this page. If you are using Python script, you need to change the beginning of all commands from `tatarubook` to `python tatarubook.py` (assuming that your Python interpreter can be invoked by `python`). For example, to create a database file named `example.db`, change the `tatarubook init example.db` command to `python tatarubook.py init example.db`.

# General Features

The following describes some features that are relevant to multiple commands:

## Character encoding format

By default, TataruBook reads and writes files using the operating system's default character encoding format. However, note that the default character encoding format for a non-English Windows operating system is not UTF-8, so TataruBook may encounter decoding errors when reading UTF-8 CSV files on Windows. To work around this problem, TataruBook will try to decode in UTF-8 again when decoding in default format fails.

If you want TataruBook to read and write files using other character encoding formats, you can specify the character encoding format using the `--encoding` option in the relevant command; a list of supported encoding formats can be found [here](https://docs.python.org/3/library/codecs.html#standard-encodings).

## Automatically generated index fields

There are some fields whose values are automatically generated on insertion, such as `account_index` in [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table, `posting_index` in [postings]({{ site.baseurl }}/tables_and_views.html#postings) table, etc. When inserting records into these tables with the [insert]({{ site.baseurl }}/commands.html#insert) command, the value of these fields should be filled in as `NULL`; with the [import]({{ site.baseurl }}/commands.html#import) or [paste]({{ site.baseurl }}/commands.html#paste) command When importing records, the content of the cell corresponding to this field should be empty. This way, TataruBook will automatically find a new index value which is different from the other records to fill in this field.

## Input format of date 

When entering a date, TataruBook requires that a date contains and only contains three members: year, month, and day, and that the members are listed in the order of year, month, and day. The members can be separated by any of the three characters: `/`, `-`, `.`, but the separators must be consistent. The year must be a 4-digit number, the month and day may be 1-digit or 2-digit numbers, with or without leading zeros.

There can also be no separators in between year and month, month and day, but in this case the entire date must be strictly 8 digits in the form `yyyymmdd`.

The following date formats are all legal: `2023/5/3`, `2023-5-3`, `2023.5.3`, `2023-05-03`, `2023/5/03`, `20230503`.

The following date formats are all illegal: `2023-5/3` (separators are inconsistent), `23-05-03` (the year is not a 4-digit number), `2023053` (no separators but not an 8-digit number).

## Lookup index by name

When a record in one table references a record in another table, according to database design principles, the reference is to the record's **index**. But manually enter the index is more cumbersome and error-prone. For example: If the contents of [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table are as follows:

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | Sharlayan Bank current | 1 | 0 |
| 2 | Food and Beverages | 1 | 1 |

Now we want to insert a record into the [postings]({{ site.baseurl }}/tables_and_views.html#postings) table indicating a `Food and Beverage` spending on the `Sharlayan Bank current` account, which in fact looks like this:

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-07 | 1 | -67.5 | 2 | Dinner at the Last Stand |

However, writing this record requires manually finding the `account_index` of the `Sharlayan Bank current` to be `1` and filling that in the `src_account` field, and finding the `account_index` of the `Food and Beverages` to be `2` and filling that in the `dst_account` field. This lookup process is cumbersome - especially when the `accounts` table has dozens of records.

To solve this problem, TataruBook allows filling in **names** in certain places where indexes need to be filled in. For example, to insert the above record into the `postings` table, you can write it as this (if you don't understand why the cell below `posting_index` is empty, see [automatically generated index fields]({{ site.baseurl }}/commands.html#automatically-generated-index-fields)):

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-01-07 | Sharlayan Bank current | -67.5 | Food and Beverages | Dinner at the Last Stand |

When inserting this record, TataruBook will automatically find which record in the `accounts` table has `account_name` as `Sharlayan Bank current`, which record has `account_name ` as `Food and Beverages` and populate the corresponding field with the `account_index` of those two records.

This feature is applied not only by [import]({{ site.baseurl }}/commands.html#import) and [paste]({{ site.baseurl }}/commands.html#paste) command, but also by [insert]({{ site.baseurl }}/commands.html#insert) command. The record above can also be inserted directly with a single command:

~~~
tatarubook insert example.db postings NULL 2023-01-07 "Sharlayan Bank current" -67.5 "Food and Beverages" "Dinner at the Last Stand"
~~~

The specific rules for TataruBook to look up an index by name are as follows:

1. First consider the field content as **index**, if the record corresponding to this index exists, then directly use this index value without conversion. For example, if there exists a record with an index of `666`, then the entered `666` will be interpreted directly as an index - even if there are other records with a **name** that is `666`, they will be ignored.
1. if the record corresponding to that index does not exist, then look for a **unique** record with a name **equal to or containing the contents of the** field. If found, convert the field contents to the index of this record. This process is demonstrated in the examples above in this section.
1. If there is no record with a name equal to or containing the contents of the field, or if more than one record is found, then execution fails and an error is reported. For example, if there are two `accounts` table records with the names `Sharlayan Bank current` and `Sharlayan workplace pension`, then an error is reported when the lookup field content is `Sharlayan` because TataruBook cannot determine which index corresponds to it.

Below is a list of all fields that support filling in name instead of the index, as well as the table and fields involved in the automatical lookup for that index:

| Tables | Fields | Referenced Tables | Name Field | Index Field |
|:-:|:-:|:-:|:-:|:-:|
| postings | src_account | accounts | account_name | account_index |
| postings | dst_account | accounts | account_name | account_index |
| interest_accounts | account_index | accounts | account_name | account_index |
| accounts | asset_index | asset_types | asset_name | asset_index |
| prices | asset_index | asset_types | asset_name | asset_index |
| standard_asset | asset_index | asset_types | asset_name | asset_index |

It is highly recommended that you fill in the name instead of the index when inserting a record. This practice greatly reduces the likelihood of errors.
{: .notice}

## Automatically insert into the associated table

A records of the [posting_extras]({{ site.baseurl }}/tables_and_views.html#posting_extras) table is almost always inserted at the same time with the insertion of the corresponding record of the [postings]({{ site.baseurl }}/tables_and_views.html#postings) table - because they describe the same transaction. So when adding a transaction, you need to first insert a record into the `postings` table, then query the `posting_index` of the record you just inserted, then create a record with this `posting_index`, and finally insert the latter record into the `posting_extras` table.

This process is obviously cumbersome. To simplify the insertion of transaction records, TataruBook supports **automatically inserting into the associated table**. When inserting a record into the `postings` table, if you write an extra field at the end, TataruBook assumes that this is a request to insert into the `posting_extras` table, and that the extra field is the value of the `dst_change` field of the `posting_extras` table.

For example: either inserting a record like the one below with [paste]({{ site.baseurl }}/commands.html#paste) command, or importing a CSV file like the one below with [import]({{ site.baseurl }}/commands.html#import) command will inserts a record into both the `postings` table and the `posting_extras` table with the same `posting_index` for both records. (If you don't understand why the values of `src_account` and `dst_account` are not numbers, see [lookup index by name]({{ site.baseurl }}/commands.html#lookup-index-by-name); if you don't understand why the cells below `posting_index` are empty, see [automatically generated index fields]({{ site.baseurl }}/commands.html#automatically-generated-index-fields))

| posting_index | trade_date | src_account | src_change | dst_account | comment | dst_change |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-05-22 | Sharlayan Bank current | -10000 | Garlond Ironworks shares | Buy shares | 500 |

The [insert]({{ site.baseurl }}/commands.html#insert) command also supports this function, and the same effect can be achieved with the following command:

~~~
tatarubook insert example.db postings NULL 2023-05-22 "Sharlayan Bank current" -10000 "Garlond Ironworks shares" "Buy shares" 500
~~~

Note that the `dst_change` field must be placed at the end. TataruBook only recognizes fields based on position, it doesn't care about the contents of the header row.

The [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table also supports associative insertion: if a record of `accounts` table as well as an associated record of `asset_types` table both needs to be inserted, the two records can be inserted using a single command, with the following content:

| account_index | account_name | asset_index | is_external | asset_name | asset_order |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | Moogle:Garlond Ironworks shares | | 0 | Garlond Ironworks shares | 0 |

This scenario is common when buying a new fund/stock, where a new asset and a new account needs to be added at the same time.

# Command Usage

## help

Command help information is given when using the `-h` or `--help` parameter. There are two cases:

1. when there are no subcommands (e.g., enter `tatarubook -h`), a brief description of the function of all other commands is listed.
1. When there is a subcommand (e.g., enter `tatarubook insert -h`), the detailed usage of the corresponding subcommand is prompted.

## init

Creates and initializes an empty DB file.

**Command Format**:

~~~
tatarubook init [-h] db_file
~~~

**Parameters**:
- `db_file`: DB file name, with or without path. If the file already exists, no action will be performed, only an error message will be printed. If there are spaces in the path or file name, you need to surround this parameter with quotes.

## check

Checks whether the data in the DB file conforms to the consistency constraints.

**New in v1.1**: Checks if all tables, indexes, and view definitions in a DB file are consistent with the current version.
{: .notice}

**Command Format**:

~~~
tatarubook check [-h] db_file
~~~

**Parameters**:
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.

There are two types of data consistency constraints:

1. Mandatory constraints: if the result does not satisfy these constraints, the operation will fail immediately and the data will be rolled back immediately. In general, constraints for field value type/range, foreign key validity are mandatory constraints. Since mandatory constraints have been guaranteed by the underlying database and cannot be violated under normal circumstances, the `check` command does not check for mandatory constraints.
1. Warning constraints: If these constraints are not satisfied, the data is still allowed to preserve, but TataruBook will indicate that the data needs to be fixed. Such constraints are mostly checked by specific `check` views, such as requiring price information for a specific asset on a specific date. The `check` command only checks for warning constraints.

To see what checks are included for data consistency constraints, see the description in [tables and views]({{ site.baseurl }}/tables_and_views.html).

Since data consistency has an impact on the correctness of many reports, TataruBook automatically runs a data consistency check and reports the results after performing any operation that modifies a DB file.
{: .notice}

## export

Exports the contents of the specified table/view or all tables/views to a CSV file.

**Command Format**:

~~~
tatarubook export [-h] [--table TABLE] [--encoding ENCODING] db_file
~~~

**Parameters**:
- `--table TABLE` (optional): specifies a table or view with the name `TABLE`. Without this parameter, exports all tables and views.
- `--encoding ENCODING` (optional): specifies the character encoding. See the description in [character encoding format]({{ site.baseurl }}/commands.html#character-encoding-format).
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.

Rules for generating filenames: the name of the corresponding table/view plus the `.csv` suffix. If a file already exists, it will be **skipped**, but other non-conflicting files (if they exist) will still be exported.

## insert

Inserts a record into the specified table (usually one, unless the [automatically insert into the associated table]({{ site.baseurl }}/commands.html#automatically-insert-into-the-associated-table) function is triggered).

**Command format**:

~~~
tatarubook insert [-h] db_file table values
~~~

**Parameters**:
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.
- `table`: table name.
- `values`: values of all fields, with fields separated by spaces. If a field contains spaces, it needs to be surrounded with quotes.

The insert operation has some special handling, as described in [general features]({{ site.baseurl }}/commands.html#general-features).

## import

Batch import (add) a batch of records from a CSV file into a specified table, records that already exist in the table are not affected.

**Command Format**:

~~~
tatarubook import [-h] [--table TABLE] [--encoding ENCODING] db_file csv_file
~~~

**Parameters**:
- `--table TABLE` (optional): specifies a table with the name `TABLE`. If this parameter is not present, determine which table to import based on the filename of `csv_file`.
- `--encoding ENCODING` (optional): specifies the character encoding. See the description in [character encoding format]({{ site.baseurl }}/commands.html#character-encoding-format).
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.
- `csv_file`: CSV file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.

TataruBook will automatically determine if the CSV file includes a header row or not, the judgment is: if no column of the first row of the CSV contains a number, then it is considered to be a header row. Note: TataruBook only determines and skips the header row, it does not adjust the field order based on the content of the header row. The field order must be consistent with the table definition.

If the processing fails when inserting a row, then TataruBook performs a **rollback** and the entire DB file is restored to the state it was in before this `import` command was executed, even if other rows in the CSV file can be inserted successfully.

The import operation has some special handling, see the description in [general features]({{ site.baseurl }}/commands.html#general-features).

## overwrite

Removes all contents of the specified table and inserts a row. This command only works on tables with only one field: [start_date]({{ site.baseurl }}/tables_and_views.html#start_date), [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), [standard_asset]({{ site.baseurl }}/tables_and_views.html#standard_asset).

**Command format**:

~~~
tatarubook overwrite [-h] db_file table content
~~~

**Parameters**:
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.
- `table`: table name, must be one of `start_date`, `end_date`, `standard_asset`.
- `content`: the content of the only field of the only record inserted.

This command can be seen as a quick way to modify a table containing only one value.

## paste

This is a new command added in v1.2. This command uses PowerShell to read the clipboard content, and can only be used in Windows.
{: .notice}

Parse current clipboard content as one or more records of a specified table, and insert those records into that table. Multiple records in the clipboard need to be separated by newlines, multiple fields in a record need to be separated by tabs, and the content of each field is not allowed to contain tabs.

If you copy content from a text editor (such as Notepad) to the clipboard, you need to follow the above formatting requirements. If you copy cells from Excel to the clipboard, then the data format meets the requirements automatically, but you must ensure that each cell's content does not contain tabs. Be careful not to use a text editor to open a CSV file and copy the source content, because the fields in a CSV file are separated by commas and do not meet the formatting requirements. You should open the CSV file in Excel and then copy the cells.

When the `table` parameter is one of `start_date`, `end_date`, or `standard_asset`, this command performs [overwrite]({{ site.baseurl }}/commands.html#overwrite); otherwise, [insert]({{ site.baseurl }}/commands.html#insert) is performed for each record in the clipboard.

**Command format**:

~~~
tatarubook paste [-h] db_file table
~~~

**Parameters**:
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.
- `table`: table name.

TataruBook will automatically determine if the clipboard content includes a header row or not, the judgment is: if no column of the first row contains a number, then it is considered to be a header row. Note: TataruBook only determines and skips the header row, it does not adjust the field order based on the content of the header row. The field order must be consistent with the table definition.

If the processing fails when inserting a row, then TataruBook performs a **rollback** and the entire DB file is restored to the state it was in before this `paste` command was executed, even if other rows in the clipboard can be inserted successfully.

The paste operation has some special handling, see the description in [general features]({{ site.baseurl }}/commands.html#general-features).

## delete

Deletes a row at the specified index in the specified table.

**Command Format**:

~~~
tatarubook delete [-h] db_file table values
~~~

**Parameters**:
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.
- `table`: table name.
- `values`: the specified index values. If the index contains multiple fields, the fields are separated by spaces. If a field contains spaces, it needs to be surrounded with quotes.

Note that the `values` entered for the `delete` command contain only the values of the indexed fields; do not enter all fields.

When a record in the `postings` table is being deleted, if there is a corresponding record in the `posting_extras` table, that record in the `posting_extras` table will also be deleted.

## prune

Deletes a batch of records in the specified table corresponding to one or more indexes given by the CSV file.

**Command Format**:

~~~
tatarubook prune [-h] [--table TABLE] [--encoding ENCODING] db_file csv_file
~~~

**Parameters**:
- `--table TABLE` (optional): specifies a table with the name `TABLE`. If this parameter is not present, determine which table to operate on based on the filename of `csv_file`.
- `--encoding ENCODING` (optional): specifies the character encoding. See the description in [character encoding format]({{ site.baseurl }}/commands.html#character-encoding-format).
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.
- `csv_file`: CSV file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.

TataruBook will automatically determine if the CSV file has a header row or not, the judgment is: if no column of the first row of the CSV contains a number, then it is considered to be a header row. Note: TataruBook only determines and skips the header row, it does not adjust the field order based on the content of the header row. The field order must be consistent with the table definition.

Be careful that each row in the CSV file should contain only the values of the index fields and no other fields.

When a record in the `postings` table is being deleted, if there is a corresponding record in the `posting_extras` table, that record in the `posting_extras` table will also be deleted.

If the process fails when deleting an index, then TataruBook performs a **rollback** and the entire DB file is restored to the state it was in before this `prune` command was executed, even if other indexes in the CSV file can be deleted successfully.

## execsql

Execute a customized SQL command.

**Command format**:

~~~
tatarubook execsql [-h] db_file cmd
~~~

**Parameters**:
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.
- `cmd`: SQL command string, you need to surround this parameter with quotes.

TataruBook does not perform any checks and constraints on SQL commands. The user takes the responsibility of the consequences of executing customized SQL commands. If the SQL command modifies the definition of a table/view, it may result in the DB file not being able to be processed correctly by TataruBook in the future.

Since TataruBook does not have a query command, if you want to query the contents of a table/view directly from the command line (instead of exporting to a CSV file), you can use the `execsql` command to do so. For example, the following command queries the contents of the `statements` view:

~~~
tatarubook execsql example.db "select * from statements"
~~~

## upgrade

This is a new command added in v1.1.
{: .notice}

Attempts to change all table, index, and view definitions in the DB file to match the current version.

**Command Format**:

~~~
tatarubook upgrade [-h] db_file
~~~

**Parameters**:
- `db_file`: DB file name, with or without path. If there are spaces in the path or file name, you need to surround this parameter with quotes.

If the table, index, and view definitions of the DB file do not match the current version, it's usually caused by an upgrade of the TataruBook program. If the table, index, and view definitions of the TataruBook program and the DB file are inconsistent, unpredictable errors may occur during operation. It is recommended that after each TataruBook upgrade, you first use the `upgrade` command to modify the DB file to match the current version.

If there are tables and indexes in the DB file whose definitions do not exist in the current TataruBook, or are inconsistent with the definitions in TataruBook, the `upgrade` command will reject the upgrade and report an error. This is because deleting or modifying these table and index definitions may result in the loss of data. Usually, when upgrading, TataruBook program only modifies view definitions, not table and index definitions.

It is strongly recommended to backup the DB file before using the `upgrade` command.
{: .notice--warning}
