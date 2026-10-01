# Acquired sources beyond NCS

Expansion collected 1 October 2026. The expanded 37-source register records exact URLs, fields, vintages, geography, licence notes, update cadence, quality and modules. NCS live-vacancy access remains outstanding.

| Source | Delivered | Use |
|---|---|---|
| Maharashtra DVET reference service | 952 institute references, 95 trades; 61 Pune institutes, 13 talukas, 405 institute-trade links | Training-provider and trade discovery |
| DGT official ITI grading 2026-27 | 14743 national rows; 1046 Maharashtra-code rows | Institution grading context, not learner supply |
| PIB/MSDE apprenticeship table | 36 states/UTs plus national total, calendar2025 | NAPS/NATS training-engagement baseline |
| MoSPI PLFS calendar2025 | Annual report and methodology-change document | More recent state labour baseline |
| MoSPI NIC-2008 | Official classification PDF | Industry codes used by acquired surveys |
| UDISE+ public mirror | Two Pune 2025-26 enrolment files: 52993 and 56536 item records,42 columns each; schema | Future education pipeline, not available skilled workers |

## Verified public APIs

DVET base: `https://inventory.dvet.gov.in`. Ordinary website anonymous JSON GET routes:

```text
/Home/GetDistrictByRegion?regionId=6
/Home/GetTalukaByDistrict?districtId=521
/Home/GetInstituteByLocation?regionId=6&districtId=521
/Home/GetTradeByInstitute?instituteId=<DVET-ID>
```

All61 Pune institute trade calls succeeded. `DataValueField`/`DataTextField` provide IDs/names; placeholders excluded. These are website-internal references, not a guaranteed stable developer contract. DVET IDs are not interchangeable with NCVT/MIS codes. Do not join grading and provider files on name alone.

Capacity-search POST `/Home/LoadAdmissionTradeInstituteSearchList` returned HTTP200 with zero results for the sample. This does not prove zero intake. No capacity observations claimed. Page banner says2022 while site constants say2026; references have no effective year. Preserve collection date separately from academic vintage.

OpenCity CKAN `https://data.opencity.in/api/3/action/package_search?q=Pune&rows=10` returned JSON. Selected UDISE files are mirrors, not independently verified primary downloads. Catalogue lists Other (Public Domain); attribute UDISE+ and OpenCity, and confirm primary reuse terms.

## Quality and interpretation

- DGT: all serials1-14743 present; zero duplicate codes; eight numeric parameters sum to final grade.126 `NG` final grades are not zero. CFI and a publisher-spaced code are preserved. Maharashtra uses embedded code27; current grading file has no district names.
- Apprenticeship: calendar2025, published23March2026. Maharashtra NAPS303763, NATS114127. National total is separate: do not sum it with states. Engagements are not vacancies, placements or current worker stock.
- PLFS2025: calendar-year coverage and changed sample design. Read methodology before comparing with July2023-June2024. No person microdata acquired; catalogue host connection failed.
- UDISE: pseudocode/item_group/item_id plus preprimary/classes1-12 boys/girls/total columns. Multiple item rows per school expected. Do not add parts1/2, item groups, or component counts and totals together. No named pupil/teacher records collected.
- DVET historical PDFs: directory2022 actually contains provisional August2023 admissions. Staff contact details occur in originals, so those two PDFs stay local-only, excluded from ZIP and Git. No contact fields included in organizational extracts.

## Checked but not acquired

Maharashtra DES lists Pune's2025 district review, but certificate hostname verification failed; no TLS bypass. MahaSwayam and Skill India Digital homepages are accessible, but no bulk live dataset/API contract verified. No NCS-integrated route used to work around denied NCS permission. A reachable homepage is not a downloaded dataset.

## Reproduce

With expanded raw pack and repository requirements installed:

```powershell
.venv/Scripts/python.exe -m src.extract_extra
.venv/Scripts/python.exe -m src.verify_pack
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Refresh public organizational references only:

```powershell
.venv/Scripts/python.exe -m src.collect_dvet --pune-trades
```

Requests are spaced one second apart; failures recorded, no personal profiles collected. Publisher refreshes may change counts. Review new counts and provenance rather than weakening checks.
