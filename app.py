import streamlit as st
from slide_4p import run as run_4p
from slide_financial import run as run_financial
from sentiment_analysis import run as run_sentiment

st.set_page_config(page_title="AI Slide Generator")

st.sidebar.title("Slide Type")
page = st.sidebar.selectbox("Choose the slide to generate", ["4P Analysis", "Company Financial",  "Company News Sentiment"])


if page == "4P Analysis":
    run_4p()
elif page == "Company Financial":
    run_financial()
elif page == "Company News Sentiment":
    run_sentiment()
