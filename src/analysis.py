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


def median_by_answer(df, column, value="SalaryEUR", min_n=MIN_RESPONDENTS):
    """
    Median salary of the people who chose each answer of a multi-select column.
    Example: median salary of the people who use Python, of those who use Java...
    One person can be counted in several answers.
    """
    data = df[[column, value]].dropna()
    data = data.assign(answer=data[column].str.split(";")).explode("answer")
    return median_by_group(data, "answer", value, min_n)
