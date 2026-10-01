# Closing the live-demand, workforce and history gaps

Research/acquisition date: 1 October 2026. This update is additive. The earlier model-input run is an immutable snapshot and is not silently upgraded by these new sources.

## Results, and what remains missing

| Requested evidence | Acquired now | Remaining limit |
|---|---|---|
| Live NCS postings | None | NCS browser-domain access was previously declined; no approved vacancy export/API credentials supplied. No access controls bypassed. |
| Legitimate live-demand alternative | One Pune Senior Data Analyst posting from Parallel Wireless's public employer feed; 773 postings scanned across three boards | Not NCS; tiny nonrepresentative employer sample; unknown vacancy count; reuse terms need review |
| Available-workforce estimates | 180 official PLFS rate observations and 60 derived all-occupation unemployment/population baselines | No absolute Pune Data Analyst or Python/SQL-skilled availability estimate; no suitable current population denominator or skill evidence |
| Historical demand | 12 Maharashtra financial-year vacancy aggregates, normalized from existing NCS evidence, including one partial year | Not monthly Pune occupation history; insufficient for the requested forecast |
| Historical labour context | Maharashtra annual/quarterly and All India monthly PLFS rates | Workforce indicators are not employer demand; redesign/overlapping periods require separate series |

## Public statistical API that actually worked

MoSPI endpoint discovery follows the [NSO client documentation](https://github.com/nso-india/mospi-esankhyiki). Anonymous HTTPS GETs returned data from:

- `https://api.mospi.gov.in/api/plfs/getIndicatorListByFrequency?frequency_code=1`
- `https://api.mospi.gov.in/api/plfs/getFilterByIndicatorId?indicator_code=1&frequency_code=1`
- `https://api.mospi.gov.in/api/plfs/getData` with codes discovered from metadata.

Important: this API identifies Maharashtra as **16**, not Census state code 27. Do not reuse geography codes across publishers. The server caps pages at 200. The collector rejects incomplete pagination rather than accepting partial results.

The Python client's default HTTPS connection failed on legacy TLS negotiation. Windows' native HTTPS transport worked with certificate verification intact. We did not copy the external client's certificate-validation-disabling settings. This collector is consequently Windows-specific; the offline data tables remain portable.

Acquired slice: urban, persons, age 15+, LFPR/WPR/UR. Annual filters additionally select usual status PS+SS and all education/religion/social groups. Null quarterly/monthly dimensions remain unspecified, not fabricated values.

| Series | Observations | Coverage |
|---|---:|---|
| Maharashtra annual agriculture-year | 21 | 2017-18 through 2023-24 |
| Maharashtra annual calendar-year | 12 | 2022 through 2025 |
| Maharashtra quarterly | 96 | Apr-Jun 2018 through Apr-Jun 2026; check period coverage rather than assuming continuity |
| All India monthly | 51 | Apr 2025 through Aug 2026 |

Annual/calendar periods overlap. The 2025 survey redesign means these must not be concatenated as one homogeneous training series. Quarterly/monthly indicators must not be substituted for annual PS+SS rates without checking definitions.

Files: `data/processed/public_labour/public-labour-20261001-v2/`:

- `plfs_workforce_rates.csv`: 180 original API observations normalized with dimensions and provenance.
- `workforce_baseline_estimates.csv`: 60 matched LFPR/UR groups. Formula: `unemployed persons per 100 matching-age population = LFPR × UR / 100`. This is a point-derived baseline, **not 60 estimates of Data Analyst supply**. No uncertainty interval or absolute person count is supplied. Published WPR and rounding residual are retained for checking.
- `ncs_maharashtra_vacancy_history_context.csv`: 12 publisher financial-year aggregates. The 2026-2027 column is partial (publisher snapshot updated 15 July 2026); every row is excluded from Pune/Data Analyst forecasting.
- `acquisition_evidence.json`: 18 downloaded JSON response records, source URLs/times, hashes and preservation evidence for 88 pre-existing files.
- `output_hashes.json`: output integrity checks.

Raw JSON is local at `data/raw/public_labour/public-labour-20261001-v2/`, not committed to Git. The first attempt (`v1`) stopped when a request exceeded the server page cap; its two metadata responses are retained, not counted as the successful 18-response run. Empty failed-run output directory is also retained. An account/API key was not needed for these aggregate endpoints; that does not imply all MoSPI data is anonymous.

## Employer-published feed alternative

[Greenhouse's Job Board API](https://docs.greenhouse.io/job-board.html) documents public GET endpoints. [Lever's postings API](https://github.com/lever/postings-api) documents employer-published feeds. These are independent employer sources, not proxies for restricted NCS access.

We checked Capco (701 postings), Modulr (24) and Parallel Wireless (48). At collection time, only Parallel Wireless had a Data Analyst-title record with Pune in the location field. Old search-index hits were not accepted as live vacancies.

Observed posting: [Senior Data Analyst, Network Analytics & AI](https://jobs.lever.co/parallelwireless/7b25ec1c-4887-488c-a1f1-83daaa8dc659). API `createdAt` gives 24 September 2026; this is not independently verified first-publication time. Observed 1 October 2026. Rule-based description matches: Python, SQL, pandas, NumPy, Statistics.

Files: `data/processed/live_employers/employer-snapshot-20261001-v1/`. Metadata, minimal skill mentions, collection counts and checksums are saved. Full employer descriptions, applicant forms and contact data are not persisted. The full feed checksum records the response checked, not a replayable full-feed archive. Metadata rows stay excluded from verified-market-demand calculations pending source-rights, date-semantics and coverage review. Public API access is not an unrestricted content licence.

Repeatable collection exists, but **no recurring job has been scheduled**. A single observation cannot backfill historical hiring or prove that a listing will still be open tomorrow. Later disappearance must mean "not observed on that board", not "hired/filled".

## Legitimate route to the remaining workforce evidence

The [MoSPI microdata client](https://github.com/nso-india/mospi-unitdata) documents an actual API-key route: create/sign into a [microdata portal](https://microdata.gov.in/) account, verify email, then generate an API key in the profile. No key has been obtained or used. Do not send keys in chat or commit them.

Before producing a Pune occupation-specific estimate, acquire the relevant PLFS person/household layouts and microdata under their terms; confirm survey district codes, occupation codes, weights, strata/PSUs and employment statuses. Build a documented occupation-to-role crosswalk and check effective cell size and uncertainty. A broad NCO occupation is not proof of Python/SQL/Power BI competence. If the Pune cell is too small, publish a wider-geography estimate or suppress it. Skills and availability need anonymized aggregate candidate/training/employer evidence in addition to broad occupation counts.

No reliable arbitrary shortcut is supported: `Pune population × Maharashtra unemployment rate × guessed Data Analyst share` would manufacture a workforce number.

## NCS next requirement

Use the existing `docs/NCS_ACCESS_REQUEST.md` with the SIH problem owner/DGE to request an anonymized read-only vacancy export/feed with stable job IDs, occupation/location, creation/publication/expiry dates, vacancy counts, skill text, historic records/deltas, completeness and reuse terms. Ordinary account access and approved bulk API access are different. Domain permission in this app is also a separate issue. Neither SIH participation nor a public webpage alone grants API credentials or reuse rights.

No request has been sent externally on your behalf. No proxy, credential reuse, captcha or encrypted-payload bypass was attempted. Pune Data Analyst gap/forecast/severity remains blocked until comparable evidence is acquired.

## Reproduce and validate

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe -m src.verify_public_labour
.venv/Scripts/python.exe -m src.public_labour --run-id NEW_UNIQUE_ID
.venv/Scripts/python.exe -m src.live_employers --run-id ANOTHER_UNIQUE_ID
```

Collectors reject existing run directories. See `config/public_access_sources.json` for five supplemental source/access entries; the original source register and all previous data packs remain preserved.
