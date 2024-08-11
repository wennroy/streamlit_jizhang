import streamlit as st
import pandas as pd
from collections import defaultdict


st.title("欠款情况统计")
summary_dict = defaultdict(float)

if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    for index, row in df.iterrows():
        summary_dict[row["participant"]] += row["amount"]
        summary_dict[row["payer"]] -= row["amount"]

    summary_df = pd.DataFrame(summary_dict.items())
    summary_df.columns = ["参与人", "净欠款金额"]
    st.dataframe(summary_df)
else:
    st.info("目前没有任何记录。")