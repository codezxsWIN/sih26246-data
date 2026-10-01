# Counted labour-market records — 2 October 2026

[Open all nine readable CSV tables and their row counts](../README.md). This snapshot contains **24,398 rows** and a [queryable SQLite database](labour_records.sqlite). The [manifest](manifest.json) lists every column, row count, record grain, source and usage caveat. SQL columns retain publisher values as TEXT, with blank cells stored as NULL; convert numerical fields explicitly in the normalisation layer before modelling.

## Where the records came from

| Category | Acquisition and coverage | Important limit |
|---|---|---|
| Skill India | Anonymous paginated [public course API](https://courses.skillindiadigital.gov.in/api/courses/v1/courses/?page_size=100), 20 responses, 1,916 unique IDs | Advertised count changed from 1,921 to 1,916 during collection. [Pagination evidence](skillindia_pagination_evidence.json) retained. This is not proven point-in-time completeness. Test/demo names are flagged; dates, certification, seats and provider authenticity need review. |
| NSDC-linked occupational standards | NCVET [National Qualification Register](https://nqr.gov.in/qualifications-search), normal anonymous summary-download form, 2,814 exported rows | NQR is the actual publisher, not NSDC. Expired and undated qualifications remain labelled. No verified district training capacity. |
| AISHE | [Official final reports](https://aishe.gov.in/document-category/aishe-final-reports/), Table 33, academic years 2022-23 and 2023-24 | 37 geography rows × 9 level/total categories × 2 years = 666 legitimate aggregate observations. National totals and Grand Total are explicitly labelled and must not be summed with their components. Blanks remain missing. State-level pass-outs are not available skilled candidates. |
| Government training / data.gov.in alternative | Official [MSDE PMKVY parliamentary annexure](https://www.msde.gov.in/static/uploads/2024/05/Annexure-2.pdf), 725 district records, FY 2021-22 | The attempted [OGD JSS resource](https://www.data.gov.in/resource/district-wise-enrolled-and-assessed-jan-shikshan-sansthan-jss-27-april-2022) CSV returned HTTP 403. No access controls were bypassed. The delivered table is from MSDE, not an OGD API. Published dashes remain missing; numerical district totals reconcile to 615,080 trained. |
| MoSPI / PLFS | Previously acquired [official PLFS API](https://api.mospi.gov.in/api/plfs/getData), 180 observations; Maharashtra annual/quarterly and India monthly series | Retain survey dimensions and missing metadata. The 2025 redesign affects comparisons. These are general labour rates, not Data Analyst supply. |
| NCS | Previously downloaded [official dashboard](https://ncs.gov.in/NCSReportDashboard), 1,788 state/year/metric observations | Historical aggregate context only; no live individual NCS posting feed or candidate profiles acquired. The 2026-27 column is partial. |
| Maharashtra / national training providers | Existing official DVET institute references and DGT grading extracts, unchanged | Provider lists/ratings are not available seats or verified placement outcomes. |
| Kaggle | [rafunlearnhub recruitment dataset](https://www.kaggle.com/datasets/rafunlearnhub/recruitment-data), 614 examples, uploader lists CC0 | Gender excluded. Source provenance unverified; no city or observation date. Salary-unit label preserved, not assumed correct. Use only for prototype ingestion/classification. |

AISHE PDFs used:

- [2023-24 report](https://cdnbbsr.s3waas.gov.in/s392049debbe566ca5782a3045cf300a3c/uploads/2026/07/202607131602421770.pdf), physical pages 188–190.
- [2022-23 report](https://cdnbbsr.s3waas.gov.in/s392049debbe566ca5782a3045cf300a3c/uploads/2026/07/20260708401535366.pdf), physical pages 181–183.

Attribution is retained. Public access is not the same as an unrestricted reuse licence: no explicit bulk-reuse licence was verified for NQR or the Skill India catalogue. Confirm publisher terms for external redistribution or commercial deployment. No names, contact details, government IDs or resume texts from recruitment datasets are included in this pack.

The separate 23,201-row Kaggle India tech-posting download remains in the existing local raw/prototype pack; it has date/rights limitations and is **not counted again** here. Its descriptions were not copied into this public-record pack.

## Follow the project workflow

Labour market data → aggregation and normalisation → demand + supply engine → gap → 6–12 month forecast → severity → planner dashboard → training/capacity recommendations.

These files expand the **data and normalisation inputs**. They do not justify presenting a trained-person total as current available workforce, a recruitment classification example as a live vacancy, or an invented gap/forecast as evidence.

1. Load tables separately by their stated grain. Preserve source IDs, geography, period, units and quality flags.
2. Keep observed job postings separate from NCS registration/vacancy aggregates; keep educational/training flows separate from available workforce stocks.
3. Map occupations/skills to appropriate NQR versions after validity review. Review course/provider/availability evidence before recommending training.
4. Estimate supply only with explicit assumptions and uncertainty. Match demand and supply on role, location, period and unit before any gap.
5. Enable forecasts only after acquiring comparable history and evaluating held-out periods. These records alone do not establish forecast confidence.

## Reproduction and checks

New collector: `python -m src.collect_100plus_records --run NEW_UNIQUE_RUN --sources aishe_2023_24 aishe_2022_23 skillindia nqr`. OGD access can fail and should not be assumed available without a legitimate download/API key route.

Builder: `python -m src.build_100plus_pack --snapshot NEW_UNIQUE_SNAPSHOT --kaggle-archive PATH_TO_LOCAL_RAFUNLEARNHUB_ZIP`. The current builder uses the saved official acquisition run `20261002-v1`; acquisition files remain local under `data/raw/records_100plus/`. Original PLFS/NCS/DVET/DGT extracts are dependencies. A fresh clone therefore needs source acquisition before rebuilding, but the delivered CSVs/SQLite are ready to read.

Every output is created exclusively; existing snapshots are never overwritten. The builder checks unique course IDs, NQR export serials, AISHE male/female totals and all state-to-national subtotals, the PMKVY district grain and national sum, SQLite row counts and database integrity. A failed check stops completion rather than quietly inventing or dropping values.
