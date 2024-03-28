import sqlite3
import csv
import math
import datetime
import locale
from pathlib import Path
from argparse import ArgumentParser
from functools import wraps
from contextlib import contextmanager
from collections import namedtuple


INIT_SQL_CMD = """
    BEGIN;

    CREATE TABLE asset_info(asset_index INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            asset_name TEXT NOT NULL,
                            asset_category INTEGER NOT NULL) STRICT;

    CREATE TABLE standard_asset(asset_index INTEGER PRIMARY KEY NOT NULL REFERENCES asset_info(asset_index)) STRICT;

    CREATE TABLE account_info(account_index INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                              account_name TEXT NOT NULL,
                              asset_index INTEGER NOT NULL REFERENCES asset_info(asset_index),
                              is_external INTEGER NOT NULL CHECK(is_external IN (0,1))) STRICT;

    CREATE TABLE interest_account(
        account_index INTEGER PRIMARY KEY NOT NULL REFERENCES account_info(account_index)) STRICT;

    CREATE TABLE postings(posting_index INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                          trade_date TEXT NOT NULL CHECK(date(trade_date) IS trade_date),
                          src_account INTEGER NOT NULL REFERENCES account_info(account_index),
                          src_amount REAL NOT NULL CHECK(src_amount <= 0),
                          dst_account INTEGER NOT NULL REFERENCES account_info(account_index),
                          comment TEXT) STRICT;

    CREATE INDEX postings_by_date ON postings(trade_date);

    CREATE TABLE receiving(posting_index INTEGER PRIMARY KEY NOT NULL REFERENCES postings(posting_index),
                           dst_amount REAL NOT NULL CHECK(dst_amount >= 0)) STRICT;

    CREATE TABLE prices(price_date TEXT NOT NULL CHECK(date(price_date) IS price_date),
                        asset_index INTEGER NOT NULL REFERENCES asset_info(asset_index),
                        price REAL NOT NULL,
                        PRIMARY KEY(price_date, asset_index),
                        UNIQUE(price_date, asset_index)) STRICT, WITHOUT ROWID;

    CREATE TABLE start_date(val TEXT PRIMARY KEY NOT NULL CHECK(date(val) IS val)) STRICT, WITHOUT ROWID;
    CREATE TABLE end_date(val TEXT PRIMARY KEY NOT NULL CHECK(date(val) IS val)) STRICT, WITHOUT ROWID;

    CREATE VIEW single_entries AS
        SELECT posting_index, trade_date, src_account AS account_index, src_amount AS amount,
            dst_account AS target, comment
        FROM postings
        UNION
        SELECT postings.posting_index, trade_date, dst_account AS account_index,
            ifnull(receiving.dst_amount, -src_amount) AS amount, src_account AS target, comment
        FROM postings LEFT JOIN receiving ON postings.posting_index = receiving.posting_index
        WHERE amount <> 0;

    CREATE VIEW statements AS
        SELECT single_entries.*, src_acc.account_name AS src_name, src_acc.asset_index, src_acc.is_external,
            target_acc.account_name AS target_name,
            sum(amount) OVER (PARTITION BY single_entries.account_index
                ORDER BY trade_date, posting_index ROWS UNBOUNDED PRECEDING) AS balance
        FROM single_entries INNER JOIN account_info AS src_acc ON single_entries.account_index = src_acc.account_index
            INNER JOIN account_info as target_acc ON single_entries.target = target_acc.account_index
        ORDER BY single_entries.account_index, trade_date, posting_index;

    CREATE VIEW start_balance AS
        SELECT start_date.val AS date_val, account_info.account_index, account_info.account_name,
            sum(single_entries.amount) AS balance, account_info.asset_index
        FROM single_entries INNER JOIN account_info ON single_entries.account_index = account_info.account_index,
            start_date
        WHERE single_entries.trade_date <= start_date.val AND account_info.is_external = 0
        GROUP BY account_info.account_index
        HAVING sum(single_entries.amount) <> 0;

    CREATE VIEW start_stats AS
        SELECT *, balance * price as worth
        FROM (SELECT asset_info.asset_category, start_balance.*, asset_info.asset_name,
                iif(asset_info.asset_index IN (SELECT * FROM standard_asset), 1.0,
                    (SELECT price FROM prices WHERE asset_info.asset_index = prices.asset_index
                        AND prices.price_date = start_balance.date_val)) AS price
            FROM start_balance INNER JOIN asset_info ON start_balance.asset_index = asset_info.asset_index
            ORDER BY asset_info.asset_category ASC);

    CREATE VIEW diffs AS
        SELECT account_info.account_index, account_info.account_name, sum(single_entries.amount) AS amount,
            account_info.asset_index
        FROM single_entries INNER JOIN account_info ON single_entries.account_index = account_info.account_index,
            start_date, end_date
        WHERE single_entries.trade_date > start_date.val AND single_entries.trade_date <= end_date.val
            AND account_info.is_external = 0
        GROUP BY account_info.account_index;

    CREATE VIEW comparison AS
        SELECT start_balance.account_index, start_balance.account_name, start_balance.balance AS init_amount,
            ifnull(diffs.amount, 0) AS diff, start_balance.balance + ifnull(diffs.amount, 0) AS end_amount,
            start_balance.asset_index
        FROM start_balance LEFT JOIN diffs ON start_balance.account_index = diffs.account_index
        UNION
        SELECT account_index, account_name, 0 AS init_amount, amount AS diff, amount AS end_amount, asset_index
        FROM diffs WHERE account_index NOT IN (SELECT account_index FROM start_balance);

    CREATE VIEW end_stats AS
        SELECT *, balance * price as worth
        FROM (SELECT asset_info.asset_category, end_date.val AS date_val, comparison.account_index, 
                comparison.account_name, comparison.end_amount AS balance, comparison.asset_index, 
                asset_info.asset_name,
                iif(asset_info.asset_index IN (SELECT * FROM standard_asset), 1.0,
                    (SELECT price FROM prices WHERE asset_info.asset_index = prices.asset_index
                        AND prices.price_date = end_date.val)) AS price
            FROM comparison INNER JOIN asset_info ON comparison.asset_index = asset_info.asset_index, end_date
            WHERE balance <> 0
            ORDER BY asset_info.asset_category ASC);

    CREATE VIEW expense_worth AS
        SELECT asset_category, account_index, account_name, sum(amount) AS total_amount, asset_index, asset_name,
            sum(price * amount) AS worth
        FROM (SELECT asset_info.asset_category, account_info.account_index, account_info.account_name,
                single_entries.amount, account_info.asset_index, asset_info.asset_name,
                iif(asset_info.asset_index IN (SELECT * FROM standard_asset), 1.0,
                    (SELECT price FROM prices WHERE asset_info.asset_index = prices.asset_index
                        AND prices.price_date = single_entries.trade_date)) AS price
            FROM single_entries INNER JOIN account_info ON single_entries.account_index = account_info.account_index
                INNER JOIN asset_info ON account_info.asset_index = asset_info.asset_index, start_date, end_date
            WHERE single_entries.trade_date > start_date.val AND single_entries.trade_date <= end_date.val
                AND account_info.is_external = 1)
        GROUP BY account_index
        ORDER BY asset_category ASC;

    CREATE VIEW invest_gain AS
        SELECT *, profit / start_equity AS return_rate, profit / end_equity AS conservative_rate
        FROM (SELECT *, end_equity + expense - start_equity AS profit
            FROM (SELECT sum(start_stats.worth) AS start_equity FROM start_stats),
                (SELECT sum(end_stats.worth) AS end_equity FROM end_stats),
                (SELECT sum(expense_worth.worth) AS expense FROM expense_worth
                 WHERE expense_worth.account_index NOT IN (SELECT * FROM interest_account)),
                (SELECT sum(expense_worth.worth) AS interest FROM expense_worth
                 WHERE expense_worth.account_index IN (SELECT * FROM interest_account)));

    CREATE VIEW expense_stats AS
        SELECT single_entries.account_index, exp_acc.account_name AS exp_name, single_entries.target, 
            target_acc.account_name AS target_name, sum(single_entries.amount) AS amount
        FROM single_entries INNER JOIN account_info as exp_acc ON single_entries.account_index = exp_acc.account_index
            INNER JOIN account_info as target_acc ON single_entries.target = target_acc.account_index
        WHERE single_entries.trade_date > (SELECT * FROM start_date)
            AND single_entries.trade_date <= (SELECT * FROM end_date)
            AND exp_acc.is_external = 1
        GROUP BY single_entries.account_index, single_entries.target;

    CREATE VIEW cash_to_invest AS
        SELECT single_entries.*, invest_acc.account_name,
            invest_acc.asset_index, asset_info.asset_name, asset_info.asset_category,
            amount * iif(cash_acc.asset_index IN (SELECT * FROM standard_asset), 1.0,
                (SELECT price FROM prices WHERE cash_acc.asset_index = prices.asset_index
                    AND prices.price_date = single_entries.trade_date)) AS worth
        FROM single_entries INNER JOIN account_info AS invest_acc ON single_entries.target = invest_acc.account_index
            INNER JOIN asset_info ON invest_acc.asset_index = asset_info.asset_index
            INNER JOIN account_info AS cash_acc ON single_entries.account_index = cash_acc.account_index
        WHERE single_entries.trade_date > (SELECT * FROM start_date)
            AND single_entries.trade_date <= (SELECT * FROM end_date)
            AND invest_acc.is_external = 0 AND single_entries.account_index <> single_entries.target
            AND single_entries.account_index NOT IN (SELECT * FROM interest_account)
            AND asset_info.asset_index NOT IN (SELECT * FROM standard_asset)
        ORDER BY asset_info.asset_category, single_entries.target,
            single_entries.trade_date, single_entries.posting_index;

    CREATE VIEW realisation AS
        SELECT asset_category, asset_index, asset_name, account_index, account_name,
            iif(min(balance) >= 0, 0, -min(balance)) AS petty, sum(worth) AS cash_gained
        FROM (SELECT asset_category, asset_index, asset_name, target AS account_index, account_name, worth,
                sum(worth) OVER (PARTITION BY target
                    ORDER BY trade_date, posting_index ROWS UNBOUNDED PRECEDING) AS balance
            FROM cash_to_invest)
        GROUP BY account_index
        ORDER BY asset_category, account_index;

    CREATE VIEW float_return AS
        SELECT *, (cash_gained + end_worth - init_worth) AS profit,
            iif(init_worth + petty <= 0, 0,
                (cash_gained + end_worth - init_worth) / (init_worth + petty)) AS return_rate
        FROM (SELECT asset_info.asset_category, asset_info.asset_index, asset_info.asset_name,
                comparison.account_index, comparison.account_name, comparison.init_amount,
                ifnull(start_stats.worth, 0) AS init_worth, comparison.diff, comparison.end_amount,
                ifnull(end_stats.worth, 0) AS end_worth, ifnull(realisation.cash_gained, 0) AS cash_gained,
                ifnull(realisation.petty, 0) AS petty
            FROM comparison INNER JOIN asset_info ON comparison.asset_index = asset_info.asset_index
                LEFT JOIN start_stats ON comparison.account_index = start_stats.account_index
                LEFT JOIN end_stats ON comparison.account_index = end_stats.account_index
                LEFT JOIN realisation ON comparison.account_index = realisation.account_index
            WHERE comparison.asset_index NOT IN (SELECT * FROM standard_asset));

    CREATE VIEW interest_sum AS
        SELECT single_entries.account_index, receive_acc.account_name, receive_acc.asset_index,
            sum(single_entries.amount) AS amount
        FROM single_entries INNER JOIN account_info AS src_acc ON single_entries.target = src_acc.account_index
            INNER JOIN account_info AS receive_acc ON single_entries.account_index = receive_acc.account_index
        WHERE single_entries.trade_date > (SELECT * FROM start_date)
            AND single_entries.trade_date <= (SELECT * FROM end_date)
            AND receive_acc.is_external = 0
            AND src_acc.account_index IN (SELECT * FROM interest_account)
        GROUP BY single_entries.account_index;

    CREATE VIEW fixed_return AS
        SELECT *, iif(capital <= 0, 0, interest / capital) AS return_rate
        FROM (SELECT day_stats.account_index, day_stats.account_name, day_stats.asset_index,
                ifnull(start_stats.balance, 0) + sum(day_stats.amount) / days AS capital,
                interest_sum.amount AS interest
            FROM (SELECT single_entries.account_index, account_info.account_name, account_info.asset_index,
                    single_entries.trade_date,
                    sum(single_entries.amount) * (julianday(end_date.val) - julianday(single_entries.trade_date))
                    AS amount, julianday(end_date.val) - julianday(start_date.val) AS days
                FROM (single_entries INNER JOIN account_info 
                    ON single_entries.account_index = account_info.account_index), start_date, end_date
                WHERE single_entries.trade_date > start_date.val
                    AND single_entries.trade_date <= end_date.val
                    AND single_entries.account_index IN (SELECT account_index FROM interest_sum)
                GROUP BY single_entries.account_index, single_entries.trade_date) AS day_stats
            LEFT JOIN start_stats ON day_stats.account_index = start_stats.account_index
            INNER JOIN interest_sum ON day_stats.account_index = interest_sum.account_index
            GROUP BY day_stats.account_index);

    CREATE VIEW check_standard_prices AS
        SELECT * FROM prices INNER JOIN standard_asset ON prices.asset_index = standard_asset.asset_index;

    CREATE VIEW check_interest_account AS
        SELECT account_info.*
        FROM interest_account INNER JOIN account_info ON interest_account.account_index = account_info.account_index
        WHERE account_info.is_external == 0;

    CREATE VIEW check_same_account AS
        SELECT * FROM postings WHERE postings.src_account == postings.dst_account;

    CREATE VIEW check_receiving AS
        SELECT postings.posting_index, postings.trade_date, postings.src_account, src_ai.account_name,
            src_ai.asset_index, src_ai.is_external, postings.src_amount, postings.dst_account, dst_ai.account_name,
            dst_ai.asset_index, dst_ai.is_external, receiving.dst_amount, postings.comment
        FROM postings LEFT JOIN receiving ON postings.posting_index = receiving.posting_index
            INNER JOIN account_info AS src_ai ON postings.src_account = src_ai.account_index
            INNER JOIN account_info AS dst_ai ON postings.dst_account = dst_ai.account_index
        WHERE src_ai.asset_index <> dst_ai.asset_index AND receiving.dst_amount ISNULL
            AND NOT (src_ai.asset_index IN (SELECT * FROM standard_asset)
                AND dst_ai.asset_index IN (SELECT * FROM standard_asset));

    CREATE VIEW check_same_asset AS
        SELECT postings.posting_index, postings.trade_date, postings.src_account, src_ai.account_name,
            src_ai.asset_index, src_ai.is_external, postings.src_amount, postings.dst_account, dst_ai.account_name,
            dst_ai.asset_index, dst_ai.is_external, receiving.dst_amount, postings.comment
        FROM postings INNER JOIN receiving ON postings.posting_index = receiving.posting_index
            INNER JOIN account_info AS src_ai ON postings.src_account = src_ai.account_index
            INNER JOIN account_info AS dst_ai ON postings.dst_account = dst_ai.account_index
        WHERE src_ai.asset_index == dst_ai.asset_index;

    CREATE VIEW check_absent_price AS
        SELECT asset_info.asset_index, asset_info.asset_name, asset_info.asset_category, absence.date_val
        FROM (SELECT start_balance.asset_index, start_date.val AS date_val
            FROM start_balance, start_date
            UNION
            SELECT comparison.asset_index, end_date.val AS date_val
            FROM comparison, end_date
            WHERE comparison.end_amount <> 0
            UNION
            SELECT cash_acc.asset_index, single_entries.trade_date AS date_val
            FROM single_entries
                INNER JOIN account_info AS invest_acc ON single_entries.target = invest_acc.account_index
                INNER JOIN account_info AS cash_acc ON single_entries.account_index = cash_acc.account_index
            WHERE single_entries.trade_date > (SELECT * FROM start_date)
                AND single_entries.trade_date <= (SELECT * FROM end_date)
                AND invest_acc.is_external = 0 AND single_entries.account_index <> single_entries.target
                AND single_entries.account_index NOT IN (SELECT * FROM interest_account)
                AND invest_acc.asset_index NOT IN (SELECT * FROM standard_asset)
            EXCEPT
            SELECT asset_index, price_date AS date_val FROM prices) AS absence
            INNER JOIN asset_info ON absence.asset_index = asset_info.asset_index
        WHERE absence.asset_index NOT IN (SELECT * FROM standard_asset)
        ORDER BY asset_info.asset_category, asset_info.asset_index, absence.date_val;

    COMMIT;
"""

EXPORT_TABLES = ("asset_info", "standard_asset", "account_info", "interest_account", "postings", "receiving", "prices",
                 "start_date", "end_date", "statements", "start_stats", "end_stats", "expense_worth", "invest_gain",
                 "expense_stats", "cash_to_invest", "float_return", "fixed_return")

DATE_COLUMNS = {("postings", "trade_date"), ("prices", "price_date"), ("start_date", "val"), ("end_date", "val")}

Step = namedtuple("Step", ("table_name", "indices", "returning"), defaults=(None, None, None))

COMBINED_INSERT = {("postings", 7):
                   (Step(table_name="postings", indices=(0, 1, 2, 3, 4, 5), returning="posting_index"),
                    Step(table_name="receiving", indices=(7, 6))),
                   ("account_info", 6):
                   (Step(table_name="asset_info", indices=(2, 4, 5), returning="asset_index"),
                    Step(table_name="account_info", indices=(0, 1, 6, 3)))}

VALUE_LOOKUPS = {("postings", "src_account"): (("account_info", 0, 0), ("account_info", 1, 0)),
                 ("postings", "dst_account"): (("account_info", 0, 0), ("account_info", 1, 0)),
                 ("interest_account", "account_index"): (("account_info", 0, 0), ("account_info", 1, 0)),
                 ("account_info", "asset_index"): (("asset_info", 0, 0), ("asset_info", 1, 0)),
                 ("prices", "asset_index"): (("asset_info", 0, 0), ("asset_info", 1, 0)),
                 ("standard_asset", "asset_index"): (("asset_info", 0, 0), ("asset_info", 1, 0))}


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
    except Exception as e:
        print(e)
        print("Operation failed! Rollback! File stays unmodified.")
    finally:
        con.close()


def decode_csv(con, csv_file, encoding, op):
    codecs = [encoding] if encoding else (
        [None] if locale.getpreferredencoding(False) == "utf-8" else [None, "utf-8"])
    for codec in codecs:
        try:
            with con:
                with csv_file.open(newline='', encoding=codec) as file:
                    for row in csv.reader(file):
                        if not op(row):
                            return
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
        ("check_receiving",
         "These postings should have receiving attached because source asset is different from target asset:"),
        ("check_same_asset",
         "These postings should NOT have receiving attached because source and target assets are same:"),
        ("check_absent_price", "These (date, asset) pairs need price info in calculation:")
    )
    all_passed = all((check_view(con, x, y) for x, y in views)) and all_passed

    if all_passed:
        print("Everything is fine, no integrity breach found.")


@db_file_to_path
def check(db_file):
    with fence(sqlite3.connect(db_file)) as con:
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

        with con:
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

        def import_by_row(row):
            print("> {}".format(row))
            if len(row) > len(col_info) and not any(row[len(col_info):]):
                row = row[:len(col_info)]

            if is_headline(row):
                print("Headline detected, Skip this row.")
            elif len(col_info) != len(row) and (table, len(row)) not in COMBINED_INSERT:
                print("Table {} has {} columns but {} columns are provided.".format(table, len(col_info), len(row)))
                return False
            else:
                atomic_insert(con, table, col_info, row)
            return True

        decode_csv(con, csv_file, encoding, import_by_row)

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

        with con:
            con.execute("DELETE FROM {}".format(table))
            insert_row(con, table, col_info, (content,))

        print("Integrity check after overwrite:")
        integrity_check(con)


def delete_row(con, table, col_info, content):
    condition = " AND ".join((x[1] + " = " + format_value(y, x[2], (table, x[1]) in DATE_COLUMNS)
                              for x, y in zip(col_info, content)))
    cmd = "DELETE FROM {} WHERE {}".format(table, condition)
    print(cmd)
    con.execute(cmd)


def atomic_delete(con, table, col_info, content):
    if table == "postings":
        sub_cols = get_table_columns(con, "receiving")
        delete_row(con, "receiving", [sub_cols[0]], content)
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

        with con:
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

        def prune_by_row(row):
            print("> {}".format(row))
            if is_headline(row):
                print("Headline detected, Skip this row.")
            elif len(col_info) != len(row):
                print("Table {} has {} key columns but {} columns are provided.".format(table, len(col_info), len(row)))
                return False
            atomic_delete(con, table, col_info, row)
            return True

        decode_csv(con, csv_file, encoding, prune_by_row)

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
