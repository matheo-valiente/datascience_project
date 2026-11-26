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

## Structure

```
app.py              entry point: menu and common sidebar
views/              one file per page (main dashboard + 5 axes)
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
| 4. Skills and AI | Which technologies and AI practices are linked to higher salaries? | `axis-4` | _to complete_ |
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

## Rigour

- Every figure states its population: who, which year, how many respondents.
- Comparisons between 2025 and 2026 only use harmonised questions ([docs/HARMONISATION.md](docs/HARMONISATION.md)).
- The respondents are volunteers who answered an online survey: the figures describe them,
  not all developers.
