# Harmonisation between 2025 and 2026

The brief requires that every comparison between 2025 and 2026 relies on an explicit
harmonisation of the questions and answers. This document lists, question by question,
what is compared and how. The checks are in `notebooks/02_harmonisation_2025_2026.ipynb`,
the code in `src/labels.py` (`RENAME_2025`, `EDUCATION_2025`, `ROLES_2025`) and
`src/cleaning.py` (`harmonise_2025`).

## General rules

1. The **same cleaning rules** are applied to both years (`clean_survey`).
2. Salaries of each year are converted to euros with **the rate of that year**
   (the rate used by Stack Overflow, found in the data).
3. Salaries are **nominal**: not corrected for inflation.
4. The respondents are **not the same people** each year: we compare two samples of
   volunteers, not the evolution of the same developers.
5. Only the columns of `HARMONISED_COLUMNS` (`src/labels.py`) can be compared.

## Question by question

| Question | 2025 column | 2026 column | Status | What we do |
|---|---|---|---|---|
| Country | `Country` | `Country` | ✅ Comparable | Same question "Where do you live?". 14 small countries only in 2025, 6 only in 2026: comparisons are made on countries present both years |
| Salary | `CompTotal`, `ConvertedCompYearly` | `Compensation`, `ConvertedCompYearly` | ✅ Comparable | Same question (total yearly compensation before taxes). Same cleaning, rate of each year |
| Employment | `Employment` | `Employment` | ✅ Comparable | Same answers |
| Company size | `OrgSize` | `OrgSize` | ✅ Comparable | Same answers |
| Work setting | `RemoteWork` | `WorkSetting` | ✅ Comparable | Same question and answers, column renamed |
| Professional experience | `WorkExp` | `WorkExp` | ✅ Comparable | Wording slightly changed ("years of professional work experience" → "years working professionally"), same meaning |
| Years of coding | `YearsCode` | `YearsCode` | ✅ Comparable | Same question |
| Education | `EdLevel` | `Education` | ✅ After harmonisation | Only the apostrophe (`’` → `'`) and the text of "Other" change |
| Age | `Age` | `Age` | ✅ Except under 18 | "Under 18" only exists in 2026: exclude it when comparing the two years |
| Role | `DevType` | `Role` | ⚠️ By family only | 12 roles are new in 2026 (for example "Software engineer", "Platform engineer"). 3 roles renamed (`ROLES_2025`). Compare `RoleGroup`, not `Role` |
| Languages used | `LanguageHaveWorkedWith` | `LanguagesHaveWorkedWith` | ⚠️ Common languages only | 7 languages only in 2026 (Clojure, Haskell, Julia, Nix, Objective-C, Solidity, Other). Compare only the languages present both years |
| Industry | `Industry` | `Industry` | ❌ Not compared | The list of answers changed a lot |
| AI questions | `AISelect`, `AISent`... | `AISelect`, `AISentiment`... | ❌ Not compared | Different questions and answers |
| Gender | — | `Gender` | ❌ 2026 only | Not asked in 2025 |

## Results used in the main dashboard

| | 2025 | 2026 |
|---|---|---|
| France: median salary (n) | 55,000 € (920) | 55,000 € (504) |
| Rest of the EU: median salary (n) | 64,440 € (6,907) | 66,521 € (3,922) |
| Gap France vs rest of the EU | -14.6% | -17.3% |
