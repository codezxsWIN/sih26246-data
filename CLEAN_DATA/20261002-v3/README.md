# Filtered labour inputs — rules version 1

[Open tables and exact counts](../README.md). [Review the machine-readable audit](quality_report.json). Original data, previous databases and local extraction attempts were preserved.

## What changed

- **Courses:** 265 bulk records matched conservative suspected test/demo heuristics, including concatenated `Democourse` and underscore-delimited test names. Placeholder/navigation names, future or uninterpretable start dates, and providers outside a documented label allowlist were excluded from the working table. Exclusion reasons overlap. 664 catalogue candidates remain; this is not provider identity verification, verified certification or current seat availability.
- **Qualifications:** 949 expired records and rows missing essential qualification metadata were excluded; overlapping rules produce 952 exclusions. 1,862 records remain within the publisher's listed validity and with essential fields present. The 508-role MVP subset covers IT-ITeS, Automotive and Electronics & HW.
- **AISHE:** national totals and Grand Total rows were removed from the working table to prevent accidental double-counting. Records without a reported pass-out total were excluded. 507 state/UT/level/year observations remain. Missing male/female cells stay NULL rather than being invented as zero.
- **PMKVY:** 15 publisher dash/missing values were excluded from numerical working inputs. The 710 retained observations still sum to the reported national training total of **615,080**. Trained does not mean currently available or employed.
- **PLFS:** 147 observations with unspecified year-type or survey-reference metadata were separated; 33 fully specified rate observations remain. Further alignment on year, geography, frequency and the 2025 methodology break is still required.
- **Kaggle:** the recruitment demo is excluded entirely from this current-labour working database. It remains labelled in the bulk pack for pipeline experiments only.

The provider-label allowlist is a reproducible conservative selection rule, not a verified accreditation list. Legitimate excluded courses can be reinstated after review. A testing-related occupational title such as `Software Vulnerability/Penetration Tester` is not automatically treated as a test placeholder.

## Inspect excluded records

[Course exclusions](course_catalogue_candidates_quarantine.csv) · [Qualification exclusions](valid_qualifications_quarantine.csv) · [Education exclusions](education_passout_observations_quarantine.csv) · [Training exclusions](district_training_observations_quarantine.csv) · [PLFS exclusions](fully_specified_workforce_rates_quarantine.csv).

Exclusions preserve the original row and append `excluded_reason`. Nothing is deleted from the original source pack. Exclusion counts are not unique-person counts.

## Use safely in the project

Load [filtered_labour_records.sqlite](filtered_labour_records.sqlite) or the CSVs into the **aggregation and normalisation** stage. In SQLite, reported person/training counts and page numbers are INTEGER, PLFS values are REAL, and missing cells are NULL. Qualification levels and parsed hours are numeric, dates use ISO format, and placeholder version labels become NULL. Original labels are retained beside parsed values; codes remain TEXT. Optional certifying-body contact/address text is omitted. CSV has no enforced types; use the same explicit conversion rules as the supplied cleaner.

Keep demand, workforce rates, education flows, training flows, qualifications and course candidates separate. Do not add their counts together as workforce supply. Do not enable shortage/forecast outputs solely because these tables are bigger or cleaner. Follow the required workflow, but withhold gap/forecast/severity claims until comparable evidence and validation exist.

Source links, coverage and licence/reuse limitations are retained in the [bulk pack documentation](../../DATA_100PLUS/20261002-v6/README.md). In particular, public catalogue access does not establish an unrestricted reuse licence for Skill India or NQR.

Reproduce from the existing bulk snapshot with `python -m src.clean_100plus_pack --snapshot NEW_UNIQUE_SNAPSHOT`. Existing snapshot folders are never overwritten. Automated checks cover row accounting, SQLite integrity, typed numeric storage, course-placeholder edge cases and expired-standard exclusion.
