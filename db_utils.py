import sqlite3
import pandas as pd
import numpy as np

DB_FILE = "bookkeeping.sql"


def execute_query(query, params=None):
    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.fetchall()


def load_data(token):
    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
        records = pd.read_sql_query(f"SELECT * FROM records WHERE token = ?", conn, params=(token,))
        comments = pd.read_sql_query(f"SELECT * FROM comments WHERE token = ?", conn, params=(token,))
    return records, comments


def create_merge_view(left, right):
    merge_df = pd.merge(left, right, how="inner", on="record_id")
    merge_df_1 = merge_df[["record_id", "comment", "payer", "participant", "amount", "currency"]]
    mask = merge_df_1.groupby(["record_id", 'comment', 'payer']).cumcount() == 0

    result = merge_df_1.copy()
    result.loc[~mask, ['record_id', 'comment', 'payer']] = np.nan

    return result
