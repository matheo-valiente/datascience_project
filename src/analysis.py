"""
Analysis functions: they take a DataFrame and return a small table.
No Streamlit and no charts here, so each function can be tested on its own.

All the salary tables have the same columns:
    n        number of respondents in the group
    median   median salary
    q1, q3   first and third quartiles (the middle 50% of the salaries)
    reliable True if n >= MIN_RESPONDENTS
"""

import pandas as pd

from src.config import MIN_RESPONDENTS


def salary_summary(df, value="SalaryEUR"):
    """Number of respondents, median and quartiles of a salary column."""
    salary = df[value].dropna()
    return {
        "n": len(salary),
        "median": salary.median(),
        "q1": salary.quantile(0.25),
        "q3": salary.quantile(0.75),
    }


def gap_percent(value, reference):
    """Gap in % between a value and a reference (negative = below the reference)."""
    if pd.isna(value) or pd.isna(reference) or reference == 0:
        return None
    return (value / reference - 1) * 100


def median_by_group(df, group_column, value="SalaryEUR", min_n=MIN_RESPONDENTS):
    """Median salary for each value of a column (for example each country)."""
    data = df[[group_column, value]].dropna()
    grouped = data.groupby(group_column, observed=True)[value]
    table = pd.DataFrame({
        "n": grouped.size(),
        "median": grouped.median(),
        "q1": grouped.quantile(0.25),
        "q3": grouped.quantile(0.75),
    }).reset_index()
    table["reliable"] = table["n"] >= min_n
    return table


def compare_groups(groups, group_column, value="SalaryEUR", min_n=MIN_RESPONDENTS):
    """
    Same as median_by_group, for several populations at once.
    groups is a dict {label: DataFrame}, for example {"France": ..., "EU": ...}.
    The result has a column "group" with the label.
    """
    tables = []
    for label, df in groups.items():
        table = median_by_group(df, group_column, value, min_n)
        table.insert(0, "group", label)
        tables.append(table)
    return pd.concat(tables, ignore_index=True)


def evolution(df_old, df_new, group_column=None, value="SalaryEUR", min_n=MIN_RESPONDENTS):
    """
    Median salary of two years side by side, and the change in %.
    Without group_column, it compares the two whole populations.
    Only use it on harmonised columns (see docs/HARMONISATION.md).
    """
    old_year = int(df_old["Year"].iloc[0])
    new_year = int(df_new["Year"].iloc[0])

    if group_column is None:
        rows = []
        for year, df in [(old_year, df_old), (new_year, df_new)]:
            summary = salary_summary(df, value)
            rows.append({"Year": year, "n": summary["n"], "median": summary["median"]})
        table = pd.DataFrame(rows)
        table["reliable"] = table["n"] >= min_n
        return table

    old = median_by_group(df_old, group_column, value, min_n)
    new = median_by_group(df_new, group_column, value, min_n)
    table = old.merge(new, on=group_column, suffixes=(f"_{old_year}", f"_{new_year}"))
    table["change_percent"] = (table[f"median_{new_year}"] / table[f"median_{old_year}"] - 1) * 100
    table["reliable"] = table[f"reliable_{old_year}"] & table[f"reliable_{new_year}"]
    return table


def evolution_of_groups(groups, value="SalaryEUR", min_n=MIN_RESPONDENTS):
    """
    Evolution of several whole populations between two years.
    groups is a dict {label: (df_old, df_new)}, for example {"France": (fr_2025, fr_2026)}.
    Returns one row per label, in the same format as evolution(..., group_column).
    """
    rows = []
    for label, (df_old, df_new) in groups.items():
        table = evolution(df_old, df_new, value=value, min_n=min_n)
        old, new = table.iloc[0], table.iloc[1]
        rows.append({
            "group": label,
            f"n_{old['Year']}": old["n"],
            f"median_{old['Year']}": old["median"],
            f"n_{new['Year']}": new["n"],
            f"median_{new['Year']}": new["median"],
            "change_percent": gap_percent(new["median"], old["median"]),
            "reliable": bool(table["reliable"].all()),
        })
    return pd.DataFrame(rows)


def count_multiselect(series):
    """
    Count the answers of a multi-select column (answers separated by ";").
    Example: "Python;SQL" counts 1 for Python and 1 for SQL.
    percent = share of the people who answered the question.
    """
    answered = series.dropna()
    counts = answered.str.split(";").explode().value_counts()
    table = counts.rename_axis("answer").reset_index(name="count")
    table["percent"] = table["count"] / len(answered) * 100
    return table


def count_single_choice(series):
    """
    Same table as count_multiselect, for a question with only one answer per person.
    The order of the categories is kept (for example from "Very unfavorable" to "Very favorable").
    """
    answered = series.dropna()
    counts = answered.value_counts(sort=False)
    if not isinstance(series.dtype, pd.CategoricalDtype):
        counts = counts.sort_values(ascending=False)
    table = counts.rename_axis("answer").reset_index(name="count")
    table["answer"] = table["answer"].astype(str)
    table["percent"] = table["count"] / len(answered) * 100
    return table


def compare_shares(groups, column, multiselect=True, min_n=MIN_RESPONDENTS):
    """
    Share of each answer of a question, for several populations.
    groups is a dict {label: DataFrame}.
    n is the number of people of the group who answered the question:
    the shares are reliable if n >= min_n.
    """
    count = count_multiselect if multiselect else count_single_choice
    tables = []
    for label, df in groups.items():
        table = count(df[column])
        table.insert(0, "group", label)
        table["n"] = df[column].notna().sum()
        table["reliable"] = table["n"] >= min_n
        tables.append(table)
    return pd.concat(tables, ignore_index=True)


def common_answers(series_old, series_new):
    """Answers of a multi-select question that exist in both years (harmonisation)."""
    old = set(series_old.dropna().str.split(";").explode())
    new = set(series_new.dropna().str.split(";").explode())
    return sorted(old & new)


def evolution_of_shares(series_old, series_new, old_year, new_year, answers=None):
    """
    Share of each answer of a multi-select question in two years, and the change
    in percentage points. answers: list of answers to keep (by default the common ones).
    """
    if answers is None:
        answers = common_answers(series_old, series_new)
    old = count_multiselect(series_old).set_index("answer")
    new = count_multiselect(series_new).set_index("answer")
    table = pd.DataFrame({
        "answer": answers,
        f"n_{old_year}": series_old.notna().sum(),
        f"percent_{old_year}": old["percent"].reindex(answers).fillna(0).values,
        f"n_{new_year}": series_new.notna().sum(),
        f"percent_{new_year}": new["percent"].reindex(answers).fillna(0).values,
    })
    table["change_points"] = table[f"percent_{new_year}"] - table[f"percent_{old_year}"]
    return table


def median_by_answer(df, column, value="SalaryEUR", min_n=MIN_RESPONDENTS):
    """
    Median salary of the people who chose each answer of a multi-select column.
    Example: median salary of the people who use Python, of those who use Java...
    One person can be counted in several answers.
    """
    data = df[[column, value]].dropna()
    data = data.assign(answer=data[column].str.split(";")).explode("answer")
    return median_by_group(data, "answer", value, min_n)
