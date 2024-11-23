import streamlit as st
import pandas as pd
import sqlite3
from collections import defaultdict

# 初始化数据库连接
DB_FILE = "bookkeeping.sql"
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

conn = get_db_connection()

st.title("欠款情况统计")

token = st.session_state.token
if not token:
    st.warning("请在第一页输入token以继续。")
    st.stop()

if token:
    # 从数据库中加载记录
    query = "SELECT payer, participant, amount FROM records WHERE token = ?"
    records_df = pd.read_sql_query(query, conn, params=(token,))

    if not records_df.empty:
        summary_dict = defaultdict(float)

        # 计算欠款
        for _, row in records_df.iterrows():
            summary_dict[row["participant"]] += row["amount"]
            summary_dict[row["payer"]] -= row["amount"]

        # 转换为 DataFrame
        summary_df = pd.DataFrame(summary_dict.items(), columns=["参与人", "净欠款金额"])
        st.dataframe(summary_df)
    else:
        st.info("目前没有任何记录。")
