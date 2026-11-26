"""
Download and read the raw survey files.

The files are downloaded once into data/raw/ (this folder is not on GitHub),
then read from the disk.
"""

import shutil
import urllib.request

import pandas as pd

from src.config import RAW_DIR, RAW_FILES

NUMBER_COLUMNS = ["ResponseId", "YearsCode", "WorkExp", "JobSat",
                  "Compensation", "CompTotal", "ConvertedCompYearly"]


def download_file(url, path):
    """Download a file, only if it is not already on the disk."""
    if path.exists():
        return
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".part")
    print(f"Downloading {url} ...")
    with urllib.request.urlopen(url) as response, open(temporary_path, "wb") as file:
        shutil.copyfileobj(response, file)
    # Rename at the end: a download stopped in the middle never looks complete
    temporary_path.rename(path)


def download_year(year):
    """Download the answers and the questions of one year."""
    files = RAW_FILES[year]
    download_file(files["survey_url"], files["survey_path"])
    download_file(files["schema_url"], files["schema_path"])


def read_survey(year, columns):
    """
    Read the answers of one year, keeping only some columns.

    We also remove exact duplicates (same answers to ALL the questions).
    The file is read by pieces of 5,000 rows to use little memory: for each
    piece we keep a "fingerprint" (hash) of the full row, and only the columns we need.
    Everything is read as text, so that two identical rows always have the same
    fingerprint (pandas could guess another type in another piece).
    """
    download_year(year)
    pieces = []
    fingerprints = []
    reader = pd.read_csv(RAW_FILES[year]["survey_path"], encoding="utf-8-sig",
                         chunksize=5_000, dtype=str)
    for chunk in reader:
        all_answers = chunk.drop(columns="ResponseId")
        fingerprints.append(pd.util.hash_pandas_object(all_answers, index=False))
        pieces.append(chunk[columns])

    df = pd.concat(pieces, ignore_index=True)
    is_duplicate = pd.concat(fingerprints, ignore_index=True).duplicated()
    df = df[~is_duplicate.values].reset_index(drop=True)

    # Columns with numbers (they were read as text)
    for column in NUMBER_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column])
    return df


def read_schema(year):
    """Read the file that describes the questions of one year."""
    download_year(year)
    return pd.read_csv(RAW_FILES[year]["schema_path"], encoding="utf-8-sig")


if __name__ == "__main__":
    # python -m src.data  -> downloads all the files in advance
    for survey_year in RAW_FILES:
        download_year(survey_year)
    print("All files are in", RAW_DIR)
