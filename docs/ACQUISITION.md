# Acquisition order and minimum viable data pack

Exact URLs and source-level fields, coverage, geography, licence, frequency, quality, modules and status are in `config/sources.json`. Raw downloads are in the local ZIP; Git contains code, factual aggregates and provenance. This is acquisition, not modeling.

1. **NCS official aggregates: done.** `data/processed/ncs/ncs_state_year_metrics.csv` and Maharashtra subset. Four metrics, twelve years; 2026-2027 partial. Separate totals from annual observations.
2. **NCS metadata: done.** `data/raw/ncs/ncs_metadata_2026_09.xlsx` and metadata CSV. Establish coverage and contact route.
3. **NCS live Pune vacancies: outstanding first priority.** Browser permission was declined. Plain JSON search returned 400. Enable normal authorized access or obtain approved export/feed credentials. Request job ID, title, description/skills, location, education, experience, salary disclosure, posted/closing dates, status, source and update timestamp. These are requested, not confirmed response fields. `NCS_ACCESS_REQUEST.md` is a draft; no message sent.
4. **Skill/occupation standards: done.** `data/raw/skills/`: NCO-2015, automotive ASC/Q3604, electronics ELE/Q2501 and Python/SQL qualification PDFs. Retain IDs, versions and validity. Assembly Operator is not CNC Technician.
5. **Training supply: done.** `data/raw/training/` and 36-district Maharashtra trained-count CSV, FY 2021-22. Centre-location annexure is historical, not a current active-centre list.
6. **Education pipeline: report done.** `data/raw/supply/aishe_2021_22.pdf`. Select Maharashtra tables with units/table IDs. Pune institution-level graduate microdata remains unverified; do not fabricate it.
7. **Labour baseline: report/layout/metadata done.** `data/raw/baseline/plfs_*`. Start with state-level published estimates. Person files require official account/terms. Study 213 is 2023-24, not a claim to the newest release; inspect newer calendar/quarterly releases separately.
8. **Geography: historical files done.** `data/raw/geography/census_*`; extracted Maharashtra and Pune town CSVs. Preserve Census codes separately from current LGD. Current LGD export and concordance remain future acquisition.
9. **Economic context: done.** Maharashtra Economic Survey 2024-25 report in baseline folder. Keep period, units and footnotes when extracting tables.
10. **OGD NCS cross-check: pending.** Resource UUID `6de4f0bd-8514-4fa3-a86f-e240a2d26eeb`. CSV returned 403; API host unreachable this session. Use official download or your data.gov.in API key when accessible. Metadata is not acquired observations.
11. **Fallback postings: done, local only.** `data/raw/demand/kaggle_india_tech_2026.zip`; `data/processed/demand/kaggle_pune_jobs.csv`. Use for ingestion/parser demonstration only. Dates inconsistent; not credible live demand.

## What the first prototype can claim

The minimum acquired pack supports a data explorer and ingestion prototype: NCS state aggregates, district training, geography, skill standards and education/labour context. It does not yet establish Pune role-level demand/supply gaps or forecasts. Registered seekers, postings, graduates and trained people have different units, coverage and periods; do not subtract them as though comparable.

Live-demand gate: an authorized NCS vacancy sample with verified record fields and dates. Aim initially for 100-500 relevant postings as an inspection sample, not a completeness guarantee. Check multiple locations, vacancies per posting, duplicate integrated sources, expired jobs and salary missingness.

## Access and collection safeguards

- No candidate personal profiles, contact details, resumes or applications are needed.
- Do not bypass denied permission, encryption, CAPTCHA, login or limits. SIH participation does not itself supply credentials.
- Retain originals, hashes, retrieval times, publisher vintages and failure logs.
- Distinguish tested anonymous references, internal website routes and approved partner feeds.
- NSDC main-site access was restricted; public SSC and NQR standards were acquired instead.

## Download these first: eight starter groups

Already acquired except the explicitly pending feed:

1. NCS dashboard CSV and Maharashtra slice.
2. NCS official metadata workbook/CSV.
3. Authorized NCS live-vacancy export/feed — **pending**.
4. PMKVY Maharashtra FY 2021-22 district-trained CSV and original annexure.
5. NCO-2015 and three qualification PDFs.
6. AISHE 2021-22 report.
7. PLFS 2023-24 report, layout and study metadata.
8. Pune Census handbook and Maharashtra town-code workbook/CSV.

Kaggle is additional test material, not a replacement for item 3.
