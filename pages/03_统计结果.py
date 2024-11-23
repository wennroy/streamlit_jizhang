import streamlit as st
import pandas as pd
import sqlite3
from db_utils import DB_FILE, execute_query
from collections import defaultdict

st.title("欠款情况统计")

token = st.session_state.token
if not token:
    st.warning("请在第一页输入token以继续。")
    st.stop()

convert_ratios = {}

if token:
    currencies = execute_query("SELECT distinct currency FROM records WHERE token = ?", (token,))
    if len(currencies) == 1 and currencies[0][0] == "CNY":
        convert_ratios["CNY"] = 1.0
    else:
        for currency in currencies:
            currency_name = currency[0]
            if currency_name == "CNY":
                convert_ratios["CNY"] = 1.0
                continue
            convert_ratios[currency_name] = st.number_input(f"{currency_name}兑CNY汇率", min_value=0.0, format="%0.5f", value=1.0)

    if st.button("没有外币/已完成汇率换算填写"):
        with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            query = "SELECT payer, participant, currency, amount FROM records WHERE token = ?"
            records_df = pd.read_sql_query(query, conn, params=(token,))

            if not records_df.empty:
                summary_dict = defaultdict(float)

                # 计算欠款
                for _, row in records_df.iterrows():
                    summary_dict[row["participant"]] += row["amount"] * convert_ratios[row["currency"]]
                    summary_dict[row["payer"]] -= row["amount"] * convert_ratios[row["currency"]]

                # 转换为 DataFrame
                summary_df = pd.DataFrame(summary_dict.items(), columns=["参与人", "净欠款金额"])
                st.dataframe(summary_df)
            else:
                st.info("目前没有任何记录。")
