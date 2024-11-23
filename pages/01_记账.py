import streamlit as st
import pandas as pd
import sqlite3
import os

# 初始化数据库连接
DB_FILE = "bookkeeping.sql"
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

conn = get_db_connection()
cursor = conn.cursor()

# 创建表结构
cursor.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    payer TEXT,
    participant TEXT,
    amount REAL,
    token TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    comment TEXT,
    token TEXT
)
""")
conn.commit()

# 用户登录
st.title("记账系统")
token = st.session_state.token
if not token:
    st.warning("请在第一页输入token以继续。")
    st.stop()

# 加载用户数据
def load_data():
    records = pd.read_sql_query(f"SELECT * FROM records WHERE token = ?", conn, params=(token,))
    comments = pd.read_sql_query(f"SELECT * FROM comments WHERE token = ?", conn, params=(token,))
    return records, comments

records_df, comments_df = load_data()

# 第一个页面 - 记账模式
st.subheader("记账模式")

if token:
    # 从数据库获取用户列表
    users = [row[0] for row in conn.execute("SELECT username FROM users WHERE token = ?", (token,)).fetchall()]

    if not users:
        st.warning("请先添加用户！")
    else:
        # 使用用户列表
        st.write("当前用户列表:", ", ".join(users))
        # 你的记账逻辑可以继续使用 `users` 列表
else:
    st.info("请输入 token 以加载用户列表。")

total_amount = st.number_input("总金额", min_value=0.0, step=0.01)
convert_ratio = st.number_input("汇率(如有)", min_value=0.0, format="%0.5f", value=1.0)
comment = st.text_input("事项与注释")
participants = st.multiselect("参与人", users)
payer = st.selectbox("付款人", users)
mode = st.selectbox("记账模式", ["人均模式", "个人金额记录"])

if mode == "人均模式":
    if st.button("添加记录"):
        if payer and participants:
            amount_per_person = total_amount * convert_ratio / len(participants)
            cursor.execute("SELECT MAX(record_id) FROM records WHERE token = ?", (token,))
            record_id = (cursor.fetchone()[0] or 0) + 1
            for person in participants:
                cursor.execute("""
                    INSERT INTO records (record_id, payer, participant, amount, token)
                    VALUES (?, ?, ?, ?, ?)
                """, (record_id, payer, person.strip(), amount_per_person, token))
            cursor.execute("""
                INSERT INTO comments (record_id, comment, token)
                VALUES (?, ?, ?)
            """, (record_id, comment, token))
            conn.commit()
            st.success(f"记录 {record_id} 已添加！")
        else:
            st.error("请选择参与人和付款人。")

elif mode == "个人金额记录":
    individual_amounts = {}
    for person in participants:
        max_value = total_amount
        individual_amounts[person] = st.number_input(f"{person.strip()} 应付金额", min_value=0.0, step=0.01, max_value=max_value)
    total_individual_amounts = sum(individual_amounts.values())

    if st.button("添加记录"):
        if abs(total_individual_amounts - total_amount) > 1e-5:
            st.error("总金额与各参与者金额总和不符。")
        elif payer and participants:
            cursor.execute("SELECT MAX(record_id) FROM records WHERE token = ?", (token,))
            record_id = (cursor.fetchone()[0] or 0) + 1
            for person, amount in individual_amounts.items():
                cursor.execute("""
                    INSERT INTO records (record_id, payer, participant, amount, token)
                    VALUES (?, ?, ?, ?, ?)
                """, (record_id, payer, person.strip(), amount, token))
            cursor.execute("""
                INSERT INTO comments (record_id, comment, token)
                VALUES (?, ?, ?)
            """, (record_id, comment, token))
            conn.commit()
            st.success(f"记录 {record_id} 已添加！")
        else:
            st.error("请选择参与人和付款人。")

# 显示所有记录
st.subheader("所有记录")
st.dataframe(records_df)
st.subheader("事项记录 (通过 record_id 连接)")
st.dataframe(comments_df)

# 删除记录
st.subheader("删除记录")
row_to_delete = st.number_input("输入要删除的 id", min_value=0, step=1)
if st.button("删除记录"):
    cursor.execute("DELETE FROM records WHERE id = ? AND token = ?", (row_to_delete, token))
    cursor.execute("""
        DELETE FROM comments 
        WHERE record_id NOT IN (SELECT record_id FROM records WHERE token = ?) AND token = ?
    """, (token, token))
    conn.commit()
    st.success(f"记录 {row_to_delete} 已删除！")
    st.experimental_rerun()

# 清空所有数据
if st.button("清空所有数据"):
    cursor.execute("DELETE FROM records WHERE token = ?", (token,))
    cursor.execute("DELETE FROM comments WHERE token = ?", (token,))
    conn.commit()
    st.success("所有记录已清空！")
    st.experimental_rerun()

# 关闭数据库连接
st.on_shutdown(lambda: conn.close())
