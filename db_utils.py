import sqlite3
import pandas as pd

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
