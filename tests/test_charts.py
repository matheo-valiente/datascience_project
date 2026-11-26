"""Tests of the small helpers of src/charts.py."""

import pandas as pd

from src import charts


def test_format_euros():
    assert charts.format_euros(55_000) == "55k €"
    assert charts.format_euros(66_521) == "66.5k €"


def test_ordinal():
    assert [charts.ordinal(n) for n in [1, 2, 3, 4, 11, 12, 13, 21, 22]] == \
        ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd"]


def test_bar_ranking_highlights_france():
    table = pd.DataFrame({"Country": ["France", "Spain"], "median": [55_000, 60_000],
                          "n": [100, 100], "q1": [1, 1], "q3": [2, 2]})
    fig = charts.bar_ranking(table, "Country")
    colors = dict(zip(fig.data[0].y, fig.data[0].marker.color))
    assert colors["France"] != colors["Spain"]
