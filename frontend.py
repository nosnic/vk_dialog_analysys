import streamlit as st
import vk_api

from tools import analyzer
from importlib import reload

reload(analyzer)
if 'token' not in st.session_state:
    st.session_state['token'] = ''
st.page_link("frontend.py", label="Home")

st.write("Введите свой access token:")
token = st.text_input("Access Token")
st.session_state.token = token
if st.session_state.token:
    try:
        vk_api.VkApi(token=token)
    except Exception as e:
        st.write("Пожалуйста, введите валидный access token.")
else:
    st.write("Пожалуйста, введите access token.")


st.page_link("./pages/dialog_analysis.py", label="Chat analyze")
st.page_link("./pages/friend_graph.py", label="Friend Graph")