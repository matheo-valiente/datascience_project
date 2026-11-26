"""
Stack Overflow Developer Survey 2026 - Streamlit app
Data Visualisation final project (ECE)
"""

import pandas as pd
import streamlit as st

DATA_PATH = "data/survey_results_public.csv"
SCHEMA_PATH = "data/survey_results_schema.csv"


@st.cache_data
def load_data(path):
    # The files start with a BOM, so we read them with "utf-8-sig"
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


st.set_page_config(page_title="SO Survey 2026", layout="wide")
st.title("Stack Overflow Developer Survey 2026")
st.write("First look at the raw data.")

df = load_data(DATA_PATH)
schema = load_data(SCHEMA_PATH)

# Some key numbers
col1, col2, col3 = st.columns(3)
col1.metric("Respondents", f"{len(df):,}")
col2.metric("Columns", df.shape[1])
col3.metric("Countries", df["Country"].nunique() if "Country" in df.columns else "?")

st.subheader("Preview of the data")
st.dataframe(df.head(20))

st.subheader("Columns description")
st.dataframe(schema[["column", "question", "type", "nonmissing"]])
