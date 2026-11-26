# Developer salaries in France - Stack Overflow Survey 2026

Final project of the ECE Data Visualisation course: a Streamlit analytics app built on the
Stack Overflow Developer Survey 2026 (and 2025 for some comparisons).

- **Theme:** salaries
- **Sponsor:** the Apec (French association for the employment of executives)
- **Message of the main dashboard:** developers in France earn less than in the rest of the EU,
  at every experience level, and the gap did not close between 2025 and 2026.
  The message is computed from the data by the app.

## Run the app (from a fresh clone)

Python 3.12 is recommended.

```bash
git clone https://github.com/matheo-valiente/datascience_project.git
cd datascience_project
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The first launch downloads the survey files (about 250 MB, from the official Stack Overflow
archive) into `data/raw/`, then cleans them: it takes about one minute. After that, the data is
read from the disk and kept in the cache. To download the files in advance: `python -m src.data`.

The data is never committed to the repository.

## Deploy online (Streamlit Community Cloud)

1. Go to https://share.streamlit.io and sign in with the GitHub account that owns the repository.
2. **Create app** → repository `matheo-valiente/datascience_project`, branch `main`,
   main file `app.py`.
3. **Advanced settings** → Python version **3.12**.
4. **Deploy**. The first start downloads and cleans the data (about one minute).

Nothing else is needed: no secret, no data file in the repository.

## Structure

```
app.py              entry point: menu and common sidebar
views/              one file per page (main dashboard, 5 axes, methodology)
ui.py               Streamlit helpers shared by the pages (cache, captions, sidebar)
src/                shared logic, without Streamlit
    config.py       settings and rules
    data.py         download and read the raw files
    labels.py       labels and 2025 -> 2026 harmonisation
    cleaning.py     cleaning of one year
    population.py   who is behind each figure
    analysis.py     statistics (small tables)
    charts.py       Plotly figures
data/countries.csv  country reference table (ISO3, continent)
notebooks/          shared explorations
tests/              automatic tests
docs/               architecture, data cleaning, harmonisation
.github/workflows/  tests run automatically on GitHub at each push
```

## Documentation

- [Technical architecture](docs/ARCHITECTURE.md): features, files, data flow, cache and session
- [Data and cleaning](docs/DATA.md): source, cleaning rules, columns, limits
- [Harmonisation 2025 / 2026](docs/HARMONISATION.md): what is compared and how

## The five axes

| Axis | Question | Branch | Owner |
|---|---|---|---|
| 1. Geography | Where does France stand compared with other countries and continents? | `axis-1` | _to complete_ |
| 2. Experience | How do salaries grow with experience, and is the gap the same at every stage? | `axis-2` | _to complete_ |
| 3. Roles | Which jobs pay best in France, compared with the rest of Europe? | `axis-3` | _to complete_ |
| 4. Skills and AI | Which technologies and AI practices are linked to higher salaries? | `axis-4` | matheo-valiente |
| 5. Work conditions | Do company size, sector, remote work and freelancing change the pay? | `axis-5` | _to complete_ |

## Work as a group

- The common core is on `main`. Each axis is developed on its own branch, then merged into `main`.
- Start an axis: `git checkout main && git pull && git checkout -b axis-1`
- Put the logic in `src/` (no Streamlit there), the display in `views/axis_*.py`.
- Every figure shows its population: use `ui.show_chart` or `ui.show_population`.
- Before merging: run the tests and start the app.

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Project log

### Wednesday 26 November 2026 - common core and axis 4

**Setup**
- Repository created, `.gitignore` (raw data, virtual environment and local files are never committed).
- Reproducible environment: Python 3.12, exact versions in `requirements.txt` and `requirements-dev.txt`.

**Taking over the data** (`notebooks/01_exploration_2026.ipynb`)
- 2026 survey: 30,903 respondents, 212 columns. France: 794 respondents, 6th country of the survey, 3rd in Europe.
- Problems found: 9,533 respondents without country (they stopped the survey early), absurd salaries
  (from 1 $ to 32 million $ a year), multi-select answers separated by `;`, very long labels,
  duplicated country names.
- A fixed salary threshold was rejected: 10,000 $ would remove 31% of the salaries in India and
  81% in Nigeria. We use the boxplot rule on the log of the salary, country by country.

**Framing**
- Theme: salaries. Sponsor: the Apec.
- Message: developers in France earn less than in the rest of the EU (55k € vs 66.5k €, -17%),
  at every experience level, and the gap widened since 2025 (-14.6% → -17.3%).

**Common core** (`src/`, `ui.py`, `app.py`)
- The app downloads the official data itself (never committed), then cleans it with the same rules
  for 2025 and 2026, and checks the result (`check_clean_data`).
- 2025 / 2026 harmonisation, question by question (`docs/HARMONISATION.md`,
  `notebooks/02_harmonisation_2025_2026.ipynb`).
- Shared logic without Streamlit: population, analysis, charts. Streamlit only in `ui.py` and `views/`.
- Cache with `st.cache_data`, comparison group and axis filters in `st.session_state`.
- Main dashboard: message computed from the data, 4 key figures, 3 charts (France among EU countries,
  gap by experience, 2025 → 2026). The comparison group can be changed (EU, Europe, world, one country).
- Every chart shows its population (who, year, n), its data table and a CSV download.
  Groups with fewer than 30 respondents are hidden or marked.
- Methodology page in the app, a clear message if the data cannot be downloaded.

**Axis 4 - Skills and AI** (branch `axis-4`, merged into `main`)
- Exploration: `notebooks/axis_4_skills_and_ai.ipynb`.
- 6 views: salary by technology, most used technologies, AI and salary (also at equal experience),
  opinions on AI, AI tools, languages 2025 → 2026 and languages people want to learn.
- Findings: Rust users earn the most in France (66k €, +20%); AI users earn 29% more, also at equal
  experience (correlation, not causation); Rust is the most wanted language (41% want it, 23% use it).

**Quality**
- 26 automatic tests (`tests/`), run by GitHub Actions at each push.
- The app was tested from a fresh clone of GitHub, and on every page with every comparison group.
- Documentation: `docs/ARCHITECTURE.md`, `docs/DATA.md`, `docs/HARMONISATION.md`.

**Next steps**
- Axes 1, 2, 3 and 5: one member each, on branches `axis-1`, `axis-2`, `axis-3`, `axis-5`.
- Deploy on Streamlit Community Cloud (see above).
- Prepare the 5-minute demo: main dashboard and message, then one axis live.

## Rigour

- Every figure states its population: who, which year, how many respondents.
- Comparisons between 2025 and 2026 only use harmonised questions ([docs/HARMONISATION.md](docs/HARMONISATION.md)).
- The respondents are volunteers who answered an online survey: the figures describe them,
  not all developers.
