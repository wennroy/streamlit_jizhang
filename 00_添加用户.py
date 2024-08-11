import streamlit as st
import pandas as pd

# 初始化数据
if 'records' not in st.session_state:
    st.session_state.records = []

if 'users' not in st.session_state:
    st.session_state.users = []

if 'success' not in st.session_state:
    st.session_state.success = ""

st.title("添加用户")

# 输入新用户名称
new_user = st.text_input("输入新用户名称")
if st.button("添加用户"):
    if new_user and new_user not in st.session_state.users:
        st.session_state.users.append(new_user)
        st.success(f"用户 {new_user} 已添加！")
    elif new_user in st.session_state.users:
        st.warning("用户已存在，请输入不同的名称。")
    else:
        st.error("请输入有效的用户名称。")

# 显示所有用户
if st.session_state.users:
    st.subheader("当前用户列表")
    st.write(", ".join(st.session_state.users))

    # 删除用户
    user_to_delete = st.selectbox("选择要删除的用户", st.session_state.users)
    if st.button("删除用户"):
        st.session_state.users.remove(user_to_delete)
        st.success(f"用户 {user_to_delete} 已删除！")
else:
    st.info("目前没有任何用户，请添加新用户。")