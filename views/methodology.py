"""
Methodology page: population, cleaning rules, harmonisation and limits.
The text comes from docs/DATA.md and docs/HARMONISATION.md, so the app and the
repository always say the same thing.
"""

from pathlib import Path

import streamlit as st

from src.config import CURRENT_YEAR, FOCUS_COUNTRY, PREVIOUS_YEAR, SURVEY_WARNING
from src.population import focus_country
from ui import footer, load_paid, load_survey

DOCS = Path(__file__).resolve().parent.parent / "docs"

st.title("📖 Methodology")
st.markdown("How the figures of this app are made: who answered, how the data was cleaned, "
            "and how 2025 and 2026 are compared.")
st.warning(SURVEY_WARNING, icon="⚠️")

# Live numbers, computed from the data used by the app
st.subheader("Population of the app")
rows = []
for year in [PREVIOUS_YEAR, CURRENT_YEAR]:
    everyone = load_survey(year)
    paid = load_paid(year)
    rows.append({
        "Year": str(year),
        "Respondents kept": f"{len(everyone):,}",
        "Clean salaries": f"{len(paid):,}",
        f"Respondents in {FOCUS_COUNTRY}": f"{len(focus_country(everyone)):,}",
        f"Salaries in {FOCUS_COUNTRY}": f"{len(focus_country(paid)):,}",
    })
st.dataframe(rows, hide_index=True)

tab_data, tab_harmonisation = st.tabs(["Data and cleaning", "Harmonisation 2025 / 2026"])
with tab_data:
    st.markdown((DOCS / "DATA.md").read_text(encoding="utf-8"))
with tab_harmonisation:
    st.markdown((DOCS / "HARMONISATION.md").read_text(encoding="utf-8"))

footer()
