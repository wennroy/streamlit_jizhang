import streamlit as st
import pandas as pd
from io import BytesIO

# 初始化session_state
if 'records' not in st.session_state:
    st.session_state.records = []
if 'comments' not in st.session_state:
    st.session_state.comments = []
if 'success' not in st.session_state:
    st.session_state.success = None

st.title("导出/导入")

# 导出为Excel
if st.session_state.records or st.session_state.comments:
    records_df = pd.DataFrame(st.session_state.records)
    comments_df = pd.DataFrame(st.session_state.comments)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        records_df.to_excel(writer, index=False, sheet_name='records')
        comments_df.to_excel(writer, index=False, sheet_name='comment')

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
    with pd.ExcelFile(uploaded_file) as xls:
        if 'records' in xls.sheet_names and 'comment' in xls.sheet_names:
            records_df = pd.read_excel(xls, sheet_name='records')
            user_set = set()
            comments_df = pd.read_excel(xls, sheet_name='comment')

            # 计算新的 record_id 和 id 的起始值
            max_record_id = max([r["record_id"] for r in st.session_state.records], default=-1) + 1
            max_id = max([r["id"] for r in st.session_state.records], default=-1) + 1

            # 重新分配 record_id 和 id
            record_id_map = {}
            for i, row in records_df.iterrows():
                original_record_id = row['record_id']
                user_set.add(row["payer"])
                user_set.add(row["participant"])
                if original_record_id not in record_id_map:
                    record_id_map[original_record_id] = max_record_id
                    max_record_id += 1

                st.session_state.records.append({
                    "id": max_id,
                    "record_id": record_id_map[original_record_id],
                    "payer": row["payer"],
                    "participant": row["participant"],
                    "amount": row["amount"]
                })
                max_id += 1

            # Update user
            for user in user_set:
                if user not in st.session_state.users:
                    st.session_state.users.append(user)

            # 更新 comments 中的 record_id
            for i, row in comments_df.iterrows():
                if row['record_id'] in record_id_map:
                    new_record_id = record_id_map[row['record_id']]
                    st.session_state.comments.append({
                        "record_id": new_record_id,
                        "comment": row["comment"]
                    })

            st.success("数据已导入并重新分配 ID！")
        else:
            st.error("Excel文件中缺少必要的工作表（'records'或'comment'）。")

# 显示导入后的数据
if st.session_state.records:
    st.subheader("所有记录")
    records_df = pd.DataFrame(st.session_state.records)
    st.dataframe(records_df)

if st.session_state.comments:
    st.subheader("事项记录 (通过 record_id 进行连接)")
    comments_df = pd.DataFrame(st.session_state.comments)
    st.dataframe(comments_df)
