import streamlit as st
import sqlite3
import threading

# 数据库文件
DB_FILE = "bookkeeping.sql"

# 创建线程局部存储，用于管理线程独立的数据库连接
thread_local = threading.local()

def get_db_connection():
    """为当前线程获取数据库连接"""
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect(DB_FILE, check_same_thread=False)
        # 确保数据库写操作有约束，减少冲突
        thread_local.connection.execute("PRAGMA journal_mode=WAL;")
    return thread_local.connection


if "db_connection" not in st.session_state:
    st.session_state["db_connection"] = get_db_connection()


# 初始化数据库表
def init_db():
    conn = st.session_state["db_connection"]
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE
            )
        """)

init_db()

# Streamlit 主界面
st.title("添加用户")

# 输入 token
if 'token' not in st.session_state:
    st.session_state.token = None

token = st.text_input("请输入您的 token", type="password")
if token:
    st.success(f"当前 token 为：{token}")
    st.session_state.token = token

    # 添加用户
    new_user = st.text_input("输入新用户名称")
    if st.button("添加用户"):
        if new_user:
            try:
                conn = get_db_connection()
                with conn:
                    conn.execute("INSERT INTO users (token, username) VALUES (?, ?)", (token, new_user))
                st.success(f"用户 {new_user} 已添加！")
            except sqlite3.IntegrityError:
                st.warning(f"用户 {new_user} 已存在。")
        else:
            st.error("请输入有效的用户名称。")

    # 显示用户列表
    conn = get_db_connection()
    with conn:
        users = conn.execute("SELECT username FROM users WHERE token = ?", (token,)).fetchall()
    users = [user[0] for user in users]
    if users:
        st.subheader("当前用户列表")
        st.write(", ".join(users))

        # 删除用户
        user_to_delete = st.selectbox("选择要删除的用户", users)
        if st.button("删除用户"):
            conn = get_db_connection()
            with conn:
                conn.execute("DELETE FROM users WHERE token = ? AND username = ?", (token, user_to_delete))
            st.success(f"用户 {user_to_delete} 已删除！")
            st.experimental_rerun()
    else:
        st.info("目前没有任何用户，请添加新用户。")

@st.on_session_end
def close_db_connection():
    if "db_connection" in st.session_state:
        st.session_state["db_connection"].close()
        del st.session_state["db_connection"]