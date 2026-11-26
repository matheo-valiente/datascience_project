"""Tests of the cleaning rules (src/cleaning.py) on small tables."""

import pandas as pd
import pytest

from src import cleaning, labels


def test_apply_labels_short_names_and_order():
    series = pd.Series(["25-34 years old", "Under 18 years old", "Prefer not to say"], name="Age")
    result = cleaning.apply_labels(series, labels.AGE_LABELS, ordered=True)
    assert list(result[:2]) == ["25-34", "Under 18"]
    assert pd.isna(result[2])                      # "Prefer not to say" is not an answer
    assert result.ordered and result.categories[0] == "Under 18"


def test_apply_labels_stops_on_unknown_answer():
    with pytest.raises(ValueError):
        cleaning.apply_labels(pd.Series(["Something new"], name="Age"), labels.AGE_LABELS, ordered=True)


def test_every_role_has_one_group():
    all_roles = [role for roles in labels.ROLE_GROUPS.values() for role in roles]
    assert len(all_roles) == len(set(all_roles))
    result = cleaning.group_roles(pd.Series(["Data scientist", "Developer, back-end"]))
    assert list(result) == ["Data & AI", "Developer"]


def test_roles_of_2025_exist_in_2026():
    all_roles = {role for roles in labels.ROLE_GROUPS.values() for role in roles}
    assert set(labels.ROLES_2025.values()) <= all_roles


def test_outliers_are_removed_country_by_country():
    # Same salaries in two countries, plus one absurd value in France
    salary = pd.Series([50_000, 52_000, 55_000, 58_000, 60_000, 5_000_000,
                        5_000, 5_200, 5_500, 5_800, 6_000])
    country = pd.Series(["France"] * 6 + ["India"] * 5)
    result = cleaning.remove_outliers_by_country(salary, country)
    assert pd.isna(result[5])                      # 5 million in France: removed
    assert result[6:].notna().all()                # low salaries are normal in India: kept


def test_experience_above_50_years_is_removed():
    df = pd.DataFrame({"YearsCode": [10, 60], "WorkExp": [5, 55]})
    result = cleaning.clean_experience(df)
    assert result["WorkExp"].isna().tolist() == [False, True]
    assert result["ExperienceLevel"].iloc[0] == "3-5 years"


def test_every_country_of_the_eu_list_is_in_the_reference_table():
    countries = pd.read_csv("data/countries.csv")
    assert set(labels.EU_COUNTRIES) <= set(countries["Country"])
