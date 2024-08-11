import streamlit as st
import pandas as pd
from io import BytesIO

st.title("导出/导入")

# 导出为Excel
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()

    st.download_button(
        label="导出为 Excel",
        data=processed_data,
        file_name="bookkeeping.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 导入Excel
uploaded_file = st.file_uploader("从 Excel 导入", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.session_state.records.extend(df.to_dict(orient="records"))
    st.success("数据已导入！")
