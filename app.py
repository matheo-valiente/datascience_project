"""
Stack Overflow Developer Survey 2026 - Streamlit app for the Apec
Data Visualisation final project (ECE)

Entry point: python -m streamlit run app.py
This file only builds the menu and the common sidebar; each page is in views/.
"""

import streamlit as st

from src.config import SPONSOR, THEME
from ui import comparison_selector, load_paid

st.set_page_config(page_title=THEME, page_icon="💶", layout="wide")

pages = {
    "Overview": [
        st.Page("views/dashboard.py", title="Main dashboard", icon="🏠", default=True),
    ],
    "Deeper analysis": [
        st.Page("views/axis_1_geography.py", title="1. Geography", icon="🌍"),
        st.Page("views/axis_2_experience.py", title="2. Experience", icon="📈"),
        st.Page("views/axis_3_roles.py", title="3. Roles", icon="🧑‍💻"),
        st.Page("views/axis_4_skills.py", title="4. Skills and AI", icon="🛠️"),
        st.Page("views/axis_5_work_conditions.py", title="5. Work conditions", icon="🏢"),
    ],
}
navigation = st.navigation(pages)

# Common sidebar, the same on every page
st.sidebar.markdown(f"**{THEME}**  \nAn app for the {SPONSOR}")
comparison_selector(load_paid(2026))

navigation.run()
