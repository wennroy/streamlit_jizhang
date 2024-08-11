import streamlit as st
import pandas as pd


st.title("欠款情况统计")

if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    summary = df.groupby("participant")["amount"].sum().reset_index()
    summary.columns = ["参与人", "净欠款金额"]
    st.dataframe(summary)
else:
    st.info("目前没有任何记录。")