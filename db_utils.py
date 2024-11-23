import sqlite3
import threading

DB_FILE = "bookkeeping.sql"
thread_local = threading.local()


def get_db_connection():
    """为当前线程获取数据库连接"""
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect(DB_FILE, check_same_thread=False)
        thread_local.connection.execute("PRAGMA journal_mode=WAL;")
    return thread_local.connection
