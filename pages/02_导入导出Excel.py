import streamlit as st
import pandas as pd
from db_utils import execute_query, DB_FILE, load_data
import sqlite3
from io import BytesIO

# 初始化数据库连接
DB_FILE = "bookkeeping.sql"
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

conn = get_db_connection()

st.title("导出/导入")


token = st.session_state.token
if not token:
    st.warning("请在第一页输入token以继续。")
    st.stop()

if token:
    records_df, comments_df = load_data(token)

    if not records_df.empty or not comments_df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            records_df.to_excel(writer, index=False, sheet_name="records")
            comments_df.to_excel(writer, index=False, sheet_name="comments")

        processed_data = output.getvalue()
        st.download_button(
            label="导出为 Excel",
            data=processed_data,
            file_name="bookkeeping.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# 导入Excel
uploaded_file = st.file_uploader("从 Excel 导入", type=["xlsx"])
if uploaded_file and token:
    with pd.ExcelFile(uploaded_file) as xls:
        if "records" in xls.sheet_names and "comments" in xls.sheet_names:
            imported_records_df = pd.read_excel(xls, sheet_name="records")
            imported_comments_df = pd.read_excel(xls, sheet_name="comments")

            # 插入到数据库
            with conn:
                imported_records_df["token"] = token
                imported_comments_df["token"] = token
                imported_records_df.to_sql("records", conn, if_exists="append", index=False)
                imported_comments_df.to_sql("comments", conn, if_exists="append", index=False)

            st.success("数据已导入！")
        else:
            st.error("Excel 文件中缺少必要的工作表（'records' 或 'comments'）。")

# 显示导入后的数据
if token:
    st.subheader("所有记录")
    st.dataframe(records_df)

    st.subheader("事项记录 (通过 record_id 进行连接)")
    st.dataframe(comments_df)
