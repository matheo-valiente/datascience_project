"""
Data cleaning script for the Stack Overflow Developer Survey 2026.

It reads the raw CSV (too big for GitHub), keeps the useful columns,
cleans them and saves:
- data/survey_clean.parquet  -> used by the Streamlit app (keeps the category order)
- data/survey_clean.csv      -> same data, easy to open in Excel
- data/data_dictionary.csv   -> description of every column

Run it with:  python prepare_data.py
"""

import html

import numpy as np
import pandas as pd

RAW_PATH = "data/survey_results_public.csv"
SCHEMA_PATH = "data/survey_results_schema.csv"
COUNTRIES_PATH = "data/countries.csv"

CLEAN_PARQUET_PATH = "data/survey_clean.parquet"
CLEAN_CSV_PATH = "data/survey_clean.csv"
DICTIONARY_PATH = "data/data_dictionary.csv"

# ---------------------------------------------------------------------------
# 1. Columns we keep from the raw data (31 out of 212)
# ---------------------------------------------------------------------------
COLUMNS = [
    # Profile
    "ResponseId", "Age", "Gender", "Education", "Employment", "CodeMain",
    "Country", "YearsCode", "WorkExp",
    # Job
    "Role", "ICorPM", "OrgSize", "Industry", "WorkSetting", "JobSat",
    # Salary (Compensation and Currency are only used to get the EUR rate)
    "Compensation", "Currency", "ConvertedCompYearly",
    # Technologies (multi-select columns, answers separated by ";")
    "LanguagesHaveWorkedWith", "LanguagesWantToWorkWith", "LanguagesAdmired",
    "DatabasesHaveWorkedWith", "CloudPlatHaveWorkedWith",
    "WebFrameworkHaveWorkedWith", "DevIDEHaveWorkedWith",
    # AI
    "AISelect", "AISentiment", "AITrust", "AIAvoid",
    "LLMHaveWorkedWith", "AICodeAgentHaveWorkedWith",
]

# Order of the columns in the clean file
FINAL_COLUMNS = [
    "ResponseId",
    # Where
    "Country", "ISO3", "Continent", "IsEU",
    # Who
    "Age", "Gender", "Education", "Employment", "CodeMain",
    # Job
    "Role", "RoleGroup", "ICorPM", "OrgSize", "Industry", "WorkSetting",
    "YearsCode", "WorkExp", "ExperienceLevel", "JobSat",
    # Salary
    "SalaryUSD", "SalaryEUR",
    # Technologies
    "LanguagesHaveWorkedWith", "LanguagesWantToWorkWith", "LanguagesAdmired",
    "DatabasesHaveWorkedWith", "CloudPlatHaveWorkedWith",
    "WebFrameworkHaveWorkedWith", "DevIDEHaveWorkedWith",
    # AI
    "AISelect", "UsesAI", "AISentiment", "AITrust", "AIAvoid",
    "LLMHaveWorkedWith", "AICodeAgentHaveWorkedWith",
]

# Description of the columns we create (the others come from the survey schema)
NEW_COLUMNS_DESCRIPTION = {
    "ISO3": "ISO 3166 alpha-3 country code (for maps).",
    "Continent": "Continent of the country.",
    "IsEU": "True if the country is one of the 27 countries of the European Union.",
    "RoleGroup": "Role grouped in 8 families (from Role).",
    "ExperienceLevel": "Years of professional experience in 5 groups (from WorkExp).",
    "SalaryUSD": "Cleaned yearly salary in USD (employed and freelancers only, outliers removed).",
    "SalaryEUR": "SalaryUSD converted to euros (1 EUR = 1.137 USD, rate used by Stack Overflow).",
    "UsesAI": "True if the person uses at least one AI tool at work (from AISelect).",
}

# ---------------------------------------------------------------------------
# 2. Countries: shorter names and merge of duplicates
# ---------------------------------------------------------------------------
COUNTRY_NAMES = {
    "United States of America": "United States",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Russian Federation": "Russia",
    "Republic of Korea": "South Korea",
    "Democratic People's Republic of Korea": "North Korea",
    "Republic of Moldova": "Moldova",
    "Iran, Islamic Republic of...": "Iran",
    "Venezuela, Bolivarian Republic of...": "Venezuela",
    "Congo, Republic of the...": "Republic of the Congo",
    "Viet Nam": "Vietnam",
    "Syrian Arab Republic": "Syria",
    "Lao People's Democratic Republic": "Laos",
    "Libyan Arab Jamahiriya": "Libya",
    "United Republic of Tanzania": "Tanzania",
    "Republic of North Macedonia": "North Macedonia",
    "Hong Kong (S.A.R.)": "Hong Kong",
    "Brunei Darussalam": "Brunei",
    "Swaziland": "Eswatini",
}

# The 27 countries of the European Union (to compare France with the EU)
EU_COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
    "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta",
    "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
    "Spain", "Sweden",
]

# ---------------------------------------------------------------------------
# 3. Roles: 41 roles grouped in 8 families
# ---------------------------------------------------------------------------
ROLE_GROUPS = {
    "Developer": [
        "Developer, full-stack", "Developer, back-end", "Developer, front-end",
        "Developer, desktop or enterprise applications", "Developer, mobile",
        "Developer, embedded applications or devices", "Developer, game or graphics",
        "Developer, QA or test", "Developer, AI apps or physical AI", "Software engineer",
    ],
    "Data & AI": [
        "AI/ML engineer", "Data engineer", "Data scientist",
        "Data or business analyst", "Applied scientist",
    ],
    "Infrastructure & security": [
        "DevOps engineer or professional", "Cloud infrastructure engineer",
        "System administrator", "Site reliability engineer", "Platform engineer",
        "Database administrator or engineer", "Cybersecurity or InfoSec professional",
        "Support engineer or analyst",
    ],
    "Architect & solutions": [
        "Architect, software or solutions",
        "Solutions engineer, implementation engineer, or forward-deployed engineer",
    ],
    "Management": [
        "Engineering manager", "Senior executive (C-suite, VP, etc.)",
        "Founder or entrepreneur", "Project manager", "Product manager",
    ],
    "Research & education": ["Academic researcher", "Educator or instructor"],
    "Student": ["Student"],
    "Other": [
        "Hardware engineer", "UX, research, or UI design professional",
        "Developer advocate or developer relations professional",
        "Technical writer or documentation professional",
        "Financial analyst or engineer", "Marketing/Sales professional",
        "Retired", "Other",
    ],
}

# ---------------------------------------------------------------------------
# 4. Shorter labels for the charts (None = non-answer, becomes missing)
# ---------------------------------------------------------------------------
AGE_LABELS = {
    "Under 18 years old": "Under 18",
    "18-24 years old": "18-24",
    "25-34 years old": "25-34",
    "35-44 years old": "35-44",
    "45-54 years old": "45-54",
    "55-64 years old": "55-64",
    "65 years or older": "65+",
    "Prefer not to say": None,
}

EDUCATION_LABELS = {
    "Primary/elementary school": "Primary school",
    "Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)": "Secondary school",
    "Some college/university study without earning a degree": "Some university, no degree",
    "Associate degree (A.A., A.S., etc.)": "Associate degree",
    "Bachelor's degree (B.A., B.S., B.Eng., etc.)": "Bachelor's degree",
    "Master's degree (M.A., M.S., M.Eng., MBA, etc.)": "Master's degree",
    "Professional degree (JD, MD, Ph.D, Ed.D, etc.)": "Doctorate / professional degree",
    "Other, please specify": None,   # cannot be placed in the order
}

ORG_SIZE_LABELS = {
    "Just me - I am a freelancer, sole proprietor, etc.": "Just me",
    "Less than 20 employees": "1-19",
    "20 to 99 employees": "20-99",
    "100 to 499 employees": "100-499",
    "500 to 999 employees": "500-999",
    "1,000 to 4,999 employees": "1,000-4,999",
    "5,000 to 9,999 employees": "5,000-9,999",
    "10,000 or more employees": "10,000+",
    "I don’t know": None,
}

WORK_SETTING_LABELS = {
    "In-person": "In-person",
    "Hybrid (some remote, leans heavy to in-person)": "Hybrid, mostly in-person",
    "Hybrid (some in-person, leans heavy to flexibility)": "Hybrid, mostly remote",
    "Your choice (very flexible, you can come in when you want or just as needed)": "Free choice",
    "Remote": "Remote",
}

IC_OR_PM_LABELS = {
    "Individual contributor": "Individual contributor",
    "Individual contributor in a senior or staff-level role": "Senior individual contributor",
    "Both people manager and individual contributor": "Manager and contributor",
    "People manager": "People manager",
}

AI_SENTIMENT_LABELS = {
    "Very unfavorable": "Very unfavorable",
    "Somewhat unfavorable": "Somewhat unfavorable",
    "Neutral": "Neutral",
    "Somewhat favorable": "Somewhat favorable",
    "Very favorable": "Very favorable",
    "Not sure": None,
}

AI_TRUST_LABELS = {
    "I do not trust it for most work tasks": "Does not trust it",
    "I trust it for low-risk work tasks only": "Low-risk tasks only",
    "I trust it when I can easily verify the output": "When output is easy to verify",
    "I trust it for many tasks, but not important work decisions": "Many tasks, not key decisions",
    "I trust it for many tasks, including important work decisions": "Many tasks, including key decisions",
    "Not sure / I do not use AI tools": None,
}

EMPLOYMENT_LABELS = {
    "Employed": "Employed",
    "Independent contractor, freelancer, or self-employed": "Freelancer / self-employed",
    "Student": "Student",
    "Not employed": "Not employed",
    "Retired": "Retired",
    "I prefer not to say": None,
}

GENDER_LABELS = {
    "Man": "Man",
    "Woman": "Woman",
    "Non-binary": "Non-binary",
    "Prefer to self-describe:": "Self-described",
    "Prefer not to say": None,
}

CODE_MAIN_LABELS = {
    "I create code as a primary part of my job": "Codes as main job",
    "I create code occasionally": "Codes occasionally",
    "I review/maintain code but rarely create it": "Reviews or maintains code",
    "I manage or support people who create code": "Manages people who code",
    "I do not create code": "Does not code",
}

AI_AVOID_LABELS = {
    "I do not avoid using AI at work or school": "Does not avoid AI",
    "Concern over losing job skills or training an AI to replace you": "Fear of losing skills or job",
    "Moral or ethical concerns": "Moral or ethical concerns",
    "Issues with privacy or security": "Privacy or security",
    "Environmental concerns": "Environmental concerns",
    "Difficulty or lack of training": "Lack of training",
    "Other, please specify:": "Other",
}

INDUSTRY_LABELS = {
    "IT services, consulting, systems integration, or managed services": "IT services & consulting",
    "Retail, e-commerce, or consumer services": "Retail & e-commerce",
    "Banking/financial services": "Banking & finance",
    "Engineering services or applied R&D": "Engineering & R&D",
    "Utilities, internet, or telecommunications": "Telecom & utilities",
    "Media or advertising services": "Media & advertising",
    "Transportation or supply chain": "Transport & logistics",
    "Hospitality or travel": "Hospitality & travel",
    "Non-profit or social services": "Non-profit",
    "Agriculture, forestry, fishing, and hunting": "Agriculture",
    "Life sciences or biotechnology": "Life sciences & biotech",
    "Mining or construction": "Mining & construction",
    "Broadcasting or publishing": "Broadcasting & publishing",
    "Other, please specify": "Other",
}

# Columns with a natural order (the order of the dict is the order)
ORDERED_COLUMNS = {
    "Age": AGE_LABELS,
    "Education": EDUCATION_LABELS,
    "OrgSize": ORG_SIZE_LABELS,
    "WorkSetting": WORK_SETTING_LABELS,
    "ICorPM": IC_OR_PM_LABELS,
    "AISentiment": AI_SENTIMENT_LABELS,
    "AITrust": AI_TRUST_LABELS,
}

# Columns without a natural order
UNORDERED_COLUMNS = {
    "Employment": EMPLOYMENT_LABELS,
    "Gender": GENDER_LABELS,
    "CodeMain": CODE_MAIN_LABELS,
    "AIAvoid": AI_AVOID_LABELS,
}

# ---------------------------------------------------------------------------
# 5. Cleaning rules (numbers)
# ---------------------------------------------------------------------------
MAX_YEARS = 50                    # more than 50 years of experience is not realistic
SALARY_MIN_USD = 1_000            # below this, it is surely a monthly salary or a typo
SALARY_MAX_USD = 1_000_000
PAID_STATUS = ["Employed", "Freelancer / self-employed"]

EXPERIENCE_BINS = [-1, 2, 5, 10, 20, MAX_YEARS]
EXPERIENCE_LABELS = ["0-2 years", "3-5 years", "6-10 years", "11-20 years", "20+ years"]


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------
def apply_labels(series, labels, ordered):
    """Replace long answers by short labels and turn the column into a category."""
    unknown = set(series.dropna()) - set(labels)
    if unknown:
        raise ValueError(f"Answers without a label in {series.name}: {unknown}")
    new_series = series.map(labels)
    categories = [label for label in labels.values() if label is not None]
    return pd.Categorical(new_series, categories=categories, ordered=ordered)


def group_roles(role_series):
    """Give each role its family (for example 'Data scientist' -> 'Data & AI')."""
    role_to_group = {}
    for group, roles in ROLE_GROUPS.items():
        for role in roles:
            role_to_group[role] = group

    unknown = set(role_series.dropna()) - set(role_to_group)
    if unknown:
        raise ValueError(f"Roles without a group: {unknown}")
    return pd.Categorical(role_series.map(role_to_group), categories=list(ROLE_GROUPS))


def remove_outliers_by_country(df, column):
    """
    Boxplot rule (1.5 x IQR) applied country by country, on the log of the salary.
    - by country: a normal salary in India is not the same as in the US
    - on the log: salaries are very skewed, the log makes them more symmetric
    Outliers are set to NaN (the respondent is kept for the other questions).
    """
    log_salary = np.log10(df[column])
    groups = log_salary.groupby(df["Country"])
    q1 = groups.transform(lambda x: x.quantile(0.25))
    q3 = groups.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1
    is_outlier = (log_salary < q1 - 1.5 * iqr) | (log_salary > q3 + 1.5 * iqr)
    return df[column].where(~is_outlier)


def get_usd_per_eur(df):
    """Exchange rate used by Stack Overflow, found with the people paid in euros."""
    paid_in_eur = df["Currency"].str.startswith("EUR", na=False)
    ratio = df.loc[paid_in_eur, "ConvertedCompYearly"] / df.loc[paid_in_eur, "Compensation"]
    return ratio.median()


def make_dictionary(df):
    """Table with the description of every column of the clean data."""
    schema = pd.read_csv(SCHEMA_PATH, encoding="utf-8-sig")
    questions = dict(zip(schema["column"], schema["question"].map(html.unescape)))

    rows = []
    for column in df.columns:
        if column in NEW_COLUMNS_DESCRIPTION:
            description = NEW_COLUMNS_DESCRIPTION[column]
            source = "Created in prepare_data.py"
        else:
            description = questions.get(column, "")
            source = "Survey question"
        rows.append({
            "column": column,
            "description": description,
            "source": source,
            "type": str(df[column].dtype),
            "non_missing": df[column].notna().sum(),
        })
    return pd.DataFrame(rows)


def check_data(df):
    """Some checks to be sure the clean data is correct."""
    assert df["ResponseId"].is_unique, "duplicated respondents"
    assert df["Country"].notna().all(), "respondents without a country"
    assert df["Continent"].notna().sum() == (df["Country"] != "Nomadic").sum(), "country without continent"
    assert df["IsEU"].groupby(df["Country"]).first().sum() == 27, "EU should have 27 countries"
    assert df["SalaryUSD"].dropna().between(SALARY_MIN_USD, SALARY_MAX_USD).all(), "salary out of bounds"
    assert df["WorkExp"].dropna().le(MAX_YEARS).all(), "experience out of bounds"
    assert df["JobSat"].dropna().between(0, 10).all(), "job satisfaction should be between 0 and 10"
    assert list(df.columns) == FINAL_COLUMNS, "unexpected columns"
    print("  all checks passed")


def main():
    print("Loading raw data...")
    df = pd.read_csv(RAW_PATH, encoding="utf-8-sig", low_memory=False)
    print(f"  raw data: {len(df):,} rows, {df.shape[1]} columns")

    # --- Rows ---------------------------------------------------------------
    # People without a country stopped the survey early (about 13 answers out of 212)
    df = df[df["Country"].notna()]
    print(f"  after removing incomplete answers (no country): {len(df):,} rows")

    # A duplicate = same answers to ALL the questions (only the id is different)
    all_answers = [c for c in df.columns if c != "ResponseId"]
    df = df.drop_duplicates(subset=all_answers)
    print(f"  after removing duplicates: {len(df):,} rows")

    # We only keep the useful columns after the duplicate check
    df = df[COLUMNS].copy()

    # --- Countries ----------------------------------------------------------
    df["Country"] = df["Country"].replace(COUNTRY_NAMES)
    countries = pd.read_csv(COUNTRIES_PATH, keep_default_na=False, na_values=[""])
    df = df.merge(countries, on="Country", how="left")
    df["IsEU"] = df["Country"].isin(EU_COUNTRIES)

    # --- Categories ---------------------------------------------------------
    for column, labels in ORDERED_COLUMNS.items():
        df[column] = apply_labels(df[column], labels, ordered=True)
    for column, labels in UNORDERED_COLUMNS.items():
        df[column] = apply_labels(df[column], labels, ordered=False)
    df["Industry"] = df["Industry"].replace(INDUSTRY_LABELS)
    df["RoleGroup"] = group_roles(df["Role"])

    # --- Numbers ------------------------------------------------------------
    # Whole numbers, "Int64" allows missing values
    for column in ["YearsCode", "WorkExp"]:
        df[column] = df[column].where(df[column] <= MAX_YEARS).astype("Int64")
    df["JobSat"] = df["JobSat"].astype("Int64")
    df["ExperienceLevel"] = pd.cut(df["WorkExp"], bins=EXPERIENCE_BINS, labels=EXPERIENCE_LABELS)

    # --- Salary -------------------------------------------------------------
    usd_per_eur = get_usd_per_eur(df)
    print(f"  exchange rate used: 1 EUR = {usd_per_eur:.3f} USD")

    salary = df["ConvertedCompYearly"]
    is_paid = df["Employment"].isin(PAID_STATUS)
    is_possible = salary.between(SALARY_MIN_USD, SALARY_MAX_USD)
    df["SalaryUSD"] = salary.where(is_paid & is_possible)
    df["SalaryUSD"] = remove_outliers_by_country(df, "SalaryUSD").round()
    df["SalaryEUR"] = (df["SalaryUSD"] / usd_per_eur).round()
    print(f"  salaries kept: {df['SalaryUSD'].notna().sum():,} out of {salary.notna().sum():,}")

    # --- AI -----------------------------------------------------------------
    # AISelect is multi-select: someone uses AI if they chose at least one tool
    # (stays missing when the person did not answer the question)
    uses_ai = (df["AISelect"] != "I don’t use AI tools").astype("boolean")
    df["UsesAI"] = uses_ai.where(df["AISelect"].notna())

    # --- Check and save -----------------------------------------------------
    df = df[FINAL_COLUMNS]
    check_data(df)

    df.to_parquet(CLEAN_PARQUET_PATH, index=False)
    df.to_csv(CLEAN_CSV_PATH, index=False, encoding="utf-8-sig")   # utf-8-sig: accents OK in Excel
    make_dictionary(df).to_csv(DICTIONARY_PATH, index=False, encoding="utf-8-sig")

    france = df[df["Country"] == "France"]
    print(f"Saved {CLEAN_PARQUET_PATH} and {CLEAN_CSV_PATH}: {len(df):,} rows, {df.shape[1]} columns")
    print(f"Saved {DICTIONARY_PATH}")
    print(f"  France: {len(france)} respondents, median salary {france['SalaryEUR'].median():,.0f} EUR")


if __name__ == "__main__":
    main()
