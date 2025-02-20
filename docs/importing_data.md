---
title: Data Importing Guide
---
Nowadays, electronic trading has been popularized, banks, brokerage firms, and other financial institutions can provide **account statements** which contain transaction records, users usually do not need to manually record each transaction. However, how to batch import transaction records from various account statements into TataruBook is a major problem that affects the efficiency of bookkeeping.

This page provides a possible set of methods to convert and import transaction record data. These approaches are for guidance only, users may use other methods as they like.

# Convert the transaction records to Excel

The account statement you received may be in various formats, such as plain text, CSV, Excel, PDF and so on. If the account statement is a CSV file or Excel file, then this step can often be skipped. Otherwise, you need to first convert the transaction records in the account statement into an Excel worksheet.

Note that the content of the Excel worksheet should meet the following two requirements:

- Each row represents a transaction;
- Transaction records are in ascending order according to time (especially the order of multiple transactions within a day, because in this case sorting by date can not make the order correct).

Unfortunately, bank statements or brokerage statements are often given in PDF or HTML format. In this case, you need to extract transaction records from the account statement and convert them to Excel format. There is no fixed approach for this process, but there are various solutions: you can use regular expressions, converting tools, online services, or many other choices. Searching "convert an account statement to Excel" in Google will give you a plenty of instructions on how to do this.

An example of a worksheet as a result of convertion is given below, this example simulates a segment of transactions from a credit card statement. Your real account statement is likely to be different from this example - there may be more or fewer columns, and the order of the columns may be different. But it doesn't matter, as long as the worksheet meets the two requirements above, the later steps just need to be adjusted accordingly, and the import will eventually be completed.

| Post Date | Tran Date | Description | Amount |
|:-:|:-:|:-:|:-:|
| 21/07/23 | 20/07/23 | The Last Stand | 32.55 |
| 28/07/23 | 27/07/23 | The Last Stand | 45.45 |
| 05/08/23 | 04/08/23 | The Manderville Gold Saucer | 690.00 |
| 15/08/23 | 14/08/23 | Payment from Moogle Bank | -150.00 |
| 15/08/23 | 14/08/23 | Payment from Sharlayan Bank | -150.00 |
| 15/08/23 | 14/08/23 | Payment from Sharlayan Bank | -150.00 |

In this step you need to pay attention to check Excel cells for the presence of redundant spaces, tabs, returns and other characters, these characters may lead to the failure of the subsequent processing steps. And because these characters are not visible in Excel, this problem is more difficult to be located. After the convertion of the account statement, these redundant characters should be removed as soon as possible.
{: .notice--warning}

# Create a reusable conversion template

Create a new Excel file and name the first worksheet in it `Raw Data` and paste the data obtained in the previous step in this worksheet.

This Excel file will become the **conversion template** for all account statements that have similar patterns as this one. In the future, for this data pattern, as long as it is pasted into the `Raw Data` worksheet, the conversion will be almost automatically completed. That is to say, **most of the steps described in this article are only needed the first time you process data from a certain kind of account statements**, and once the conversion template has been created, most of the steps can be done automatically when you process similar data in the future.

Account statements of different account types or from different institutions may be in different patterns, so it is usually necessary to create a conversion template specific to each account type and financial institution.

# Configure parameters

Create a new worksheet named `Parameters` after the `Raw Data` in the conversion template.

Then observe the `Raw Data`, think of for each transaction, **what information can be used to determine the account of the other party in each transaction**. For example, for the previous example:

- If the content of the `Description` column is `The Last Stand`, then the account of the other party is the external account named `Food and Beverages`;
- If the content of the `Description` column is `The Manderville Gold Saucer`, then the account of the other party is the external account named `Entertainment`;
- If the content of the `Description` column is `Payment from Moogle Bank`, then the account of the other party is the internal account named `Moogle Bank current`;
- If the content of the `Description` column is `Payment from Sharlayan Bank`, then the account of the other party is the internal account named `Sharlayan Bank current`.

Based on these rules, the correspondence between `Description` and the account of the other party is entered in the `Parameters` worksheet as follows:

| The Last Stand | Food and Beverages |
| The Manderville Gold Saucer | Entertainment |
| Payment from Moogle Bank | Moogle Bank current |
| Payment from Sharlayan Bank | Sharlayan Bank current |

When the `Raw Data` contains a lot of daily purchases and transfers, the processing of this step can be quite personalized. For example, how do you define a transaction as a `Food and Beverages` expense? If you eat at a particular restaurant most of the time, then these transaction records may all have the same value in one column, and a correspondence between a column feature and `Food and Beverages` can be added to the `Parameters` worksheet. But using this approach is often not enough to handle all the data. There may be some special charges or revenues that require manual intervention.
{: .notice}

# Grab and convert the information needed

There may be some columns of information in the `Raw Data` that do not need to be imported into the DB file, such as the `Post Date` in the example. Of course, if you feel necessary, you can also put some information that needs to be kept into the `comment` field of the [postings]({{ site.baseurl }}/tables_and_views.html#postings) table. But the most important thing is to grab the key information about the transaction from the `Raw Data`.

Create a new worksheet named `Intermediate Results` after `Parameters` in the conversion template and write the following column names in the first row of that worksheet:

| trade_date | this_account | amount | other_account | comment | other_change |

Next, formulas need to be devised for each column to grab and transform the data based on the structure of the `Raw Data`. Take the formulas for each column in the second row of the worksheet (i.e., the first row of the data content) as an example:

`trade_date` is the trade date. The trade date in the `Raw Data` is in the `Tran Date` column (i.e., column B). The `Tran Date` in the `Raw Data` is in DD/MM/YY format and needs to be converted to Excel date format. The designed formula is: `=DATE(CONCAT("20",RIGHT('Raw Data'!B2,2)),MID('Raw Data'!B2,4,2),LEFT('Raw Data'!B2,2))`. This combination of formulas uses a string processing function and a date constructor. If the date format in your `Raw Data` is not like this, then the formula will need to be modified as appropriate.

`this_account` is the account from which the original account statement is generated. Let's assume that the name of the account in the example is `Sharlayan Bank credit card` and populate the `this_account` column with it. There is no need to use a formula in this column because the `this_account` value is the same for every transaction.

If you have a number of different accounts that share the same data pattern, they can be processed using the same conversion template. In this case, you'd better configure the account name as a parameter written in the `Parameters` worksheet and reference this parameter in the `this_account` column.
{: .notice}

`amount` is the amount of change in balance of `this_account` account in the transaction, indicated by `Amount` in column D of the `Raw Data`. Notice that for credit card, the change in asset is the opposite of `Amount` in the account statement, because `Amount` is the number you owe. So the formula for this column is: `=-'Raw Data'!D2`.

`other_account` is the name of the account of the other party in the transaction. Based on the parameters configured in the [Configure Parameters]({{ site.baseurl }}/importing_data.html#configure-parameters) step, the formula can be designed as: `=VLOOKUP('Raw Data'!C2,Parameters!A:B,2,FALSE)`.

The `comment` is the comment or description for the transaction, what data is filled in this column depends on the user's preferences. Our example grabs the `Description` and puts it directly into the comment: `='Raw Data'!C2`.

`other_change` is the amount of change in balance of the account of the other party in the transaction. This data is only needed when a transaction involves two accounts which contain different assets, otherwise it should be empty. In this example the values in this column are all empty, because every transaction here involves two accounts which contain the some asset. Notice that if there are transactions that do not satisfy this criteria (for example, if there are stock trade transactions), then you need to grab information into `other_change`.

The formulas designed for each column according to the above process are summarized as below:

| Column | Formula |
|:-:|:-:|
| trade_date | `=DATE(CONCAT("20",RIGHT('Raw Data'!B2,2)),MID('Raw Data'!B2,4,2),LEFT('Raw Data'!B2,2))` |
| this_account | `Sharlayan Bank credit card` |
| amount | `=-'Raw Data'!D2` |
| other_account | `=VLOOKUP('Raw Data'!C2,Parameters!A:B,2,FALSE)` |
| comment | `='Raw Data'!C2` |
| other_change | (empty) |

After all the formulas in the first line of the data content are filled in, you can use Excel's auto-fill function to fill the other lines with the corresponding formulas, and get the results of the calculations as follows:

| trade_date | this_account | amount | other_account | comment | other_change |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 2023/7/20 | Sharlayan Bank credit card | -32.55 | Food and Beverages | The Last Stand | |
| 2023/7/27 | Sharlayan Bank credit card | -45.45 | Food and Beverages | The Last Stand | |
| 2023/8/4 | Sharlayan Bank credit card | -690 | Entertainment | The Manderville Gold Saucer | |
| 2023/8/14 | Sharlayan Bank credit card | 150 | Moogle Bank current | Payment from Moogle Bank | |
| 2023/8/14 | Sharlayan Bank credit card | 150 | Sharlayan Bank current | Payment from Sharlayan Bank | |
| 2023/8/14 | Sharlayan Bank credit card | 150 | Sharlayan Bank current | Payment from Sharlayan Bank | |

The design of formulas in this step depends on your actual data pattern and may require frequent reference to [Excel functions](https://support.microsoft.com/en-us/office/excel-functions-by-category-5f91f4e9-7b42-46d2-9bd1-63f26a86c0eb). If you're not very familiar with Excel formulas, consider using a search engine, or ask AI for help.
{: .notice}

# Check the correctness of the intermediate results

Now it is necessary to perform a manual review of the data in the `Intermediate Results` worksheet. Since each transaction in the `Raw Data` may not always follow the same rule, sometimes there may be some anomalies in the data, so it needs to be manually reviewed and processed. But note: when modifying the data, only the `Raw Data` worksheet should be modified, not the `Intermediate Results` worksheet, otherwise the formulas will be overwritten and the conversion template can no longer be reused.

# Select source and target accounts

Create a new worksheet named `Final Results` after the `Intermediate Results` in the conversion template, and in the first row of that worksheet, write the following column names according to the import requirements of the [postings]({{ site.baseurl }}/tables_and_views.html#postings) table:

| posting_index | trade_date | src_account | src_change | dst_account | comment | dst_change |

`dst_change` is a field in the [posting_extras]({{ site.baseurl }}/tables_and_views.html#posting_extras) table instead of the [postings]({{ site.baseurl }}/tables_and_views.html#postings) table, but due to the [automatically insert into the associated table]({{ site.baseurl }}/commands.html#automatically-insert-into-the-associated-table) feature, which allows TataruBook to insert associated data in both tables at the same time, this column is needed when importing transaction records.
{: .notice}

In the `Final Results`, the `posting_index` column is left empty (see [automatically generated index fields]({{ site.baseurl }}/commands.html#automatically-generated-index-fields) for the reason), and the data in the `trade_date` and `comment` columns are directly quoted from the corresponding columns in the `intermediate result`. The contents of the columns `src_account`, `src_change`, `dst_account`, `dst_change` need to be determined according to **the direction of flow in each transaction**.

Looking at the `Intermediate Results`, one can see that if the value of `amount` is less than $$ 0 $$, then `src_account` (i.e., the account from which the value is flowing out) is `this_account` and `dst_account` (i.e., the account into which the value is flowing in) is `other_account`; and if the value of the `amount` column is greater than $$ 0 $$, then `src_account` is `other_account` and `dst_account` is `this_account`. That is, you need to determine whether to exchange two accounts based on the amount of change in the transaction.

But what if `amount` is equal to $$ 0 $$? In the example, there is no transaction with an `amount` of $$ 0 $$, but in reality, if there is a stock split or a reverse stock split, it is possible that only the number of shares changes in the corresponding transaction, while the amount of cash is $$ 0 $$. In order to adapt the conversion template to these scenarios, it is best to determine the direction of flow based on whether the `other_change` value is positive or negative when `amount` is $$ 0 $$.

When the `other_change` value is not empty in the `Intermediate Results`, the calculations for the `src_change` and `dst_change` columns are similar to those of the `src_account` and `dst_account`, and the results in the `src_account` column can be utilized to determine whether or not to exchange these two numbers. However, if `other_change` in `intermediate_result` is empty, then the `dst_change` column in `final_result` should also be empty, and `src_change` should be chosen between the value of `amount` or the opposite of `amount` (because `src_change` is always less than or equal to $$ 0 $$).

In summary, the formulas for each column of the second row (i.e., the first row of data content) of the `Final Results` worksheet are:

| Column | Formula |
|:-:|:-:|
| posting_index | |
| trade_date | `='Intermediate Results'!A2` |
| src_account | `=IF('Intermediate Results'!C2<0,'Intermediate Results'!B2,IF('Intermediate Results'!C2>0,'Intermediate Results'!D2,IF('Intermediate Results'!F2<0,'Intermediate Results'!D2,'Intermediate Results'!B2)))` |
| src_change | `=IF('Intermediate Results'!F2="",IF('Intermediate Results'!B2=C2,'Intermediate Results'!C2,-'Intermediate Results'!C2),IF('Intermediate Results'!B2=C2,'Intermediate Results'!C2,'Intermediate Results'!F2))` |
| dst_account | `=IF('Intermediate Results'!B2=C2,'Intermediate Results'!D2,'Intermediate Results'!B2)` |
| comment | `='Intermediate Results'!E2` |
| dst_change | `=IF('Intermediate Results'!F2="","",IF('Intermediate Results'!B2=C2,'Intermediate Results'!F2,'Intermediate Results'!C2))` |

Although these formulas may seem a bit complicated, **the formulas in the `Final Results` worksheet can be reused in almost any conversion template**. As long as the `Intermediate Results` worksheet is in a fixed format generated strictly according to the previous steps, all the formulas in the `Final Results` worksheet can be copied directly from an existing conversion template.

Populate all rows with these formulas to get the calculation results as follows:

| posting_index | trade_date | src_account | src_change | dst_account | comment | dst_change |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023/7/20 | Sharlayan Bank credit card | -32.55 | Food and Beverages | The Last Stand | |
| | 2023/7/27 | Sharlayan Bank credit card | -45.45 | Food and Beverages | The Last Stand | |
| | 2023/8/4 | Sharlayan Bank credit card | -690 | Entertainment | The Manderville Gold Saucer | |
| | 2023/8/14 | Moogle Bank current | -150 | Sharlayan Bank credit card | Payment from Moogle Bank | |
| | 2023/8/14 | Sharlayan Bank current | -150 | Sharlayan Bank credit card | Payment from Sharlayan Bank | |
| | 2023/8/14 | Sharlayan Bank current | -150 | Sharlayan Bank credit card | Payment from Sharlayan Bank | |

# Recognize transaction records that have already been imported

In the above example, the last three transactions each is a transfer from another account to the `Sharlayan Bank credit card` account. Normally, these transaction records would exist in both accounts on both sides of the transaction. For example, If we had imported the `Sharlayan Bank current` transaction records first, then the last two records would have been in the DB file before importing the `Sharlayan Bank credit card` transaction records. Therefore, while importing the transaction records of `Sharlayan Bank credit card`, you need to first identify these already imported transaction records to avoid these records from being duplicated in the DB file.

This step is not required and can be skipped if you are sure that the transaction records that need to be imported do not exist in the DB file.
{: .notice}

Create a new worksheet named `statements` after the `Final Results` worksheet.

Use the [export]({{ site.baseurl }}/commands.html#export) command to export the content of [statements]({{ site.baseurl }}/tables_and_views.html#statements) view from the DB file, then open it in Excel and filter on the `src_name` column to show only records for the `Sharlayan Bank current` account. Observe the time period that overlap with the current transaction records to be imported, and copy the transaction records within this period into the `statements` worksheet.

Next, we need to perform a **one-to-one match** between the transaction records in the `Intermediate Results` worksheet and the `statements` worksheet. The correct bookkeeping data should satisfy such a match result:

- When two records match, they have the same transaction date and transaction amount. (Note*)
- For each record in the `statements` worksheet, there is a unique record in the `Intermediate Results` worksheet that matches it.
- If transactions for an account during this time period have already been imported, then for each transaction in the `Intermediate Results` worksheet that occurs with this account, there should be a unique row in the `statements` worksheet that matches it.

Note*: In reality, transfers, remittances, etc. may not arrive at the same day, or the received amount may be different from the transferred amount due to fees, etc. In these cases, you need to do some manual processing of the transfer transaction. For example, you can split a transfer into two transactions, one for payment of fees and the other for the actual transfer, or you can add a new "in-transit" account, so that the funds can be transferred to the "in-transit" account first, and then to the destination account.
{: .notice}

Let's demonstrate this matching process using an example `statements` worksheet. The contents of the `statements` worksheet are as follows:

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 102 | 2023/8/14 | 1 | 150 | 3 | Payment | Sharlayan Bank current | 1 | 0 | Sharlayan Bank credit card | 18450 |
| 103 | 2023/8/14 | 1 | 150 | 3 | Payment | Sharlayan Bank current | 1 | 0 | Sharlayan Bank credit card | 18300 |

In this example, the two rows in `statements` (the second and third rows) should match the last two rows in `Intermediate Results`, respectively. But the problem is: the last three rows of `Intermediate Results` have the same transaction date and the same transaction amount, which will lead to incorrect results if you use the normal **VLOOKUP** function to match them. Therefore, some special formulas will be used as below.

First, add a new column `key_info` (column G) to the right of `other_change` (column F), the current last column of `Intermediate Results`, and fill in the second row (i.e., the first row of the data) with the formula: `=CONCAT(A2," ",C2)`. Add a new column, `key_info` (column L), to the right of the current last column of `statements`, `balance` (column K), and fill in the second row (i.e., the first row of data) with the formula: `=CONCAT(B2," ",D2)`. Both formulas serve to concatenate the transaction date and transaction amount fields for subsequent processing. You may see the date in the result displayed as an integer, this is because Excel uses integers internally when representing dates, this will not affect further processing.

Then add a new column `force_align` (column H) to the right of the `key_info` column (column G) in `Intermediate Results`. This column has no formula and is empty for now, it is used to allow the user to manually match a record to a record in `statements` if necessary.

Next, add a new column (column M) to the right of the `key_info` column (column L) of `statements`, and enter the number `1` in the first row of column M (the header row); in the second row, enter the formula: `=IF(COUNTIF('Intermediate Results'!H:H,ROW())>0,MATCH(ROW(),'Intermediate Results'!H:H,0),MATCH(L2,OFFSET('Intermediate Results'!G$1,M1,0,9999),0)+M1)`

This formula first determines if there is a manually specified match in the `force_align` column (column H) of the `Intermediate Results`, and if there is, the specified match is used directly. Otherwise, it looks for a match in the `Intermediate Results` to that row of `statements`, from the previous row that has already been matched, downwards. This processing ensures that no two `Intermediate Results` records match the same `statements` record.

Fill all the rows with these formulas using Excel's auto-fill function. Then you can see that in column M of `statements`, the matches found for the two records in the second and third rows are `5` and `6`, respectively, which are the fifth and sixth records of `Intermediate Results`.

This matching relationship is incorrect because the fifth record of `Intermediate Results` should not be involved in the match (because that transfer is not from `Sharlayan Bank current` account), but because the transaction date and transaction amount of that record happens to be the same as the records that need to be matched, it gets matched first. This situation requires manual intervention: enter the number `2` in cell H6 of the `Intermediate Results` worksheet to specify that this record of `Intermediate Results` matches the record in the second row of `statements`.

After modifying the contents of cell H6, the contents of column M of `statements` are updated: the two records now find matches of `6` and `7`, respectively, and the matches are correct.

Finally, add a new column, `skip` (column H), to the right of the current last column, `dst_change` (column G), in the `Final Results` worksheet, and fill a formula in the second row: `=COUNTIF(statements!M:M,ROW())`. This formula is used to show whether the row has a match in `statements`, if so, the result is `1`, otherwise `0`. Fill this formula to all rows and filter this row for `0` records, these are the transactions that do not exist in the DB file and need to be imported.

The columns added to the relevant worksheet and the formulas for the second row of each column according to the above process are summarized as below:

| Worksheet | Column Header | Column Name | Formula |
|:-:|:-:|:-:|:-:|
| Intermediate Results | key_info | G | `=CONCAT(A2," ",C2)` |
| Intermediate Results | force_align | H | No formula, used for manually specifying match |
| statements | key_info | L | `=CONCAT(B2," ",D2)` |
| statements | 1 | M | `=IF(COUNTIF('Intermediate Results'!H:H,ROW())>0,MATCH(ROW(),'Intermediate Results'!H:H,0),MATCH(L2,OFFSET('Intermediate Results'!G$1,M1,0,9999),0)+M1)` |
| Final Results | skip | H | `=COUNTIF(statements!M:M,ROW())` |

# Import data into the DB file

The data in the `Final Results` worksheet already meets the formatting requirements of [postings]({{ site.baseurl }}/tables_and_views.html#postings) table. Copy these data to clipboard and import them into the DB file by using [paste]({{ site.baseurl }}/commands.html#paste) command, then all the work is done.

But be careful: there are some transactions that involve accounts that may not have been created in TataruBook yet. For example, if a transaction involves a stock that has never been traded before, it is possible that the [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table and the [asset_types]({{ site .baseurl }}/tables_and_views.html#asset_types) table does not contain this stock, causing the import to fail. However, TataruBook triggers an automatic rollback when any record fails to be imported without affecting existing data. So you can try to import multiple times and supplement the [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table and the [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table according to the failure message each time until all the records can be imported successfully. In the `Intermediate Results` worksheet of the conversion template, you can add a few new columns to grab the information needed by the [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table and the [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
