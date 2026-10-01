# Database contract — current v2 snapshot

This contract applies to `DATABASES/v2/`. Earlier root-level SQLite files are
preserved unchanged and have a different v1 schema; do not mix their tables with
the v2 schema or examples. The supported current builder is
`src/build_team_databases.py`.

Two SQLite snapshots package the already acquired, public-safe evidence. No new
personal profiles, recruiter contacts or live NCS vacancies are implied.

## Recruiter-side input

`recruiter.sqlite`: `employers` (organizations), `recruiter_accounts` (empty),
`job_postings` (observations, not vacancy headcounts), `job_skills` (mentions),
`aggregate_demand` (NCS state/year metrics) and `source_files` (provenance).
Employer IDs and posting IDs are source-scoped strings. Skills use existing
repository skill IDs. Posting publication and observation dates stay separate.
Unknown vacancy counts are NULL. Current postings are supplementary and not
eligible for verified market-demand estimation. Accounts are not employers.

## Job-seeker-side input

`job_seekers.sqlite`: `candidate_profiles` and `candidate_skills` are empty
because no authorized profile dataset has been acquired. `aggregate_jobseekers`
contains NCS Maharashtra registered/active metrics, not individual people.
`labour_rates` and `workforce_baselines` preserve geography, reference period,
survey dimensions, methodology and units. They describe all-role labour context,
not available Data Analysts. No population headcount is inferred from a rate.

Candidate profiles accept only pseudonymous IDs, normalized geography/occupation,
availability status, availability observation date and provenance/consent fields.
Consent evidence and reuse authority require review before any import; a database
flag is not proof of permission. Pseudonymous profiles remain private: never add
them to these committed snapshots. No candidate import functionality is provided.

## Invariants

- SQL foreign keys, uniqueness, non-negative counts and rate checks are enforced.
- Enable `PRAGMA foreign_keys=ON` on every SQLite connection.
- Source CSVs retain SHA-256 provenance; CSV previews equal SQLite table counts.
- Snapshots are additive. The builder refuses to overwrite any output file.
- Aggregate NCS metrics cannot be subtracted from individual posting observations.
- PS+SS/CWS, annual/quarterly/monthly and pre/post-2025 PLFS series stay distinct.
- Registered, active and trained populations are not interchangeable supply.
- Gap, forecast, severity and training capacity remain unassessed until matching
  population, geography, occupation/skill, time, rights and uncertainty evidence exist.

The shared databases are evidence inputs for aggregation/normalisation, not a
trained model, operational account service or complete recruitment platform.
