"""Tests of src/population.py."""

import pandas as pd

from src import population


def make_respondents():
    return pd.DataFrame({
        "Country": ["France", "Germany", "Italy", "United States", "France"],
        "IsEU": [True, True, True, False, True],
        "Continent": ["Europe", "Europe", "Europe", "North America", "Europe"],
        "SalaryEUR": [50_000, 70_000, None, 120_000, 55_000],
    })


def test_paid_population_keeps_only_salaries():
    assert len(population.paid_population(make_respondents())) == 4


def test_comparison_groups_never_contain_france():
    df = make_respondents()
    for group in population.COMPARISON_GROUPS:
        assert "France" not in set(population.comparison_group(df, group)["Country"])


def test_comparison_groups():
    df = make_respondents()
    assert len(population.comparison_group(df, "European Union (without France)")) == 2
    assert len(population.comparison_group(df, "World (without France)")) == 3
    assert len(population.comparison_group(df, "Germany")) == 1


def test_apply_filters_empty_list_means_all():
    df = make_respondents()
    assert len(population.apply_filters(df, {"Country": []})) == 5
    assert len(population.apply_filters(df, {"Country": ["France"]})) == 2


def test_labels_in_sentences():
    assert population.label_in_sentence("European Union (without France)") == "the rest of the EU"
    assert population.label_in_sentence("United States") == "the United States"
    assert population.label_in_sentence("Germany") == "Germany"


def test_describe_population():
    text = population.describe_population(make_respondents(), "Developers", 2026)
    assert "2026" in text and "n = 5" in text
