"""
Axis 2 - Experience
Question: How do salaries grow with experience in France, and is the gap with Europe the same at every stage?

Built on the branch axis-2 by its owner (see README), then merged into main.
Use the shared functions of src/ (analysis, charts, population) and ui.py.
"""

import streamlit as st

from src.config import CURRENT_YEAR
from src.population import comparison_group, focus_country, label_in_sentence
from ui import footer, get_comparison, load_paid, page_header, show_population

WHO = "Employed developers and freelancers who gave their salary"

page_header("📈 Axis 2 · Experience", "How do salaries grow with experience in France, and is the gap with Europe the same at every stage?")

comparison = get_comparison()
paid = load_paid(CURRENT_YEAR)
france = focus_country(paid)
others = comparison_group(paid, comparison)

show_population(france, f"{WHO} in France", CURRENT_YEAR)
show_population(others, f"{WHO} in {label_in_sentence(comparison)}", CURRENT_YEAR)

st.info("This axis is being built on the branch `axis-2`.", icon="🚧")
st.markdown("""
**Ideas of views for this axis:**
- Median salary by years of experience (`WorkExp`), France vs comparison group
- Filters: role family, employed / freelancer
- Salary by age and by education
- 2025 → 2026 by experience level (harmonised)
""")

footer()
