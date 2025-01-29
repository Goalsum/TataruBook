---
title: Tables and Views
---
This page describes all the tables and views contained in the DB file.

**Tables** contain the financial data provided by the user and they are source of data for all reports. To ensure data integrity and consistency, when adding, modifying, or deleting data from the table, TataruBook checks all aspects to ensure that there are no conflicts or logical contradictions in data.

**Views** are reports calculated using the data in the tables and contain various statistics such as net assets, categorized income and expenses, and ROI. Whenever the data in any table changes, all views are immediately recalculated and updated. Typically the views are updated so quickly that the user is often unaware of the delay. View updates do not need to be triggered manually.

Some views are user-oriented reports, and some views are intermediate calculations used by other views. Users usually don't need to pay attention to these intermediate results views. However, if you have doubts about some report data and want to check the calculation process, you can check these intermediate result views. Also, for advanced users who write their own SQL queries, intermediate result views may be useful.

All the views whose names start with `check` are used to check data consistency. When the data is consistent, these `check` views should contain no records. If TataruBook finds that the contents of a view beginning with `check` are not empty, it will report the associated data error on the command-line and prompt the user to fix it.

# Simplified double-entry bookkeeping

![Bookkeeping data architecture]({{ site.baseurl }}/assets/images/architecture.png)

TataruBook follows the "two accounts must be involved in every transaction" requirement of [double-entry bookkeeping](https://en.wikipedia.org/wiki/Double-entry_bookkeeping). However, it does not use the professional accounting method of account categorization and the [debit and credit rules for each type of account](https://en.wikipedia.org/wiki/Debits_and_credits). Strict adherence to professional accounting methods would make bookkeeping too complex and difficult to understand for the average individual or family. TataruBook therefore uses a simpler and more intuitive method of bookkeeping, dividing all accounts into just two categories:

- **Internal account**: A positive amount of a change means an increase in asset, a negative amount means an decrease in asset; a positive balance means asset owned, a negative balance means external liabilities.
- **external account**: A positive amount of a change indicates an expense and a negative amount indicates income or interest.

Thus, the sum of the changes in the two accounts involved in each transaction is always exactly equal to $$ 0 $$ (when the two accounts contain the same assets). Adding up the balances of all the internal accounts at any given moment gives you the net worth at that time.

If you have studied professional accounting methods, then be aware that in TataruBook's simplified double-entry bookkeeping, there are some terms that don't mean exactly the same thing as the terms used in the professional accounting methods. For example, **asset** in TataruBook means a currency or a type of tradable ownership with a separate price per unit, NOT **liabilites** plus **equity** in the **accounting equation**.
{: .notice}

In the bookkeeping method used by TataruBook, the two accounts involved in each transaction can contain different assets (e.g., two different currencies, or one a currency and the other a stock), such that the amount of change in the two accounts resulting from the transaction no longer adds up to $$ 0 $$ (except when the unit prices of the two assets happen to be equal). TataruBook requires that an asset be designated as **standard asset** (i.e., home currency), and all other assets are converted to standard asset at the corresponding unit price on certain date.

In some views' names, non-standard assets may be named as **shares** and standard assets may be named as **cash**, but note that this is just an analogy for ease of understanding, and does not strictly correspond to shares and cash in reality. For example, if a user defines a standard asset as US dollar, then his Japanese yen cash holdings will be treated as "shares" by TataruBook, because the unit price of Japanese yen fluctuates, and Japanese yen cash holdings may generate gains or losses when valued in US dollar. The amount of asset may not be a whole number, e.g. $$ 0.1 $$ or $$ 0.001 $$ is allowed for bookkeeping purposes.

# Tables

## asset_types

A list of assets. In TataruBook, an **asset** is a type of tradable ownership with **separate unit price**, such as a currency, a stock, a mutual fund, and so on.

If you use only one currency and do not hold or trade other investments or commodities, then your `asset_types` table has only one record: the currency you use.

**Fields**
- `asset_index` (integer): automatically generated index, need not to input.
- `asset_name` (string): name of the asset, not allowed to be empty. Used only for display in views, does not affect calculations.
- `asset_order` (integer): asset serial number, not allowed to be empty. It is only used for sorting the assets when displayed in views (assets with smaller serial numbers will be listed first), and does not affect calculations. If sorting is not required, you can set `asset_order` to $$ 0 $$ for all assets.

## standard_asset

The standard asset, which is used as the **home currency** for bookkeeping purposes. All other assets are converted to standard asset to measure the market value.

**Fields**
- `asset_index` (integer): asset index, not allowed to be empty, must be an index of one of the assets present in the [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.

**Constraints**
- Only one record is allowed in this table.
- The `asset_index` of any record in the [prices]({{ site.baseurl }}/tables_and_views.html#prices) table is not allowed to be equal to the `asset_index` in this table because the unit price of standard asset is fixed at $$ 1 $$. (Checked by [check_standard_prices]({{ site.baseurl }}/tables_and_views.html#check_standard_prices) view)

## accounts

List of accounts. An **account** is an entity with **separate balance**. A person can have multiple accounts in a bank, such as current account, investment account, credit account, etc., so care should be taken when naming accounts.

The unit used for the balance of an account is defined by the asset it contains. For example, if the asset contained in the account is a currency, the account balance is the value in that currency; if the asset contained in the account is a stock, the account balance is the number of shares.

The account balance is not always positive; when the balance is negative, it means that there is a liability in the account. For example, most of the time the balance of a credit card is negative, indicating that the user has a future liability on this account that needs to be returned.

There are two types of accounts: **internal accounts** and **external accounts**, see [simplified double-entry bookkeeping]({{ site.baseurl }}/tables_and_views.html#simplified-double-entry-bookkeeping). An external account represents a class of income/expenses, and the user can customize how the income/expenses are categorized by defining external accounts.

**Fields**
- `account_index` (integer): automatically generated index, need not to input.
- `account_name` (string): account name, not allowed to be empty. Used only for display in views, does not affect calculations.
- `asset_index` (integer): index of the assets contained in the account. Not allowed to be empty, must be an index of one of the assets present in the [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `is_external` (`0` or `1`): a value of `0` indicates an internal account, a value of `1` indicates an external account.

## interest_accounts

A list of interest accounts. **interest accounts** are a special class of **external accounts** that provide interest earnings in transactions such as interests on deposits and financial income.

When a transaction arises between an interest account and an internal account, TataruBook assumes that the internal account generates interest earning and calculates the associated **interest rate**. For this calculation, TataruBook considers the **average daily balance** of that internal account to be the denominator of the interest rate. See [interest_rates]({{ site.baseurl }}/tables_and_views.html#interest_rates) view.

In order not to distort the interest rate data, transactions describing fund/stock distributions should not be related to interest accounts. This is because these distributions are paid in cash to another internal account, not to the internal account in which the fund/share itself resides. To see what way fund/share distributions and splits are recorded, see the example in [return_on_shares]({{ site.baseurl }}/tables_and_views.html#return_on_shares) view.

**Fields**
- `account_index` (integer): the account index, not allowed to be empty, must be one of the account indexes present in [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.

**Constraints**
- All interest accounts must be external, i.e., the `is_external` field corresponding to `1` in [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table. (checked by [check_interest_account]({{ site.baseurl }}/tables_and_views.html#check_interest_account) view)

## postings

List of transactions. According to [simplified double-entry bookkeeping]({{ site.baseurl }}/tables_and_views.html#simplified-double-entry-bookkeeping), each transaction can be viewed as a transfer of value from one account to another. Thus each transaction record in this list contains a **source account** and a **destination account**, and the transaction makes the source account's balance smaller and the destination account's balance larger.

As long as the source and destination account contains the same asset, the amount of change in the destination account is equal to the opposite of the amount of change in the source account, i.e., they add up to $$ 0 $$. In this case, only the amount of change in the source account needs to be entered and the amount of change in the destination account will be calculated automatically. When the source and destination account contains different assets, it is necessary to use [posting_extras]({{ site.baseurl }}/tables_and_views.html#posting_extras) table as an aid to record the amount of destination account's change in this transaction.

**Fields**
- `posting_index` (integer): automatically generated index, need not to input. Usually, the index of the record entered later is larger than the one entered first.
- `trade_date` (string): the date of the transaction, not allowed to be empty, fixed to ISO 8601 format: yyyy-mm-dd. For transactions occurring on the same day, the order is determined according to the `posting_index`, with smaller indexes coming first, and larger ones coming second.
- `src_account` (integer): source account index, not allowed to be empty, must be one of the account indexes present in the [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `src_change` (float): the amount of change in the source account, not allowed to be empty. The value must be less than or equal to $$ 0 $$.
- `dst_account` (integer): the destination account index, not allowed to be empty, must be one of the account indexes present in the [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `comment` (string): transaction comment information, can be empty. Used only for display in views, does not affect calculations.

**Constraints**
- The value of `src_account` in a record cannot equal the value of `dst_account`. (Checked by [check_same_account]({{ site.baseurl }}/tables_and_views.html#check_same_account) view)
- The source and destination account in a record cannot both be external account. (Checked by [check_both_external]({{ site.baseurl }}/tables_and_views.html#check_both_external) view) (New in v1.1)
- When the source or destination account is an external account in a record, the external account must either contains standard asset or the same asset as another account. (Checked by [check_external_asset]({{ site.baseurl }}/tables_and_views.html#check_external_asset) view) (New in v1.1)

Users who are new to bookkeeping may be wondering how to import the existing balances for each account into a DB file. The recommended approach is to create an external account called `Opening balance` and for each internal account that needs to have its balance brought forward, add a transaction record transferring value from `Opening balance` to that internal account.
{: .notice}

## posting_extras

The amount of change in the destination account when the source and destination account contains different assets. See related description in [postings]({{ site.baseurl }}/tables_and_views.html#postings) table.

**Fields**
- `posting_index` (integer): the transaction index, not allowed to be empty, must be one of the indexes present in [postings]({{ site.baseurl }}/tables_and_views.html#postings) table.
- `dst_change` (floating point): the amount of change in the destination account, not allowed to be empty. The value must be greater than or equal to $$ 0 $$.

**Constraints**
- The transaction is not allowed to have any `posting_extras` record related when the source and destination account contains the same asset. In this situation, the amount of change in the destination account is equal to the opposite of the amount of change in the source account. (Checked by [check_same_asset]({{ site.baseurl }}/tables_and_views.html#check_same_asset) view)
- When the source and destination account contains different assets, the transaction must have a `posting_extras` record related to record the amount of change in the specified destination account. (Checked by [check_diff_asset]({{ site.baseurl }}/tables_and_views.html#check_diff_asset) view)

## prices

The unit price of an asset, used to convert a non-standard asset to the [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset) (home currency) when needed. An asset can have at most one unit price per day, i.e., the unit price of the asset at the end of that day. For assets such as stocks, which have intraday price movements, the asset's unit price is the closing price of the day. Therefore, if an asset is bought or sold in the transaction for a given day, the actual unit price (real-time price) in that transaction can be unequal to the unit price (closing price) of that asset in the `prices` table for that day. (See [start_stats]({{ site.baseurl }}/tables_and_views.html#start_stats) view for an example)

**Fields**
- `price_date` (string): date, not allowed to be empty, fixed to ISO 8601 format: yyyy-mm-dd.
- `asset_index` (integer): asset index, not allowed to be empty, must be one of the asset indexes present in the [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `price` (floating point): the unit price (i.e., $$ 1 $$ unit of this asset is equal to how many units of standard asset), not allowed to be empty.

**Constraints**
- There should be no price record associated with the standard asset. (Checked by [check_standard_prices]({{ site.baseurl }}/tables_and_views.html#check_standard_prices) view)
- There should be no more than one price record for one asset on one day, i.e., the `price_date` and `asset_index` of any two records cannot both be the same.
- On [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), all non-standard assets must have a price record associated. (Checked by [check_absent_price]({{ site.baseurl }}/tables_and_views.html#check_absent_price) view)
- If a transaction occurs between two accounts containing the same non-standard asset (or containing different non-standard assets), no matter either account is internal or external, the non-standard asset contained by each account that has an amount of change other than $$ 0 $$ in the transaction must have a price record associated on the day of the transaction. For example: if HK dollar is a non-standard asset, then when HK dollar is used to buy a HK stock, the unit price of HK dollar and the unit price of that stock (noting that they are prices measured in the standard asset) must both be present on the day of the transaction. This is because when calculating ROI on these two accounts, they both have an inflow or outflow on the day of the transaction and the value of the inflow/outflow needs to be calculated. (Checked by [check_absent_price]({{ site.baseurl }}/tables_and_views.html#check_absent_price) view)

## start_date

The start date of the statistics period, which serves as the starting point of the statistics period for some views. Note that transactions on the start date are not included in the statistics, because statistics period starts at the end of the day of the start date. For example, to statistically analyze financial data for the entire year 2023, the `start_date` would be `2022-12-31` and the `end_date` would be `2023-12-31`.

**Fields**
- `val` (string): start date, not allowed to be empty, fixed to ISO 8601 format: yyyy-mm-dd.

**Constraints**
- Only one record is allowed in this table.
- The start date must be less than the end date.

## end_date

The end date of the statistics period, which serves as the ending point of the statistics period for some views.  Note that transactions on the end date are included in the statistics. For example, to statistically analyze financial data for the entire year 2023, the `start_date` would be `2022-12-31` and the `end_date` would be `2023-12-31`.

**Fields**
- `val` (string): end date, not allowed to be empty, fixed to ISO 8601 format: yyyy-mm-dd.

**Constraints**
- Only one record is allowed in this table.
- The end date must be greater than the start date.

# Views

## single_entries

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

Converts the double-entry transaction records into single-entry. Each record in the [postings]({{ site.baseurl }}/tables_and_views.html#postings) table becomes two records in this view.

**Fields**
- `posting_index`: `posting_index` from [postings]({{ site.baseurl }}/tables_and_views.html#postings) table.
- `trade_date`: `trade_date` from [postings]({{ site.baseurl }}/tables_and_views.html#postings) table.
- `account_index`: `src_account` or `dst_account` from [postings]({{ site.baseurl }}/tables_and_views.html#postings) table.
- `amount`: the amount of change in the transaction for this account, from `src_change` (or its opposite) in the [postings]({{ site.baseurl }}/tables_and_views.html#postings) table; or from `dst_change` in the [posting_extras]({{ site.baseurl }}/tables_and_views.html#posting_extras) table.
- `target`: the account of the other party in the transaction, from `src_account` or `dst_account` in [postings]({{ site.baseurl }}/tables_and_views.html#postings) table.
- `comment`: `comment` from [postings]({{ site.baseurl }}/tables_and_views.html#postings) table.

## statements

Converts the double-entry bookkeeping transaction records into single-entry and displays account information related to each transaction.

**Fields**
- Contains all fields in [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view, as well as:
- `src_name`, `target_name`: `account_name` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `asset_index`: `asset_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `is_external`: `is_external` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `balance`: the balance of the account after this transaction (derived from all previous transaction records). For external accounts, the opposite of balance represents the sum of income/expenses for that category.

**Examples**

Assume that the existing table contents are as follows:

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | Garlond Ironworks shares | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | Sharlayan Bank current | 1 | 0 |
| 2 | Moogle:Garlond Ironworks shares | 2 | 0 |
| 3 | Food and Beverages | 1 | 1 |
| 4 | Salary | 1 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comments |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-06 | 4 | -50000.0 | 1 | Monthly salary |
| 2 | 2023-01-07 | 1 | -67.5 | 3 | Dinner at the Last Stand |
| 3 | 2023-01-09 | 1 | -13000.0 | 2 | Buy shares |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 3 | 260.0 |

Then the `statements` view contents are:

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-06 | 1 | 50000.0 | 4 | Monthly salary | Sharlayan Bank current | 1 | 0 | Salary | 50000.0 |
| 1 | 2023-01-06 | 4 | -50000.0 | 1 | Monthly salary | Salary | 1 | 1 | Sharlayan Bank current | -50000.0 |
| 2 | 2023-01-07 | 1 | -67.5 | 3 | Dinner at the Last Stand | Sharlayan Bank current | 1 | 0 | Food and Beverages | 49,932.5 |
| 2 | 2023-01-07 | 3 | 67.5 | 1 | Dinner at the Last Stand | Food and Beverages | 1 | 1 | Sharlayan Bank current | 67.5 |
| 3 | 2023-01-09 | 1 | -13000.0 | 2 | Buy shares | Sharlayan Bank current | 1 | 0 | Moogle:Garlond Ironworks shares | 36932.5 |
| 3 | 2023-01-09 | 2 | 260.0 | 1 | Buy shares | Moogle:Garlond Ironworks shares | 2 | 0 | Sharlayan Bank current | 260.0 |

Note: The `statements` view is more like the single-entry billing statements that people are usually used to. If you only want to see the movement records for a particular account, you can use other software to open the DB file and filter by `account_index` or `src_name`. For example, filtering on a record with `account_index` of `1` will show all historical transactions and balance changes for `Sharlayan Bank current`.

## start_balance

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

The balances of all internal accounts which has a balance greater than $$ 0 $$ at the end of the day [start_date]({{ site.baseurl }}/tables_and_views.html#start_date).

**Fields**
- `date_val`: `val` from [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) table.
- `account_index`: `account_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_name`: `account_name` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `balance`: the balance of the account obtained by accumulating the amount of change from `start_date` and all previous transaction records.
- `asset_index`: `asset_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.

## start_values

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

The balances of all internal accounts which has a balance greater than $$ 0 $$ at the end of the day [start_date]({{ site.baseurl }}/tables_and_views.html#start_date), as well as the market values measured in [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset) calculated according to the unit price of the day.

**Fields**
- Contains all fields from [start_balance]({{ site.baseurl }}/tables_and_views.html#start_balance) view, as well as:
- `price`: `price` from [prices]({{ site.baseurl }}/tables_and_views.html#prices) table; in the case of the standard asset, the value is $$ 1 $$.
- `market_value`: the market value calculated by $$ \text{price} \times \text{balance} $$.

## start_stats

At the end of the day [start_date]({{ site.baseurl }}/tables_and_views.html#start_date), the balances of all internal accounts which has a balance greater than $$ 0 $$, as well as the market values measured in [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset) calculated according to each balance multiplied by the unit price of the day, as well as the percentage of each account's market value to the total value (i.e. the sum of all accounts' market values).

**Fields**
- Contains all fields in [start_values]({{ site.baseurl }}/tables_and_views.html#start_values) view, as well as:
- `asset_order`: `asset_order` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `asset_name`: `asset_name` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `proportion`: the proportion of this account's market value to the sum of all accounts' market values.

**Examples**

Assume following additional tables are added to existing tables in the example in [statements]({{ site.baseurl }}/tables_and_views.html#statements) view:

`start_date`

| val |
|:-:|
| 2023-1-9 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-1-9 | 2 | 51 |

Then the `start_stats` view contents are:

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-01-09 | 1 | Sharlayan Bank current | 36932.5 | 1 | Gil | 1.0 | 36932.5 | 0.7358 |
| 0 | 2023-01-09 | 2 | Moogle:Garlond Ironworks shares | 260.0 | 2 | Garlond Ironworks shares | 51.0 | 13260.0 | 0.2642 |

Note: Note that the values in the `balance` column are the same as the balances in the `statements` view for each account on that date; external accounts do not appear in the `start_stats` view. The purchase of `Garlond Ironworks shares` is at a unit price of $$ 13,000 \div 260 = 50 $$ for the transaction at that time, but the price record (which denotes the closing price) in the `prices` table on `2023-1-9` is $$ 51 $$, and the market value is based on unit price $$ 51 $$. This example shows that the real-time trading price can be different from the closing price.

## start_assets

At the end of the day [start_date]({{ site.baseurl }}/tables_and_views.html#start_date), the quantity of each asset, as well as the market value measured in [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset) calculated according to the unit price of the day, as well as the percentage of each asset's value to the total value.

**Fields**
- `asset_order`: `asset_order` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `date_val`: `val` from [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) table.
- `asset_index`: `asset_index` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `asset_name`: `asset_name` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `amount`: the amount of asset calculated by accumulating the balances of all accounts containing this asset.
- `price`: `price` from [price]({{ site.baseurl }}/tables_and_views.html#prices) table; in the case of the standard asset, the value is $$ 1 $$.
- `total_value`: the market value calculated by $$ \text{price} \times \text{amount} $$.
- `proportion`: the proportion of the value of this asset to the sum of the values of all assets.

## diffs

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

Statistics on the amount of change per account between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date). The transactions on `start_date` are not counted, transactions on `end_date` are counted.

**Fields**
- `account_index`: `account_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_name`: `account_name` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `amount`: the amount of change obtained by totaling the amount of change for all transaction records between `start_date` and `end_date`.
- `asset_index`: `asset_index` from the [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.

## comparison

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

The balance of each account at the end of [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), and the amount of change between the two dates.

**Fields**
- Contains the `account_index`, `account_name`, and `asset_index` fields from [diffs]({{ site.baseurl }}/tables_and_views.html#diffs) view, as well as:
- `start_amount`: from `balance` in [start_balance]({{ site.baseurl }}/tables_and_views.html#start_balance) view.
- `diff`: `amount` from [diffs]({{ site.baseurl }}/tables_and_views.html#diffs) view; or $$ 0 $$ if the account balance has not changed between the two dates.
- `end_amount`: the ending balance calculated by $$ \text{start_amount} + \text{diff} $$.

## end_values

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

The balances of all internal accounts which has a balance greater than $$ 0 $$ at the end of the day [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), as well as the market values measured in [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset) calculated according to the unit price of the day.

**Fields**
- All fields are the same as in [start_values]({{ site.baseurl }}/tables_and_views.html#start_values) view, but the statistics are taken for [end_date]({{ site.baseurl }}/tables_and_views.html#end_date).

## end_stats

At the end of the day [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), the balances of all internal accounts which has a balance greater than $$ 0 $$, as well as the market values measured in [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset) calculated according to the unit price of the day, as well as the percentage of each account's value to the total value.

Note: The [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) table and the [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) table must each have one record for the `end_stats` view to display correctly.
{: .notice--warning}

**Fields**
- All fields are the same as in [start_stats]({{ site.baseurl }}/tables_and_views.html#start_stats) view, but the statistics are taken for [end_date]({{ site.baseurl }}/tables_and_views.html#end_date).

**Examples**

Assume following additional tables are added to existing tables in the example in [statements]({{ site.baseurl }}/tables_and_views.html#statements) view:

`start_date`

| val |
|:-:|
| 2023-1-5 |

`end_date`

| val |
|:-:|
| 2023-1-9 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-1-9 | 2 | 51 |

Then the `end_stats` view contents are:

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-01-09 | 1 | Sharlayan Bank current | 36932.5 | 1 | Gil | 1.0 | 36932.5 | 0.7358 |
| 0 | 2023-01-09 | 2 | Moogle:Garlond Ironworks shares | 260.0 | 2 | Garlond Ironworks Shares | 51.0 | 13260.0 | 0.2642 |

Note: You can see that the content of the `end_stats` view is almost the same as the [start_stats]({{ site.baseurl }}/tables_and_views.html#start_stats) view, with the only difference being that the statistics date is `end_date`.

## end_assets

At the end of the day [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), the quantity of each asset, as well as the market value measured in [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset) calculated according to the unit price of the day, as well as the percentage of each asset's value to the total value.

Note: The [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) table and the [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) table must each have one record for the `end_assets` view to display the correct content.
{: .notice--warning}

**Fields**
- All fields are the same as in [start_assets]({{ site.baseurl }}/tables_and_views.html#start_assets) view, but the statistics are taken for [end_date]({{ site.baseurl }}/tables_and_views.html#end_date).

## external_flows

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

Transactions between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) for each **external account**, and the unit price of the according asset on the day of the transaction. Transactions on the day of `start_date` are not counted, transactions on the day of `end_date` are counted. Note that each external account (other than the interest account) represents a specific category of income and expenses.

Although the view name is **external flows**, unlike the definition of **external flows** in [Rate of Return]({{ site.baseurl }}/rate-of-return.html), this view includes interests.
{: .notice}

**Fields**
- `trade_date`: `trade_date` from [postings]({{ site.baseurl }}/tables_and_views.html#postings) table.
- `asset_order`: `asset_order` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `account_index`: `account_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_name`: `account_name` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `amount`: `amount` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.
- `asset_index`: `asset_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `asset_name`: `asset_name` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `price`: `price` from [price]({{ site.baseurl }}/tables_and_views.html#prices) table; value `1` if standard asset.

## income_and_expenses

The total amount of change with transactions between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) per each **external account**, as well as the corresponding market value measured in standard asset. Transactions on the `start_date` are not counted, transactions on the `end_date` are counted. Note that external accounts (other than interest accounts) represent specific categories of income and expenses, so this view can be viewed as a categorized count of income, expenses, and interest over the statistics period.

**Fields**
- Contains `asset_order`, `account_index`, `account_name`, `asset_ index`, `asset_name` fields in [external_flows]({{ site.baseurl }}/tables_and_views.html#external_flows) view, as well as:
- `total_amount`: the total amount of change (not converted to standard asset) obtained by accumulating the amount of change in all transaction records for this external account between `start_date` and `end_date`.
- `total_value`: the total market value obtained by converting the amount of change in each transaction to standard assets at the asset's unit price of the day and adding it up. Assuming that there are a total of $$ n $$ transactions in an external account, and the amount of change in each transaction is $$ a_1 \dots a_n $$ respectively, and the unit price of the asset contained in the account on the day of each transaction is $$ p_1 \dots p_n $$ respectively, then the total value will be: $$ \displaystyle\sum_{i=1}^{n} p_ia_i $$.

**Examples**

Assume that the existing table contents are as follows:

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | MGP | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | Sharlayan Bank current | 1 | 0 |
| 2 | Manderville Gold Saucer account | 2 | 0 |
| 3 | Salary | 1 | 1 | 1 | 1
| 4 | MGP spending | 2 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comments |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-02-06 | 3 | -50000.0 | 1 | Monthly salary |
| 2 | 2023-02-07 | 1 | -30000.0 | 2 | Purchase MGP |
| 3 | 2023-02-12 | 2 | -30.0 | 4 | Gaming entertainment |
| 4 | 2023-02-15 | 2 | -100.0 | 4 | Purchase accessories |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 2 | 300.0 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-02-12 | 2 | 90.0 |
| 2023-02-15 | 2 | 110.0 |

Then the content of the `income_and_expenses` view is:

| asset_order | account_index | account_name | total_amount | asset_index | asset_name | total_value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 3 | Salary | -50000.0 | 1 | Gil | -50000.0 |
| 0 | 4 | MGP spending | 130.0 | 2 | MGP | 13700.0 |

Note: Note that the amount of change in the external account is equal to the opposite of the amount of change in the internal account, e.g., the `Salary` account's `total_amount` is $$ -50000.0 $$, which means that the internal account has a total of $$ 50000.0 $$ in salary income.

If an external account contains the standard asset (such as `Gil` in the example), the total market value is equal to the amount of the change accrued; however, if an external account contains non-standard asset (such as `MGP` in the example), each transaction's amount is converted to the standard asset at the unit price on the day the transaction occurred, and then accumulated. In this example, the `total_value` of `MGP` is calculated as $$ 30 \times 90 + 100 \times 110 = 13700 $$.

## portfolio_stats

There is only one record: consider the set of all internal accounts as a **portfolio**, showing the portfolio's net assets at the beginning and ending of the statistics period, as well as total income and expenses, investment profit or loss during the statistics period.

**Fields**
- `start_value`: market value at the beginning of the statistics period, obtained by accumulating `market_value` from [start_values]({{ site.baseurl }}/tables_and_views.html#start_values) view.
- `end_value`: market value at the ending of the statistics period, obtained by accumulating `market_value` from [end_values]({{ site.baseurl }}/tables_and_views.html#end_values) view.
- `net_outflow`: the value of net outflow during the statistical period, obtained by accumulating `total_value` from all external accounts other than [interest_accounts]({{ site.baseurl }}/tables_and_views.html#interest_accounts) in [income_and_expenses]({{ site.baseurl }}/tables_and_views.html#income_and_expenses) view. Note that interest is not an inflow or outflow. If there is a net inflow during the statistics period, then this value is negative.
- `interest`: the total amount of interest earnings incurred during the statistics period, obtained  by accumulating `total_value` from all [interest_accounts]({{ site.baseurl }}/tables_and_views.html#interest_accounts) in [income_and_expenses]({{ site.baseurl }}/tables_and_views.html#income_and_expenses) view.
- `net_gain`: the total gain (or total loss) generated by the investments during the statistics period, calculated as $$ \text{end_value} + \text{net_outflow} - \text{start_value} $$. That is, all changes in net assets are considered investment income (or loss) except for changes in net assets resulting from income and expenses. Interest earnings are part of investment income.
- `rate_of_return`: the rate of return on investments calculated using the [simple Dietz method]({{ site.baseurl }}/rate_of_return.html#simple-dietz-method).

## flow_stats

The amount of change in all transactions which involves **external account** between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) per each internal account. Transactions on the day of `start_date` are not counted, transactions on the day of `end_date` are counted. Note that external accounts (other than interest accounts) represent specific categories of income and expenses, so this view can be viewed as a categorized count of income, expenses, and interest by each internal account separately during the statistics period.

Note that there are two differences between this view compared to [income_and_expenses]({{ site.baseurl }}/tables_and_views.html#income_and_expenses) view:
1. In `flow_stats`, different internal accounts are counted separately, but in `income_and_expenses` the amounts of transactions from different internal accounts and the same external account are added up and combined;
1. `flow_stats` only shows statistics that are aggregated by the amount of change in the corresponding asset, but `income_and_expenses` also shows market values converted to standard asset based on the unit price of the asset.

**Fields**
- `flow_index`: external account index from `account_index` in [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `flow_name`: external account name from `account_name` in [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_index`: internal account index from `account_index` in [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_name`: internal account name from `account_name` in [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `amount`: total amount (not converted to standard asset) obtained by accumulating the amount of change in all transaction records between `start_date` and `end_date` for this internal account and this external account.

**Example**

Assume that on the base of existing tables in the example in [income_and_expenses]({{ site.baseurl }}/tables_and_views.html#income_and_expenses) view, the following additional records are added to these two tables:

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 5 | Sharlayan workplace pension | 1 | 0 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 2023-02-06 | 3 | -10000.0 | 5 | Workplace pension contribution |

Then the `flow_stats` view contents are:

| flow_index | flow_name | account_index | account_name | amount |
|:-:|:-:|:-:|:-:|:-:|
| 3 | Salary | 1 | Sharlayan Bank current | -50000.0 |
| 3 | Salary | 5 | Sharlayan workplace pension | -10000.0 |
| 4 | MGP spending | 2 | Manderville Gold Saucer account | 130.0 |

Note: `Salary` has separate statistics for the two different internal accounts, compared to the `income_and_expenses` view which will only show one `salary` record (all internal accounts totaled together). In addition, `MGP spending` counts quantities in `MGP`, not the standard asset `Gil`.

## share_trade_flows

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

This is a new view added in v1.2.
{: .notice}

Transactions between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) that involves internal account (indicated by `target` field) which contains non-standard asset, as well as the amount of change which will be used to calculate the inflow or outflow value in each transaction. This data is used to calculate the ROI on non-standard asset.

**Fields**
- `posting_index`：`posting_index` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.
- `trade_date`：`trade_date` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.
- `account_index`：`account_index` or `target` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view: `account_index` if the `amount` in [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view is not $$ 0 $$, otherwise `target`.
- `amount`：`amount` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view or the negtive number of `dst_change` from the corresponding record of [posting_extras]({{ site.baseurl }}/tables_and_views.html#posting_extras) table: `amount` if the `amount` in [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view is not $$ 0 $$, otherwise the negtive number of `dst_change`.
- `target`：`target` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.
- `comment`：`comment` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.
- `account_name`：The account name of `target`, i.e. `account_name` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.
- `asset_index`：The index of asset that the `target` account contains, i.e. `asset_index` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.
- `asset_name`：The name of asset that the `target` account contains, i.e. `asset_name` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.
- `asset_order`：The order of asset that the `target` account contains, i.e. `asset_order` from [single_entries]({{ site.baseurl }}/tables_and_views.html#single_entries) view.

## share_trades

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

Transactions between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) that involves internal account which contains non-standard asset, as well as the market values of the change in these transactions measured in standard asset. This data is used to calculate the ROI on non-standard asset.

If you think of non-standard assets as stocks, then this view can be interpreted as the cost of buying or the income from selling in each stock trade.

**Fields**
- Contains all the fields in [share_trade_flows]({{ site.baseurl }}/tables_and_views.html#share_trade_flows) view, as well as:
- `cash_flow`: the amount of change in the transaction converted to the market value of standard asset at that day's unit price.

## share_stats

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

The required minimum initial cash between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date) for each internal account containing non-standard asset if the balance cannot be less than $$ 0 $$, as well as the incremental amount of cash (measured in standard asset) obtained by trading and holding the asset in that internal account. See the introduction to the [minimum initial cash method]({{ site.baseurl }}/rate_of_return.html#minimum-initial-cash-method) to understand the data in this view.

**Fields**
- `asset_order`: `asset_order` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `asset_index`: `asset_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `asset_name`: `asset_name` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `account_index`: `account_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_name`: `account_name` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `min_inflow`: the required minimum initial cash for this account during the statistics period if the balance cannot be less than $$ 0 $$.
- `cash_gained`: the incremental amount of cash (measured in standard asset) obtained by trading and holding the asset in this account.

## return_on_shares

The rate of return on investment for each internal account containing non-standard asset between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), the market value is measured in standard asset. Transactions on the day of `start_date` are not counted, transactions on the day of `end_date` are counted. The rate of return is calculated using the [minimum initial cash method]({{ site.baseurl }}/rate_of_return.html#minimum-initial-cash-method).

**Fields**
- `asset_order`: `asset_order` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `asset_index`: `asset_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `asset_name`: `asset_name` from [asset_types]({{ site.baseurl }}/tables_and_views.html#asset_types) table.
- `account_index`: `account_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_name`: `account_name` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `start_amount`: the balance at the start of the statistics period. From `start_amount` in [comparison]({{ site.baseurl }}/tables_and_views.html#comparison) view.
- `start_value`: the market value at the start of the statistics period. From `market_value` in [start_values]({{ site.baseurl }}/tables_and_views.html#start_values) view, or $$ 0 $$ if this account is not present in `start_values`.
- `diff`: amount of change during the statistics period. From `diff` in [comparison]({{ site.baseurl }}/tables_and_views.html#comparison) view.
- `end_amount`: the balance at the end of the statistics period. From `end_amount` in [comparison]({{ site.baseurl }}/tables_and_views.html#comparison) view.
- `end_value`: the market value at the end of the statistics period. From `market_value` in [end_values]({{ site.baseurl }}/tables_and_views.html#end_values) view, or $$ 0 $$ if this account is not present in `end_values`.
- `cash_gained`: realized gain. From `cash_gained` in [share_stats]({{ site.baseurl }}/tables_and_views.html#share_stats) view, or $$ 0 $$ (if this account is not present in `share_stats`).
- `min_inflow`: the required minimum net inflow. From `min_inflow` in [share_stats]({{ site.baseurl }}/tables_and_views.html#share_stats) view, or $$ 0 $$ (if this account is not present in `share_stats`).
- `profit`: the profit (or loss) on the investment in this account, calculated as $$ \text{cash_gained} + \text{end_value} - \text{start_value} $$.
- `rate_of_return`: the rate of return on investment in this account, calculated using the [minimum initial cash method]({{ site.baseurl }}/rate_of_return.html#minimum-initial-cash-method).

**Example 1**

Assume that the existing table contents are as follows:

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | Garlond Ironworks shares | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | Sharlayan Bank current | 1 | 0 |
| 2 | Moogle:Garlond Ironworks shares | 2 | 0 |
| 3 | Opening balance in Gil | 1 | 1 |
| 4 | Opening balance in Garlond Ironworks shares | 2 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comments |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022-12-31 | 3 | -10000.0 | 1 | Brought forward |
| 2 | 2022-12-31 | 4 | -10.0 | 2 | Brought forward |
| 3 | 2023-02-08 | 1 | -60.0 | 2 | Buy shares |
| 4 | 2023-03-08 | 2 | -6.0 | 1 | Sell shares |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 3 | 5.0 |
| 4 | 90.0 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2022-12-31 | 2 | 10.0 |
| 2023-06-30 | 2 | 11.0 |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-06-30 |

Then the `return_on_shares` view contents are:

| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2 | Garlond Ironworks shares | 2 | Moogle:Garlond Ironworks shares | 10.0 | 100.0 | -1.0 | 9.0 | 99.0 | 30.0 | 60.0 | 29.0 | 0.18125 |

Note: This example is very similar to **Example 1** in [minimum initial cash method]({{ site.baseurl }}/rate_of_return.html#minimum-initial-cash-method), except that the intervals between inflows and outflows are different, so the resulting rate of return is the same as in that example. Note that the `prices` table only needs to provide the unit prices at the beginning and end of the statistics period, not the unit price at the time of each transaction, since the transaction itself already reflects the unit price information.

**Example 2**

Assume that the existing table contents are as follows:

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | MGP | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | Manderville Gold Saucer account | 2 | 0 |
| 2 | Opening balance in MGP | 2 | 1 |
| 3 | Interest in MGP | 2 | 1 |

`interest_accounts`

| account_index |
|:-:|
| 3 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022-12-31 | 2 | -1000.0 | 1 | Brought forward |
| 2 | 2023-06-21 | 3 | -10.0 | 1 | Interest payment |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2022-12-31 | 2 | 10.0 |
| 2023-06-21 | 2 | 11.0 |
| 2023-06-30 | 2 | 12.0 |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-06-30 |

Then the `return_on_shares` view contents are:

| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2 | 金碟币 | 1 | 金碟钱包 | 1000.0 | 10000.0 | 10.0 | 1010.0 | 12120.0 | 0 | 0 | 2120.0 | 0.212 |

Description: `MGP` is a non-standard asset, and it has interest earned. In this case, the `return_on_shares` view calculates the overall return including interest earnings. The separate interest earnings can be checked in the [interest_rates]({{ site.baseurl }}/tables_and_views.html#interest_rates) view. Remember to add interest account to `interest_accounts` table. In this example, if the record in `interest_accounts` is missing, things will become very differenet.

## interest_stats

This view serves as an intermediate process for the calculations of the other views, and users usually don't need to care about this view.
{: .notice}

The interest earned by each internal account between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date).

**Fields**
- `account_index`: `account_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_name`: `account_name` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `asset_index`: `asset_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `amount`: interest earned on this account (not converted to standard asset) during the statistics period.

## interest_rates

The interest earned by each internal account between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), as well as the average daily balance, and the **interest rate** calculated according to the [modified Dietz method]({{ site.baseurl }}/rate_of_return.html#modified-dietz-method) for each account.

The rate of return shown in this view is only the rate of return on the interest component and does not include the return generated by changes in the price of the asset.

**Fields**
- `account_index`: `account_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `account_name`: `account_name` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `asset_index`: `asset_index` from [accounts]({{ site.baseurl }}/tables_and_views.html#accounts) table.
- `avg_balance`: the average daily balance (not converted to standard asset) of the account over the statistics period.
- `interest`: `amount` from [interest_stats]({{ site.baseurl }}/tables_and_views.html#interest_stats) view.
- `rate_of_return`: the return on investment (i.e., the interest rate) calculated using the [modified Dietz method]({{ site.baseurl }}/rate_of_return.html#modified-dietz-method).

**Examples**

Assume that the existing table contents are as follows:

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | Sharlayan Bank current | 1 | 0 |
| 2 | Salary | 1 | 1 |
| 3 | Spending | 1 | 1 |
| 4 | Gil interest | 1 | 1 |

`interest_accounts`

| account_index |
|:-:|
| 4 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comments |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-03-31 | 2 | -10000.0 | 1 | Monthly salary |
| 2 | 2023-09-30 | 1 | -10000.0 | 3 | Big-ticket Spending |
| 3 | 2023-12-21 | 4 | -100.0 | 1 | Interest payment |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-12-31 |

Then the `interest_rates` view contents are:

| account_index | account_name | asset_index | avg_balance | interest | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Sharlayan Bank current | 1 | 5016.44 | 100.0 | 0.02 |

Note: See [modified Dietz method]({{ site.baseurl }}/rate_of_return.html#modified-dietz-method) for interest rate calculation. Note that the `interest_rates` table calculates rate based on the amounts of the asset unit included in this account and does not convert them to standard asset, so changes in asset's unit prices are not reflected in the rate. To see the overall rate of return including changes in asset's unit prices, see [return_on_shares]({{ site.baseurl }}/tables_and_views.html#return_on_shares) view.

## periods_cash_flows

Consider the set of all internal accounts as a **portfolio** and show everyday's net inflow/outflow value into/from that portfolio between [start_date]({{ site.baseurl }}/tables_and_views.html#start_date) and [end_date]({{ site.baseurl }}/tables_and_views.html#end_date), only days that the net inflow/outflow value of which is not $$ 0 $$ are shown. The flows on the day of `start_date` are not counted, the flows on the day of `end_date` are counted. Interest earnings, as investment income, are not counted as inflows/outflows; transactions between external and internal accounts other than interest accounts are counted as inflows/outflows. At the beginning of the cycle, the net assets of the portfolio are treated as a net inflow; at the end of the cycle, the net assets of the portfolio are treated as a net outflow.

This view is the data needed to calculate the [internal rate of return (IRR)]({{ site.baseurl }}/rate_of_return.html#internal-rate-of-return-irr).

**Fields**
- `trade_date`: the date of the net inflow/outflow.
- `period`: the number of days that have elapsed since the start date.
- `cash_flow`: the net inflow/outflow on that date, converted to standard asset. Note that according to the definition of [internal rate of return (IRR)]({{ site.baseurl }}/rate_of_return.html#internal-rate-of-return-irr), inflows are negative and outflows are positive, which is different from the usual definition.

## check_standard_prices

Normally this view has no records. If a record appears, it means that a price record of the standard asset is present in the [prices]({{ site.baseurl }}/tables_and_views.html#prices) table, violating the constraint.

## check_interest_account

Normally this view has no records. If a record appears, it means that there are [interest accounts]({{ site.baseurl }}/tables_and_views.html#interest_accounts) that are internal accounts, violating the constraint.

## check_same_account

Normally this view has no records. If a record appears, it means that [postings]({{ site.baseurl }}/tables_and_views.html#postings) table contains records whose `src_account` and `dst_account` are the same, violating the constraint.

## check_both_external

This is a new view in v1.1.
{: .notice}

Normally this view has no records. If a record appears, it means that [postings]({{ site.baseurl }}/tables_and_views.html#postings) table contains records whose `src_account` and `dst_account` are both external accounts, violating the constraint.

## check_diff_asset

Normally this view has no records. If a record appears, it means that [postings]({{ site.baseurl }}/tables_and_views.html#postings) table contains records whose source and destination accounts contains different assets, but the [posting_extras table]({{ site.baseurl }}/tables_and_views.html#posting_extras) has no corresponding records, violating the constraint.

## check_same_asset

Normally this view has no records. If a record appears, it means that [postings]({{ site.baseurl }}/tables_and_views.html#postings) table contains records whose source and destination accounts contains the same asset, but the [posting_extras table]({{ site.baseurl }}/tables_and_views.html#posting_extras) has corresponding records, violating the constraint.

## check_external_asset

This is a new view added in v1.1.
{: .notice}

Normally this view has no records. If a record appears, it means that there is at least a record in [postings]({{ site.baseurl }}/tables_and_views.html#postings) table, of which the source or destination account is an external account, and the external account neither contains standard asset nor the same asset as another account, violating the constraint.

## check_absent_price

Normally this view has no records. If a record appears, it means that the [prices]({{ site.baseurl }}/tables_and_views.html#prices) table is missing unit prices for certain assets that need to be used on certain dates, violating the constraint.