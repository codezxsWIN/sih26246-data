# START HERE: filtered working tables

**[Open the filtered records](20261002-v3/README.md)**. This is the team's working entry point. The larger [bulk source pack](../DATA_100PLUS/README.md) is retained as source evidence, not advertised as clean model input.

| Read actual records | Retained rows | Excluded from working table |
|---|---:|---:|
| [Course catalogue candidates](20261002-v3/course_catalogue_candidates.csv) | 664 | 1,252 |
| [Qualifications within listed validity](20261002-v3/valid_qualifications.csv) | 1,862 | 952 |
| [Education pass-out observations](20261002-v3/education_passout_observations.csv) | 507 | 159 |
| [District training observations](20261002-v3/district_training_observations.csv) | 710 | 15 |
| [Fully specified PLFS workforce rates](20261002-v3/fully_specified_workforce_rates.csv) | 33 | 147 |
| [IT/ITES, automotive and electronics qualification subset](20261002-v3/mvp_sector_qualifications.csv) | 508 | Subset of the 1,862; not extra unique records |

[Filtered SQLite database](20261002-v3/filtered_labour_records.sqlite) · [Exact quality report and exclusion reasons](20261002-v3/quality_report.json).

**Filtered does not mean independently verified or ready for a reliable forecast.** These are conservative, rule-filtered records for normalisation and contextual features. Courses remain catalogue candidates, not confirmed available training seats. Qualification dates are the publisher's listed dates, not independent proof of current approval. Education/training totals are flows, not available job seekers. NCS live postings and verified skill-specific available workforce are still missing.

No records were deleted. Excluded rows remain in `*_quarantine.csv`, with the reason attached. A quarantine decision can mean missing metadata, possible test content or outside the provider-label allowlist; it does **not** establish that every excluded course is fake. No missing value was replaced with an invented zero, and the 33 fully specified PLFS observations were not padded to 100.
