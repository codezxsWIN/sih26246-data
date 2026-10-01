# Team databases — start here

This folder is the model-facing entry point for the SIH26246 labour-market
pipeline. Download or open the two SQLite files first:

| Database | Use | Current evidence |
|---|---|---|
| [`recruiter.sqlite`](recruiter.sqlite) | employer, posting, skill and demand inputs | 1 employer, 1 observed Pune posting, 5 skill mentions, 24 NCS demand observations |
| [`job_seekers.sqlite`](job_seekers.sqlite) | job-seeker supply and labour-force inputs | 24 NCS aggregate job-seeker observations, 180 PLFS rates, 60 derived baselines |

CSV previews are in [`recruiter_data/`](recruiter_data/) and
[`job_seeker_data/`](job_seeker_data/), so teammates can inspect the data
directly in GitHub or Excel. The schema contract is in
[`CONTRACT.md`](CONTRACT.md), and `manifest.json` contains row counts and
source hashes.

## Sources represented

- [NCS](https://www.ncs.gov.in/) — Maharashtra registered/active job seekers,
  vacancies and active employers. These are official aggregate dashboard
  observations, not individual profiles or live vacancy records.
- [data.gov.in](https://www.data.gov.in/) — source register and acquisition
  routes are recorded in `../config/sources.json`; only validated, committed
  extracts are loaded into these snapshots.
- [AISHE](https://aishe.gov.in/) — official higher-education supply context;
  acquired report evidence remains in the repository’s source inventory and is
  not silently converted into individual candidates.
- [NSDC](https://www.nsdcindia.org/) — occupational and qualification-pack
  taxonomy context for normalisation.
- [Skill India Digital](https://www.skillindiadigital.gov.in/) — training and
  certification context for later recommendations.
- [MoSPI/PLFS](https://www.mospi.gov.in/) — the job-seeker database includes
  the acquired public aggregate rate series and documented comparability flags.
- [Kaggle](https://www.kaggle.com/) — prototype job-posting data remains
  local-only pending upstream reuse rights; it is not mixed into the verified
  recruiter snapshot.

## Important limitation

The individual `candidate_profiles` and `candidate_skills` tables are present
but intentionally empty. The team does not have an authorised candidate
export. Do not add names, phone numbers, emails, government IDs, resumes or
social-profile data to this repository. The databases are clean inputs for
aggregation and normalisation; they are not yet sufficient for a reliable
Pune/Data-Analyst demand–supply gap or forecast.

To rebuild a fresh snapshot after source CSVs change:

```powershell
.venv/Scripts/python.exe -m src.team_databases
```

The builder refuses to overwrite an existing snapshot. Use a new output
directory for a new version.
