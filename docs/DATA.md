# Data and cleaning

## Source

Stack Overflow Developer Survey, official archive on GitHub
(`StackExchange/Survey`, folder `packages/archive`):

| Year | Answers | Questions | Respondents | Columns |
|---|---|---|---|---|
| 2026 | `survey_results_public.csv` | `survey_results_schema.csv` | 30,903 | 212 |
| 2025 | `results.csv` | `schema.csv` | 49,191 | 172 |

The data is **never committed**: the app downloads it into `data/raw/` the first time
(`src/data.py`). To download it in advance: `python -m src.data`.

The respondents are volunteers who answered an online survey. The figures describe them,
not all developers.

## Cleaning rules

All the rules are in `src/cleaning.py` (and the labels in `src/labels.py`).
The same rules are applied to 2025 and 2026. The exploration that justifies them is in
`notebooks/01_exploration_2026.ipynb`.

| Step | Rule | Why |
|---|---|---|
| Rows | Remove exact duplicates (same answers to all questions) | 1 row in 2026 among people with a country |
| Rows | Remove respondents without a country | They stopped the survey early (about 13 answers out of 212 in 2026, no salary) |
| Countries | Shorter names, merge duplicates ("Republic of Korea" and "South Korea", two "Moldova") | Readable charts, correct counts |
| Countries | `ISO3`, `Continent` (from `data/countries.csv`) and `IsEU` (27 countries) | Maps, comparisons France / EU / continents |
| Roles | `RoleGroup`: 41 roles grouped in 8 families | 41 bars are not readable; also needed to compare with 2025 |
| Categories | Short labels and a logical order (age, company size, ...) | Readable and well sorted charts |
| Categories | "Prefer not to say", "I don't know", "Not sure" become missing | They are not real answers |
| Experience | `YearsCode` and `WorkExp` above 50 years become missing | Not realistic |
| Experience | `ExperienceLevel`: 0-2, 3-5, 6-10, 11-20, 20+ years | Compare groups |
| Salary | Only employed people and freelancers | Students and retired people have no salary |
| Salary | Keep salaries between 1,000 and 1,000,000 USD per year | Remove typos (monthly salary, 99999999...) |
| Salary | Boxplot rule (1.5 × IQR) on the log of the salary, **country by country** | A normal salary in India is not the same as in the US; the log makes salaries more symmetric (skewness 4.9 → -0.9 in France) |
| Salary | `SalaryUSD`, and `SalaryEUR` with the rate used by Stack Overflow that year (found in the data) | Euros for a French sponsor |
| AI (2026) | `UsesAI` from the multi-select `AISelect` | Simple yes / no |

A respondent is never removed because of one bad answer: if the salary is wrong,
only the salary becomes missing.

At the end, `check_clean_data` stops the app with a clear message if something is wrong
(duplicated respondents, unknown country, salary out of bounds...).
A new answer that has no label also stops the cleaning (`apply_labels`), so no answer
can be lost without us knowing.

## Result

| | 2025 | 2026 |
|---|---|---|
| Respondents kept | 35,437 | 21,369 |
| Clean salaries | 20,947 | 11,542 |
| France: respondents / salaries | 1,409 / 920 | 794 / 504 |
| France: median salary | 55,000 € | 55,000 € |

## Columns of the clean table

Columns in **both years** (harmonised, see [HARMONISATION.md](HARMONISATION.md)):

| Column | Description |
|---|---|
| `Year` | 2025 or 2026 |
| `ResponseId` | Id of the respondent in the survey of that year |
| `Country`, `ISO3`, `Continent`, `IsEU` | Where the person lives |
| `Age`, `Education`, `Employment` | Profile |
| `Role`, `RoleGroup` | Job (detailed, and family) |
| `OrgSize`, `WorkSetting` | Company size, remote / hybrid / in-person |
| `YearsCode`, `WorkExp`, `ExperienceLevel` | Years of coding, years of professional experience |
| `SalaryUSD`, `SalaryEUR` | Clean yearly salary |
| `LanguagesHaveWorkedWith` | Languages used (multi-select, `;`) |

Columns **only in 2026**: `Gender`, `CodeMain`, `ICorPM`, `Industry`, `JobSat`,
`LanguagesWantToWorkWith`, `LanguagesAdmired`, `DatabasesHaveWorkedWith`,
`CloudPlatHaveWorkedWith`, `WebFrameworkHaveWorkedWith`, `DevIDEHaveWorkedWith`,
`AISelect`, `UsesAI`, `AISentiment`, `AITrust`, `AIAvoid`, `LLMHaveWorkedWith`,
`AICodeAgentHaveWorkedWith`.

The exact question of each column is in the schema file of the year (`data/raw/schema_*.csv`).

## Limits to keep in mind

- Volunteers, mostly Stack Overflow users: not a representative sample of all developers.
- Some questions have few answers in France (about 360 to 515 for the technologies):
  always show n.
- Only 51 women among the 794 French respondents in 2026: no salary analysis by gender.
- Medians of groups with fewer than 30 respondents are not reliable.
