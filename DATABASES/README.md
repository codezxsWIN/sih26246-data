# TEAM START HERE — recruiter and job-seeker databases

These are the shared database files for SIH26246. This folder sits directly at
the repository root and is linked near the top of the main README.

**Important: database structure and available evidence are packaged; individual
job-seeker profiles and recruiter accounts have NOT been acquired.** There are no
fabricated people, contacts, resumes or synthetic candidates in these files.

## Download or browse

**Use the current [v2 snapshot](v2/).** Earlier root-level SQLite/CSV files remain
untouched for preservation, but have a different schema. Do not mix versions.

| What you need | SQLite file | Browse CSV tables on GitHub |
|---|---|---|
| Recruiter / employer demand evidence | [recruiter.sqlite](v2/recruiter.sqlite) | [recruiter_data](v2/recruiter_data/) |
| Job-seeker / workforce evidence | [job_seekers.sqlite](v2/job_seekers.sqlite) | [job_seekers_data](v2/job_seekers_data/) |

On a SQLite file's GitHub page, click **Download raw file**. A clone also includes
both files. GitHub does not display SQLite tables; use the CSV links to preview
the same records without a database application. Private-repository teammates
need collaborator access to see or download these files.

## Exactly what is populated

| Database / table | Rows | What the rows mean |
|---|---:|---|
| Recruiter / `employers` | 1 | Parallel Wireless organization, not a person |
| Recruiter / `recruiter_accounts` | 0 | No individual recruiter accounts acquired |
| Recruiter / `job_postings` | 1 | Pune analyst posting observed 1 Oct 2026; not an NCS posting |
| Recruiter / `job_skills` | 5 | Python, SQL, pandas, NumPy, statistics mentions in that posting |
| Recruiter / `aggregate_demand` | 24 | Maharashtra NCS vacancies/active-employer metrics: 2 metrics × 12 financial years |
| Job seekers / `candidate_profiles` | 0 | No authorized individual job-seeker dataset acquired |
| Job seekers / `candidate_skills` | 0 | No candidate-level skill evidence acquired |
| Job seekers / `aggregate_jobseekers` | 24 | Maharashtra NCS registered/active metrics: 2 metrics × 12 financial years |
| Job seekers / `labour_rates` | 180 | Official PLFS all-role rate observations, not job-seeker headcounts |
| Job seekers / `workforce_baselines` | 60 | Derived all-role per-100-population baselines, not available Data Analysts |

Each database also has a `source_files` table containing 3 source CSV references
and their SHA-256 hashes. [manifest.json](v2/manifest.json) records all counts,
source hashes, database hashes and explicit readiness flags.

### Evidence limits your model must respect

- Employer posting: supplementary, one-employer sample. Vacancy headcount is
  **NULL**, not 1. Publication date is API `createdAt`, not independently verified
  first publication. `eligible_for_verified_market_demand=0`. Reuse terms have
  not been fully reviewed. Presence is a historical snapshot, not current status.
- NCS: public state/year dashboard snapshot updated 15 July 2026, FY 2015–16
  through partial FY 2026–27. Registered and active metrics have different meanings;
  definitions require confirmation. Do not sum them as distinct people or assume
  a Pune/Data Analyst split. NCS individual live vacancies are still unavailable.
- PLFS: Maharashtra annual/quarterly and All-India monthly series preserve their
  dimensions. PS+SS/CWS, frequency and the 2025 redesign require comparability
  review. Unspecified publisher dimensions remain **NULL**, not assumed “all.”
- Baselines: `LFPR × UR / 100` gives unemployed people per 100 in the matching
  population, not an absolute skilled workforce count. Every
  `available_data_analysts_estimate` is NULL.
- Candidate and recruiter-person tables are genuinely empty. The presence of
  their schema must never be reported as acquired candidate/recruiter records.

## Where this fits your workflow

Labour-market data → aggregation/normalisation → demand + supply engine →
gap → 6–12 month forecast → shortage/surplus severity → planner dashboard →
training/capacity recommendations.

Use these databases as **evidence inputs to aggregation/normalisation**. The
schema is usable in Python/SQL today; the evidence is not yet sufficient for
reliable role-level gaps or forecasts. Do not subtract state/year aggregate
job-seeker counts from one Pune job posting. Do not train a forecast on mixed
survey dimensions or use unknown dates as publication dates. Existing training,
taxonomy and geography data remain in [data/processed](../data/processed/);
this folder does not replace them.

## Read in Python — no new dependencies

Run from the repository root after cloning:

```python
import sqlite3
from pathlib import Path

path = Path('DATABASES/v2/recruiter.sqlite').resolve()
with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
    rows = db.execute('''
        SELECT e.company_name, j.job_title, j.location, s.skill_id,
               j.vacancy_count, j.eligible_for_verified_market_demand
        FROM job_postings j
        JOIN employers e USING (employer_id)
        JOIN job_skills s USING (posting_id)
    ''').fetchall()
    print(rows)
```

Equivalent read-only connections work for `job_seekers.sqlite`. If any runtime
code writes to a private copy, enable `PRAGMA foreign_keys=ON` on every connection.
The shared SQLite files are snapshots, not running database servers or APIs.

## Future candidate data — private, authorized only

There is no candidate importer in this version. A future authorized source must
provide a pseudonymous candidate ID, geography, occupation, current availability,
normalized skills, observation dates and reviewed reuse/consent evidence. The
empty [profile](v2/job_seekers_data/candidate_profiles.csv) and
[skill](v2/job_seekers_data/candidate_skills.csv) exports show the proposed fields.
See [CONTRACT.md](CONTRACT.md) and [SQL schemas](schema/) for constraints.

An opt-in team/college/placement-partner collection is a possible acquisition
route; only count verified available candidates in the matched role, location
and time window. A consent checkbox or pseudonymous ID alone does not establish
permission for every use. Do not scrape protected candidate directories.

**Never add real or pseudonymized candidate profiles to Git.** Keep authorized
operational profiles in an ignored private runtime location such as
`data/private/`, with appropriate access controls and retention. No names,
emails, phone numbers, government IDs, passwords or full resumes belong in
these shared files. Existing snapshots must stay public-safe and immutable.

## Rebuild and test

The committed databases are ready to download; rebuilding is optional. The
tested builder is [src/build_team_databases.py](../src/build_team_databases.py).
It reads only the five committed processed source CSVs listed in the manifest;
no network, raw-download archive or local Kaggle data is required.

```powershell
python -m src.build_team_databases --output-dir work/team-databases-new-snapshot
python -m unittest discover -s tests -v
```

Choose a **new output directory** each time. The builder refuses to overwrite
existing database, manifest or CSV files. A failed build can leave a partial
directory without a completed manifest; preserve it and retry in a new directory.
Only a completed manifest plus successful integrity/foreign-key checks denotes
a valid snapshot. Source data and earlier packs are untouched.
