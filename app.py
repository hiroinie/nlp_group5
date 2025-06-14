import streamlit as st
from slide_4p import run as run_4p
from slide_financial import run as run_financial

st.set_page_config(page_title="AI Slide Generator")

st.sidebar.title("Slide Type")
page = st.sidebar.selectbox("Choose the slide to generate", ["4P Analysis", "Company Financial"])

if page == "4P Analysis":
    run_4p()
else:
    run_financial()
