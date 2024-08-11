import streamlit as st
import pandas as pd

# 第一个页面 - 记账模式
st.title("记账模式")

if not st.session_state.users:
    st.warning("请先添加用户！")

# 输入框
total_amount = st.number_input("总金额", min_value=0.0, step=0.01)
convert_ratio = st.number_input("汇率(如有)", min_value=0.0, format="%0.5f", value=1.0)
comment = st.text_input("事项与注释")
participants = st.multiselect("参与人", st.session_state.users)
payer = st.selectbox("付款人", st.session_state.users)
mode = st.selectbox("记账模式", ["人均模式", "个人金额记录"])

if mode == "人均模式":
    if st.button("添加记录"):
        if payer and participants:
            amount_per_person = total_amount * convert_ratio / len(participants)
            record_id = st.session_state.records[-1]["record_id"] + 1 if st.session_state.records else 0
            for person in participants:
                st.session_state.records.append({
                    "id": st.session_state.records[-1]["id"] + 1 if st.session_state.records else 0,
                    "record_id": record_id,
                    "payer": payer,
                    "participant": person.strip(),
                    "amount": amount_per_person,
                })
            st.session_state.comments.append({
                "record_id": record_id,
                "comment": comment
            })
            st.session_state.success = f"记录{record_id}已添加！"
        else:
            st.error("请选择参与人和付款人。")

elif mode == "个人金额记录":
    individual_amounts = {}
    for person in participants:
        max_value = total_amount
        input_num = st.number_input(f"{person.strip()} 应付金额", min_value=0.0, step=0.01,
                                                                max_value=max_value)
    total_individual_amounts = sum(individual_amounts.values())

    if st.button("添加记录"):
        if abs(total_individual_amounts - total_amount) > 1e-5:
            st.error("总金额与各参与者金额总和不符。")
        elif payer and participants:
            record_id = st.session_state.records[-1]["record_id"] + 1 if st.session_state.records else 0
            for person, amount in individual_amounts.items():
                st.session_state.records.append({
                    "id": st.session_state.records[-1]["id"] + 1 if st.session_state.records else 0,
                    "record_id": record_id,
                    "payer": payer,
                    "participant": person.strip(),
                    "amount": amount
                })
            st.session_state.comments.append({
                "record_id": record_id,
                "comment": comment
            })
            st.session_state.individual_amounts = {}
            st.session_state.success = f"记录{record_id}已添加！"
        else:
            st.error("请选择参与人和付款人。")

if st.session_state.success:
    st.success(st.session_state.success)

if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.subheader("所有记录")
    st.dataframe(df)
    comment_df = pd.DataFrame(st.session_state.comments)
    st.subheader("事项记录(通过record_id)进行连接")
    st.dataframe(comment_df)

    # 删除某一行数据
    st.subheader("删除记录")
    row_to_delete = st.number_input("输入要删除的id", min_value=0, step=1)
    if st.button("删除记录"):
        if len(df) > 0:
            record_id_to_remove = -1
            for ind, row in enumerate(st.session_state.records):
                if row["id"] == row_to_delete:
                    record_id_to_remove = row["record_id"]
                    st.session_state.records.pop(ind)
                    st.session_state.success = "记录已删除！"
            all_were_deleted = True
            for ind, row in enumerate(st.session_state.records):
                if record_id_to_remove == row["record_id"]:
                    all_were_deleted = False
                    break
            if all_were_deleted:
                ind_to_delete = None
                for ind, row in enumerate(st.session_state.comments):
                    if row["record_id"] == record_id_to_remove:
                        ind_to_delete = ind
                        break
                if ind_to_delete is not None:
                    st.session_state.comments.pop(ind_to_delete)
            st.rerun()

    # 清空所有数据
    if st.button("清空所有数据"):
        st.session_state.records.clear()
        st.session_state.comments.clear()
        st.session_state.success = "所有记录已清空！"
        st.rerun()
else:
    st.info("目前没有任何记录。")
