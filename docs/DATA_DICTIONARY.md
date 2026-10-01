# Data dictionary and join boundaries

## NCS aggregates

`ncs_state_year_metrics.csv`: one metric/state/year per row. Exact publisher labels: Jobseeker Registered, Active Jobseekers, Vacancies, Active Employer. `value` is the published count. `publisher_updated_at`, `source_url`, `access_method`, `quality_flag` preserve provenance. `ncs_reported_totals.csv` holds separate row totals, not extra annual observations. Some metrics include unspecified-state rows; retain these for reconciliation. Stock/flow metric definitions need confirmation. Maharashtra has 48 records (four by twelve), no Pune skill/salary/posting detail.

## PMKVY

Fields: `state`, `district`, `financial_year`, `trained`, `page`, `source_url`. FY 2021-22 flow, not current stock/certification/placements. Pune 4206. Parser requires all 36 Maharashtra rows. Original PDF retained.

## Town geography

Fields: `state_code`, `state`, `district_code`, `district`, `subdistrict_code`, `subdistrict`, `town_code`, `town`, `households`, `population`, `male_population`, `female_population`. First twelve columns of Census sheet `Town_2700`. Census-era codes, not current LGD. Historical population, not 2026 denominator. Town directory is not full rural-village coverage.

## Metadata and fallback

NCS metadata fields: `section`, `field`, `value`; 54 nonempty rows. Coverage descriptions do not mean described record-level data were acquired.

Kaggle original 32-column schema: `data/manifests/kaggle_quality.json`. Main fields: job ID/title/company/location/skills/description, experience bounds, salary LPA bounds/disclosure, job URL, source, scraped_at, primary_city. Added fields: `source_tier=3`, `date_quality_flag`, `description_truncated`, `salary_quality_flag`. Pune matching searches location or primary_city; 5327 matches are not verified unique Pune vacancies. Deduplicate nonempty URLs; preserve multi-city status. Undisclosed zero salary is missing. Inconsistent dates prohibit current trends/forecasts.

## Scalable separation

Keep demand postings, aggregate demand observations, training flows, education flows and survey estimates in separate tables. Future canonical keys must retain source ID/native ID, period, geography code system, unit, retrieval/publisher timestamps and quality flags. Skill mappings retain QP/NOS/occupation IDs, version and reviewed provenance. No apparent gap from joining unrelated counts.
