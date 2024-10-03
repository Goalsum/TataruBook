---
title: Quick Start
---
This page is an introductory tutorial for people who are new to using TataruBook. This tutorial shows you how to use TataruBook's common features from start to finish, through a series of use cases.

# Initialize the DB file

Start by downloading and installing TataruBook, if you don't already know how, see [here]({{ site.baseurl }}/index.html#how-to-download-and-install-tatarubook).

For convenience, it is assumed in the following that TataruBook was installed using the second installation approach - the executable file approach. if the user is using the first installation approach - the Python script approach, he/she will need to replace all the command-lines in the following beginning with `tatarubook` to beginning with `python tatarubook.py`. For example, the command to create the DB file needs to be changed from `tatarubook init accounting.db` to `python tatarubook.py init accounting.db`.

Once the installation is complete, open your operating system's command-line terminal, switch to the directory where the TataruBook program is located, and execute the command:

~~~
tatarubook init accounting.db
~~~

After the execution is completed, there will be an additional `accounting.db` file in the directory, which is the **DB file** where the bookkeeping data is stored.

Next, add a currency type using the [insert]({{ site.baseurl }}/commands.html#insert) command:

~~~
tatarubook insert accounting.db asset_types NULL Gil 0
~~~

This will insert a record in the [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table containing three fields: `asset_index` field is `NULL`, which means that the index will be automatically generated; `asset_name` field is `Gil`, which means the name of the asset (currency); `asset_order` field is `0`, which means the serial number of the asset - TataruBook will use the serial number to sort the assets when displaying multiple assets.

The [insert]({{ site.baseurl }}/commands.html#insert) command inserts a record into any table, with the name of the table and the values of the fields in the record to be inserted.
{: .notice}

Many of the examples in the TataruBook documentation are borrowed from the **Final Fantasy 14** game setting. In Final Fantasy 14, the primary currency is `Gil`, so this article uses that currency for its examples. When it comes to actual bookkeeping, you can use any currency name, such as USD, JPY, RMB, etc.
{: .notice}

The command just executed displays some strange messages:

~~~
Integrity check after insertion:
start_date should contain exactly 1 row but 0 row(s) are found.
end_date should contain exactly 1 row but 0 row(s) are found.
standard_asset should contain exactly 1 row but 0 row(s) are found.
~~~

This is a problem reported by TataruBook after performing a **Data Consistency Check**. TataruBook contains a number of **Views** that analyze financials, many of which require specific data to exist in order to perform calculations. Therefore, if TataruBook finds that the required data is missing, it will prompt for it. Often the message text is enough to understand what problem it is reporting.

Let's solve the problems in the prompt message one by one:

First set the only currency `Gil` as the bookkeeping **home currency** to solve the problem of needing a record in the [standard_asset]({{ site.baseurl }}/tables_and_views.html#standard_asset) table:

~~~
tatarubook overwrite accounting.db standard_asset Gil
~~~

Then set the start time and end time of the **statistics period** to solve the problem of [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) table and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) table each need to have a record in them:

~~~
tatarubook overwrite accounting.db start_date 2022-12-31
tatarubook overwrite accounting.db end_date 2023-12-31
~~~

Note: The starting point of the statistics period is the **end** moment of the day of `start_date`, so if you want to count the whole year of 2023, don't write `start_date` as `2023-1-1`, otherwise the data of the day of `2023-1-1` will be omitted from the statistics.

The content of the vast majority of views in TataruBook is determined by the statistics period defined by [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) table and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) table. For example, [start_stats]({{ site.baseurl }}/tables_and_views.html#start_stats) view displays the account balances and values at the end of the day `start_date`; [end_stats]({{ site.baseurl }}/tables_and_views.html#end_stats) view shows the account balances and values at the end of the day `end_date`; the ROI related view shows the returns over the statistics period, and so on. By modifying `start_date` and `end_date`, you can modify the statistics period to look at the financials for a specified historical period.
{: .notice}

Now that the data consistency issues are out of the way, TataruBook reports:

~~~
Integrity check after overwrite:
Everything is fine, no integrity breach found.
~~~

# Start bookkeeping

Let's start by adding a bank account:

~~~
tatarubook insert accounting.db accounts NULL "Sharlayan Bank current" Gil 0
~~~

This command means that the name of the account is `Sharlayan Bank current`, the corresponding asset (currency) is `Gil`, and the last field has a value of `0` which means that the account is an **internal account**.

You may be wondering what is "internal account"? --The answer to this question will come soon.

Let's say that the balance inside the `Sharlayan Bank current` account is not $$ 0 $$ before we start bookkeeping, and now we want to enter this balance into TataruBook. However, TataruBook uses [double-entry bookkeeping]({{ site.baseurl }}/tables_and_views.html#simplified-double-entry-bookkeeping). So, **to add value to an account, there must be another account that reduces the value by an equal amount**. To fulfill this requirement, we add an **external account** named `Opening balance` (note that the last field value is `1`):

~~~
tatarubook insert accounting.db accounts NULL "Opening balance" Gil 1
~~~

Value can now be transferred from the `Opening balance` account to the `Sharlayan Bank current` account. Add a balance of $$ 5000 $$ Gil to the `Sharlayan Bank current` account with this command:

~~~
tatarubook insert accounting.db postings NULL 2022-12-31 "Opening balance" -5000 "Sharlayan Bank current" "Brought forward"
~~~

After executing this command, TataruBook believes that on the day `2022-12-31`, the `Opening balance` account was decreased by $$ 5000 $$ Gil and the `Sharlayan Bank current` account was increased by $$ 5000 $$ Gil.

Next we want to record food and beverage spendings by first adding an external account named `Food and Beverages`:

~~~
tatarubook insert accounting.db accounts NULL "Food and Beverages" Gil 1
~~~

Then, add two purchases:

~~~
tatarubook insert accounting.db postings NULL 2023-1-5 "Sharlayan Bank current" -20 "Food and Beverages" "Breakfast at Inn"
tatarubook insert accounting.db postings NULL 2023-1-7 "Sharlayan Bank current" -45 "Food and Beverages" "Dinner at the Last Stand"
~~~

After execution is complete, export the [statements]({{ site.baseurl }}/commands.html#statements) view using [export]({{ site.baseurl }}/tables_and_views.html#export) command:

~~~
tatarubook export accounting.db --table statements
~~~

This command causes the `statements.csv` file to appear in the directory. Open it in Excel and see the following:

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022/12/31 | 1 | 5000 | 2 | Brought forward | Sharlayan Bank current | 1 | 0 | Opening balance | 5000 |
| 1 | 2022/12/31 | 2 | -5000 | 1 | Brought forward | Opening balance | 1 | 1 | Sharlayan Bank current | -5000 |
| 2 | 2023/1/5 | 1 | -20 | 3 | Breakfast at Inn | Sharlayan Bank current | 1 | 0 | Food and Beverages | 4980 |
| 2 | 2023/1/5 | 3 | 20 | 1 | Breakfast at Inn | Food and Beverages | 1 | 1 | Sharlayan Bank current | 20 |
| 3 | 2023/1/7 | 1 | -45 | 3 | Dinner at the Last Stand | Sharlayan Bank current | 1 | 0 | Food and Beverages | 4935 |
| 3 | 2023/1/7 | 3 | 45 | 1 | Dinner at the Last Stand | Food and Beverages | 1 | 1 | Sharlayan Bank current | 65 |

This data is similar to the usual transaction ledger statements that we see all the time. Filtering on `src_name` using Excel gives a different perspective: when filtering on the internal account `Sharlayan Bank current`, you see a chronological record of transactions and balances for that account; when filtering by the external account `Food and Beverages`, you see all transactions that occurred in the name of `Food and Beverages`. So, **external accounts are categorization of income and expenses**. In TataruBook, you can categorize your income and expenses statistics any way you like - just add the corresponding external accounts.

# Bulk import data

Building on the previous section, let's move on to importing more bookkeeping data. Start by adding some internal and external accounts:

~~~
tatarubook insert accounting.db accounts NULL "Sharlayan Bank credit card" Gil 0
tatarubook insert accounting.db accounts NULL Shopping Gil 1
tatarubook insert accounting.db accounts NULL Rent Gil 1
tatarubook insert accounting.db accounts NULL Salary Gil 1
~~~

We then wish to enter a batch of transaction records. For efficient data entry, we would like to batch import the transaction details provided by banks or other organizations. For this, TataruBook provides [import]({{ site.baseurl }}/commands.html#import) command.

First, process the data in Excel into the following format and save it as a `postings.csv` file (The data in the column `posting_index` is intentionally left empty because it will be automatically generated on import. See [automatically generated index fields]({{ site.baseurl }}/commands.html#automatically-generated-index-fields)):

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023/2/10 | Salary | -8000 | Sharlayan Bank current | Monthly salary |
| | 2023/2/13 | Sharlayan Bank credit card | -190 | Shopping | Clothes shopping |
| | 2023/2/26 | Sharlayan Bank credit card | -140 | Shopping | Buying Household Items |
| | 2023/3/2 | Sharlayan Bank credit card | -9000 | Rent | Half-yearly rent |
| | 2023/3/10 | Salary | -8000 | Sharlayan Bank current | Monthly salary |
| | 2023/3/10 | Sharlayan Bank credit card | -43 | Food and Beverages | Lunch at the Last Stand |
| | 2023/3/20 | Sharlayan Bank current | -9300 | Sharlayan Bank credit card | Pay off credit card |

Then use this command to import all the records from the CSV file into the [postings]({{ site.baseurl }}/tables_and_views.html#postings) table:

~~~
tatarubook import accounting.db postings.csv
~~~

When it comes to actual bookkeeping, the [import]({{ site.baseurl }}/commands.html#import) command may be more commonly used than the [insert]({{ site.baseurl }}/commands.html#insert) command, because the data for bookkeeping often comes from banks, brokerage firms, and other organizations that provide transaction detail records. Since TataruBook has a lot of checks on the inserted data, you may encounter a failure of inserting a certain record during batch import. In this case, the `import` command triggers a **rollback** - restoring the DB file to the state it was in before the `import` was executed. The user can then modify the errors in the contents of the CSV file and re-execute the `import` command. The automatic rollback feature eliminates the need for users to worry about importing huge CSV files with partially successful inserts that make the state of the DB file difficult to determine.
{: .notice}

Now we want to look at the breakdown statistics of income and expenses. Start by exporting the [income_and_expenses]({{ site.baseurl }}/tables_and_views.html#income_and_expenses) view using the [export]({{ site.baseurl }}/commands.html#export) command:

~~~
tatarubook export accounting.db --table income_and_expenses
~~~

Then open the generated `income_and_expenses.csv` file, the contents are:

| asset_order | account_index | account_name | total_amount | asset_index | asset_name | total_value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 3 | Food and Beverages | 108.0 | 1 | Gil | 108.0 |
| 0 | 5 | Shopping | 330.0 | 1 | Gil | 330.0 |
| 0 | 6 | Rent | 9000.0 | 1 | Gil | 9000.0 |
| 0 | 7 | Salary | -16,000.0 | 1 | Gil | -16,000.0 |

These data show the statistics for each type of income and expense during the statistics period. Note: Since the amount changed in the external account is the opposite of the internal account when they are both contained in one transaction, therefore positive numbers in these data indicate expenses and negative numbers indicate income.

The [income_and_expenses]({{ site.baseurl }}/tables_and_views.html#income_and_expenses) view shows the sum of the transaction amounts of all the internal accounts on a particular type of income and expense. If you want to see the statistics broken down to each internal account, you can check out the [flow_stats]({{ site.baseurl }}/tables_and_views.html#flow_stats) view:

~~~
tatarubook export accounting.db --table flow_stats
~~~

| flow_index | flow_name | account_index | account_name | amount |
|:-:|:-:|:-:|:-:|:-:|
| 3 | Food and Beverages | 1 | Sharlayan Bank current | 65.0 |
| 3 | Food and Beverages | 4 | Sharlayan Bank credit card | 43.0 |
| 5 | Shopping | 4 | Sharlayan Bank credit card | 330.0 |
| 6 | Rent | 4 | Sharlayan Bank credit card | 9000.0 |
| 7 | Salary | 1 | Sharlayan Bank current | -16000.0 |

In the [flow_stats]({{ site.baseurl }}/tables_and_views.html#flow_stats) view, you can see how many `Food and Beverages` have been incurred by each of the `Sharlayan Bank current` and `Sharlayan Bank credit card` internal accounts.

If you want to know what the final balance of each internal account is after these transactions, you can check the [end_stats]({{ site.baseurl }}/tables_and_views.html#end_stats) view:

~~~
tatarubook export accounting.db --table end_stats
~~~

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | Sharlayan Bank current | 11635.0 | 1 | Gil | 1.0 | 11635.0 | 1.006 |
| 0 | 2023-12-31 | 4 | Sharlayan Bank credit card | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.006 |

Note that the credit card has a negative balance - this is the norm for most credit card accounts.

TataruBook does not allow account balances to be input directly (the previous operation of entering an opening balance actually enters a transaction), and the balances of all accounts are calculated automatically from the transaction history. During bookkeeping, the data entered can be effectively verified for completeness and accuracy by checking whether the balance displayed by TataruBook and the actual account balance are the same.
{: .notice}

# Interest earnings

Funds in a bank account often have interest earnings. In order to record the interest, first add the external account that represents the interest:

~~~
tatarubook insert accounting.db accounts NULL "Gil interest" Gil 1
~~~

If there are many different currencies in use, you need to set up different external accounts by different currencies. The interest account is named `Gil interest` for this reason: if other currencies are added later, the external accounts corresponding to the interest in the other currencies can be distinguished from `Gil interest`. Of course, if you only use one currency, you don't need to take this into account.
{: .notice}

TataruBook can calculate actual interest rate for each account. In order to perform that, interest accounts need to be added to the [interest_accounts]({{ site.baseurl }}/tables_and_views.html#interest_accounts) table:

~~~
tatarubook insert accounting.db interest_accounts "Gil interest"
~~~

Now you can add the interest earnings:

~~~
tatarubook insert accounting.db postings NULL 2023-3-30 "Gil interest" -30 "Sharlayan Bank current" "Interest payment"
tatarubook insert accounting.db postings NULL 2023-6-30 "Gil interest" -35 "Sharlayan Bank current" "Interest payment"
~~~

The [interest_rates]({{ site.baseurl }}/tables_and_views.html#interest_rates) view then allows you to view the account's interest rate calculated with the current data:

~~~
tatarubook export accounting.db --table interest_rates
~~~

| account_index | account_name | asset_index | avg_balance | interest | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Sharlayan Bank current | 1 | 11278.38 | 65.0 | 0.00576 |

These figures indicate that the average daily account balance of `Sharlayan Bank current` during the statistics period was $$ 11278.38 $$ Gil, and the interest rate was about $$ 0.576\% $$. For a detailed description on this calculation, see the [modified Dietz method]({{ site.baseurl }}/rate_of_return.html#modified-dietz-method).

Checking the interest rate for each account helps to avoid errors in bookkeeping - if the calculated interest rate doesn't make sense, it's an indication that there may be an error in the bookkeeping data.
{: .notice}

# Stock Investments

To record a stock investment, you first need to add an **asset** representing a particular stock. For TataruBook, stocks and currencies are not fundamentally different; they are both specific assets. Therefore, adding a stock asset to the [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table is the same as adding a currency:

~~~
tatarubook insert accounting.db asset_types NULL "Garlond Ironworks shares" 1
~~~

We write the value of the last field `asset_order` as `1` so that the stock asset will come after the currency asset in views like [end_stats]({{ site.baseurl }}/tables_and_views.html#end_stats). If you don't care about the order in which the assets are listed in the various views, you can set the `asset_order` to `0` for all assets.

Next add the internal account that holds this stock. tataruBook allows multiple internal accounts to hold the same stock, but we'll just add a stock account for now:

~~~
tatarubook insert accounting.db accounts NULL "Moogle:Garlond Ironworks shares" "Garlond Ironworks shares" 0
~~~

Stock trading in TataruBook is nothing more than a transfer of assets between internal accounts. But now a problem arises: in every previous transaction, the decrease in the source account (i.e. the transfer out account) is always equal to the increase in the target account (i.e. the transfer in account). So when recording a transaction, we only had to write a single number, and TataruBook would complete the balance change for both the source and target accounts. Now, however, the cash and stock accounts contain different assets: the balance in the cash account is the amount of money, while the balance in the stock account is the amount of shares. So the amount of change in the cash account in a transaction does not equal the opposite of the amount of change in the stock account (unless the share price happens to be $$ 1 $$).

To solve this problem, TataruBook specifies that **when two accounts in a transaction record contain different assets, the change amounts for both the source and target accounts must be provided**. This is reflected in the command by having an extra number at the end of the insert command to indicate the amount of change in the target account:

~~~
tatarubook insert accounting.db postings NULL 2023-7-3 "Sharlayan Bank current" -2000 "Moogle:Garlond Ironworks shares" "Buy shares" 200
~~~

The $$ 200 $$ at the end of the command indicates that the transaction purchased $$ 200 $$ shares. If importing records using the [import]({{ site.baseurl }}/commands.html#import) command, it is also necessary to add a field at the end of the line (record) to indicate the amount of change in the target account.

It is not necessary to provide the real-time transaction price when adding the transaction, as the amount of change for both accounts already reflects the transaction price at that time. If you wish to record the fees/commissions/taxes for a transaction, then you can add the corresponding external account and split a transaction into multiple entries.

After adding this transaction, TataruBook again reports data consistency issues:

~~~
Integrity check after insertion.
These (date, asset) pairs need price info in calculation.
(2, 'Garlond Ironworks shares', 1, '2023-12-31')
~~~

This is because TataruBook needs to know the value of the other assets measured in the home currency when calculating the net assets, so you need to enter the share price on a specific date. We add records to the [prices]({{ site.baseurl }}/tables_and_views.html#prices) table to fulfill this requirement:

~~~
tatarubook insert accounting.db prices 2023-12-31 "Garlond Ironworks shares" 12
~~~

It is now possible to view all records on [end_stats]({{ site.baseurl }}/tables_and_views.html#end_stats) view to see all account balances and market values on the [end_date]({{ site.baseurl }}/tables_and_views.html#end_date):

If you follow this tutorial all along, now there is already an `end_stats.csv` file existing in this folder because we've exported it before. In this circumstance, when you execute the command below, that file will not be updated - because TataruBook avoids accidentally damaging existing files. So you need to delete the `end_stats.csv` file first, and then run the command below.
{: .notice--warning}

~~~
tatarubook export accounting.db --table end_stats
~~~

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | Sharlayan Bank current | 9700.0 | 1 | Gil | 1.0 | 9700.0 | 0.8065 |
| 0 | 2023-12-31 | 4 | Sharlayan Bank credit card | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.0061 |
| 1 | 2023-12-31 | 9 | Moogle:Garlond Ironworks shares | 200.0 | 2 | Garlond Ironworks shares | 12.0 | 2400.0 | 0.1996 |

# Rate of return on investments

In addition to stocks, other assets such as funds, bonds, commodities, and futures are recorded in a similar way. Let's add a fund asset and the corresponding account:

~~~
tatarubook insert accounting.db asset_types NULL "Eorzea 100 Index Fund" 1
tatarubook insert accounting.db accounts NULL "Moogle:Eorzea 100" "Eorzea 100 Index Fund" 0
~~~

This fund has multiple transactions, both purchases and redemptions, we use [import]({{ site.baseurl }}/commands.html#import) command to import all transaction records at once. Start by writing the contents of the CSV file:

| posting_index | trade_date | src_account | src_change | dst_account | comment | dst_change |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023/8/2 | Sharlayan Bank current | -3000 | Moogle:Eorzea 100 | Purchase | 1500 |
| | 2023/8/21 | Sharlayan Bank current | -1000 | Moogle:Eorzea 100 | Purchase | 450 |
| | 2023/9/12 | Moogle:Eorzea 100 | -1000 | Sharlayan Bank current | Redemption | 2500 |
| | 2023/9/30 | Sharlayan Bank current | -1200 | Moogle:Eorzea 100 | Purchase | 630 |

The `dst_change` column has been added to the header row to more clearly illustrate the last field of each row. But actually TataruBook doesn't care about the contents of the header row when importing the CSV file, it just fills in the values of each field in the required order.
{: .notice}

Then import the contents of this CSV file:

~~~
tatarubook import accounting.db postings.csv
~~~

As before, add the price information for the `Eorzea 100 Index Fund` on the date [end_date]({{ site.baseurl }}/tables_and_views.html#end_date):

~~~
tatarubook insert accounting.db prices 2023-12-31 "Eorzea 100 Index Fund" 2.35
~~~

When finished, view all account balances and market values as of [end_date]({{ site.baseurl }}/tables_and_views.html#end_date): (if `end_stats.csv` file already exists, delete it first)

~~~
tatarubook export accounting.db --table end_stats
~~~

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | Sharlayan Bank current | 7000.0 | 1 | Gil | 1.0 | 7000.0 | 0.5368 |
| 0 | 2023-12-31 | 4 | Sharlayan Bank credit card | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.0056 |
| 1 | 2023-12-31 | 9 | Moogle:Garlond Ironworks shares | 200.0 | 2 | Garlond Ironworks shares | 12.0 | 2400.0 | 0.1840 |
| 1 | 2023-12-31 | 10 | Moogle:Eorzea 100 | 1580.0 | 3 | Eorzea 100 Index Fund | 2.35 | 3713.0 | 0.2847 |

In addition to displaying values by account, you can also view the quantity and value of each asset via [end_assets]({{ site.baseurl }}/tables_and_views.html#end_assets) view:

~~~
tatarubook export accounting.db --table end_assets
~~~

| asset_order | date_val | asset_index | asset_name | amount | price | total_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | Gil | 6927.0 | 1.0 | 6927.0 | 0.5312 |
| 1 | 2023-12-31 | 2 | Garlond Ironworks shares | 200.0 | 12.0 | 2400.0 | 0.1840 |
| 1 | 2023-12-31 | 3 | Eorzea 100 Index Fund | 1580.0 | 2.35 | 3713.0 | 0.2847 |

While the final value is calculated, the investor is also concerned about the profit or loss of this fund through these buy and sell transactions. The [return_on_shares]({{ site.baseurl }}/tables_and_views.html#return_on_shares) view allows you to see the returns for each account that contains investments (TataruBook treats all assets that aren't in the home currency as investments):

~~~
tatarubook export accounting.db --table return_on_shares
~~~


| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2 | Garlond Ironworks shares | 9 | Moogle:Garlond Ironworks shares | 0 | 0 | 200.0 | 200.0 | 2400.0 | -2000.0 | 2000.0 | 400.0 | 0.2 |
| 1 | 3 | Eorzea 100 Index Fund | 10 | Moogle:Eorzea 100 | 0 | 0 | 1580.0 | 1580.0 | 3713.0 | -2700.0 | 4000.0 | 1013.0 | 0.25325 |

These figures show that the `Moogle:Garlond Ironworks shares` account has an investment return of $$ 400 $$ Gil, with a rate of return of $$ 20\% $$, and the `Moogle:Eorzea 100` account has an investment return of $$ 1013.0 $$ Gil, with a rate of return of $$ 25.325\% $$. If you want to know the detailed calculation process, you can refer to [minimum initial cash method]({{ site.baseurl }}/rate_of_return.html#minimum-initial-cash-method).

TataruBook will also see the set of all internal accounts as a **portfolio** and calculate the rate of return for this portfolio as a whole, the results of which are displayed in [portfolio_stats]({{ site.baseurl }}/tables_and_views.html#portfolio_stats) view in:

~~~
tatarubook export accounting.db --table portfolio_stats
~~~

| start_value | end_value | net_outflow | interest | net_gain | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5000.0 | 13040.0 | -6562.0 | -65.0 | 1478.0 | 0.178 |

These figures show that all internal accounts had a total investment return of $$ 1478 $$ Gil over the statistics period, for a rate of return of $$ 17.8\% $$. Note that interest earnings are included in the investment return. For a detailed description on this calculation, see [simple Dietz method]({{ site.baseurl }}/rate_of_return.html#simple-dietz-method).

TataruBook is often used to keep track of all of an individual or family's assets, so the information in [portfolio_stats]({{ site.baseurl }}/tables_and_views.html#portfolio_stats) view is important: it shows the net worth at the end of both [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), as well as the net income and expenses and investment income between the two dates.
{: .notice}

# Viewing DB files with GUI software

TataruBook is a command-line program and does not have a graphical interface. However, the DB file containing all the tables and views is a **SQLite format** file, and any software that supports the SQLite format can view the tables and views in the DB file (provided that the software supports the new features of SQLite). Take the open-source software [DB Browser for SQLite](https://sqlitebrowser.org/) as an example to demonstrate: first download and install the [nightly version](https://nightlies.sqlitebrowser.org/latest) of `DB Browser for SQLite` (only the nightly version supports the new features of SQLite), then run `DB Browser for SQLite`, and finally click the `Open Database` button and select the `accounting.db` file to view the data of tables and views in the DB file.

![DB Browser for SQLite界面]({{ site.baseurl }}/assets/images/statements.png)

You can also use software other than TataruBook to edit the data in the DB file, but only TataruBook does a perfect consistency check when inserting data. So if you use other software to edit the DB file, it is better to use TataruBook to do the check again. If you know how to use SQL, you can also write your own SQL commands to develop data analysis functions that TataruBook does not provide.
{: .notice}