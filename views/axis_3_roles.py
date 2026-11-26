"""
Axis 3 - Roles
Question: Which jobs pay best in France, and how do they compare with the rest of Europe?

Built on the branch axis-3 by its owner (see README), then merged into main.
Use the shared functions of src/ (analysis, charts, population) and ui.py.
"""

import streamlit as st

from src.config import CURRENT_YEAR
from src.population import comparison_group, focus_country, label_in_sentence
from ui import footer, get_comparison, load_paid, page_header, show_population

WHO = "Employed developers and freelancers who gave their salary"

page_header("🧑‍💻 Axis 3 · Roles", "Which jobs pay best in France, and how do they compare with the rest of Europe?")

comparison = get_comparison()
paid = load_paid(CURRENT_YEAR)
france = focus_country(paid)
others = comparison_group(paid, comparison)

show_population(france, f"{WHO} in France", CURRENT_YEAR)
show_population(others, f"{WHO} in {label_in_sentence(comparison)}", CURRENT_YEAR)

st.info("This axis is being built on the branch `axis-3`.", icon="🚧")
st.markdown("""
**Ideas of views for this axis:**
- Ranking of role families (`RoleGroup`) and of detailed roles (`Role`)
- France vs comparison group for each role family
- Individual contributor vs manager (`ICorPM`, 2026 only)
- Filter: experience level
""")

footer()
