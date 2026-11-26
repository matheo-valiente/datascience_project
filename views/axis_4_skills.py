"""
Axis 4 - Skills and AI
Question: Which technologies and AI practices are linked to higher salaries in France?

Built on the branch axis-4 by its owner (see README), then merged into main.
Use the shared functions of src/ (analysis, charts, population) and ui.py.
"""

import streamlit as st

from src.config import CURRENT_YEAR
from src.population import comparison_group, focus_country, label_in_sentence
from ui import footer, get_comparison, load_paid, page_header, show_population

WHO = "Employed developers and freelancers who gave their salary"

page_header("🛠️ Axis 4 · Skills and AI", "Which technologies and AI practices are linked to higher salaries in France?")

comparison = get_comparison()
paid = load_paid(CURRENT_YEAR)
france = focus_country(paid)
others = comparison_group(paid, comparison)

show_population(france, f"{WHO} in France", CURRENT_YEAR)
show_population(others, f"{WHO} in {label_in_sentence(comparison)}", CURRENT_YEAR)

st.info("This axis is being built on the branch `axis-4`.", icon="🚧")
st.markdown("""
**Ideas of views for this axis:**
- Median salary by language, database, cloud platform (`analysis.median_by_answer`)
- Most used technologies in France vs comparison group (`analysis.count_multiselect`)
- AI users vs non-users (`UsesAI`), AI sentiment and trust (2026 only)
- Languages 2025 → 2026: only the languages present both years
""")

footer()
