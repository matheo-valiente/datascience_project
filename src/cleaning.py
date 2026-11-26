"""
Cleaning and harmonisation of the survey (2025 and 2026).

clean_survey(year) returns one clean table per year, with the same columns
and the same labels for the questions that exist in both years.
All the rules are explained in docs/DATA.md and docs/HARMONISATION.md.
"""

import numpy as np
import pandas as pd

from src import labels
from src.config import COUNTRIES_PATH, MAX_YEARS, SALARY_MAX_USD, SALARY_MIN_USD
from src.data import read_survey


# ---------------------------------------------------------------------------
# Small cleaning functions
# ---------------------------------------------------------------------------
def apply_labels(series, labels_dict, ordered):
    """Replace long answers by short labels and turn the column into a category."""
    unknown = set(series.dropna()) - set(labels_dict)
    if unknown:
        raise ValueError(f"Answers without a label in {series.name}: {unknown}")
    categories = [label for label in labels_dict.values() if label is not None]
    return pd.Categorical(series.map(labels_dict), categories=categories, ordered=ordered)


def group_roles(role_series):
    """Give each role its family (for example 'Data scientist' -> 'Data & AI')."""
    role_to_group = {}
    for group, roles in labels.ROLE_GROUPS.items():
        for role in roles:
            role_to_group[role] = group

    unknown = set(role_series.dropna()) - set(role_to_group)
    if unknown:
        raise ValueError(f"Roles without a group: {unknown}")
    return pd.Categorical(role_series.map(role_to_group), categories=list(labels.ROLE_GROUPS))


def add_country_info(df):
    """Shorter country names, then ISO3 code, continent and EU membership."""
    df["Country"] = df["Country"].replace(labels.COUNTRY_NAMES)
    countries = pd.read_csv(COUNTRIES_PATH, keep_default_na=False, na_values=[""])
    df = df.merge(countries, on="Country", how="left")
    df["IsEU"] = df["Country"].isin(labels.EU_COUNTRIES)
    return df


def get_usd_per_eur(df):
    """Exchange rate used by Stack Overflow, found with the people paid in euros."""
    paid_in_eur = df["Currency"].str.startswith("EUR", na=False)
    ratio = df.loc[paid_in_eur, "ConvertedCompYearly"] / df.loc[paid_in_eur, "Compensation"]
    return ratio.median()


def remove_outliers_by_country(salary, country):
    """
    Boxplot rule (1.5 x IQR) applied country by country, on the log of the salary.
    - by country: a normal salary in India is not the same as in the US
    - on the log: salaries are very skewed, the log makes them more symmetric
    Outliers become NaN (the respondent is kept for the other questions).
    """
    log_salary = np.log10(salary)
    groups = log_salary.groupby(country)
    q1 = groups.transform(lambda x: x.quantile(0.25))
    q3 = groups.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1
    is_outlier = (log_salary < q1 - 1.5 * iqr) | (log_salary > q3 + 1.5 * iqr)
    return salary.where(~is_outlier)


def clean_salary(df):
    """Create SalaryUSD and SalaryEUR (yearly, employed people and freelancers only)."""
    salary = df["ConvertedCompYearly"]
    is_paid = df["Employment"].isin(labels.PAID_STATUS)
    is_possible = salary.between(SALARY_MIN_USD, SALARY_MAX_USD)

    df["SalaryUSD"] = salary.where(is_paid & is_possible)
    df["SalaryUSD"] = remove_outliers_by_country(df["SalaryUSD"], df["Country"]).round()
    df["SalaryEUR"] = (df["SalaryUSD"] / get_usd_per_eur(df)).round()
    return df


def clean_experience(df):
    """Whole numbers, no more than 50 years, and 5 experience groups."""
    for column in ["YearsCode", "WorkExp"]:
        df[column] = df[column].where(df[column] <= MAX_YEARS).astype("Int64")
    df["ExperienceLevel"] = pd.cut(df["WorkExp"], bins=labels.EXPERIENCE_BINS,
                                   labels=labels.EXPERIENCE_LABELS)
    return df


# ---------------------------------------------------------------------------
# Steps that depend on the year
# ---------------------------------------------------------------------------
def harmonise_2025(df):
    """Put the 2025 answers in the 2026 format (see docs/HARMONISATION.md)."""
    df = df.rename(columns=labels.RENAME_2025)
    df["Education"] = df["Education"].replace(labels.EDUCATION_2025)
    df["Role"] = df["Role"].replace(labels.ROLES_2025)
    return df


def clean_only_2026(df):
    """Columns that only exist in 2026."""
    for column, labels_dict in labels.ORDERED_LABELS_2026.items():
        df[column] = apply_labels(df[column], labels_dict, ordered=True)
    for column, labels_dict in labels.UNORDERED_LABELS_2026.items():
        df[column] = apply_labels(df[column], labels_dict, ordered=False)

    df["Industry"] = df["Industry"].replace(labels.INDUSTRY_LABELS)
    df["JobSat"] = df["JobSat"].astype("Int64")

    # AISelect is multi-select: someone uses AI if they chose at least one tool
    # (stays missing when the person did not answer the question)
    uses_ai = (df["AISelect"] != "I don’t use AI tools").astype("boolean")
    df["UsesAI"] = uses_ai.where(df["AISelect"].notna())
    return df


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------
def clean_survey(year):
    """Return the clean table of one year (2025 or 2026)."""
    if year == 2026:
        df = read_survey(2026, labels.COLUMNS_2026)
    elif year == 2025:
        df = harmonise_2025(read_survey(2025, labels.COLUMNS_2025))
    else:
        raise ValueError(f"No data for {year}")

    # People without a country stopped the survey early (very few answers, no salary)
    df = df[df["Country"].notna()].copy()
    df["Year"] = year

    df = add_country_info(df)
    for column, labels_dict in labels.ORDERED_LABELS_COMMON.items():
        df[column] = apply_labels(df[column], labels_dict, ordered=True)
    for column, labels_dict in labels.UNORDERED_LABELS_COMMON.items():
        df[column] = apply_labels(df[column], labels_dict, ordered=False)
    df["RoleGroup"] = group_roles(df["Role"])
    df = clean_experience(df)
    df = clean_salary(df)

    if year == 2026:
        df = clean_only_2026(df)
        columns = labels.HARMONISED_COLUMNS + labels.ONLY_2026_COLUMNS
    else:
        columns = labels.HARMONISED_COLUMNS

    df = df[columns].reset_index(drop=True)
    check_clean_data(df)
    return df


def check_clean_data(df):
    """Stop with a clear message if the clean data is not as expected."""
    assert df["ResponseId"].is_unique, "duplicated respondents"
    assert df["Country"].notna().all(), "respondents without a country"
    unknown = df.loc[df["Continent"].isna() & (df["Country"] != "Nomadic"), "Country"].unique()
    assert len(unknown) == 0, f"countries missing in data/countries.csv: {list(unknown)}"
    assert df["SalaryUSD"].dropna().between(SALARY_MIN_USD, SALARY_MAX_USD).all(), "salary out of bounds"
    assert df["WorkExp"].dropna().le(MAX_YEARS).all(), "experience out of bounds"
    if "JobSat" in df.columns:
        assert df["JobSat"].dropna().between(0, 10).all(), "job satisfaction not between 0 and 10"
