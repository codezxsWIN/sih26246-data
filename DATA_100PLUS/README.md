# OPEN THE LARGE DATA TABLES HERE

**Bulk source evidence, not the clean working layer. [Start with filtered tables and the quality audit](../CLEAN_DATA/README.md).**

**[Open the complete 24,398-row pack](20261002-v6/README.md)** — collected/extracted on 2 October 2026. The earlier small `DATABASES` snapshot is preserved.

Click a CSV below to read the actual records on GitHub. Each table has more than 100 data rows, excluding its header.

| Actual table | Rows | What a row means |
|---|---:|---|
| [Skill India courses](20261002-v6/skillindia_courses.csv) | 1,916 | Unique public course ID; includes flagged test/demo entries |
| [NQR qualifications](20261002-v6/nqr_qualifications.csv) | 2,814 | Official NCVET qualification, linked through NSDC's standards ecosystem |
| [AISHE pass-outs](20261002-v6/aishe_state_level_passouts.csv) | 666 | State/UT or national total × education level × academic year |
| [PMKVY district training](20261002-v6/pmkvy_district_training.csv) | 725 | District training total for FY 2021-22 |
| [PLFS workforce rates](20261002-v6/plfs_workforce_rates.csv) | 180 | Survey rate observation, with geography/time/survey dimensions |
| [NCS historical aggregates](20261002-v6/ncs_state_year_metrics.csv) | 1,788 | State/year/registration or vacancy-related metric |
| [Maharashtra DVET institutes](20261002-v6/dvet_maharashtra_institutes.csv) | 952 | Training institute reference |
| [DGT ITI grading](20261002-v6/dgt_iti_grading.csv) | 14,743 | National ITI grading record |
| [Kaggle recruitment demo](20261002-v6/kaggle_recruitment_demo.csv) | 614 | Prototype classification example; not verified available candidates |

**[Download the combined SQLite database](20261002-v6/labour_records.sqlite)** or [read counts, fields and provenance](20261002-v6/manifest.json). GitHub cannot display SQLite rows directly; use the CSV links above for reading.

The sum is **24,398 heterogeneous table rows**, not 24,398 people, jobs or distinct organisations. No rows were fabricated to meet the requested count. Public aggregates and training totals are not individual job-seeker profiles. Reliable Pune skill gaps and forecasts still require comparable job demand, skill-specific available supply and enough history.

Incomplete local extraction attempts were retained without being published as separate completed packs. Existing repo snapshots and data were not deleted.
