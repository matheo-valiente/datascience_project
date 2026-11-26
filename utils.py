"""
Functions shared by all the pages of the app.
"""

import pandas as pd
import streamlit as st

CLEAN_PATH = "data/survey_clean.parquet"


@st.cache_data
def load_data():
    """Load the clean data (created by prepare_data.py)."""
    return pd.read_parquet(CLEAN_PATH)


def count_multiselect(series):
    """
    Count the answers of a multi-select column (answers separated by ";").
    Example: "Python;SQL" counts 1 for Python and 1 for SQL.

    Returns a table with, for each answer, the number of respondents and
    the percentage of people who answered the question.
    """
    answered = series.dropna()
    counts = answered.str.split(";").explode().value_counts()
    result = counts.rename_axis("answer").reset_index(name="count")
    result["percent"] = (result["count"] / len(answered) * 100).round(1)
    return result
