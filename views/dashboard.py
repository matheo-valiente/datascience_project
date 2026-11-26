"""
Main dashboard: the message for the sponsor.

Message: French developers are paid less than their European neighbours,
at every experience level, and the gap did not close between 2025 and 2026.
Every number of the message is computed from the data (nothing is written by hand).
"""

import streamlit as st

from src import analysis, charts
from src.config import (COLOR_COMPARE, COLOR_FOCUS, CURRENT_YEAR, FOCUS_COUNTRY,
                        MIN_RESPONDENTS, PREVIOUS_YEAR, SPONSOR)
from src.population import comparison_group, focus_country, label_in_sentence, short_label
from ui import footer, get_comparison, load_paid, show_chart

WHO = "Employed developers and freelancers who gave their salary"

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
comparison = get_comparison()
other = short_label(comparison)            # for legends: "Rest of the EU"
other_text = label_in_sentence(comparison)  # in sentences: "the rest of the EU"

paid_new = load_paid(CURRENT_YEAR)
paid_old = load_paid(PREVIOUS_YEAR)

france_new = focus_country(paid_new)
others_new = comparison_group(paid_new, comparison)
france_old = focus_country(paid_old)
others_old = comparison_group(paid_old, comparison)

france = analysis.salary_summary(france_new)
others = analysis.salary_summary(others_new)
france_before = analysis.salary_summary(france_old)
others_before = analysis.salary_summary(others_old)

gap_new = analysis.gap_percent(france["median"], others["median"])
gap_old = analysis.gap_percent(france_before["median"], others_before["median"])
france_change = analysis.gap_percent(france["median"], france_before["median"])
others_change = analysis.gap_percent(others["median"], others_before["median"])

# Is France lower at every experience level? (only levels with enough people on both sides)
by_experience = analysis.compare_groups({FOCUS_COUNTRY: france_new, other: others_new},
                                        "ExperienceLevel")
level_is_reliable = by_experience.groupby("ExperienceLevel", observed=True)["reliable"].all()
reliable_levels = level_is_reliable[level_is_reliable].index
wide = by_experience.pivot(index="ExperienceLevel", columns="group", values="median")
wide = wide.loc[wide.index.isin(reliable_levels)]
france_is_lower_everywhere = len(wide) > 0 and bool((wide[FOCUS_COUNTRY] < wide[other]).all())


def trend_sentence(gap_before, gap_now):
    """How the gap changed between the two years, in words."""
    if gap_before is None:
        return ""
    numbers = f"({gap_before:+.1f}% → {gap_now:+.1f}%)"
    if (gap_before < 0) != (gap_now < 0):
        return f" In {PREVIOUS_YEAR}, the gap was the other way round {numbers}."
    if abs(abs(gap_now) - abs(gap_before)) < 1:
        return f" It is stable since {PREVIOUS_YEAR} {numbers}."
    if abs(gap_now) > abs(gap_before):
        return f" It has widened since {PREVIOUS_YEAR} {numbers}."
    return f" It has narrowed since {PREVIOUS_YEAR} {numbers}."


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------
st.title(f"Developer salaries in {FOCUS_COUNTRY}, {CURRENT_YEAR}")
st.caption(f"Main dashboard for the {SPONSOR} · Stack Overflow Developer Survey {CURRENT_YEAR}")

direction = "less" if gap_new < 0 else "more"
message = (f"In {CURRENT_YEAR}, developers in {FOCUS_COUNTRY} earn a median of "
           f"**{charts.format_euros(france['median'])}** a year: "
           f"**{abs(gap_new):.0f}% {direction}** than in {other_text} "
           f"({charts.format_euros(others['median'])}).")
if gap_new < 0 and france_is_lower_everywhere:
    message += " The gap exists **at every experience level**."
message += trend_sentence(gap_old, gap_new)
st.info(message, icon="💡")

# ---------------------------------------------------------------------------
# Key figures
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"Median salary in {FOCUS_COUNTRY}", charts.format_euros(france["median"]),
            delta=f"{france_change:+.1f}% vs {PREVIOUS_YEAR}" if france_change is not None else None)
col2.metric(f"Median salary, {other}", charts.format_euros(others["median"]),
            delta=f"{others_change:+.1f}% vs {PREVIOUS_YEAR}" if others_change is not None else None)
col3.metric(f"Gap {FOCUS_COUNTRY} vs {other}", f"{gap_new:+.1f}%",
            delta=f"{gap_new - gap_old:+.1f} pts vs {PREVIOUS_YEAR}" if gap_old is not None else None)
col4.metric(f"Salaries in {FOCUS_COUNTRY} ({CURRENT_YEAR})", f"{france['n']:,}")
st.caption(f"👥 {WHO} · Stack Overflow Developer Survey {CURRENT_YEAR} and {PREVIOUS_YEAR} · "
           f"n = {france['n']:,} in {FOCUS_COUNTRY} and {others['n']:,} in {other_text} "
           f"({CURRENT_YEAR}); {france_before['n']:,} and {others_before['n']:,} ({PREVIOUS_YEAR})")

st.divider()
left, right = st.columns(2)

# ---------------------------------------------------------------------------
# Chart 1: France among the EU countries
# ---------------------------------------------------------------------------
with left:
    eu = paid_new[paid_new["IsEU"]]
    ranking = analysis.median_by_group(eu, "Country")
    ranking = ranking[ranking["reliable"]]
    rank = ranking["median"].rank(ascending=False, method="min")
    position = int(rank[ranking["Country"] == FOCUS_COUNTRY].iloc[0])
    st.subheader(f"{FOCUS_COUNTRY} ranks {charts.ordinal(position)} out of {len(ranking)} EU countries")

    rest_of_eu = analysis.salary_summary(eu[eu["Country"] != FOCUS_COUNTRY])["median"]
    fig = charts.bar_ranking(ranking, "Country", reference=rest_of_eu,
                             reference_label=f"Rest of the EU: {charts.format_euros(rest_of_eu)}")
    show_chart(fig, ranking,
               f"{WHO} in the EU · {CURRENT_YEAR} · n = {ranking['n'].sum():,} respondents",
               note=f"Only the {len(ranking)} EU countries with at least {MIN_RESPONDENTS} salaries are shown.")

# ---------------------------------------------------------------------------
# Chart 2: the gap at every experience level
# ---------------------------------------------------------------------------
with right:
    st.subheader("The gap at every experience level")
    fig = charts.lines_compare(by_experience, "ExperienceLevel",
                               group_colors={FOCUS_COUNTRY: COLOR_FOCUS, other: COLOR_COMPARE})
    fig.update_xaxes(title="Years of professional experience")
    show_chart(fig, by_experience,
               f"{WHO} · {CURRENT_YEAR} · n = {france['n']:,} in {FOCUS_COUNTRY}, "
               f"{others['n']:,} in {other_text}",
               note=(f"Empty markers: fewer than {MIN_RESPONDENTS} respondents, to read with care "
                     "(they are not used in the message above)."))

# ---------------------------------------------------------------------------
# Chart 3: 2025 -> 2026
# ---------------------------------------------------------------------------
if france_change is not None and others_change is not None:
    st.subheader(f"From {PREVIOUS_YEAR} to {CURRENT_YEAR}: {france_change:+.1f}% in {FOCUS_COUNTRY}, "
                 f"{others_change:+.1f}% in {other_text}")
else:
    st.subheader(f"From {PREVIOUS_YEAR} to {CURRENT_YEAR}")

evolution = analysis.evolution_of_groups({
    FOCUS_COUNTRY: (france_old, france_new),
    other: (others_old, others_new),
})
fig = charts.dumbbell_years(evolution, "group", PREVIOUS_YEAR, CURRENT_YEAR)
show_chart(fig, evolution,
           f"{WHO} · {PREVIOUS_YEAR} and {CURRENT_YEAR} · "
           f"n = {france_before['n']:,} → {france['n']:,} in {FOCUS_COUNTRY}, "
           f"{others_before['n']:,} → {others['n']:,} in {other_text}",
           note=("Harmonised comparison: same question, same cleaning rules, each year converted to "
                 "euros with its own rate (see docs/HARMONISATION.md). Salaries are not corrected for "
                 "inflation, and the respondents are not the same people each year."))

# ---------------------------------------------------------------------------
# Method and links to the axes
# ---------------------------------------------------------------------------
with st.expander("How to read these figures"):
    st.markdown(f"""
- **Population:** {WHO.lower()}, after cleaning (rules in `docs/DATA.md`).
  Students, retired people and unemployed people are not included.
- **Median:** half of the people earn less, half earn more. We use it instead of the mean
  because a few very high salaries would pull the mean up.
- **Groups with fewer than {MIN_RESPONDENTS} respondents** are hidden or shown with empty markers.
- **Comparison group:** change it in the sidebar (EU, Europe, world or one country).
""")

st.markdown("#### Go further")
links = st.columns(5)
links[0].page_link("views/axis_1_geography.py", label="Geography", icon="🌍")
links[1].page_link("views/axis_2_experience.py", label="Experience", icon="📈")
links[2].page_link("views/axis_3_roles.py", label="Roles", icon="🧑‍💻")
links[3].page_link("views/axis_4_skills.py", label="Skills and AI", icon="🛠️")
links[4].page_link("views/axis_5_work_conditions.py", label="Work conditions", icon="🏢")

footer()
