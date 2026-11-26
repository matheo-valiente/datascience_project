"""
The population behind every figure: who, which year, how many respondents.

The main population of the app is the "paid population": employed people and
freelancers who gave a salary that passed the cleaning rules.
"""

from src.config import FOCUS_COUNTRY

# Comparison groups that the user can choose (France is never inside them)
COMPARISON_GROUPS = [
    "European Union (without France)",
    "Europe (without France)",
    "World (without France)",
]


def paid_population(df):
    """Respondents with a clean salary (employed people and freelancers)."""
    return df[df["SalaryEUR"].notna()]


def apply_filters(df, filters):
    """
    Keep the rows that match the filters.
    filters is a dict {column: list of accepted values}; an empty list means "all".
    """
    for column, values in filters.items():
        if values:
            df = df[df[column].isin(values)]
    return df


def focus_country(df):
    """Respondents of the focus country (France)."""
    return df[df["Country"] == FOCUS_COUNTRY]


def comparison_group(df, group):
    """
    Respondents of the comparison group.
    group is one of COMPARISON_GROUPS, or the name of a country.
    """
    others = df[df["Country"] != FOCUS_COUNTRY]
    if group == "European Union (without France)":
        return others[others["IsEU"]]
    if group == "Europe (without France)":
        return others[others["Continent"] == "Europe"]
    if group == "World (without France)":
        return others
    return others[others["Country"] == group]


def short_label(group):
    """Short name of a comparison group, for legends: 'Rest of the EU', 'Germany'..."""
    names = {
        "European Union (without France)": "Rest of the EU",
        "Europe (without France)": "Rest of Europe",
        "World (without France)": "Rest of the world",
    }
    return names.get(group, group)


def label_in_sentence(group):
    """Name of a comparison group inside a sentence: 'the rest of the EU', 'Germany'..."""
    names = {
        "European Union (without France)": "the rest of the EU",
        "Europe (without France)": "the rest of Europe",
        "World (without France)": "the rest of the world",
    }
    # Countries that take "the" in English ("in the Netherlands")
    countries_with_the = ["United States", "United Kingdom", "Netherlands", "Czech Republic",
                          "Philippines", "United Arab Emirates", "Dominican Republic"]
    if group in countries_with_the:
        return f"the {group}"
    return names.get(group, group)


def describe_population(df, who, year):
    """Short sentence that says who is behind a figure."""
    return f"{who} · Stack Overflow Developer Survey {year} · n = {len(df):,} respondents"


def describe_filters(filters):
    """Readable text of the filters, for example 'Experience: 0-2 years, 3-5 years'."""
    parts = []
    for column, values in filters.items():
        if values:
            parts.append(f"{column}: {', '.join(str(v) for v in values)}")
    return " · ".join(parts) if parts else "no filter"
