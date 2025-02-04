---
title: The Calculation Methods of Rate of Return
---
This page describes some common methods of calculating the rate of return on investments.

# Some basic concepts

The rate of return is the investment performance of a particular **portfolio** over a particular **statistics period**.

A **portfolio** may contain only one underlying investment (account) or multiple underlying investments. Cash may be part of the portfolio - cash as an investment may seem counter-intuitive, but the percentage of cash in a portfolio often has a significant impact on investment performance, and cash positions should not be ignored when calculating the rate of return. If the portfolio contains only one account, the rate of return on the portfolio is also called the rate of return on that account.

A **statistics period** is a specified period of time, with the point in time at which the period begins called the **start** and the point in time at which the period ends called the **end**. Common statistics periods are full or half years. When the statistics period is not a full year, there are calculations that convert returns to **annualized returns**. TataruBook allows specifying any period of time in days as the statistics period and does not annualize the rate of returns.

The **market value** (or **value**) of a portfolio is calculated for all assets in the portfolio denominated in a currency. The currency used for denomination is referred to in TataruBook as [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset).

**External flows** refers to the flows of value between the portfolio and the outside which are **not results of investments**. Flows from the outside to the portfolio are called **inflows**; flows from the portfolio to the outside are called **outflows**. For example, if all the assets of a family are viewed as a portfolio, the paychecks and daily consumption expenditures of family members are common external flows. Flows of value between accounts within the portfolio are not external flows, such as transfers between family members or the use of cash from the portfolio to purchase stocks, etc. Derivative income from investments, such as interest, coupons, dividends, etc., are also not external flows, they are considered investment gains and are retained in the portfolio as they are generated. External flows need to be compensated for in the calculation of the rate of return, otherwise it will result in a distorted rate of return.

# Calculation in the absence of external flows

Assuming that at the start of the period, the market value of the portfolio is $$ V_s $$; and at the end of the period, the market value of the portfolio is $$ V_e $$, then the rate of return $$ R $$ is:

$$ R = \frac{V_e - V_s}{V_s} $$

Note that $$ V_e $$ includes all interest, coupons, dividends, etc. earned by the portfolio during the statistics period, not just the market value of the investments at the end of the period.

Example: Suppose that there is only one stock in the portfolio and that $$ 100 $$ shares of the stock are held at the start of the period at a price of $$ 10 $$ per share, so that the starting value of the portfolio is $$ 10 \times 100 = 1000 $$. During the statistics period, the stock made a dividend of $$ 0.5 $$ per share, and at the end of the period the stock was priced at $$ 9.8 $$ per share, so the total dividends received were $$ 0.5 \times 100 = 50 $$, and the value of the stock held at the end of the period was $$ 9.8 \times 100 = 980 $$. Therefore, $$ V_e = 980 + 50 = 1030 $$ with a return of $$ \displaystyle R = \frac{30}{1000} = 3\% $$.

This algorithm is simple and easy to understand, but it is only applicable when there are no external flows during the statistics period. In the example above, if the investor buys an additional $$ 100 $$ shares during the statistics period, and the purchase price remains at $$ 10 $$, then the portfolio market value at the end of the period is $$ 2060 $$ (twice the original example), at which point the return along the lines of the original formula would be calculated as $$\displaystyle R = \frac{2060 - 1000}{1000} = 106\% $$, which is obviously an inaccurate rate of return.

One might wonder: is it feasible to add the value of the inflows over the statistics period to the starting value of the $$ V_s $$? It's fine for this example because there are only inflows and no outflows in this example. However, the actual situation may be much more complicated than that, for example, a short term trader may have large inflows and outflows every day, and the rate of return would be inaccurate if only the value of all inflows were added.

Obviously, we need some way to compensate for the impact caused by external flows. A few common methods are described below.

# Simple Dietz method

[Simple Dietz method](https://en.wikipedia.org/wiki/Simple_Dietz_method) accumulates the value of all inflows and outflows during the statistics period (the sign of inflows is positive, the sign of outflows is negative), calculates the **net inflow** $$ F $$ (negative to indicate a net outflow), and then add the value at the start of the period to half of the net inflow, i.e:

$$ R = \frac{V_e - V_s - F}{V_s + \displaystyle \frac{F}{2}} $$

The simple Dietz method is based on the assumption that inflows and outflows occur roughly evenly throughout the statistics period, and can therefore be viewed as a net inflow occurring at the **midpoint** of the statistics period.

Example: Assuming that there is only one stock in the portfolio and the statistics period has $$ 3 $$ days, the stock price and inflows and outflows for each day are as follows:

| Days | Stock Price | Number of Shares Added | Inflows | Number of Shares Held | Market Value |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 10 | 0 | 0 | 10 | 100 |
| 1 | 12 | 5 | 60 | 15 | 180 |
| 2 | 11 | 0 | 0 | 15 | 165 |

Then the rate of return calculated by the simple Dietz method is:

$$ R = \frac{V_e - V_s - F}{V_s + \displaystyle \frac{F}{2}} = \frac{165 - 100 - 60}{100 + \displaystyle \frac{60}{2}} = \frac{5}{130} \approx 3.85\% $$

The disadvantage of the simple Dietz method is that the calculations will be inaccurate if the inflows and outflows are not evenly distributed throughout the statistics period. Suppose an extreme case: in a one-year statistics period, the initial market value is $$ 0 $$; on day $$ 2 $$, a large inflow comes in and buys the stock; on day $$ 364 $$, an outflow of about the same value as the inflow happens. Since the absolute value of the net inflow over the entire statistics period is very small (perhaps even $$ 0 $$), the value of the denominator in the formula is very small (or $$ 0 $$), resulting in a large bias in the return.

Despite the shortcomings of the simple Dietz method, the overall inflows and outflows to and from individuals or families tend to be very close to the assumptions of the simple Dietz method (i.e., that inflows and outflows are roughly evenly distributed over time). TataruBook therefore uses the simple Dietz method in calculating the rate of return on a portfolio that includes all internal accounts. (see [portfolio_stats]({{ site.baseurl }}/tables_and_views.html#portfolio_stats) view).
{: .notice}

# Modified Dietz method

To address the shortcomings of the simple Dietz method, the [modified Dietz method](https://en.wikipedia.org/wiki/Modified_Dietz_method) no longer assumes that a net inflow is generated only once at the midpoint of the statistics period, but instead calculates the **average** capital (i.e., the average market value of the portfolio) over the statistics period based on actual inflows and outflows, and then use the average capital as the denominator:

$$ R = \frac{V_e - V_s - F}{V_s + \displaystyle \sum_{i=1}^{n} W_i \times F_i} $$

Where $$ F = \displaystyle \sum_{i=1}^{n} F_i $$, is the net inflow over the entire statistics period; $$ n $$ is the sum of the number of inflows and outflows; $$ F_i $$ is the value of the $$ i $$th inflow or outflow (inflows are positive, outflows are negative); $$ W_i $$ is the **weight** of the $$ i $$th inflow or outflow, the weight is calculated based on when the inflow or outflow occurs, i.e.:

$$ W_i = \frac{T - t_i}{T} $$

Where $$ T $$ is the length of the statistics period; $$ t_i $$ is the length of time from the start of the period when the $$ i $$th inflow or outflow occurs. The earlier the inflow or outflow occurs, the higher its weight and the greater the impact on the return.

Example: Assuming a statistics period of $$ 365 $$ days, the stock price and inflows/outflows for each day would be as follows (omitting days with no change in between):

| Days | Stock Price | Number of Shares Added | Inflows | Number of Shares Held | Market Value |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 10 | 0 | 0 | 0 | 0 |
| 1 | 10 | 1100 | 11000 | 1100 | 11000 |
| 364 | 11 | -1000 | -11000 | 100 | 1100 |
| 365 | 11 | 0 | 0 | 100 | 1100 |

Then the modified Dietz method for calculating the rate of return is:

$$ W_0 = \frac{365 - 1}{365} \approx 0.997 $$

$$ W_1 = \frac{365 - 364}{365} \approx 0.003 $$

$$ R = \frac{V_e - V_s - F}{V_s + \displaystyle \sum_{i=1}^{n} W_i \times F_i} \approx \frac{1100 - 0 - 0}{0 + 0.997 \times 11000 - 0.003 \times 11000} \approx 10\% $$

This calculation is intuitive because the stock price rises from $$ 10 $$ to $$ 11 $$ by exactly $$ 10\% $$. If the simple Dietz method were to be used for this example, it would not work because the denominator is $$ 0 $$.

In general, if the return on an investment grows steadily over time (e.g., interest on deposits, money market mutual funds), then the rate of return calculated by the modified Dietz method tends to be very accurate. However, if the price of the investment changes drastically, then the results calculated by the modified Dietz method can be significantly biased. In the above example, if the inflow of capital was not on day $$ 1 $$ but on day $$ 363 $$, then the calculated average capital would be small, resulting in a huge number for the rate of return, which is not in line with reality.

Because of the accuracy of the modified Dietz method of calculating interest earnings, TataruBook uses the modified Dietz method in calculating the interest rate for each account. (See [interest_rates]({{ site.baseurl }}/tables_and_views.html#interest_rates) view.)
{: .notice}

# Internal rate of return (IRR)

The [internal rate of return](https://en.wikipedia.org/wiki/Internal_rate_of_return) is the rate of return that sets the [net present value](https://en.wikipedia.org/wiki/Net_present_value) (NPV) of all cash flows (both positive and negative) from the investment equal to zero. In other words, assuming that the value of a portfolio has been growing at a fixed rate $$ R $$, the $$ R $$ that satisfies this assumption is the IRR: using the starting value, inflows, outflows of the portfolio and the $$ R $$ to calculate the ending value, that ending value happens to match the actual.

The calculation of the IRR has some special requirements: the inflows or outflows must occur at fixed intervals, and the calculated rate of return $$ R $$ can only be the rate of return for the length of this interval. Assuming that there is an inflow or outflow $$ F_i $$ every interval of time $$ T $$, then the IRR $$ R $$ over the statistics period $$ T $$ is a solution to the following equation:

$$ \sum_{i=0}^{n} \frac{F_i}{(1 + R)^i} = 0 $$

Note: When calculating the IRR, $$ F_i $$ for inflows is negative and $$ F_i $$ for outflows is positive, contrary to the sign defined in the other methods. $$ F_0 $$ is the opposite of the value at the start of the period, i.e., $$ F_0 = -V_s $$; $$ F_n $$ is the value at the end of the period, i.e., $$ F_n = V_e $$. In other words, consider the value at the start of the period as an inflow and the value at the end of the period as an outflow.

Example: Assuming a statistics period of $$ 3 $$ years, the portfolio has an outflow after each year as follows:

| Year | Outflow |
|:-:|:-:|
| 0 | -123400 |
| 1 | 36200 |
| 2 | 54800 |
| 3 | 48100 |

Then, the IRR is the solution to the following equation:

$$ \sum_{i=0}^{n} \frac{F_i}{(1 + R)^i} = -123400 + \frac{36200}{(1 + R)} + \frac{54800}{(1 + R)^2} + \frac{48100}{(1 + R)^3} = 0 $$

From this equation, the IRR for **one year** can be solved $$ R \approx 5.96\% $$

The IRR has a wide range of applications in reality. For example, for a loan that requires a fixed amount of money to be returned each month, the IRR represents the true interest rate on that loan. However, IRR has many drawbacks, for example, the calculation can be troublesome when inflows and outflows do not occur at fixed intervals. Although the calculation can be crudely done by treating inflows and outflows as intervals of days and treating days with no inflows or outflows as $$ F_i = 0 $$, the IRR calculated in this way is a one-day return, not a return on the original statistics period. If one day's return is converted to a year's return on an annualized basis, again there can be a significant bias.

For example, a portfolio with a one-year statistics period has a starting value of $$ 100 $$, an outflow of $$ 101 $$ at the end of the first day, and no inflows or outflows after that, with an ending value of $$ 0 $$. For this portfolio, the calculated IRR is $$ 1\% $$ per **day**. If the rate of return is simply annualized, then the annualized rate of return is $$ (1 + 0.01)^{365} \approx 37.78 $$ times. Obviously this annualized rate of return is grossly distorted.

Another disadvantage of IRR is that the calculation requires solving high order equations, which is so computationally intensive that it is almost impossible to calculate by hand and can only be solved programmatically.

Since neither the SQLite database nor the Python standard library provides a function for calculating IRR, TataruBook does not directly provide a function for calculating IRR in order not to increase the dependency of the software and to avoid a long response time of the operation. However, TataruBook provides the [periods_cash_flows]({{ site.baseurl }}/tables_and_views.html#periods_cash_flows) view, which shows the value of net inflows/outflows for all the internal accounts on a daily basis. By copying the data from this view to Excel and using the **XIRR** function, you can calculate the IRR of all internal accounts as a portfolio.
{: .notice}

# Time-weighted return

The [time-weighted return](https://en.wikipedia.org/wiki/Time-weighted_return) is based on the idea that there is no inflow or outflow in the time period between any two flows, so for each **sub-period** where there is no inflow or outflow, one can apply the [calculation in the absence of external flows]({{ site.baseurl }}/rate_of_return.html#calculation-in-the-absence-of-external-flows) to calculate the rate of return. The rate of return for all subperiods can then be multiplied together to get the total rate of return.

To calculate the time-weighted return, it is not enough to know the starting and ending value of the portfolio; one must also know the value of the portfolio at each inflow and outflow. Assuming that there are $$ n - 1 $$ inflows and outflows, then $$ V_0 = V_s $$ is the starting value; $$ V_n = V_e $$ is the ending value; and $$ V_i $$ is the value after the $$ i $$th inflow or outflow $$ F_i $$. Then the time-weighted rate of return $$ R $$ is the solution to this equation:

$$ 1 + R = \frac{V_1 - F_1}{V_0} \times \frac{V_2 - F_2}{V_1} \times \frac{V_3 - F_3}{V_2} \times \dots \times \frac{V_{n-1} - F_{n-1}}{V_{n-2}} \times \frac{V_{n} - F_{n}}{V_{n-1}} $$

Example: Assuming that there is only one stock in the portfolio and the statistics period is $$ 2 $$ years, the initial and end-of-year stock prices and inflows and outflows are as follows:

| Year | Share Price | Number of New Shares | Inflows | Number of Shares Held | Market Value |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 10 | 0 | 0 | 50 | 500 |
| 1 | 20 | 50 | 1000 | 100 | 2000 |
| 2 | 15 | 0 | 0 | 100 | 1500 |

Then the time-weighted return is:

$$ \frac{V_1 - F_1}{V_0} \times \frac{V_2 - F_2}{V_1} - 1 = \frac{2000 - 1000}{500} \times \frac{1500 - 0}{2000} - 1 = 2 \times 0.75 - 1 = 50\% $$

This rate of return is actually the rate of change of the share price itself and does not reflect the effect of the inflow and outflow on the real return. If you look at the actual profit on this investment, you will see that with a starting value of $$ 500 $$, an intermediate increase in inputs of $$ 1000 $$, and an ending value of $$ 1500 $$, the real return is $$ 0 $$, which is not consistent with a time-weighted rate of return.

However, this is the characteristic of time-weighted return, which views the entire portfolio as a **fund**, with inflows and outflows equivalent to **purchases** and **redemptions** of **fund shares**. Time-weighted return wants to exclude the impact caused by purchases and redemptions, and only reflect the investment performance of the fund itself. For this reason, sometimes time-weighted returns are also called the **fund NAV method**.

If the inflows and outflows of a portfolio are not controlled by the portfolio's manager, then the time-weighted return is a good indicator of the manager's investment performance. But if the manager itself controls the inflows and outflows of the portfolio, then as in the example above, the time-weighted returns do not reflect the true returns.

TataruBook does not provide the ability to calculate time-weighted returns because it requires the ability to calculate the value of the portfolio at each time of the inflows or outflows. For personal or family bookkeeping, this means that the prices of all non-standard assets must be provided every time there is a spending or income, which is not an easy task for the average user. In the future, depending on the situation, TataruBook may include a time-weighted income feature.
{: .notice}

# Minimum initial cash method

If there is only one investment in the portfolio, then all external flows are buy/sell operations on this investment. Suppose a virtual **cash account** is added to the portfolio, and the value of this cash account is able to satisfy all the buy/sell operations during the statistics period, i.e., each purchase is viewed as a transfer of value from the cash account to the investment account; and each sale is viewed as a transfer of value from the investment account to the cash account. In this way, all of the original external flows become internal flows between the investment and cash accounts in the new portfolio. For this new portfolio, there are no longer external flows, and the [calculation in the absence of external flows]({{ site.baseurl }}/rate_of_return.html#calculation-in-the-absence-of-external-flows) can be applied to calculate the rate of return.

In order to most accurately represent the actual rate of return, the starting value in the virtual cash account should be as small as possible, as long as it is just enough to complete all buy and sell operations. This smallest starting value of the virtual cash account is called the **minimum initial cash** $$ C_s $$. To calculate the minimum initial cash $$ C_s $$, considered in this way: first assuming that $$ C_s = 0 $$, in this case if the value of the cash account in the statistics period will not be negative, then it means that $$ 0 $$ is the minimum initial cash; if the value of the cash account in the statistics period will be negative, then to find the largest absolute value among all negative values, and make that absolute value as the minimum initial cash $$ C_s $$, which is just enough so that the value of the cash account will not go negative during the statistics period.

$$ C_s = \text{max}(0, F_1, F_1 + F_2, F_1 + F_2 + F_3, \dots, \sum_{i=1}^{n}F_i) $$

In the above equation, $$ F_i $$ is the value of the $$ i $$th inflow or outflow (positive for inflows and negative for outflows). Note that inflows and outflows are viewed from the perspective of the original portfolio, and from the perspective of the new portfolio, inflows are transferring value from the cash account to the investment account, which causes the cash account value to decrease. So the balance of the cash account is already the opposite of $$ F_i $$ accrued and does not need to be inverted again.

After calculated using the minimum initial cash above, the value in the virtual cash account at the end of the period is $$ C_e $$.

$$ C_e = C_s - \sum_{i=1}^{n}F_i $$

The rate of return $$ R $$ is calculated as:

$$ R = \frac{(V_e + C_e) - (V_s + C_s)}{V_s + C_s} $$

Example 1: Assuming that there is only one stock in the original portfolio and there are $$ 4 $$ days in the statistics period, the daily stock prices and inflows and outflows are as follows:

| Days | Stock Price | Change in Number of Shares | Inflow/Outflow | Number of Shares Held | Market Value |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 10 | 0 | 0 | 10 | 100 |
| 1 | 12 | 5 | 60 | 15 | 180 |
| 2 | 15 | -6 | -90 | 9 | 135 |
| 3 | 11 | 0 | 0 | 9 | 99 |

Since an inflow worth $$ 60 $$ is generated on day $$ 1 $$, the virtual cash account has a minimum initial cash of $$ C_s = 60 $$. There is an outflow worth $$ 90 $$ on day $$ 2 $$, so the value in the virtual cash account at the end of the period $$ C_e = 90 $$. Calculate the rate of return:

$$ R = \frac{(99 + 90) - (100 + 60)}{100 + 60} = 18.125\% $$

Note that if the order of the two inflows and outflows were exchanged in this example, the minimum initial cash of the virtual cash account would not be this value.

Example 2: In the above example, exchange the data of day $$ 1 $$ and day $$ 2 $$ to get the daily stock price and inflow/outflow as follows:

| Day | Stock Price | Change in Number of Shares | Inflow/Outflow | Number of Shares Held | Market Value |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 10 | 0 | 0 | 10 | 100 |
| 1 | 15 | -6 | -90 | 4 | 60 |
| 2 | 12 | 5 | 60 | 9 | 108 |
| 3 | 11 | 0 | 0 | 9 | 99 |

Because there is an outflow of $$ 90 $$ on day $$ 1 $$, the virtual cash account will have an extra $$ 90 $$ value in it. On day $$ 2 $$ there is an inflow of $$ 60 $$, but the value of the virtual cash account is sufficient to cover the inflow and there is $$ 30 $$ left after the inflow. Therefore, the virtual cash account does not need to have a value at the start of the period, and the minimum initial cash is $$ 0 $$. Rate of return:

$$ R = \frac{(99 + 30) - (100 + 0)}{100 + 0} = 29\% $$

For a single investment with a floating price, the rate of return calculated by the minimum initial cash method yields results that look reasonable under a variety of different inflow and outflow scenarios. Therefore, TataruBook uses the minimum initial cash method for accounts that contain non-standard asset to calculate the rate of return of a single account, see [return_on_shares]({{ site.baseurl }}/tables_and_views.html#return_on_shares) view.
{: .notice}

# How to determine the value of an external flow?

External flows are all valued in [standard asset]({{ site.baseurl }}/tables_and_views.html#standard_asset). When the inflows or outflows of a portfolio are in the form of standard asset (i.e., home currency), their values can be easily determined. However, sometimes inflows or outflows are not in form of standard asset.

Take a transaction as an example:

| outflow account | outflow amount | inflow account | inflow amount |
|:-:|:-:|:-:|:-:|
| A | -500 | B | 10 |

If the portfolio contains account `A` only, then this transaction is an outflow; if the portfolio contains account `B` only, then this transaction is an inflow. Assuming that both account `A` and `B` contain non-standard assets, then for this transaction it is necessary to determine the value of the inflow or outflow measured in standard asset.

A scenario that corresponds to such a transaction in reality is an investment in a currency other than the home currency: for example, the purchase of Japanese stocks in Japanese Yen when the home currency is U.S. dollar. In such a transaction, the accurate way to determine the value of the inflow or outflow measured in U.S. dollar should be to record the instantaneous USD-JPY exchange rate at the moment of the transaction and convert it.

However, TataruBook's [prices]({{ site.baseurl }}/tables_and_views.html#prices) table only has information on asset prices at the end of each day, and does not contain the instant price at the moment of the transaction. So for the inflow and outflow values of such transactions, TataruBook's calculations are not entirely accurate. However, considering that most of the time asset prices do not fluctuate much during the day, this approximation is often sufficient.

Generally TataruBook uses such an algorithm: when calculating the outflow value of account `A`, using the inflow amount of account `B` multiplied by the price of the assets contained in account `B` on the same day; and when calculating the inflow value of account `B`, using the outflow amount of account `A` multiplied by the price of the assets contained in account `A` on the same day.

However, there is a special type of transaction for which this algorithm does not apply: when one of the parties in the transaction has an amount of change of $$ 0 $$ in the account:

| outflow account | outflow amount | inflow account | inflow amount |
|:-:|:-:|:-:|:-:|
| A | 0 | B | 200 |

This type of transaction usually occurs when dividends are paid on stocks or funds, or when coupons are paid on bonds. For example, if account `A` is a Japanese stock, and account `B` is a Japanese Yen account that receives dividends, then if the above algorithm is still used, account `B` will have an inflow value of $$ 0 $$ for this transaction, which is not reasonable.

To solve this problem, TataruBook does a special treatment: if one party of the transaction has an amount of change of $$ 0 $$, then the inflow and outflow values of both accounts are determined according to the type of asset and the amount of change of the other party (the amount of change of which is not $$ 0 $$). In the example just given, the outflow value of account `A` and the inflow value of account `B` are both $$ 200 $$ multiplied by the price of the asset contained in account `B` on that day. This processing can be observed with the [share_trade_flows]({{ site.baseurl }}/tables_and_views.html#share_trade_flows) view.

If you do need to accurately calculate the inflow and outflow values using instant prices, then you can split a single transaction into two transactions using an intermediate account:

| outflow account | outflow amount | inflow account | inflow amount |
|:-:|:-:|:-:|:-:|
| A | -500 | X | 100 |
| X | -100 | B | 10 |

The account `X` in this example contains the standard asset, and the amount of change in `X` reflects the immediate inflow and outflow values at the time of the transaction. By entering transactions in this way, TataruBook can accurately calculate inflow and outflow values, and no longer needs to use the price information in the [prices]({{ site.baseurl }}/tables_and_views.html#prices) table.