# India's NCS: verified access findings

Research date: 2026-10-01. Website: https://ncs.gov.in/. API host observed in public site configuration: https://api.ncs.gov.in/.

## Endpoint evidence

| Endpoint | Method | Observed result | Use |
|---|---|---|---|
| `/api/location/state` | GET | HTTP 200, JSON, no login supplied | State names and state codes |
| `/employer-service/api/functional-areas-master/fetch-all-functional-area` | GET | JSON HTTP 200 embedded in public search-page state; direct Python attempt hit a local trust-store problem | Functional-area IDs and names |
| `/employer-service/api/v1/hiring/top-companies?year=2026&limit=4` | GET | Direct HTTP 200, JSON, no login supplied | Company name, employer ID when populated, total vacancies and job-post counts |
| `/api/v1/job-posts/filter-options` | GET | Public page state contains HTTP 200 but encoded response text | Search-filter options; not saved as usable JSON |
| `/api/v1/job-posts/search?page=0&size=20` | POST | Direct request returned HTTP 400: `Invalid or unencrypted request payload` | Individual vacancy search, currently unverified through normal browser flow |
| `/api/jobs/detail?id=<job-id>` | GET | Observed in public client service; not called | Job detail endpoint, response/auth requirements unverified |
| `/api/v1/jobs/keyword-search` | GET | Observed in client service; not called | Alternate keyword search, unverified |

These are website service endpoints, not a published, stable developer contract. Working reference endpoints do not prove that the vacancy feed is openly reusable or that bulk collection is approved.

Public search code shows request filters such as `keyword`, `cities`, `states`, `jobTitles`, `skills`, `functionalAreas`, `functionalRoles`, `industries`, `educationTypes`, salary/experience limits and `sortBy`. Request pagination uses `page` and `size`. Responses are expected by the website as `data.content`; the actual live vacancy response was not obtained. Field names are client observations, not a response schema guaranteed by NCS.

## Access route for individual live vacancies

1. Enable the NCS browser domain permission that was denied in this session.
2. Use the ordinary public search page with Pune/Maharashtra filters; verify that the current website displays results.
3. For reliable recurring ingestion, ask NCS/DGE or the SIH problem owner for an approved read-only vacancy feed or anonymized export, credentials, documentation and reuse terms.
4. Test one page for stable IDs, posting/expiry dates, location, vacancy counts and skills before collecting more pages.
5. Keep snapshots and source timestamps. Ask whether closed/expired postings and historical deltas are provided.

No publicly documented, self-service Indian NCS API-key signup was established. Historical official ministry procurement documents describe integrations with states and partner institutions, but the indexed PDF links tested here returned 404. The previously linked UK API portal is not a route to Indian data.

## Official data collected without a live vacancy feed

The saved public dashboard page and its already downloaded client bundle contain four tables: Jobseeker Registered, Active Jobseekers, Vacancies, Active Employer. The columns run from 2015-16 to a publisher-labelled `2026-2027`. The last column is partial because the dashboard says it was updated on 15 July 2026.

`src.extract_ncs` reads these literal data tables offline without evaluating JavaScript. It verifies the initially visible table against the saved HTML, exports all four tables, and checks row and national totals. The CSV preserves the publisher's metric/year labels. Confirm the precise cohort/flow definitions with DGE before comparing active and annual measures.

The public NCS metadata workbook describes live vacancy availability and identifies state, gender, age-group, education and sector disaggregation. It is a statistical metadata document, not a dataset of individual records. It lists collection via registration and integrations, with daily, weekly and monthly collection depending on the channel.

Sources: [NCS dashboard](https://ncs.gov.in/NCSReportDashboard), [public job search](https://ncs.gov.in/job-listing), [NCS public resources](https://ncs.gov.in/), [official historical integration document indexed by search](https://labour.gov.in/sites/default/files/final_rfp_27.08.2024.pdf).
