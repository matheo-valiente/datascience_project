"""
Streamlit helpers shared by all the pages: cached loading, the common filter
kept in the session, and the display of the population behind each figure.

This is the only shared file that imports Streamlit (the logic is in src/).
"""

import pandas as pd
import streamlit as st

from src.cleaning import clean_survey
from src.config import FOCUS_COUNTRY, MIN_RESPONDENTS, SPONSOR, SURVEY_WARNING
from src.population import COMPARISON_GROUPS, describe_population, paid_population


# ---------------------------------------------------------------------------
# Data (cached: the raw files are read and cleaned only once)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading and cleaning the survey (only the first time)...")
def load_survey(year):
    """All the clean respondents of one year."""
    return clean_survey(year)


@st.cache_data(show_spinner=False)
def load_paid(year):
    """Respondents with a clean salary (employed people and freelancers)."""
    return paid_population(load_survey(year))


# ---------------------------------------------------------------------------
# Common filter (in the sidebar of every page, kept in st.session_state)
# ---------------------------------------------------------------------------
def comparison_selector(df):
    """
    Sidebar choice of the group France is compared with.
    It is drawn by app.py on every page, so its value
    st.session_state["comparison"] stays the same when the page changes.
    """
    # Only countries with enough salaries to compare a median
    counts = df["Country"].value_counts()
    countries = sorted(set(counts[counts >= MIN_RESPONDENTS].index) - {FOCUS_COUNTRY})
    st.sidebar.selectbox(
        f"Compare {FOCUS_COUNTRY} with",
        COMPARISON_GROUPS + countries,
        key="comparison",
        help=f"Used by all the pages. Countries with at least {MIN_RESPONDENTS} salaries in 2026.",
    )


def get_comparison():
    """Comparison group chosen in the sidebar."""
    return st.session_state.get("comparison", COMPARISON_GROUPS[0])


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
def page_header(title, question):
    """Title of the page and the question it answers."""
    st.title(title)
    st.markdown(f"**Question:** {question}")


def show_population(df, who, year):
    """Caption under a figure: who, which year, how many respondents."""
    st.caption(f"👥 {describe_population(df, who, year)}")


def show_chart(fig, table, population_text, note=None):
    """
    A chart, its population, an optional note, and the data behind it
    (table view: useful to read the exact values and for accessibility).
    """
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
    st.caption(f"👥 {population_text}")
    if note:
        st.caption(note)
    with st.expander("See the data of this chart"):
        st.dataframe(format_table(table), hide_index=True, width="stretch")


def format_table(table):
    """Round the numbers of a result table to make it readable."""
    table = table.copy()
    for column in table.columns:
        if pd.api.types.is_float_dtype(table[column]):
            table[column] = table[column].round(1 if "percent" in column else 0)
    return table


def footer():
    """Reminder at the bottom of each page."""
    st.divider()
    st.caption(f"⚠️ {SURVEY_WARNING}")
    st.caption(f"Source: Stack Overflow Developer Survey 2025 and 2026 · App made for {SPONSOR}.")
