"""
Data cleaning script for the Stack Overflow Developer Survey 2026.

It reads the raw CSV (too big for GitHub), keeps the useful columns,
cleans them and saves a small file: data/survey_clean.parquet.
The Streamlit app only reads this clean file.

Run it with:  python prepare_data.py
"""

import numpy as np
import pandas as pd

RAW_PATH = "data/survey_results_public.csv"
CLEAN_PATH = "data/survey_clean.parquet"

# ---------------------------------------------------------------------------
# 1. Columns we keep (about 30 out of 212)
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

# ---------------------------------------------------------------------------
# 2. Country names: shorter names and merge of duplicates
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
# 3. Shorter labels for the charts (None = non-answer, becomes missing)
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
    "Other, please specify": "Other",
}

EMPLOYMENT_LABELS = {
    "Employed": "Employed",
    "Independent contractor, freelancer, or self-employed": "Freelancer / self-employed",
    "Student": "Student",
    "Not employed": "Not employed",
    "Retired": "Retired",
    "I prefer not to say": None,
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

GENDER_LABELS = {
    "Man": "Man",
    "Woman": "Woman",
    "Non-binary": "Non-binary",
    "Prefer to self-describe:": "Self-described",
    "Prefer not to say": None,
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

# Columns that have a natural order (the order of the dict is the order)
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
}

# ---------------------------------------------------------------------------
# 4. Cleaning rules (numbers)
# ---------------------------------------------------------------------------
MAX_YEARS = 50                    # more than 50 years of experience is not realistic
SALARY_MIN_USD = 1_000            # below this, it is surely a monthly salary or a typo
SALARY_MAX_USD = 1_000_000
PAID_STATUS = ["Employed", "Freelancer / self-employed"]

EXPERIENCE_BINS = [-1, 2, 5, 10, 20, MAX_YEARS]
EXPERIENCE_LABELS = ["0-2 years", "3-5 years", "6-10 years", "11-20 years", "20+ years"]


def apply_labels(series, labels, ordered):
    """Replace long answers by short labels and turn the column into a category."""
    new_series = series.map(lambda value: labels.get(value, value))
    categories = [label for label in labels.values() if label is not None]
    return pd.Categorical(new_series, categories=categories, ordered=ordered)


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
    print(f"  columns kept: {len(COLUMNS)} out of 212")

    # --- Countries ----------------------------------------------------------
    df["Country"] = df["Country"].replace(COUNTRY_NAMES)
    df["IsEU"] = df["Country"].isin(EU_COUNTRIES)

    # --- Categories ---------------------------------------------------------
    for column, labels in ORDERED_COLUMNS.items():
        df[column] = apply_labels(df[column], labels, ordered=True)
    for column, labels in UNORDERED_COLUMNS.items():
        df[column] = apply_labels(df[column], labels, ordered=False)
    df["Education"] = df["Education"].cat.remove_categories("Other")
    df["Industry"] = df["Industry"].replace("Other, please specify", "Other")

    # --- Experience ---------------------------------------------------------
    for column in ["YearsCode", "WorkExp"]:
        df[column] = df[column].where(df[column] <= MAX_YEARS)
    df["ExperienceLevel"] = pd.cut(df["WorkExp"], bins=EXPERIENCE_BINS, labels=EXPERIENCE_LABELS)

    # --- Salary -------------------------------------------------------------
    usd_per_eur = get_usd_per_eur(df)
    print(f"  exchange rate used: 1 EUR = {usd_per_eur:.3f} USD")

    salary = df["ConvertedCompYearly"]
    is_paid = df["Employment"].isin(PAID_STATUS)
    is_possible = salary.between(SALARY_MIN_USD, SALARY_MAX_USD)
    df["SalaryUSD"] = salary.where(is_paid & is_possible)
    df["SalaryUSD"] = remove_outliers_by_country(df, "SalaryUSD")
    df["SalaryEUR"] = (df["SalaryUSD"] / usd_per_eur).round()
    print(f"  salaries kept: {df['SalaryUSD'].notna().sum():,} out of {salary.notna().sum():,}")

    df = df.drop(columns=["Compensation", "Currency", "ConvertedCompYearly"])

    # --- AI -----------------------------------------------------------------
    # AISelect is multi-select: someone uses AI if they chose at least one tool
    # (stays missing when the person did not answer the question)
    uses_ai = (df["AISelect"] != "I don’t use AI tools").astype("boolean")
    df["UsesAI"] = uses_ai.where(df["AISelect"].notna())

    # --- Save ---------------------------------------------------------------
    df = df.reset_index(drop=True)
    df.to_parquet(CLEAN_PATH, index=False)
    print(f"Saved {CLEAN_PATH}: {len(df):,} rows, {df.shape[1]} columns")
    print(f"  France: {(df['Country'] == 'France').sum()} respondents, "
          f"median salary {df.loc[df['Country'] == 'France', 'SalaryEUR'].median():,.0f} EUR")


if __name__ == "__main__":
    main()
