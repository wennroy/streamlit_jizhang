import streamlit as st
from db_utils import execute_query
import sqlite3


# 初始化数据库表
def init_db():
    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            token TEXT NOT NULL,
            username TEXT NOT NULL
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
                execute_query("INSERT INTO users (token, username) VALUES (?, ?)", (token, new_user))
                st.success(f"用户 {new_user} 已添加！")
            except sqlite3.IntegrityError:
                st.warning(f"用户 {new_user} 已存在。")
        else:
            st.error("请输入有效的用户名称。")

    # 显示用户列表
    users = execute_query("SELECT username FROM users WHERE token = ?", (token,))
    users = [user[0] for user in users]
    if users:
        st.subheader("当前用户列表")
        st.write(", ".join(users))

        # 删除用户
        user_to_delete = st.selectbox("选择要删除的用户", users)
        if st.button("删除用户"):
            execute_query("DELETE FROM users WHERE token = ? AND username = ?", (token, user_to_delete))
            st.success(f"用户 {user_to_delete} 已删除！")
            st.rerun()
    else:
        st.info("目前没有任何用户，请添加新用户。")
