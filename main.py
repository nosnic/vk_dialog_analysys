import streamlit as st
from tools import analyzer
from importlib import reload

reload(analyzer)


st.page_link("main.py", label="Home")
st.page_link("./pages/app.py", label="Chat analyze")
st.page_link("./pages/friend_graph.py", label="Friend Graph")