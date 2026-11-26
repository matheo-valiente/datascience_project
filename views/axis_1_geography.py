"""
Axis 1 - Geography
Question: Where does France stand compared with other countries and continents?

Built on the branch axis-1 by its owner (see README), then merged into main.
Use the shared functions of src/ (analysis, charts, population) and ui.py.
"""

import streamlit as st

from src.config import CURRENT_YEAR
from src.population import comparison_group, focus_country, label_in_sentence
from ui import footer, get_comparison, load_paid, page_header, show_population

WHO = "Employed developers and freelancers who gave their salary"

page_header("🌍 Axis 1 · Geography", "Where does France stand compared with other countries and continents?")

comparison = get_comparison()
paid = load_paid(CURRENT_YEAR)
france = focus_country(paid)
others = comparison_group(paid, comparison)

show_population(france, f"{WHO} in France", CURRENT_YEAR)
show_population(others, f"{WHO} in {label_in_sentence(comparison)}", CURRENT_YEAR)

st.info("This axis is being built on the branch `axis-1`.", icon="🚧")
st.markdown("""
**Ideas of views for this axis:**
- World map of the median salary (`charts.choropleth`, table needs `ISO3`)
- Ranking of countries, with a filter on the continent
- France vs the comparison group: distribution of salaries
- 2025 → 2026 by country (harmonised columns only)
""")

footer()
