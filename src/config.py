"""
Settings of the project: where the data comes from, where it is saved,
and the main rules used everywhere in the app.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------
SPONSOR = "Apec"
THEME = "Developer salaries in France"
FOCUS_COUNTRY = "France"

YEARS = [2025, 2026]
CURRENT_YEAR = 2026
PREVIOUS_YEAR = 2025

# ---------------------------------------------------------------------------
# Data files (official Stack Overflow archive on GitHub)
# The data is never committed: the app downloads it the first time.
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
COUNTRIES_PATH = PROJECT_DIR / "data" / "countries.csv"

ARCHIVE_URL = "https://media.githubusercontent.com/media/StackExchange/Survey/main/packages/archive"

RAW_FILES = {
    2026: {
        "survey_url": f"{ARCHIVE_URL}/2026/survey_results_public.csv",
        "schema_url": f"{ARCHIVE_URL}/2026/survey_results_schema.csv",
        "survey_path": RAW_DIR / "survey_2026.csv",
        "schema_path": RAW_DIR / "schema_2026.csv",
    },
    2025: {
        "survey_url": f"{ARCHIVE_URL}/2025/results.csv",
        "schema_url": f"{ARCHIVE_URL}/2025/schema.csv",
        "survey_path": RAW_DIR / "survey_2025.csv",
        "schema_path": RAW_DIR / "schema_2025.csv",
    },
}

# ---------------------------------------------------------------------------
# Rules used in the analysis
# ---------------------------------------------------------------------------
MIN_RESPONDENTS = 30          # below 30 people, a median is not reliable
SALARY_MIN_USD = 1_000        # below this, it is surely a monthly salary or a typo
SALARY_MAX_USD = 1_000_000
MAX_YEARS = 50                # more than 50 years of experience is not realistic

SURVEY_WARNING = (
    "Respondents are volunteers who answered an online survey: "
    "the figures describe them, not all developers."
)

# ---------------------------------------------------------------------------
# Colors (validated palette, see docs/ARCHITECTURE.md)
# ---------------------------------------------------------------------------
COLOR_FOCUS = "#2a78d6"       # France
COLOR_COMPARE = "#eb6834"     # comparison group (EU, other country...)
COLOR_CONTEXT = "#b4b2a9"     # other countries, background
COLOR_YEAR = {2025: "#86b6ef", 2026: "#1c5cab"}   # light blue = old, dark blue = new
