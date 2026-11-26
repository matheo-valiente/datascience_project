# Stack Overflow Developer Survey 2026 - Streamlit app

Final project for the ECE Data Visualisation course.
An analytics app built with Streamlit on the Stack Overflow Developer Survey 2026,
for a sponsor interested in the French market.

## Run the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app reads `data/survey_clean.parquet` (1.3 MB), which is on GitHub.

## Data

The raw data comes from https://survey.stackoverflow.co/ (30,903 respondents, 212 columns).
The raw CSV is not on GitHub because it is too big (117 MB).
To rebuild the clean file, put `survey_results_public.csv` in `data/` and run:

```bash
python prepare_data.py
```

## Data cleaning

All the rules are in `prepare_data.py`. The raw file is never modified.

| Step | Rule | Why |
|---|---|---|
| Rows | Remove the 9,533 respondents without a country | They stopped the survey early (about 13 answers out of 212, no salary) |
| Rows | Remove exact duplicates (same answers to all questions) | 1 row |
| Columns | Keep 31 columns out of 212 | The others are almost empty or out of our scope |
| Countries | Shorter names, merge duplicates (e.g. "Republic of Korea" and "South Korea") | Readable charts, correct counts |
| Countries | New column `IsEU` (27 countries of the European Union) | Compare France with the EU |
| Categories | Shorter labels and a logical order (age, company size, ...) | Readable and well sorted charts |
| Categories | "Prefer not to say", "I don't know", "Not sure" become missing | They are not real answers |
| Experience | `YearsCode` and `WorkExp` above 50 years become missing | Not realistic |
| Experience | New column `ExperienceLevel` (0-2, 3-5, 6-10, 11-20, 20+ years) | Compare groups |
| Salary | Only employed people and freelancers | Students and retired people have no salary |
| Salary | Keep salaries between 1,000 and 1,000,000 USD per year | Remove typos (monthly salary, 99999999, ...) |
| Salary | Boxplot rule (1.5 x IQR) on the log of the salary, **country by country** | A normal salary in India is not the same as in the US |
| Salary | New columns `SalaryUSD` and `SalaryEUR` (1 EUR = 1.137 USD, the rate used by Stack Overflow) | Euros for the French sponsor |
| AI | New column `UsesAI` (from the multi-select `AISelect`) | Simple yes / no |

Result: 21,369 respondents, 33 columns, 11,542 salaries kept out of 13,507.

Multi-select columns (languages, databases, AI tools, ...) keep the answers separated by `;`.
Use `count_multiselect()` in `utils.py` to count them.
