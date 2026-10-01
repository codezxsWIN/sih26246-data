# Data Analyst model-input pack — 1 October 2026

This is an additive integration-ready snapshot, not a trained model or a defensible labour forecast. The original collection is preserved. Run `analyst-readiness-20261001-v1` contains standardized tables, identifiers, evidence, import contracts and checksums for the updated SIH26246 flow.

## Your updated workflow

| Stage | Input/output contract | Current readiness |
|---|---|---|
| Labour market data | Original downloads, source registry and collection logs | 28 successful raw downloads; 37 registered sources, not 37 downloaded datasets |
| Aggregation & normalisation | Jobs, contextual observations, deduplication audit, binary skill features | Ready for the prototype slice; original files unchanged |
| Demand + supply engine | Approved job observations and comparable available-workforce estimates | Prototype jobs available; verified jobs and available workforce missing |
| Demand–supply gap | Same occupation, geography, reference period and compatible units | Blocked; training completions are not available workforce |
| 6–12 month forecast | Repeated demand/supply history, coverage definitions, backtesting | Blocked; one inconsistent-date posting snapshot is not a time series |
| Shortage/surplus severity | Validated gap, uncertainty and planner-agreed thresholds | `not_assessed`; no fabricated classification |
| Planner dashboard | `planner_outputs.csv`, readiness and provenance | Data contract ready; dashboard itself not implemented here |
| Training/capacity recommendations | Validated shortage, skill requirements, course fit and verified capacity | Numeric recommendation withheld; institute/trade links identify candidate providers only |

## Files to load

Public/repository-safe snapshot: `data/model_input/runs/analyst-readiness-20261001-v1/`.

- `production_jobs.csv`: canonical job schema, currently **0 verified observations**. A header-only file is intentional, not a download error.
- `job_import_template.csv`: exact allowed fields for future authorized live job observations. Personal/contact columns are rejected. Text must also be reviewed for personal information before import.
- `context_observations.csv`: **86** observations: 48 NCS Maharashtra state/year metrics, 36 PMKVY district training counts and 2 Maharashtra apprenticeship engagement counts. These are all-role contextual indicators, not Data Analyst supply.
- `dvet_pune_institute_trade_links.csv`: **405** institute/trade relationships. Does not establish filled seats, available graduates or course capacity.
- `dgt_maharashtra_iti_grading_2026_27.csv`: **1,046** Maharashtra institution grading records; grading is not capacity.
- `available_supply_import_template.csv`: workforce estimates with occupation, skill, geography, period, uncertainty, method and supporting evidence. Header only; supply estimation is not implemented.
- `demand_history_import_template.csv`: monthly observations with measure/unit, coverage and completeness. Header only; temporal aggregation and forecasting are not implemented.
- `planner_outputs.csv`: Pune/Data Analyst output contract. Missing numeric values are blank, severity is `not_assessed`.
- `readiness.json`, `input_preservation.json`, `output_hashes.json`: readiness flags and SHA-256 evidence.

Local-only fallback snapshot: `data/model_input/local_prototype/analyst-readiness-20261001-v1/`. It is excluded from Git, but included in the private local ZIP for development, subject to upstream usage rights.

- `jobs.csv`: **165 unique** Data Analyst-title postings mentioning Pune, selected from 248 matching rows. **83 duplicate links** retained for audit. Multi-location postings may be present. Selection uses the title, not the uploader's role category; adjacent analyst titles require separate review.
- `skill_features.csv`: one record per job, 15 binary skill columns, joined by `record_id`.
- `skill_evidence.csv`: **198** skill matches with exact text offsets in `skills_raw`.
- `skill_posting_counts.csv`: prototype posting counts, explicitly not current demand and not proof of fast-growing skills.
- `duplicate_links.csv`, `output_hashes.json`: deduplication evidence and file integrity.

Example prototype counts: SQL 53, Power BI 48, Python 33. These are dictionary matches within this small fallback sample, not market totals. The skill extractor is rule-based, not an AI model. Description-based extraction and supervised occupation mapping are later work. The alias dictionary is a reviewed-bootstrap starting point, not an official NOS-to-occupation crosswalk.

## Can the future model use this directly?

Yes for integration tests, joins, skill-feature experiments and dashboard wiring. No for verified current demand, available workforce, gap, growing-skill trends, forecasts or decision-grade recommendations. The Kaggle source has conflicting date information; `posted_date` stays blank. `observed_at` is our retrieval date, not the posting date. Job counts do not automatically equal vacancies. Undisclosed salary is blank, not zero.

CSV fields must be parsed according to the contract: dates as ISO dates, numeric columns as nullable numbers, eligibility flags explicitly as booleans. Do not fill unknown values with zero or let strings such as `"false"` be interpreted as truthy. `record_id` is the join key; evidence offsets refer to unmodified source field text.

Demand–supply comparisons require a common definition. Vacancies are often a flow while available workers are a stock; define a common reference window and uncertainty before subtraction. Do not sum incompatible NCS metrics, repeated job snapshots or overlapping skill populations. PLFS/AISHE reports provide baselines/proxies, not a direct Pune Python/SQL workforce inventory.

## Safe next acquisition/import

1. Obtain an authorized NCS job export/API agreement and documented fields, timestamps, coverage and vacancy semantics. SIH participation does not itself provide credentials or access rights. No login/captcha/encryption bypass is included.
2. Review source permissions and add an entry to `config/approved_job_sources.json` with reviewer, review date, evidence reference and scope `job_data_analysis`.
3. Populate `job_import_template.csv` into a separate file. Required source and job identifiers, title, description, location, posting and observation dates must be supplied. Tier 3, inconsistent dates, unconfirmed permissions, non-target roles and unapproved sources are rejected.
4. Build a **new** run ID; never reuse the existing one. Even accepted jobs require review of availability, geographic specificity and market coverage before any current-demand calculation.
5. Collect repeated snapshots with stable IDs and a documented coverage window. Acquire and review comparable workforce estimates separately. Forecast confidence needs out-of-sample evaluation, not a manually assigned percentage.

## Build and validate

From the repository root, using the repository Python environment:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe -m src.validate_model_pack --run-id analyst-readiness-20261001-v1
.venv/Scripts/python.exe -m src.model_pack --run-id NEW_UNIQUE_RUN_ID --job-import PATH_TO_AUTHORIZED_CSV
```

Omit `--job-import` to build another prototype-only snapshot. The builder refuses existing output directories and verifies existing data hashes. Validation checks output and original-file hashes, job/feature joins, prototype isolation, evidence spans, counts and absence of unsupported planner numbers. It does not prove labour-market representativeness or licensing rights.

All **29 tests passed** for this release. Snapshot validation verified 19 output files and 65 original data files. Original ZIPs are retained. Historical DVET PDFs containing staff contact details remain local and are excluded from distribution as documented in `data/manifests/distribution_policy.json`.

For source-by-source access, date coverage and limitations, see `config/sources.json`, `docs/ACQUISITION.md`, `docs/ADDITIONAL_SOURCES.md`, `docs/NCS_ACCESS.md` and `docs/DATA_LICENSES.md`.
