# SIH26246 - Labour Market Data Repository

Actual downloaded data, usable CSV extracts, tested acquisition scripts, and an evidence register for a Maharashtra/Pune labour-market prototype. NCS is the primary official demand source. Acquisition session: **1 October 2026**.

## Start here

**New: [Data Analyst model-input pack](docs/MODEL_INPUT_PACK.md)** — your updated workflow is captured in an additive, validated snapshot. It contains 165 deduplicated prototype postings, 86 contextual observations, skill features/evidence, safe import templates and explicit readiness flags. Gap, forecast, severity and training-capacity numbers are withheld until comparable evidence exists. The previous data and archives remain untouched.

1. [NCS findings and real API endpoints](docs/NCS_ACCESS.md)
2. [Source register](config/sources.json) - access, fields, dates, geography, frequency, quality, licence and module for each source
3. [Acquisition order and starter pack](docs/ACQUISITION.md)
4. [What the data can support](docs/DATA_DICTIONARY.md)
5. [Official access request draft](docs/NCS_ACCESS_REQUEST.md)
6. [Acquired sources beyond NCS](docs/ADDITIONAL_SOURCES.md) - DVET references, ITI grading, apprenticeship, PLFS2025 and UDISE+ mirror

## Data already collected

| Data | Result | Meaning |
|---|---|---|
| Official NCS dashboard tables | 1,788 state/year/metric records; 48 Maharashtra records | Four metrics, 12 year columns, publisher snapshot updated 15 July 2026 |
| Official NCS metadata workbook | 54 nonempty rows | Describes coverage, collection, dissemination and access; not individual vacancy records |
| PMKVY district training | 36 Maharashtra district rows | People trained in FY 2021-22; Pune = 4,206 |
| Kaggle India tech jobs | 23,201 rows downloaded; 5,327 mention Pune | Prototype only: every `scraped_at` value is 2025-06-10 despite the 2026 title |
| AISHE 2021-22 | Official report downloaded | State/discipline education supply; not a verified Pune graduate microdataset |
| PLFS 2023-24 | Annual report, study metadata and layout workbook downloaded | Labour baseline; person microdata requires MoSPI login |
| Pune Census 2011 | District handbook and inset tables downloaded | Historical population, workers and geography |
| Maharashtra Census town amenities | XLSX downloaded | Town geography and amenities; 2011 vintage |
| Extracted town geography | 535 Maharashtra town rows, including 35 in Pune district | Census codes and historical population; not current LGD geography |
| Maharashtra Economic Survey 2024-25 | Official report downloaded | Industry and state baseline |
| NCO-2015 and sector qualifications | Official PDFs downloaded | Occupation codes, automotive and electronics competencies |
| DVET institute/trade references | 952 Maharashtra institutes,95 trades;61 Pune institutes and405 links | Effective academic year unverified |
| DGT ITI grading 2026-27 | 14743 national rows;1046 Maharashtra-code rows | NG retained, not zero |
| NAPS/NATS engagement 2025 | 36 state/UT rows plus national total | Maharashtra:303763 NAPS;114127 NATS |
| PLFS calendar2025 | Report and methodology changes downloaded | More recent baseline; comparability caution |
| Pune UDISE+2025-26 mirror | Two aggregate enrolment files and schema | Not primary release independently verified |

The NCS extraction checks the displayed HTML table against the saved website bundle. Reported totals reconcile with year values and national totals. Some metrics have an additional unspecified-state row. Zero quality flags in this numerical check do not establish economic completeness or validity of every employer posting.

**Live individual NCS vacancies have not been downloaded.** The correct Indian API host was identified and public reference APIs returned HTTP 200. The vacancy search endpoint rejected plain JSON with HTTP 400 because it requires the website's encrypted request format. Browser access was subsequently denied by the desktop app. No encrypted-request workaround or embedded key was used.

The earlier conversation's `portal.api.nationalcareers.service.gov.uk` link belongs to the UK National Careers Service. It is unrelated to India's NCS and is excluded from this repository.

## Local setup

Python 3.11+:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m src.acquire --only aishe_2021_22 plfs_2023_24_report pmkvy_mh_centres_2021 pmkvy_district_training_2021_22 census_pune_2011
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

All downloads validate their format before saving. TLS validation uses the operating system trust store. Download attempts, including failures, are retained in `data/manifests/download_log.json` with file size and SHA-256.

The expanded local data-pack ZIP includes selected raw files. Two historical DVET PDFs contain staff contact details and are excluded from distribution. Git excludes raw files, website bundles, personal-data directories, credentials, and the virtual environment. GitHub contains code, factual aggregate extracts, inventories and audits. Kaggle posting extracts stay local-only pending the team's decision on upstream reuse rights.

After unpacking the raw-data archive into this folder:

```powershell
.venv/Scripts/python.exe -m src.process_pack
.venv/Scripts/python.exe -m src.verify_pack
```

Offline NCS reconstruction from the acquired public evidence:

```powershell
.venv/Scripts/python.exe -m src.extract_ncs --html data/raw/ncs/evidence/dashboard_table.html --bundle data/raw/ncs/evidence/dashboard_tables.js
```

NCS reference collection can be run after access has been enabled:

```powershell
.venv/Scripts/python.exe -m src.ncs_reference_api --enabled-access
```

That command retrieves state, functional-area and top-company reference data. It does not retrieve jobseeker profiles, resumes, applications, or an approved partner vacancy feed.

## Repository layout

```text
config/                 source metadata and concrete download URLs
src/                    acquisition, extraction and validation
tests/                  format and extraction correctness checks
docs/                   NCS access, acquisition order and data dictionary
data/manifests/         hashes, download outcomes and quality evidence
data/processed/ncs/     official aggregate CSVs and metadata
data/processed/training/ district training CSV
data/raw/               locally downloaded originals, excluded from Git
data/processed/demand/  local prototype posting extract, excluded from Git
```

## Data interpretation

Keep observations at their source's geography and period. Maharashtra state vacancy totals cannot establish Pune role-level demand. NCS registered jobseekers do not measure all available workers. PMKVY trained counts do not measure current employable stock, certified candidates, or placement outcomes. AISHE enrolment does not equal graduates available for employment. PLFS district codes do not automatically imply statistically representative Pune estimates.

The Kaggle download has 2,130 repeated nonempty job URLs, and 21,764 of 23,201 descriptions end in `...`. Salary zero with `salary_disclosed=False` means missing salary. Its inconsistent dates prevent credible current trends or forecasting. Keep it for demonstrating file ingestion, geography filtering, deduplication and skill parsing.

Code is MIT licensed. Third-party data retain their own rights; see [DATA_LICENSES.md](DATA_LICENSES.md). No modelling has been added.
