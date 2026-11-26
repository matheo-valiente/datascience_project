# Stack Overflow Developer Survey 2026 - Streamlit app

Final project for the ECE Data Visualisation course.
An analytics app built with Streamlit on the Stack Overflow Developer Survey 2026,
for a sponsor interested in the French market.

## Run the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data files

All the clean files are on GitHub, nothing to download to run the app.

| File | Content |
|---|---|
| `data/survey_clean.parquet` | Clean data used by the app (1.3 MB, keeps the order of the categories) |
| `data/survey_clean.csv` | Same data in CSV, easy to open in Excel (11 MB) |
| `data/data_dictionary.csv` | Description of the 36 columns |
| `data/countries.csv` | Country reference table: ISO3 code and continent |

The raw data comes from https://survey.stackoverflow.co/ (30,903 respondents, 212 columns).
The raw CSV is not on GitHub because it is too big (117 MB).
To rebuild the clean files, put `survey_results_public.csv` and `survey_results_schema.csv`
in `data/` and run:

```bash
python prepare_data.py
```

## Data cleaning

All the rules are in `prepare_data.py`. The raw file is never modified.
The script also runs some checks at the end (`check_data`) and stops if something is wrong.

| Step | Rule | Why |
|---|---|---|
| Rows | Remove the 9,533 respondents without a country | They stopped the survey early (about 13 answers out of 212, no salary) |
| Rows | Remove exact duplicates (same answers to all questions) | 1 row |
| Columns | Keep 31 columns out of 212 | The others are almost empty or out of our scope |
| Countries | Shorter names, merge duplicates (e.g. "Republic of Korea" and "South Korea") | Readable charts, correct counts |
| Countries | New columns `ISO3`, `Continent` and `IsEU` (27 countries of the EU) | Maps, comparisons France / EU / continents |
| Roles | New column `RoleGroup`: 41 roles grouped in 8 families | 41 bars are not readable on a chart |
| Categories | Shorter labels and a logical order (age, company size, ...) | Readable and well sorted charts |
| Categories | "Prefer not to say", "I don't know", "Not sure" become missing | They are not real answers |
| Experience | `YearsCode` and `WorkExp` above 50 years become missing | Not realistic |
| Experience | New column `ExperienceLevel` (0-2, 3-5, 6-10, 11-20, 20+ years) | Compare groups |
| Salary | Only employed people and freelancers | Students and retired people have no salary |
| Salary | Keep salaries between 1,000 and 1,000,000 USD per year | Remove typos (monthly salary, 99999999, ...) |
| Salary | Boxplot rule (1.5 x IQR) on the log of the salary, **country by country** | A normal salary in India is not the same as in the US |
| Salary | New columns `SalaryUSD` and `SalaryEUR` (1 EUR = 1.137 USD, the rate used by Stack Overflow) | Euros for the French sponsor |
| AI | New column `UsesAI` (from the multi-select `AISelect`) | Simple yes / no |

Result: 21,369 respondents, 36 columns, 11,542 salaries kept out of 13,507.

Notes:
- Continents follow the UN regions, except Cyprus which is in Europe (it is in the EU).
  Central America and the Caribbean are in North America.
- "Nomadic" is an answer of the survey but not a country: it has no ISO3 code and no continent.

## Good practices for the charts

- Multi-select columns (languages, databases, AI tools, ...) keep the answers separated by `;`.
  Use `count_multiselect()` in `utils.py` to count them.
- Use the **median** for salaries, not the mean.
- Only compare groups with **at least 30 respondents** (44 countries have 30 salaries or more).
- Always show the number of respondents (n): some questions have few answers.
- This is a voluntary survey of Stack Overflow users, not a representative sample of all developers.
