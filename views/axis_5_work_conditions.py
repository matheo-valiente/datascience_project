"""
Axis 5 - Work conditions
Question: Do company size, sector, remote work and freelancing change the pay in France?

Built on the branch axis-5 by its owner (see README), then merged into main.
Use the shared functions of src/ (analysis, charts, population) and ui.py.
"""

import streamlit as st

from src.config import CURRENT_YEAR
from src.population import comparison_group, focus_country, label_in_sentence
from ui import footer, get_comparison, load_paid, page_header, show_population

WHO = "Employed developers and freelancers who gave their salary"

page_header("🏢 Axis 5 · Work conditions", "Do company size, sector, remote work and freelancing change the pay in France?")

comparison = get_comparison()
paid = load_paid(CURRENT_YEAR)
france = focus_country(paid)
others = comparison_group(paid, comparison)

show_population(france, f"{WHO} in France", CURRENT_YEAR)
show_population(others, f"{WHO} in {label_in_sentence(comparison)}", CURRENT_YEAR)

st.info("This axis is being built on the branch `axis-5`.", icon="🚧")
st.markdown("""
**Ideas of views for this axis:**
- Median salary by company size (`OrgSize`) and by sector (`Industry`, 2026 only)
- Remote, hybrid or in-person (`WorkSetting`)
- Employed vs freelancer (`Employment`)
- Filters: experience level, role family
""")

footer()
