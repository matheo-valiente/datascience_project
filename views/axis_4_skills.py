"""
Axis 4 - Skills and AI
Question: Which technologies and AI practices are linked to higher salaries in France?

Sections (tabs):
1. Technologies and salary  - median salary of the users of each technology
2. Most used technologies   - France vs comparison group
3. AI and salary            - AI users vs non-users, also at equal experience
4. Opinions on AI           - sentiment and trust, France vs comparison group
5. AI tools                 - AI models and coding agents used
6. Trends and wishes        - languages 2025 -> 2026, and languages people want to learn

Exploration: notebooks/axis_4_skills_and_ai.ipynb
"""

import pandas as pd
import streamlit as st

from src import analysis, charts
from src.config import (COLOR_COMPARE, COLOR_CONTEXT, COLOR_FOCUS, CURRENT_YEAR,
                        FOCUS_COUNTRY, MIN_RESPONDENTS, PREVIOUS_YEAR)
from src.labels import AI_TOOL_FAMILIES, TECH_FAMILIES
from src.population import (apply_filters, comparison_group, describe_filters, focus_country,
                            label_in_sentence, short_label)
from ui import (filters_row, footer, get_comparison, load_paid, load_survey, page_header,
                remembered_radio, show_chart, show_population)

PAID = "Employed developers and freelancers who gave their salary"
ALL = "Respondents"
CORRELATION_NOTE = ("Correlation, not causation: people who use a technology may also differ in "
                    "role, sector or company. One person can use several technologies.")
TOP = 15   # number of answers shown in the usage charts

page_header("🛠️ Axis 4 · Skills and AI",
            "Which technologies and AI practices are linked to higher salaries in France?")

# ---------------------------------------------------------------------------
# Data and filters
# ---------------------------------------------------------------------------
comparison = get_comparison()
other = short_label(comparison)
other_text = label_in_sentence(comparison)
colors = {FOCUS_COUNTRY: COLOR_FOCUS, other: COLOR_COMPARE}

everyone_new = load_survey(CURRENT_YEAR)
everyone_old = load_survey(PREVIOUS_YEAR)
paid_new = load_paid(CURRENT_YEAR)

st.markdown("**Filter the population** (empty = everybody)")
filters = filters_row(everyone_new, "skills", {
    "ExperienceLevel": "Experience",
    "RoleGroup": "Role family",
})

everyone_new = apply_filters(everyone_new, filters)
everyone_old = apply_filters(everyone_old, filters)
paid_new = apply_filters(paid_new, filters)

france_paid = focus_country(paid_new)
france_all = focus_country(everyone_new)
others_all = comparison_group(everyone_new, comparison)
filter_suffix = f" · filters: {describe_filters(filters)}" if any(filters.values()) else ""

if len(france_paid) < MIN_RESPONDENTS:
    st.warning(f"Only {len(france_paid)} salaries in {FOCUS_COUNTRY} with these filters: "
               f"remove some filters to get reliable results (at least {MIN_RESPONDENTS}).")



def warn_if_few(n):
    """Warning when a result rests on too few respondents in France."""
    if n < MIN_RESPONDENTS:
        st.warning(f"Only {n} respondents in {FOCUS_COUNTRY} for this view: "
                   f"the result is not reliable (at least {MIN_RESPONDENTS} needed).", icon="⚠️")


tabs = st.tabs(["💶 Technologies and salary", "📊 Most used", "🤖 AI and salary",
                "💬 Opinions on AI", "🧰 AI tools", "📈 Trends and wishes"])

# ---------------------------------------------------------------------------
# 1. Technologies and salary
# ---------------------------------------------------------------------------
with tabs[0]:
    family = remembered_radio("Family of technologies", list(TECH_FAMILIES), "skills_family")
    column = TECH_FAMILIES[family]

    answered = france_paid[france_paid[column].notna()]
    by_tech = analysis.median_by_answer(answered, column)
    reliable = by_tech[by_tech["reliable"]].sort_values("median", ascending=False).head(20)
    reference = analysis.salary_summary(answered)["median"]

    if reliable.empty:
        st.info(f"No technology has {MIN_RESPONDENTS} salaries or more with these filters.")
    else:
        best = reliable.iloc[0]
        gap = analysis.gap_percent(best["median"], reference)
        st.subheader(f"{best['answer']} users earn the most in {FOCUS_COUNTRY}: "
                     f"{charts.format_euros(best['median'])}, {gap:+.0f}% vs all")
        fig = charts.bar_ranking(
            reliable, "answer", reference=reference, highlight_above_reference=True,
            reference_label=f"All ({family.lower()} question): {charts.format_euros(reference)}",
            reference_color=COLOR_CONTEXT)
        hidden = len(by_tech) - by_tech["reliable"].sum()
        show_chart(fig, reliable,
                   f"{PAID} in {FOCUS_COUNTRY} and answered the question on {family.lower()} · "
                   f"{CURRENT_YEAR} · n = {len(answered):,}{filter_suffix}",
                   note=(f"Blue: above the median of all the people who answered. {hidden} technologies "
                         f"with fewer than {MIN_RESPONDENTS} salaries are hidden (top 20 shown). "
                         f"{CORRELATION_NOTE}"),
                   key="tech_salary")

# ---------------------------------------------------------------------------
# 2. Most used technologies
# ---------------------------------------------------------------------------
with tabs[1]:
    family = remembered_radio("Family of technologies", list(TECH_FAMILIES), "skills_usage_family")
    column = TECH_FAMILIES[family]

    shares = analysis.compare_shares({FOCUS_COUNTRY: france_all, other: others_all}, column)
    top = (shares[shares["group"] == FOCUS_COUNTRY]
           .sort_values("percent", ascending=False).head(TOP)["answer"].tolist())
    shares = shares[shares["answer"].isin(top)]

    if shares.empty:
        st.info("Nobody answered this question with these filters.")
    else:
        france_top = shares[(shares["group"] == FOCUS_COUNTRY) & (shares["answer"] == top[0])].iloc[0]
        other_top = shares[(shares["group"] == other) & (shares["answer"] == top[0])]
        other_share = f" ({other_top['percent'].iloc[0]:.0f}% in {other_text})" if len(other_top) else ""
        st.subheader(f"Most used in {FOCUS_COUNTRY}: {top[0]}, "
                     f"{france_top['percent']:.0f}% of respondents{other_share}")
        warn_if_few(int(france_all[column].notna().sum()))
        fig = charts.bars_compare(shares, "answer", "percent", colors, "Users", unit="%", order=top)
        n_france = int(france_all[column].notna().sum())
        n_other = int(others_all[column].notna().sum())
        show_chart(fig, shares,
                   f"{ALL} who answered the question on {family.lower()} · {CURRENT_YEAR} · "
                   f"n = {n_france:,} in {FOCUS_COUNTRY}, {n_other:,} in {other_text}{filter_suffix}",
                   note=f"Top {TOP} in {FOCUS_COUNTRY}. Several answers per person: the bars do not add up to 100%.",
                   key="tech_usage")

# ---------------------------------------------------------------------------
# 3. AI and salary
# ---------------------------------------------------------------------------
with tabs[2]:
    ai_labels = {True: "Uses AI at work", False: "Does not use AI"}
    paid_ai = paid_new[paid_new["UsesAI"].notna()].assign(AIUse=lambda d: d["UsesAI"].map(ai_labels))
    france_ai = focus_country(paid_ai)
    others_ai = comparison_group(paid_ai, comparison)

    by_use = analysis.compare_groups({FOCUS_COUNTRY: france_ai, other: others_ai}, "AIUse")
    france_rows = by_use[by_use["group"] == FOCUS_COUNTRY].set_index("AIUse")
    if {"Uses AI at work", "Does not use AI"} <= set(france_rows.index):
        gap = analysis.gap_percent(france_rows.loc["Uses AI at work", "median"],
                                   france_rows.loc["Does not use AI", "median"])
        direction = "more" if gap >= 0 else "less"
        st.subheader(f"In {FOCUS_COUNTRY}, people who use AI at work earn {abs(gap):.0f}% {direction} "
                     f"than those who do not")
    else:
        st.subheader("AI use and salary")
    warn_if_few(int((france_ai["UsesAI"] == False).sum()))

    left, right = st.columns(2)
    with left:
        fig = charts.bars_compare(by_use, "AIUse", "median", colors, "Median salary",
                                  order=list(ai_labels.values()))
        show_chart(fig, by_use,
                   f"{PAID} and answered the question on AI · {CURRENT_YEAR} · "
                   f"n = {len(france_ai):,} in {FOCUS_COUNTRY}, {len(others_ai):,} in {other_text}{filter_suffix}",
                   note="Lighter bars: fewer than 30 respondents.", key="ai_salary")
    with right:
        st.markdown(f"**Is it only experience?** Same comparison at equal experience, in {FOCUS_COUNTRY}")
        by_level = analysis.compare_groups({
            "Uses AI at work": france_ai[france_ai["UsesAI"] == True],
            "Does not use AI": france_ai[france_ai["UsesAI"] == False],
        }, "ExperienceLevel")
        fig = charts.lines_compare(by_level, "ExperienceLevel",
                                   group_colors={"Uses AI at work": COLOR_FOCUS, "Does not use AI": COLOR_CONTEXT})
        fig.update_xaxes(title="Years of professional experience")
        show_chart(fig, by_level,
                   f"{PAID} in {FOCUS_COUNTRY} and answered the question on AI · {CURRENT_YEAR} · "
                   f"n = {len(france_ai):,}{filter_suffix}",
                   note=(f"Empty markers: fewer than {MIN_RESPONDENTS} respondents. Few French respondents "
                         f"do not use AI: compare with {other_text} in the sidebar. {CORRELATION_NOTE}"),
                   key="ai_experience")

# ---------------------------------------------------------------------------
# 4. Opinions on AI
# ---------------------------------------------------------------------------
with tabs[3]:
    questions = {
        "Attitude towards AI": ("AISentiment", "How would you describe your attitude toward using AI tools at work?"),
        "Trust in AI output": ("AITrust", "How much do you trust the output of AI tools?"),
        "Reason to avoid AI": ("AIAvoid", "Do you try to avoid using AI tools? Main reason"),
    }
    choice = remembered_radio("Question", list(questions), "skills_opinion")
    column, question_text = questions[choice]

    shares = analysis.compare_shares({FOCUS_COUNTRY: france_all, other: others_all}, column, multiselect=False)
    if shares.empty:
        st.info("Nobody answered this question with these filters.")
    else:
        if column == "AISentiment":
            france_shares = shares[shares["group"] == FOCUS_COUNTRY].set_index("answer")["percent"]
            favorable = france_shares.reindex(["Somewhat favorable", "Very favorable"]).sum()
            st.subheader(f"{favorable:.0f}% of respondents in {FOCUS_COUNTRY} are favorable to AI at work")
        else:
            st.subheader(choice)
        st.caption(f"Question of the survey: *{question_text}*")
        warn_if_few(int(france_all[column].notna().sum()))
        order = list(dict.fromkeys(shares["answer"]))
        fig = charts.bars_compare(shares, "answer", "percent", colors, "Share", unit="%", order=order)
        show_chart(fig, shares,
                   f"{ALL} who answered the question · {CURRENT_YEAR} · "
                   f"n = {int(france_all[column].notna().sum()):,} in {FOCUS_COUNTRY}, "
                   f"{int(others_all[column].notna().sum()):,} in {other_text}{filter_suffix}",
                   note="One answer per person: the bars of each group add up to 100%.",
                   key="ai_opinion")

# ---------------------------------------------------------------------------
# 5. AI tools
# ---------------------------------------------------------------------------
with tabs[4]:
    family = remembered_radio("Tools", list(AI_TOOL_FAMILIES), "skills_ai_tools")
    column = AI_TOOL_FAMILIES[family]

    shares = analysis.compare_shares({FOCUS_COUNTRY: france_all, other: others_all}, column)
    top = (shares[shares["group"] == FOCUS_COUNTRY]
           .sort_values("percent", ascending=False).head(10)["answer"].tolist())
    shares = shares[shares["answer"].isin(top)]
    if shares.empty:
        st.info("Nobody answered this question with these filters.")
    else:
        first = shares[(shares["group"] == FOCUS_COUNTRY) & (shares["answer"] == top[0])].iloc[0]
        st.subheader(f"{top[0]} is the most used in {FOCUS_COUNTRY} "
                     f"({first['percent']:.0f}% of the people who answered)")
        warn_if_few(int(france_all[column].notna().sum()))
        fig = charts.bars_compare(shares, "answer", "percent", colors, "Users", unit="%", order=top)
        show_chart(fig, shares,
                   f"{ALL} who answered the question on {family.lower()} · {CURRENT_YEAR} · "
                   f"n = {int(france_all[column].notna().sum()):,} in {FOCUS_COUNTRY}, "
                   f"{int(others_all[column].notna().sum()):,} in {other_text}{filter_suffix}",
                   note="Top 10 in France. Several answers per person: the bars do not add up to 100%.",
                   key="ai_tools")

# ---------------------------------------------------------------------------
# 6. Trends 2025 -> 2026, and languages people want to learn
# ---------------------------------------------------------------------------
with tabs[5]:
    left, right = st.columns(2)

    with left:
        column = "LanguagesHaveWorkedWith"
        france_old = focus_country(everyone_old)
        trend = analysis.evolution_of_shares(france_old[column], france_all[column],
                                             PREVIOUS_YEAR, CURRENT_YEAR)
        trend = trend.sort_values(f"percent_{CURRENT_YEAR}", ascending=False).head(12)
        if trend.empty or trend[f"n_{CURRENT_YEAR}"].iloc[0] == 0:
            st.info("Not enough answers with these filters.")
        else:
            riser = trend.sort_values("change_points", ascending=False).iloc[0]
            st.subheader(f"Languages in {FOCUS_COUNTRY}, {PREVIOUS_YEAR} → {CURRENT_YEAR}: "
                         f"{riser['answer']} {riser['change_points']:+.0f} pts")
            warn_if_few(int(trend[f"n_{CURRENT_YEAR}"].iloc[0]))
            fig = charts.dumbbell_years(trend.iloc[::-1], "answer", PREVIOUS_YEAR, CURRENT_YEAR,
                                        value_label="Users", prefix="percent", unit="%",
                                        change_column="change_points", change_unit=" pts")
            show_chart(fig, trend,
                       f"{ALL} in {FOCUS_COUNTRY} who answered the question on languages · "
                       f"{PREVIOUS_YEAR} and {CURRENT_YEAR} · n = {int(trend[f'n_{PREVIOUS_YEAR}'].iloc[0]):,} → "
                       f"{int(trend[f'n_{CURRENT_YEAR}'].iloc[0]):,}{filter_suffix}",
                       note=("Only the languages offered both years are compared (see docs/HARMONISATION.md). "
                             "The 12 most used in 2026 are shown. Not the same people each year."),
                       key="languages_trend")

    with right:
        used = analysis.count_multiselect(france_all["LanguagesHaveWorkedWith"]).assign(group="Used")
        wanted = analysis.count_multiselect(france_all["LanguagesWantToWorkWith"]).assign(group="Wanted")
        used["n"] = int(france_all["LanguagesHaveWorkedWith"].notna().sum())
        wanted["n"] = int(france_all["LanguagesWantToWorkWith"].notna().sum())
        both = used.merge(wanted, on="answer", suffixes=("_used", "_wanted"))
        if both.empty:
            st.info("Not enough answers with these filters.")
        else:
            both["gap"] = both["percent_wanted"] - both["percent_used"]
            top = both.sort_values("percent_wanted", ascending=False).head(12)["answer"].tolist()
            most_wanted = both.sort_values("gap", ascending=False).iloc[0]
            st.subheader(f"{most_wanted['answer']}: {most_wanted['percent_wanted']:.0f}% want to use it, "
                         f"{most_wanted['percent_used']:.0f}% do")
            warn_if_few(int(wanted["n"].iloc[0]))
            table = pd.concat([used, wanted], ignore_index=True)
            table["reliable"] = table["n"] >= MIN_RESPONDENTS
            table = table[table["answer"].isin(top)]
            fig = charts.bars_compare(table, "answer", "percent",
                                      {"Used": COLOR_CONTEXT, "Wanted": COLOR_FOCUS},
                                      "Respondents", unit="%", order=top)
            show_chart(fig, table,
                       f"{ALL} in {FOCUS_COUNTRY} who answered the questions on languages · {CURRENT_YEAR} · "
                       f"n = {used['n'].iloc[0]:,} (used), {wanted['n'].iloc[0]:,} (want to use){filter_suffix}",
                       note=("Used: extensive work in the past year. Wanted: want to work with it next year. "
                             "The 12 most wanted languages are shown."),
                       key="languages_wanted")

show_population(france_all, f"{ALL} in {FOCUS_COUNTRY}", CURRENT_YEAR, filters)
footer()
