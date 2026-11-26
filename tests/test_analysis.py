"""Tests of src/analysis.py on small tables where we know the answer."""

import pandas as pd

from src import analysis


def make_salaries():
    return pd.DataFrame({
        "Year": [2026] * 6,
        "Country": ["France", "France", "France", "Germany", "Germany", "Germany"],
        "SalaryEUR": [40_000, 50_000, 60_000, 60_000, 70_000, 80_000],
    })


def test_salary_summary():
    summary = analysis.salary_summary(make_salaries())
    assert summary["n"] == 6
    assert summary["median"] == 60_000


def test_gap_percent():
    assert analysis.gap_percent(50, 100) == -50
    assert analysis.gap_percent(150, 100) == 50
    assert analysis.gap_percent(50, 0) is None
    assert analysis.gap_percent(None, 100) is None


def test_median_by_group_and_reliable_flag():
    table = analysis.median_by_group(make_salaries(), "Country", min_n=3)
    france = table[table["Country"] == "France"].iloc[0]
    assert france["median"] == 50_000
    assert france["n"] == 3
    assert france["reliable"]

    table = analysis.median_by_group(make_salaries(), "Country", min_n=4)
    assert not table["reliable"].any()


def test_compare_groups_adds_the_label():
    df = make_salaries()
    table = analysis.compare_groups({"A": df[df["Country"] == "France"], "B": df}, "Country", min_n=1)
    assert set(table["group"]) == {"A", "B"}


def test_evolution_between_two_years():
    old = make_salaries().assign(Year=2025)
    new = make_salaries().assign(SalaryEUR=lambda d: d["SalaryEUR"] * 1.1)
    table = analysis.evolution(old, new, "Country", min_n=1)
    assert round(table["change_percent"].iloc[0], 6) == 10


def test_count_multiselect():
    series = pd.Series(["Python;SQL", "Python", None, "Java;Python"])
    table = analysis.count_multiselect(series).set_index("answer")
    assert table.loc["Python", "count"] == 3
    # 3 people answered the question: Python is used by 100% of them
    assert table.loc["Python", "percent"] == 100
    assert round(table.loc["SQL", "percent"], 1) == 33.3


def test_median_by_answer_counts_one_person_in_several_answers():
    df = pd.DataFrame({
        "LanguagesHaveWorkedWith": ["Python;SQL", "Python", "SQL"],
        "SalaryEUR": [100, 200, 300],
    })
    table = analysis.median_by_answer(df, "LanguagesHaveWorkedWith", min_n=1).set_index("answer")
    assert table.loc["Python", "median"] == 150
    assert table.loc["SQL", "median"] == 200


def test_count_single_choice_keeps_the_order_of_categories():
    order = ["Low", "Medium", "High"]
    series = pd.Series(pd.Categorical(["High", "Low", "High", None], categories=order, ordered=True))
    table = analysis.count_single_choice(series)
    assert list(table["answer"]) == order
    assert table.set_index("answer").loc["High", "percent"] == 2 / 3 * 100


def test_compare_shares_gives_n_of_each_group():
    groups = {
        "A": pd.DataFrame({"Tools": ["X;Y", "X", None]}),
        "B": pd.DataFrame({"Tools": ["Y"] * 40}),
    }
    table = analysis.compare_shares(groups, "Tools")
    a = table[table["group"] == "A"].set_index("answer")
    assert a.loc["X", "percent"] == 100
    assert a.loc["X", "n"] == 2 and not a.loc["X", "reliable"]
    assert table[table["group"] == "B"]["reliable"].all()


def test_evolution_of_shares_uses_only_common_answers():
    old = pd.Series(["Python;Java", "Python"])
    new = pd.Series(["Python;Rust", "Java", "Python", "Python"])
    table = analysis.evolution_of_shares(old, new, 2025, 2026).set_index("answer")
    assert list(table.index) == ["Java", "Python"]          # Rust is only in 2026
    assert table.loc["Python", "percent_2025"] == 100
    assert table.loc["Python", "percent_2026"] == 75
    assert table.loc["Python", "change_points"] == -25
