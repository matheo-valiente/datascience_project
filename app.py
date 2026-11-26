"""
Stack Overflow Developer Survey 2026 - Streamlit app
Data Visualisation final project (ECE)
"""

import streamlit as st

from utils import load_data

st.set_page_config(page_title="SO Survey 2026", layout="wide")
st.title("Stack Overflow Developer Survey 2026")
st.write("Clean data used by the app (see prepare_data.py).")

df = load_data()
france = df[df["Country"] == "France"]

# Some key numbers
col1, col2, col3, col4 = st.columns(4)
col1.metric("Respondents", f"{len(df):,}")
col2.metric("Countries", df["Country"].nunique())
col3.metric("Respondents in France", f"{len(france):,}")
col4.metric("Median salary in France", f"{france['SalaryEUR'].median():,.0f} €")

st.subheader("Preview of the clean data")
st.dataframe(df.head(20))
