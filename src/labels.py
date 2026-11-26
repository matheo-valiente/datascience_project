"""
Labels used to clean and harmonise the answers of 2025 and 2026.

- *_LABELS dicts: long answer of the survey -> short label for the charts.
  None means "not a real answer" (it becomes a missing value).
  The order of each dict is the order of the categories in the charts.
- RENAME_2025 and the *_2025 dicts: what is needed to put 2025 in the 2026 format.
  All the harmonisation choices are explained in docs/HARMONISATION.md.
"""

# ---------------------------------------------------------------------------
# Columns
# ---------------------------------------------------------------------------
# Columns of the 2026 file that we keep
COLUMNS_2026 = [
    "ResponseId", "Country", "Age", "Gender", "Education", "Employment", "CodeMain",
    "Role", "ICorPM", "OrgSize", "Industry", "WorkSetting", "YearsCode", "WorkExp",
    "JobSat", "Compensation", "Currency", "ConvertedCompYearly",
    "LanguagesHaveWorkedWith", "LanguagesWantToWorkWith", "LanguagesAdmired",
    "DatabasesHaveWorkedWith", "CloudPlatHaveWorkedWith",
    "WebFrameworkHaveWorkedWith", "DevIDEHaveWorkedWith",
    "AISelect", "AISentiment", "AITrust", "AIAvoid",
    "LLMHaveWorkedWith", "AICodeAgentHaveWorkedWith",
]

# 2025 name -> 2026 name (same question, different column name)
RENAME_2025 = {
    "EdLevel": "Education",
    "DevType": "Role",
    "RemoteWork": "WorkSetting",
    "CompTotal": "Compensation",
    "LanguageHaveWorkedWith": "LanguagesHaveWorkedWith",
}
COLUMNS_2025 = [
    "ResponseId", "Country", "Age", "EdLevel", "Employment", "DevType", "OrgSize",
    "RemoteWork", "YearsCode", "WorkExp", "CompTotal", "Currency",
    "ConvertedCompYearly", "LanguageHaveWorkedWith",
]

# Columns that exist and mean the same thing in both years
HARMONISED_COLUMNS = [
    "Year", "ResponseId", "Country", "ISO3", "Continent", "IsEU",
    "Age", "Education", "Employment", "Role", "RoleGroup", "OrgSize", "WorkSetting",
    "YearsCode", "WorkExp", "ExperienceLevel", "SalaryUSD", "SalaryEUR",
    "LanguagesHaveWorkedWith",
]

# Columns only available in 2026
ONLY_2026_COLUMNS = [
    "Gender", "CodeMain", "ICorPM", "Industry", "JobSat",
    "LanguagesWantToWorkWith", "LanguagesAdmired", "DatabasesHaveWorkedWith",
    "CloudPlatHaveWorkedWith", "WebFrameworkHaveWorkedWith", "DevIDEHaveWorkedWith",
    "AISelect", "UsesAI", "AISentiment", "AITrust", "AIAvoid",
    "LLMHaveWorkedWith", "AICodeAgentHaveWorkedWith",
]

# ---------------------------------------------------------------------------
# Countries
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
    "Micronesia, Federated States of...": "Micronesia",
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

# The 27 countries of the European Union
EU_COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
    "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta",
    "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia",
    "Spain", "Sweden",
]

# ---------------------------------------------------------------------------
# Roles: grouped in 8 families
# ---------------------------------------------------------------------------
# 2025 name -> 2026 name
ROLES_2025 = {
    "Founder, technology or otherwise": "Founder or entrepreneur",
    "UX, Research Ops or UI design professional": "UX, research, or UI design professional",
    "Other (please specify):": "Other",
}

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
# Answers with a natural order
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

# 2025 answers written differently (curly apostrophe, other "Other" text)
EDUCATION_2025 = {
    "Bachelor’s degree (B.A., B.S., B.Eng., etc.)": "Bachelor's degree (B.A., B.S., B.Eng., etc.)",
    "Master’s degree (M.A., M.S., M.Eng., MBA, etc.)": "Master's degree (M.A., M.S., M.Eng., MBA, etc.)",
    "Other (please specify):": "Other, please specify",
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

# ---------------------------------------------------------------------------
# Answers without a natural order
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Which labels go with which column
# ---------------------------------------------------------------------------
ORDERED_LABELS_COMMON = {
    "Age": AGE_LABELS,
    "Education": EDUCATION_LABELS,
    "OrgSize": ORG_SIZE_LABELS,
    "WorkSetting": WORK_SETTING_LABELS,
}
ORDERED_LABELS_2026 = {
    "ICorPM": IC_OR_PM_LABELS,
    "AISentiment": AI_SENTIMENT_LABELS,
    "AITrust": AI_TRUST_LABELS,
}
UNORDERED_LABELS_COMMON = {
    "Employment": EMPLOYMENT_LABELS,
}
UNORDERED_LABELS_2026 = {
    "Gender": GENDER_LABELS,
    "CodeMain": CODE_MAIN_LABELS,
    "AIAvoid": AI_AVOID_LABELS,
}

PAID_STATUS = ["Employed", "Freelancer / self-employed"]

EXPERIENCE_BINS = [-1, 2, 5, 10, 20, 50]
EXPERIENCE_LABELS = ["0-2 years", "3-5 years", "6-10 years", "11-20 years", "20+ years"]
