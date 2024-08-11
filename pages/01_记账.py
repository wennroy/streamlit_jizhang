import streamlit as st
import pandas as pd

# 第一个页面 - 记账模式
st.title("记账模式")


if not st.session_state.users:
    st.warning("请先添加用户！")


# 输入框
total_amount = st.number_input("总金额", min_value=0.0, step=0.01)
participants = st.multiselect("参与人", st.session_state.users)
payer = st.selectbox("付款人", st.session_state.users)
mode = st.selectbox("记账模式", ["人均模式", "个人金额记录"])

if mode == "人均模式":
    if st.button("添加记录"):
        if payer and participants:
            amount_per_person = total_amount / len(participants)
            for person in participants:
                if person.strip() == payer:
                    st.session_state.records.append({
                        "payer": person.strip(),
                        "participant": person.strip(),
                        "amount": -(total_amount - amount_per_person)
                    })
                else:
                    st.session_state.records.append({
                        "payer": payer,
                        "participant": person.strip(),
                        "amount": amount_per_person
                    })
            st.success("记录已添加！")
        else:
            st.error("请选择参与人和付款人。")

elif mode == "个人金额记录":
    individual_amounts = {}
    for person in participants:
        individual_amounts[person.strip()] = st.number_input(f"{person.strip()} 应付金额", min_value=0.0, step=0.01)

    if st.button("添加记录"):
        if payer and participants:
            total_individual_amounts = sum(individual_amounts.values())
            for person, amount in individual_amounts.items():
                if person.strip() == payer:
                    st.session_state.records.append({
                        "payer": person.strip(),
                        "participant": person.strip(),
                        "amount": -(total_individual_amounts - amount)
                    })
                else:
                    st.session_state.records.append({
                        "payer": payer,
                        "participant": person.strip(),
                        "amount": amount
                    })
            st.success("记录已添加！")
        else:
            st.error("请选择参与人和付款人。")

st.subheader("当前记录：")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.subheader("所有记录")
    st.dataframe(df)

    # 删除某一行数据
    st.subheader("删除记录")
    row_to_delete = st.number_input("输入要删除的行号 (从 0 开始)", min_value=0, max_value=len(df) - 1, step=1)
    if st.button("删除记录"):
        if len(df) > 0:
            st.session_state.records.pop(row_to_delete)
            st.session_state.success = "记录已删除！"
            st.rerun()

    # 清空所有数据
    if st.button("清空所有数据"):
        st.session_state.records.clear()
        st.session_state.success = "所有记录已清空！"
        st.rerun()
else:
    st.info("目前没有任何记录。")

if st.session_state.success:
    st.success(st.session_state.success)