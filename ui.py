"""
Streamlit helpers shared by all the pages: cached loading, the common filter
kept in the session, and the display of the population behind each figure.

This is the only shared file that imports Streamlit (the logic is in src/).
"""

import pandas as pd
import streamlit as st

from src.cleaning import clean_survey
from src.config import FOCUS_COUNTRY, MIN_RESPONDENTS, SPONSOR, SURVEY_WARNING
from src.population import (COMPARISON_GROUPS, describe_filters, describe_population,
                            paid_population)


# ---------------------------------------------------------------------------
# Data (cached: the raw files are read and cleaned only once)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Downloading and cleaning the survey (only the first time, about 1 minute)...")
def _clean_survey_cached(year):
    return clean_survey(year)


def load_survey(year):
    """All the clean respondents of one year (cached)."""
    try:
        return _clean_survey_cached(year)
    except OSError as error:
        # No internet, or the archive of Stack Overflow is not reachable
        st.error(f"The survey {year} could not be downloaded ({error}). "
                 "Check the internet connection, or download the files with "
                 "`python -m src.data`, then reload the page.")
        st.stop()


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
# Filters of an axis (kept in st.session_state when the page changes)
# ---------------------------------------------------------------------------
def _remember(key):
    st.session_state[f"saved_{key}"] = st.session_state[key]


def remembered_multiselect(label, options, key, container=st, help=None):
    """
    A multiselect whose value is kept when the user goes to another page and comes back.
    Streamlit forgets the value of a widget that is not on the screen, so we also
    save it in st.session_state["saved_<key>"].
    An empty selection means "all".
    """
    saved = st.session_state.get(f"saved_{key}", [])
    return container.multiselect(
        label, options, default=[value for value in saved if value in options],
        key=key, on_change=_remember, args=(key,), placeholder="All", help=help,
    )


def remembered_radio(label, options, key, container=st):
    """One choice among a few options (horizontal), kept when the page changes."""
    saved = st.session_state.get(f"saved_{key}", options[0])
    index = options.index(saved) if saved in options else 0
    return container.radio(label, options, index=index, key=key, horizontal=True,
                           on_change=_remember, args=(key,))


def filters_row(df, prefix, columns):
    """
    One row of filters above the charts of an axis.
    columns is a dict {column: label}, for example {"ExperienceLevel": "Experience"}.
    Returns the filters as a dict {column: selected values}, to use with
    population.apply_filters and population.describe_filters.
    """
    filters = {}
    for container, (column, label) in zip(st.columns(len(columns)), columns.items()):
        values = df[column].dropna()
        if isinstance(values.dtype, pd.CategoricalDtype):
            options = [c for c in values.cat.categories if c in set(values)]
        else:
            options = sorted(values.unique())
        filters[column] = remembered_multiselect(label, options, f"{prefix}_{column}", container)
    return filters


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
def page_header(title, question):
    """Title of the page and the question it answers."""
    st.title(title)
    st.markdown(f"**Question:** {question}")


def show_population(df, who, year, filters=None):
    """Caption under a figure: who, which year, how many respondents (and the filters)."""
    text = describe_population(df, who, year)
    if filters and any(filters.values()):
        text += f" · filters: {describe_filters(filters)}"
    st.caption(f"👥 {text}")


def show_chart(fig, table, population_text, note=None, key=None):
    """
    A chart, its population, an optional note, and the data behind it
    (table view: useful to read the exact values and for accessibility).
    key: give a unique name if the same kind of chart is shown twice on a page.
    """
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False}, key=key)
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
