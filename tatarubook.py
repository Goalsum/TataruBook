import sqlite3
import csv
import math
import datetime
import locale
from pathlib import Path
from argparse import ArgumentParser
from functools import wraps
from contextlib import contextmanager, ExitStack
from collections import namedtuple
import subprocess


SQL_CREATE_COMMANDS = (
    ("asset_types", "table",
     """CREATE TABLE asset_types(asset_index INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                 asset_name TEXT NOT NULL,
                                 asset_order INTEGER NOT NULL) STRICT"""),
    ("standard_asset", "table",
     """CREATE TABLE standard_asset(asset_index INTEGER PRIMARY KEY NOT NULL REFERENCES asset_types(asset_index))
        STRICT"""),
    ("accounts", "table",
     """CREATE TABLE accounts(account_index INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                              account_name TEXT NOT NULL,
                              asset_index INTEGER NOT NULL REFERENCES asset_types(asset_index),
                              is_external INTEGER NOT NULL CHECK(is_external IN (0,1))) STRICT"""),
    ("interest_accounts", "table",
     """CREATE TABLE interest_accounts(
        account_index INTEGER PRIMARY KEY NOT NULL REFERENCES accounts(account_index)) STRICT"""),
    ("postings", "table",
     """CREATE TABLE postings(posting_index INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                              trade_date TEXT NOT NULL CHECK(date(trade_date) IS trade_date),
                              src_account INTEGER NOT NULL REFERENCES accounts(account_index),
                              src_change REAL NOT NULL CHECK(src_change <= 0),
                              dst_account INTEGER NOT NULL REFERENCES accounts(account_index),
                              comment TEXT) STRICT"""),
    ("postings_by_date", "index",
     """CREATE INDEX postings_by_date ON postings(trade_date)"""),
    ("posting_extras", "table",
     """CREATE TABLE posting_extras(posting_index INTEGER PRIMARY KEY NOT NULL REFERENCES postings(posting_index),
                                    dst_change REAL NOT NULL CHECK(dst_change >= 0)) STRICT"""),
    ("prices", "table",
     """CREATE TABLE prices(price_date TEXT NOT NULL CHECK(date(price_date) IS price_date),
                            asset_index INTEGER NOT NULL REFERENCES asset_types(asset_index),
                            price REAL NOT NULL,
                            PRIMARY KEY(price_date, asset_index),
                            UNIQUE(price_date, asset_index)) STRICT, WITHOUT ROWID"""),
    ("start_date", "table",
     """CREATE TABLE start_date(val TEXT PRIMARY KEY NOT NULL CHECK(date(val) IS val)) STRICT, WITHOUT ROWID"""),
    ("end_date", "table",
     """CREATE TABLE end_date(val TEXT PRIMARY KEY NOT NULL CHECK(date(val) IS val)) STRICT, WITHOUT ROWID"""),
    ("single_entries", "view",
     """CREATE VIEW single_entries AS
        SELECT posting_index, trade_date, src_account AS account_index, src_change AS amount,
            dst_account AS target, comment
        FROM postings
        UNION
        SELECT postings.posting_index, trade_date, dst_account AS account_index,
            ifnull(posting_extras.dst_change, -src_change) AS amount, src_account AS target, comment
        FROM postings LEFT JOIN posting_extras ON postings.posting_index = posting_extras.posting_index
        WHERE round(amount, 6) <> 0
        ORDER BY trade_date ASC, posting_index ASC"""),
    ("statements", "view",
     """CREATE VIEW statements AS
        SELECT single_entries.*, src_acc.account_name AS src_name, src_acc.asset_index, src_acc.is_external,
            target_acc.account_name AS target_name,
            sum(amount) OVER (PARTITION BY single_entries.account_index
                ORDER BY trade_date, posting_index ROWS UNBOUNDED PRECEDING) AS balance
        FROM single_entries INNER JOIN accounts AS src_acc ON single_entries.account_index = src_acc.account_index
            INNER JOIN accounts as target_acc ON single_entries.target = target_acc.account_index
        ORDER BY trade_date ASC, posting_index ASC"""),
    ("start_balance", "view",
     """CREATE VIEW start_balance AS
        SELECT start_date.val AS date_val, accounts.account_index, accounts.account_name,
            sum(single_entries.amount) AS balance, accounts.asset_index
        FROM single_entries INNER JOIN accounts ON single_entries.account_index = accounts.account_index,
            start_date
        WHERE single_entries.trade_date <= start_date.val AND accounts.is_external = 0
        GROUP BY accounts.account_index
        HAVING round(sum(single_entries.amount), 6) <> 0
        ORDER BY accounts.asset_index ASC"""),
    ("start_values", "view",
     """CREATE VIEW start_values AS
        SELECT *, balance * price as market_value
        FROM (SELECT start_balance.*,
                iif(start_balance.asset_index IN (SELECT * FROM standard_asset), 1.0,
                    (SELECT price FROM prices WHERE start_balance.asset_index = prices.asset_index
                        AND prices.price_date = start_balance.date_val)) AS price
            FROM start_balance)
        ORDER BY asset_index ASC"""),
    ("start_stats", "view",
     """CREATE VIEW start_stats AS
        SELECT asset_types.asset_order, start_values.date_val, start_values.account_index,
            start_values.account_name, start_values.balance, asset_types.asset_index, asset_types.asset_name,
            start_values.price, start_values.market_value,
            start_values.market_value / (SELECT start_value FROM portfolio_stats) AS proportion
        FROM start_values INNER JOIN asset_types ON start_values.asset_index = asset_types.asset_index
        ORDER BY asset_order ASC, asset_types.asset_index ASC"""),
    ("start_assets", "view",
     """CREATE VIEW start_assets AS
        SELECT *, total_value / (SELECT start_value FROM portfolio_stats) AS proportion
        FROM (SELECT asset_types.asset_order, start_values.date_val, asset_types.asset_index, asset_types.asset_name, 
                sum(start_values.balance) AS amount, start_values.price, sum(start_values.market_value) AS total_value
            FROM start_values INNER JOIN asset_types ON start_values.asset_index = asset_types.asset_index
            GROUP BY asset_types.asset_order, start_values.date_val, asset_types.asset_index, asset_types.asset_name,
                start_values.price)
        ORDER BY asset_order ASC, asset_index ASC"""),
    ("diffs", "view",
     """CREATE VIEW diffs AS
        SELECT accounts.account_index, accounts.account_name, sum(single_entries.amount) AS amount,
            accounts.asset_index
        FROM single_entries INNER JOIN accounts ON single_entries.account_index = accounts.account_index,
            start_date, end_date
        WHERE single_entries.trade_date > start_date.val AND single_entries.trade_date <= end_date.val
            AND accounts.is_external = 0
        GROUP BY accounts.asset_index, accounts.account_index
        ORDER BY accounts.asset_index ASC"""),
    ("comparison", "view",
     """CREATE VIEW comparison AS
        SELECT start_balance.account_index, start_balance.account_name, start_balance.balance AS start_amount,
            ifnull(diffs.amount, 0) AS diff, start_balance.balance + ifnull(diffs.amount, 0) AS end_amount,
            start_balance.asset_index
        FROM start_balance LEFT JOIN diffs ON start_balance.account_index = diffs.account_index
        UNION
        SELECT account_index, account_name, 0 AS start_amount, amount AS diff, amount AS end_amount, asset_index
        FROM diffs WHERE account_index NOT IN (SELECT account_index FROM start_balance)
        ORDER BY asset_index ASC"""),
    ("end_values", "view",
     """CREATE VIEW end_values AS
        SELECT *, balance * price as market_value
        FROM (SELECT end_date.val AS date_val, comparison.account_index, comparison.account_name,
                comparison.end_amount AS balance, comparison.asset_index,
                iif(comparison.asset_index IN (SELECT * FROM standard_asset), 1.0,
                    (SELECT price FROM prices WHERE comparison.asset_index = prices.asset_index
                        AND prices.price_date = end_date.val)) AS price
            FROM comparison, end_date
            WHERE round(balance, 6) <> 0)
        ORDER BY asset_index ASC"""),
    ("end_stats", "view",
     """CREATE VIEW end_stats AS
        SELECT asset_types.asset_order, end_values.date_val, end_values.account_index,
            end_values.account_name, end_values.balance, asset_types.asset_index, asset_types.asset_name,
            end_values.price, end_values.market_value,
            end_values.market_value / (SELECT end_value FROM portfolio_stats) AS proportion
        FROM end_values INNER JOIN asset_types ON end_values.asset_index = asset_types.asset_index
        ORDER BY asset_order ASC, asset_types.asset_index ASC"""),
    ("end_assets", "view",
     """CREATE VIEW end_assets AS
        SELECT *, total_value / (SELECT end_value FROM portfolio_stats) AS proportion
        FROM (SELECT asset_types.asset_order, end_values.date_val, asset_types.asset_index, asset_types.asset_name, 
                sum(end_values.balance) AS amount, end_values.price, sum(end_values.market_value) AS total_value
            FROM end_values INNER JOIN asset_types ON end_values.asset_index = asset_types.asset_index
            GROUP BY asset_types.asset_order, end_values.date_val, asset_types.asset_index, asset_types.asset_name,
                end_values.price)
        ORDER BY asset_order ASC, asset_index ASC"""),
    ("external_flows", "view",
     """CREATE VIEW external_flows AS
        SELECT single_entries.trade_date, asset_types.asset_order, accounts.account_index, accounts.account_name,
            single_entries.amount, accounts.asset_index, asset_types.asset_name,
            iif(asset_types.asset_index IN (SELECT * FROM standard_asset), 1.0,
                (SELECT price FROM prices WHERE asset_types.asset_index = prices.asset_index
                    AND prices.price_date = single_entries.trade_date)) AS price
        FROM single_entries INNER JOIN accounts ON single_entries.account_index = accounts.account_index
            INNER JOIN asset_types ON accounts.asset_index = asset_types.asset_index, start_date, end_date
        WHERE single_entries.trade_date > start_date.val AND single_entries.trade_date <= end_date.val
            AND accounts.is_external = 1
        ORDER BY single_entries.trade_date ASC"""),
    ("income_and_expenses", "view",
     """CREATE VIEW income_and_expenses AS
        SELECT asset_order, account_index, account_name, sum(amount) AS total_amount, asset_index, asset_name,
            sum(price * amount) AS total_value
        FROM external_flows
        GROUP BY asset_order, asset_index, account_index
        ORDER BY asset_order ASC, asset_index ASC"""),
    ("portfolio_stats", "view",
     """CREATE VIEW portfolio_stats AS
        SELECT *, net_gain / (start_value - net_outflow / 2) AS rate_of_return
        FROM (SELECT *, end_value + net_outflow - start_value AS net_gain
            FROM (SELECT total(start_values.market_value) AS start_value FROM start_values),
                (SELECT total(end_values.market_value) AS end_value FROM end_values),
                (SELECT total(income_and_expenses.total_value) AS net_outflow FROM income_and_expenses
                 WHERE income_and_expenses.account_index NOT IN (SELECT * FROM interest_accounts)),
                (SELECT total(income_and_expenses.total_value) AS interest FROM income_and_expenses
                 WHERE income_and_expenses.account_index IN (SELECT * FROM interest_accounts)))"""),
    ("flow_stats", "view",
     """CREATE VIEW flow_stats AS
        SELECT single_entries.account_index AS flow_index, flow_acc.account_name AS flow_name,
            single_entries.target AS account_index, real_acc.account_name, sum(single_entries.amount) AS amount
        FROM single_entries INNER JOIN accounts as flow_acc ON single_entries.account_index = flow_acc.account_index
            INNER JOIN accounts as real_acc ON single_entries.target = real_acc.account_index
        WHERE single_entries.trade_date > (SELECT * FROM start_date)
            AND single_entries.trade_date <= (SELECT * FROM end_date)
            AND flow_acc.is_external = 1
        GROUP BY single_entries.account_index, single_entries.target
        ORDER BY single_entries.account_index ASC, single_entries.target ASC"""),
    ("share_trade_flows", "view",
     """CREATE VIEW share_trade_flows AS
        SELECT posting_index, trade_date, iif(shift, target, account_index) AS account_index,
            iif(shift, share_asset_index, cash_asset_index) AS cash_asset,
            iif(shift,
                -(SELECT dst_change FROM posting_extras WHERE posting_extras.posting_index = unshifted.posting_index),
                amount) as amount,
            target, comment, account_name, share_asset_index as asset_index, asset_name, asset_order
        FROM (SELECT single_entries.*, share_acc.account_name, share_acc.asset_index AS share_asset_index,
                cash_acc.asset_index AS cash_asset_index, asset_types.asset_name, asset_types.asset_order,
                (cash_acc.asset_index NOT IN (SELECT * FROM standard_asset) AND single_entries.amount = 0) AS shift
            FROM single_entries INNER JOIN accounts AS share_acc ON single_entries.target = share_acc.account_index
                INNER JOIN accounts AS cash_acc ON single_entries.account_index = cash_acc.account_index
                INNER JOIN asset_types ON share_acc.asset_index = asset_types.asset_index
            WHERE single_entries.trade_date > (SELECT * FROM start_date)
                AND single_entries.trade_date <= (SELECT * FROM end_date)
                AND share_acc.is_external = 0
                AND single_entries.account_index NOT IN (SELECT * FROM interest_accounts)
                AND asset_types.asset_index NOT IN (SELECT * FROM standard_asset)) AS unshifted"""),
    ("share_trades", "view",
     """CREATE VIEW share_trades AS
        SELECT share_trade_flows.*,
            amount * iif(cash_asset IN (SELECT * FROM standard_asset), 1.0,
                (SELECT price FROM prices WHERE share_trade_flows.cash_asset = prices.asset_index
                    AND prices.price_date = share_trade_flows.trade_date)) AS cash_flow
        FROM share_trade_flows
        ORDER BY trade_date ASC, posting_index ASC"""),
    ("share_stats", "view",
     """CREATE VIEW share_stats AS
        SELECT asset_order, asset_index, asset_name, account_index, account_name,
            iif(min(balance) >= 0, 0, -min(balance)) AS min_inflow, sum(cash_flow) AS cash_gained
        FROM (SELECT asset_order, asset_index, asset_name, target AS account_index, account_name, cash_flow,
                sum(cash_flow) OVER (PARTITION BY target
                    ORDER BY trade_date, posting_index ROWS UNBOUNDED PRECEDING) AS balance
            FROM share_trades)
        GROUP BY asset_order, asset_index, account_index
        ORDER BY asset_order ASC, asset_index ASC"""),
    ("return_on_shares", "view",
     """CREATE VIEW return_on_shares AS
        SELECT *, (cash_gained + end_value - start_value) AS profit,
            iif(start_value + min_inflow <= 0, 0,
                (cash_gained + end_value - start_value) / (start_value + min_inflow)) AS rate_of_return
        FROM (SELECT asset_types.asset_order, asset_types.asset_index, asset_types.asset_name,
                comparison.account_index, comparison.account_name, comparison.start_amount,
                ifnull(start_values.market_value, 0) AS start_value, comparison.diff, comparison.end_amount,
                ifnull(end_values.market_value, 0) AS end_value, ifnull(share_stats.cash_gained, 0) AS cash_gained,
                ifnull(share_stats.min_inflow, 0) AS min_inflow
            FROM comparison INNER JOIN asset_types ON comparison.asset_index = asset_types.asset_index
                LEFT JOIN start_values ON comparison.account_index = start_values.account_index
                LEFT JOIN end_values ON comparison.account_index = end_values.account_index
                LEFT JOIN share_stats ON comparison.account_index = share_stats.account_index
            WHERE comparison.asset_index NOT IN (SELECT * FROM standard_asset))
        ORDER BY asset_order ASC, asset_index ASC"""),
    ("interest_stats", "view",
     """CREATE VIEW interest_stats AS
        SELECT single_entries.account_index, deposit_acc.account_name, deposit_acc.asset_index,
            sum(single_entries.amount) AS amount
        FROM single_entries INNER JOIN accounts AS interest_acc ON single_entries.target = interest_acc.account_index
            INNER JOIN accounts AS deposit_acc ON single_entries.account_index = deposit_acc.account_index
        WHERE single_entries.trade_date > (SELECT * FROM start_date)
            AND single_entries.trade_date <= (SELECT * FROM end_date)
            AND deposit_acc.is_external = 0
            AND interest_acc.account_index IN (SELECT * FROM interest_accounts)
        GROUP BY deposit_acc.asset_index, single_entries.account_index
        ORDER BY deposit_acc.asset_index ASC"""),
    ("interest_rates", "view",
     """CREATE VIEW interest_rates AS
        SELECT *, iif(avg_balance <= 0, 0, interest / avg_balance) AS rate_of_return
        FROM (SELECT day_stats.account_index, day_stats.account_name, day_stats.asset_index,
                ifnull(start_balance.balance, 0) + sum(day_stats.amount) / days AS avg_balance,
                interest_stats.amount AS interest
            FROM (SELECT single_entries.account_index, accounts.account_name, accounts.asset_index,
                    single_entries.trade_date,
                    sum(single_entries.amount) * (julianday(end_date.val) - julianday(single_entries.trade_date))
                    AS amount, julianday(end_date.val) - julianday(start_date.val) AS days
                FROM (single_entries INNER JOIN accounts 
                    ON single_entries.account_index = accounts.account_index), start_date, end_date
                WHERE single_entries.trade_date > start_date.val
                    AND single_entries.trade_date <= end_date.val
                    AND single_entries.account_index IN (SELECT account_index FROM interest_stats)
                GROUP BY single_entries.account_index, single_entries.trade_date) AS day_stats
            LEFT JOIN start_balance ON day_stats.account_index = start_balance.account_index
            INNER JOIN interest_stats ON day_stats.account_index = interest_stats.account_index
            GROUP BY day_stats.account_index)
        ORDER BY asset_index ASC"""),
    ("periods_cash_flows", "view",
     """CREATE VIEW periods_cash_flows AS
        SELECT start_date.val AS trade_date, 0 AS period, -portfolio_stats.start_value AS cash_flow
        FROM portfolio_stats, start_date
        UNION
        SELECT trade_date, julianday(trade_date) - julianday(start_date.val) AS period,
            sum(price * amount) AS cash_flow
        FROM external_flows, start_date, end_date
        WHERE external_flows.account_index NOT IN (SELECT * FROM interest_accounts)
        GROUP BY trade_date
        UNION
        SELECT end_date.val AS trade_date, julianday(end_date.val) - julianday(start_date.val) AS period,
            portfolio_stats.end_value AS cash_flow
        FROM portfolio_stats, start_date, end_date
        ORDER BY trade_date ASC"""),
    ("daily_assets", "view",
     """CREATE VIEW daily_assets AS
        WITH RECURSIVE changes AS
            (SELECT trade_date, asset_index,
                sum(amount) OVER (PARTITION BY asset_index ORDER BY trade_date ROWS UNBOUNDED PRECEDING) AS amount
            FROM (WITH daily_changes AS
                    (SELECT single_entries.trade_date, accounts.asset_index, sum(single_entries.amount) AS amount
                    FROM single_entries INNER JOIN accounts ON single_entries.account_index = accounts.account_index
                    WHERE accounts.is_external = 0
                    GROUP BY single_entries.trade_date, accounts.asset_index
                    HAVING round(sum(single_entries.amount), 6) <> 0)
                SELECT start_date.val AS trade_date, daily_changes.asset_index, sum(daily_changes.amount) AS amount
                FROM daily_changes, start_date
                WHERE daily_changes.trade_date <= start_date.val
                GROUP BY daily_changes.asset_index
                HAVING round(sum(daily_changes.amount), 6) <> 0
                UNION ALL
                SELECT daily_changes.*
                FROM daily_changes, start_date, end_date
                WHERE daily_changes.trade_date > start_date.val AND daily_changes.trade_date <= end_date.val)),
        accumulation(trade_date, asset_index, amount) AS
            (SELECT * FROM changes
            UNION ALL
            SELECT date(accumulation.trade_date, '1 day'), accumulation.asset_index, accumulation.amount
            FROM (accumulation LEFT JOIN changes ON
                date(accumulation.trade_date, '1 day') = changes.trade_date AND
                accumulation.asset_index = changes.asset_index), end_date
            WHERE changes.amount ISNULL AND accumulation.trade_date < end_date.val AND
                round(accumulation.amount, 6) <> 0)
        SELECT * FROM accumulation
        WHERE round(amount, 6) <> 0
        ORDER BY trade_date, asset_index"""),
    ("price_unavailable", "view",
     """CREATE VIEW price_unavailable AS
        SELECT daily_assets.trade_date, asset_types.asset_index, asset_types.asset_name
        FROM daily_assets LEFT JOIN prices ON
            daily_assets.trade_date = prices.price_date AND daily_assets.asset_index = prices.asset_index
            INNER JOIN asset_types ON daily_assets.asset_index = asset_types.asset_index
        WHERE prices.price ISNULL AND daily_assets.asset_index NOT IN (SELECT * FROM standard_asset)
        ORDER BY daily_assets.trade_date, asset_types.asset_order, asset_types.asset_index"""),
    ("equity_trend", "view",
     """CREATE VIEW equity_trend AS
        WITH RECURSIVE all_dates(val) AS
            (SELECT * FROM start_date
            UNION ALL
            SELECT date(all_dates.val, '1 day') FROM all_dates, end_date
            WHERE all_dates.val < end_date.val)
        SELECT eligible.trade_date, sum(eligible.amount * eligible.price) AS equity
        FROM (SELECT dates.trade_date, daily_assets.asset_index, ifnull(daily_assets.amount, 0) AS amount,
                iif(daily_assets.asset_index ISNULL OR daily_assets.asset_index IN (SELECT * FROM standard_asset), 1.0,
                    (SELECT price FROM prices WHERE daily_assets.asset_index = prices.asset_index
                        AND daily_assets.trade_date = prices.price_date)) AS price
            FROM (SELECT val AS trade_date FROM all_dates EXCEPT
                SELECT trade_date FROM price_unavailable) AS dates LEFT JOIN daily_assets ON
                dates.trade_date = daily_assets.trade_date) AS eligible
        GROUP BY eligible.trade_date
        ORDER BY eligible.trade_date"""),
    ("check_standard_prices", "view",
     """CREATE VIEW check_standard_prices AS
        SELECT * FROM prices INNER JOIN standard_asset ON prices.asset_index = standard_asset.asset_index"""),
    ("check_interest_account", "view",
     """CREATE VIEW check_interest_account AS
        SELECT accounts.*
        FROM interest_accounts INNER JOIN accounts ON interest_accounts.account_index = accounts.account_index
        WHERE accounts.is_external = 0"""),
    ("check_same_account", "view",
     """CREATE VIEW check_same_account AS
        SELECT * FROM postings WHERE postings.src_account = postings.dst_account"""),
    ("check_both_external", "view",
     """CREATE VIEW check_both_external AS
        SELECT postings.posting_index, postings.trade_date, postings.src_account, src_ai.account_name,
            src_ai.asset_index, src_ai.is_external, postings.src_change, postings.dst_account, dst_ai.account_name,
            dst_ai.asset_index, dst_ai.is_external, postings.comment
        FROM postings INNER JOIN accounts AS src_ai ON postings.src_account = src_ai.account_index
            INNER JOIN accounts AS dst_ai ON postings.dst_account = dst_ai.account_index
        WHERE src_ai.is_external = 1 AND dst_ai.is_external = 1"""),
    ("check_diff_asset", "view",
     """CREATE VIEW check_diff_asset AS
        SELECT postings.posting_index, postings.trade_date, postings.src_account, src_ai.account_name,
            src_ai.asset_index, src_ai.is_external, postings.src_change, postings.dst_account, dst_ai.account_name,
            dst_ai.asset_index, dst_ai.is_external, posting_extras.dst_change, postings.comment
        FROM postings LEFT JOIN posting_extras ON postings.posting_index = posting_extras.posting_index
            INNER JOIN accounts AS src_ai ON postings.src_account = src_ai.account_index
            INNER JOIN accounts AS dst_ai ON postings.dst_account = dst_ai.account_index
        WHERE src_ai.asset_index <> dst_ai.asset_index AND posting_extras.dst_change ISNULL
            AND NOT (src_ai.asset_index IN (SELECT * FROM standard_asset)
                AND dst_ai.asset_index IN (SELECT * FROM standard_asset))"""),
    ("check_same_asset", "view",
     """CREATE VIEW check_same_asset AS
        SELECT postings.posting_index, postings.trade_date, postings.src_account, src_ai.account_name,
            src_ai.asset_index, src_ai.is_external, postings.src_change, postings.dst_account, dst_ai.account_name,
            dst_ai.asset_index, dst_ai.is_external, posting_extras.dst_change, postings.comment
        FROM postings INNER JOIN posting_extras ON postings.posting_index = posting_extras.posting_index
            INNER JOIN accounts AS src_ai ON postings.src_account = src_ai.account_index
            INNER JOIN accounts AS dst_ai ON postings.dst_account = dst_ai.account_index
        WHERE src_ai.asset_index = dst_ai.asset_index"""),
    ("check_external_asset", "view",
     """CREATE VIEW check_external_asset AS
        SELECT postings.posting_index, postings.trade_date, postings.src_account, src_ai.account_name,
            src_ai.asset_index, src_ai.is_external, postings.src_change, postings.dst_account, dst_ai.account_name,
            dst_ai.asset_index, dst_ai.is_external, postings.comment
        FROM postings INNER JOIN accounts AS src_ai ON postings.src_account = src_ai.account_index
            INNER JOIN accounts AS dst_ai ON postings.dst_account = dst_ai.account_index
        WHERE src_ai.asset_index <> dst_ai.asset_index
            AND ((src_ai.is_external = 1 AND src_ai.asset_index NOT IN (SELECT * FROM standard_asset))
                OR (dst_ai.is_external = 1 AND dst_ai.asset_index NOT IN (SELECT * FROM standard_asset)))"""),
    ("check_absent_price", "view",
     """CREATE VIEW check_absent_price AS
        SELECT absence.date_val, asset_types.asset_index, asset_types.asset_name, asset_types.asset_order
        FROM (SELECT start_balance.asset_index, start_date.val AS date_val
            FROM start_balance, start_date
            UNION
            SELECT comparison.asset_index, end_date.val AS date_val
            FROM comparison, end_date
            WHERE round(comparison.end_amount, 6) <> 0
            UNION
            SELECT cash_asset AS asset_index, trade_date AS date_val
            FROM share_trade_flows
            EXCEPT
            SELECT asset_index, price_date AS date_val FROM prices) AS absence
            INNER JOIN asset_types ON absence.asset_index = asset_types.asset_index
        WHERE absence.asset_index NOT IN (SELECT * FROM standard_asset)
        ORDER BY asset_types.asset_order, asset_types.asset_index, absence.date_val""")
)

INIT_SQL_CMD = """
    BEGIN;
    {}
    COMMIT;
""".format("".join([x[2] + ";\n" for x in SQL_CREATE_COMMANDS]))

EXPORT_TABLES = [x[0] for x in SQL_CREATE_COMMANDS if x[1] != "index"]

EXCLUDED_TABLES = ("sqlite_sequence",)

OVERWRITE_TABLES = ("standard_asset", "start_date", "end_date")

DATE_COLUMNS = {("postings", "trade_date"), ("prices", "price_date"), ("start_date", "val"), ("end_date", "val")}

Step = namedtuple("Step", ("table_name", "indices", "returning"), defaults=(None, None, None))

COMBINED_INSERT = {("postings", 7):
                   (Step(table_name="postings", indices=(0, 1, 2, 3, 4, 5), returning="posting_index"),
                    Step(table_name="posting_extras", indices=(7, 6))),
                   ("accounts", 6):
                   (Step(table_name="asset_types", indices=(2, 4, 5), returning="asset_index"),
                    Step(table_name="accounts", indices=(0, 1, 6, 3)))}

VALUE_LOOKUPS = {("postings", "src_account"): (("accounts", 0, 0), ("accounts", 1, 0)),
                 ("postings", "dst_account"): (("accounts", 0, 0), ("accounts", 1, 0)),
                 ("interest_accounts", "account_index"): (("accounts", 0, 0), ("accounts", 1, 0)),
                 ("accounts", "asset_index"): (("asset_types", 0, 0), ("asset_types", 1, 0)),
                 ("prices", "asset_index"): (("asset_types", 0, 0), ("asset_types", 1, 0)),
                 ("standard_asset", "asset_index"): (("asset_types", 0, 0), ("asset_types", 1, 0))}


class HandledError(Exception):
    pass


def db_file_to_path(f):
    @wraps(f)
    def wrapper(db_file, *p_args, **kw_args):
        db_path = Path(db_file)
        if not db_path.is_file():
            print("{} file does not exist!".format(db_path))
            return
        return f(db_path, *p_args, **kw_args)
    return wrapper


def db_csv_file_to_path(f):
    @wraps(f)
    @db_file_to_path
    def wrapper(db_file, csv_file, *p_args, **kw_args):
        csv_path = Path(csv_file)
        if not csv_path.is_file():
            print("{} file does not exist!".format(csv_path))
            return
        return f(db_file, csv_path, *p_args, **kw_args)
    return wrapper


@contextmanager
def fence(con):
    try:
        con.execute("PRAGMA foreign_keys = ON")
        yield con
    except HandledError:
        pass
    except Exception as e:
        print(e)
    finally:
        con.close()


@contextmanager
def prompt_transaction():
    try:
        yield
    except Exception as e:
        print(e)
        print("Operation failed! Rollback! File stays unmodified.")
        raise HandledError
    else:
        print("Operation done! File modified successfully.")


def in_transaction(con):
    stack = ExitStack()
    stack.enter_context(prompt_transaction())
    stack.enter_context(con)
    return stack


class BatchHandler:
    def __init__(self, con, table, col_info):
        self.con = con
        self.table = table
        self.col_info = col_info

    def handle(self, row):
        pass


class Inserter(BatchHandler):
    def __init__(self, con, table, col_info):
        super().__init__(con, table, col_info)

    def handle(self, row):
        print("> {}".format(row))
        if len(row) > len(self.col_info) and not any(row[len(self.col_info):]):
            row = row[:len(self.col_info)]

        if is_headline(row):
            print("Headline detected, Skip this row.")
        elif len(self.col_info) != len(row) and (self.table, len(row)) not in COMBINED_INSERT:
            raise TypeError("Table {} has {} columns but {} columns are provided.".format(
                self.table, len(self.col_info), len(row)))
        else:
            atomic_insert(self.con, self.table, self.col_info, row)


class Deleter(BatchHandler):
    def __init__(self, con, table, col_info):
        super().__init__(con, table, col_info)

    def handle(self, row):
        print("> {}".format(row))
        if len(row) > len(self.col_info) and not any(row[len(self.col_info):]):
            row = row[:len(self.col_info)]

        if is_headline(row):
            print("Headline detected, Skip this row.")
        elif len(self.col_info) != len(row):
            raise TypeError("Table {} has {} key columns but {} columns are provided.".format(
                self.table, len(self.col_info), len(row)))
        else:
            atomic_delete(self.con, self.table, self.col_info, row)


def decode_csv(csv_file, encoding, handler):
    codecs = [encoding] if encoding else (
        [None] if locale.getpreferredencoding(False) == "utf-8" else [None, "utf-8"])
    for codec in codecs:
        try:
            with csv_file.open(newline='', encoding=codec) as file:
                for row in csv.reader(file):
                    handler.handle(row)
            break
        except UnicodeError as e:
            if codec == codecs[-1]:
                raise e
            else:
                print("Decoding error encountered! Try again with another codec automatically:\n")


def init(db_file):
    db_path = Path(db_file)
    if db_path.exists():
        print("{} file/directory already exists, create fail!".format(db_path))
        return

    with fence(sqlite3.connect(db_path)) as con:
        con.executescript(INIT_SQL_CMD)

    print("{} file created".format(db_file))


def check_view(con, view, prompt):
    rows = con.execute("SELECT * FROM {}".format(view)).fetchall()
    if rows:
        print(prompt)
        for row in rows:
            print(row)
        return False
    return True


def integrity_check(con):
    all_passed = True

    start_date = con.execute("SELECT * FROM start_date").fetchall()
    count = len(start_date)
    if count != 1:
        print("start_date should contain exactly 1 row but {} row(s) are found.".format(count))
        all_passed = False

    end_date = con.execute("SELECT * FROM end_date").fetchall()
    count = len(end_date)
    if count != 1:
        print("end_date should contain exactly 1 row but {} row(s) are found.".format(count))
        all_passed = False

    if all_passed and datetime.date.fromisoformat(start_date[0][0]) >= datetime.date.fromisoformat(end_date[0][0]):
        print("start date {} is not earlier than end date {}".format(start_date[0][0], end_date[0][0]))
        all_passed = False

    count = len(con.execute("SELECT * FROM standard_asset").fetchall())
    if count != 1:
        print("standard_asset should contain exactly 1 row but {} row(s) are found.".format(count))
        all_passed = False

    views = (
        ("check_standard_prices", "Standard assets should not have price attached but these are found:"),
        ("check_interest_account", "Interest accounts should all be external but these are not:"),
        ("check_same_account", "The source and target accounts are same in these postings:"),
        ("check_both_external", "The source and target accounts are both external in these postings:"),
        ("check_diff_asset",
         "These postings should have posting_extras attached because source asset is different from target asset:"),
        ("check_same_asset",
         "These postings should NOT have posting_extras attached because source and target assets are same:"),
        ("check_external_asset",
         "The external accounts in these postings contain" +
         " neither standard asset nor the same asset as the other account:"),
        ("check_absent_price", "These (date, asset) pairs need price info in calculation:")
    )
    for x, y in views:
        all_passed = check_view(con, x, y) and all_passed

    if all_passed:
        print("Everything is fine, no integrity breaches found.")


def strip_trivial(s):
    return s.replace(" ", "").replace("\n", "").replace("\t", "").replace('"', "")


def definition_check(con):
    definitions = con.execute("SELECT * FROM sqlite_schema").fetchall()
    removed = []
    different = []
    remaining = list(SQL_CREATE_COMMANDS)
    incompatible = []
    for item in definitions:
        if item[1] in EXCLUDED_TABLES:
            continue
        current = [x for x in remaining if x[0] == item[1]]
        if not current:
            removed.append(item[1])
            if item[0] != "view":
                incompatible.append(item[1])
        else:
            remaining.remove(current[0])
            if strip_trivial(item[4]) != strip_trivial(current[0][2]):
                different.append(item[1])
                if item[0] != "view":
                    incompatible.append(item[1])
                print(f"{item[1]}'s definition should be changed:\nold:\n{item[4]}\nnew:\n{current[0][2]}")
    added = [x[0] for x in remaining]
    if removed:
        print(f"These definitions should be removed: {removed}")
    if added:
        print(f"These definitions should be added: {added}")
    if incompatible:
        print(f"These definitions are incompatible with current version: {incompatible}")
    if not (removed or different or added):
        print("All definitions are correct.")
    return removed, different, added, incompatible


@db_file_to_path
def check(db_file):
    with fence(sqlite3.connect(db_file)) as con:
        print("SQL definition check:")
        (removed, different, added, incompatible) = definition_check(con)
        if (removed or different or added) and not incompatible:
            print("Use upgrade command to fix all the definitions. (But make a backup first)")
        print("Integrity check:")
        integrity_check(con)


@db_file_to_path
def export(db_file, table=None, encoding=None):
    tables = (table,) if table else EXPORT_TABLES

    with fence(sqlite3.connect(db_file)) as con:
        for tb in tables:
            csv_path = Path(tb + ".csv")
            if csv_path.exists():
                print("{} file/directory already exists, skip this file!".format(csv_path))
                continue

            with csv_path.open('w', newline='', encoding=encoding) as file:
                writer = csv.writer(file)
                writer.writerow((x[0] for x in con.execute("SELECT name FROM pragma_table_info('{}')".format(tb))))
                writer.writerows(con.execute("SELECT * FROM {}".format(tb)))

            print("{} file created".format(csv_path))


def is_integer(s):
    try:
        return str(int(s, base=10)) == s
    except ValueError:
        return False


def is_number(s):
    try:
        return math.isfinite(float(s))
    except ValueError:
        return False


def is_headline(line):
    return all((not is_number(x) for x in line))


def sql_date_str(s):
    if s[4] == "-" or s[4] == "/" or s[4] == ".":
        s = s.replace(s[4], "-")
    else:
        s = s[:4] + "-" + s[4:6] + "-" + s[6:]
    return datetime.datetime.strptime(s, "%Y-%m-%d").date().isoformat()


def format_value(s, sql_type, is_date=False):
    if sql_type == "TEXT":
        if is_date:
            s = sql_date_str(s)
        return "'" + s + "'"
    if not s or s == "NULL" or s == "null":
        return "NULL"
    return s


def get_table_columns(con, table):
    return con.execute("SELECT * FROM pragma_table_info('{}')".format(table)).fetchall()


def translate_value(con, s, table, col):
    if (table, col[1]) in VALUE_LOOKUPS:
        last_info = None
        for rule in VALUE_LOOKUPS[(table, col[1])]:
            lookup_cols = get_table_columns(con, rule[0])
            if lookup_cols[rule[1]][2] == "INTEGER" and not is_integer(s):
                continue
            lookup_val = format_value(s, lookup_cols[rule[1]][2])
            condition = "{} = {}".format(lookup_cols[rule[1]][1], lookup_val)
            if lookup_cols[rule[1]][2] == "TEXT":
                condition = "instr({}, {}) > 0".format(lookup_cols[rule[1]][1], lookup_val)
            cur = con.execute("SELECT {} FROM {} WHERE {}".format(lookup_cols[rule[2]][1], rule[0], condition))
            ret = cur.fetchall()
            if len(ret) == 1:
                s = str(ret[0][0])
                break
            else:
                last_info = "Found {} matches in {} with value {}".format(len(ret), rule[0], s)
                if ret:
                    last_info += ":" + " ".join((str(x[0]) for x in ret))
        else:
            print(last_info)
            raise ValueError("Cannot find an unambiguous foreign key using the column value")
    return format_value(s, col[2], (table, col[1]) in DATE_COLUMNS)


def insert_row(con, table, col_info, row, returning=None):
    values = (translate_value(con, x, table, y) for x, y in zip(row, col_info))
    returning = " returning " + returning if returning else ""
    cmd = "INSERT INTO {} VALUES ({}){}".format(table, ",".join(values), returning)
    print(cmd)
    return con.execute(cmd)


def atomic_insert(con, table, col_info, row):
    steps = COMBINED_INSERT.get((table, len(row)))
    if not steps:
        insert_row(con, table, col_info, row)
        return

    for step in steps:
        cur = insert_row(con, step.table_name, get_table_columns(con, step.table_name),
                         [row[i] for i in step.indices], step.returning)
        if step.returning:
            row = list(row) + [str(x) for x in cur.fetchone()]


@db_file_to_path
def insert(db_file, table, content):
    if not content:
        print("Column values are needed.")
        return

    with fence(sqlite3.connect(db_file)) as con:
        col_info = get_table_columns(con, table)
        if not col_info:
            print("Table \"{}\" does not exist.".format(table))
            return

        if len(col_info) != len(content) and (table, len(content)) not in COMBINED_INSERT:
            print("Table {} has {} columns but {} columns are provided.".format(table, len(col_info), len(content)))
            return

        with in_transaction(con):
            atomic_insert(con, table, col_info, content)

        print("Integrity check after insertion:")
        integrity_check(con)


@db_csv_file_to_path
def cmd_import(db_file, csv_file, table=None, encoding=None):
    if table is None:
        table = csv_file.stem

    with fence(sqlite3.connect(db_file)) as con:
        col_info = get_table_columns(con, table)
        if not col_info:
            print("Table \"{}\" does not exist.".format(table))
            return

        inserter = Inserter(con, table, col_info)
        with in_transaction(con):
            decode_csv(csv_file, encoding, inserter)

        print("\nIntegrity check after import:")
        integrity_check(con)


@db_file_to_path
def overwrite(db_file, table, content):
    with fence(sqlite3.connect(db_file)) as con:
        col_info = get_table_columns(con, table)
        if not col_info:
            print("Table \"{}\" does not exist.".format(table))
            return

        if len(col_info) != 1:
            print("Table {} has {} columns but this command requires exactly 1 column.".format(table, len(col_info)))
            return

        with in_transaction(con):
            con.execute("DELETE FROM {}".format(table))
            insert_row(con, table, col_info, (content,))

        print("Integrity check after overwrite:")
        integrity_check(con)


@db_file_to_path
def paste(db_file, table):
    content = subprocess.getoutput("powershell.exe -Command Get-Clipboard")
    with fence(sqlite3.connect(db_file)) as con:
        col_info = get_table_columns(con, table)
        if not col_info:
            print("Table \"{}\" does not exist.".format(table))
            return

        if table in OVERWRITE_TABLES:
            content = content.strip(" \t\r\n")
            with in_transaction(con):
                con.execute("DELETE FROM {}".format(table))
                insert_row(con, table, col_info, (content,))
        else:
            inserter = Inserter(con, table, col_info)
            with in_transaction(con):
                for row in content.splitlines():
                    inserter.handle(row.split("\t"))

        print("Integrity check after paste:")
        integrity_check(con)


def delete_row(con, table, col_info, content):
    condition = " AND ".join((x[1] + " = " + format_value(y, x[2], (table, x[1]) in DATE_COLUMNS)
                              for x, y in zip(col_info, content)))
    cmd = "DELETE FROM {} WHERE {}".format(table, condition)
    print(cmd)
    con.execute(cmd)


def atomic_delete(con, table, col_info, content):
    if table == "postings":
        sub_cols = get_table_columns(con, "posting_extras")
        delete_row(con, "posting_extras", [sub_cols[0]], content)
    delete_row(con, table, col_info, content)


@db_file_to_path
def delete(db_file, table, content):
    if not content:
        print("Key column values are needed.")
        return

    with fence(sqlite3.connect(db_file)) as con:
        col_info = get_table_columns(con, table)
        if not col_info:
            print("Table \"{}\" does not exist.".format(table))
            return

        col_info = [x for x in col_info if x[5] > 0]
        if len(col_info) != len(content):
            print("Table {} has {} key columns but {} columns are provided.".format(table, len(col_info), len(content)))
            return

        with in_transaction(con):
            atomic_delete(con, table, col_info, content)

        print("Integrity check after deletion:")
        integrity_check(con)


@db_csv_file_to_path
def prune(db_file, csv_file, table=None, encoding=None):
    if table is None:
        table = csv_file.stem

    with fence(sqlite3.connect(db_file)) as con:
        col_info = get_table_columns(con, table)
        if not col_info:
            print("Table \"{}\" does not exist.".format(table))
            return
        col_info = [x for x in col_info if x[5] > 0]

        deleter = Deleter(con, table, col_info)
        with in_transaction(con):
            decode_csv(csv_file, encoding, deleter)

        print("\nIntegrity check after prune:")
        integrity_check(con)


@db_file_to_path
def execsql(db_file, cmd):
    with fence(sqlite3.connect(db_file)) as con:
        with con:
            cur = con.execute(cmd)
            return_value = cur.fetchall()
            print("Execution success! Returns{}".format(
                ":\n" + "\n".join([str(x) for x in return_value]) if return_value else " nothing"))

        print("Integrity check after execution:")
        integrity_check(con)


@db_file_to_path
def upgrade(db_file):
    with fence(sqlite3.connect(db_file)) as con:
        (removed, different, added, incompatible) = definition_check(con)
        if incompatible:
            print("Unable to upgrade because some definitions are incompatible.")
            return
        if not (removed or different or added):
            return
        for x in removed + different:
            con.execute("DROP VIEW {}".format(x))
        for x in different + added:
            con.execute([s[2] for s in SQL_CREATE_COMMANDS if s[0] == x][0])
        print("All definitions have been fixed.")


if __name__ == "__main__":
    parser = ArgumentParser(description="Database operations")
    subparsers = parser.add_subparsers(required=True, help="sub-command help")

    parser_init = subparsers.add_parser("init", help="create a new db file and initialize")
    parser_init.add_argument("db_file", help="db filename to create with")
    parser_init.set_defaults(func=init)

    parser_check = subparsers.add_parser("check", help="check integrity of database content")
    parser_check.add_argument("db_file", help="db filename to check")
    parser_check.set_defaults(func=check)

    parser_export = subparsers.add_parser("export", help="export table(s) to csv file(s)")
    parser_export.add_argument("db_file", help="db filename to export")
    parser_export.add_argument("--table", help="single table name to export", choices=EXPORT_TABLES)
    parser_export.add_argument("--encoding", help="manually specify csv file's encoding")
    parser_export.set_defaults(func=export)

    parser_insert = subparsers.add_parser("insert", help="insert one row from command line")
    parser_insert.add_argument("db_file", help="db filename to insert into")
    parser_insert.add_argument("table", help="table name to insert into")
    parser_insert.set_defaults(func=insert)

    parser_import = subparsers.add_parser("import", help="import table content from csv file")
    parser_import.add_argument("db_file", help="db filename to import into")
    parser_import.add_argument("csv_file", help="csv filename to import from")
    parser_import.add_argument("--table", help="manually specify table name to import")
    parser_import.add_argument("--encoding", help="manually specify csv file's encoding")
    parser_import.set_defaults(func=cmd_import)

    parser_overwrite = subparsers.add_parser("overwrite", help="clear table content and insert only one value")
    parser_overwrite.add_argument("db_file", help="db filename to modify with")
    parser_overwrite.add_argument("table", help="table name to modify with")
    parser_overwrite.add_argument("content", help="the only value that will exist in the table")
    parser_overwrite.set_defaults(func=overwrite)

    parser_paste = subparsers.add_parser("paste", help="paste clipboard content info table")
    parser_paste.add_argument("db_file", help="db filename to paste into")
    parser_paste.add_argument("table", help="table name to paste into")
    parser_paste.set_defaults(func=paste)

    parser_delete = subparsers.add_parser("delete", help="delete one row by key columns")
    parser_delete.add_argument("db_file", help="db filename to delete from")
    parser_delete.add_argument("table", help="table name to delete from")
    parser_delete.set_defaults(func=delete)

    parser_prune = subparsers.add_parser("prune", help="delete all keys given by csv file")
    parser_prune.add_argument("db_file", help="db filename to delete from")
    parser_prune.add_argument("csv_file", help="csv filename to provide keys to delete")
    parser_prune.add_argument("--table", help="manually specify table name to delete from")
    parser_prune.add_argument("--encoding", help="manually specify csv file's encoding")
    parser_prune.set_defaults(func=prune)

    parser_execsql = subparsers.add_parser("execsql", help="execute custom SQL command")
    parser_execsql.add_argument("db_file", help="db filename to operate with")
    parser_execsql.add_argument("cmd", help="the SQL command string")
    parser_execsql.set_defaults(func=execsql)

    parser_upgrade = subparsers.add_parser("upgrade", help="upgrade SQL definitions in db file")
    parser_upgrade.add_argument("db_file", help="db filename to operate with")
    parser_upgrade.set_defaults(func=upgrade)

    args = parser.parse_known_args()
    func = vars(args[0]).pop("func")
    if func in [insert, delete]:
        func(**vars(args[0]), content=args[1])
    else:
        if args[1]:
            parser.print_usage()
            print("Error: unrecognized arguments: {}".format(" ".join(args[1])))
        else:
            func(**vars(args[0]))