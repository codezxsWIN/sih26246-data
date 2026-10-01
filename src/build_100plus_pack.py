"""Build an additive, counted public-record snapshot; no candidate identities.

AISHE record grain is year/state/education level, not an individual graduate.
PDF columns retain missing cells rather than converting blanks to zero.
All deliverables are exclusive new files and acquisition evidence is retained.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import openpyxl
from pypdf import PdfReader
from .acquire import ROOT

RAW = ROOT / 'data/raw/records_100plus/20261002-v1'
OUT = ROOT / 'DATA_100PLUS/20261002-v1'
TODAY = date(2026, 10, 2)
TABLES = []


def json_new(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def emit(name, rows, source, grain, use, constraints, **extra):
    # Preserve raw publisher downloads separately; deliver single-line cells.
    rows = [{k: ' '.join(v.split()) if isinstance(v, str) else v for k, v in r.items()} for r in rows]
    if len(rows) < 100:
        raise ValueError(f'{name}: fewer than 100 records: {len(rows)}')
    fields = list(rows[0])
    path = OUT / (name + '.csv')
    with path.open('x', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    TABLES.append({'table': name, 'file': path.name, 'rows': len(rows), 'fields': fields,
                   'source_url': source, 'record_grain': grain, 'module': use,
                   'usage_constraints': constraints, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                   **extra})
    print(name, len(rows), flush=True)


def aishe():
    rows = []
    group_names = [['Ph.D.', 'M.Phil.', 'Post Graduate'],
                   ['Under Graduate', 'PG Diploma', 'Diploma'],
                   ['Certificate', 'Integrated', 'Grand Total']]
    for year, first in [('2022-23', 180), ('2023-24', 187)]:
        reader = PdfReader(RAW / ('aishe_' + year.replace('-', '_') + '.pdf'))
        url = 'https://aishe.gov.in/document-category/aishe-final-reports/'
        state_names = {}
        for offset, levels in enumerate(group_names):
            lines = reader.pages[first + offset].extract_text(extraction_mode='layout').splitlines()
            header = next(line for line in lines if len(re.findall(r'\bMale\b', line)) == 3)
            spans = list(re.finditer(r'\b(?:Male|Female|Total)\b', header))
            centers = [(m.start() + m.end()) / 2 for m in spans]
            # In the 2023-24 PDF, right-aligned figures sit about eight layout
            # characters to the right of the centered labels. Reconcile every
            # sex total and national total below to detect any misassignment.
            if year == '2023-24':
                centers = [c + 8 for c in centers]
            bounds = [int(centers[0] - (centers[1] - centers[0]) / 2)]
            if year == '2023-24':
                bounds[0] -= 8  # Long national totals begin left of the centered label.
            bounds += [int((a + b) / 2) for a, b in zip(centers, centers[1:])]
            bounds.append(len(header) + 100)
            blocks = []
            for line in lines:
                label = line[:bounds[0]].strip()
                match = re.match(r'^(\d+)\s+(.+)$', label)
                is_total = label == 'All India'
                if (match and re.search('[A-Za-z]', match[2])) or is_total:
                    cells = [line[bounds[i]:bounds[i + 1]].strip() for i in range(9)]
                    if any(c and not re.fullmatch(r'[\d,]+', c) for c in cells):
                        raise ValueError(f'AISHE column alignment failed: {year} {label} {cells}')
                    blocks.append({'serial': int(match[1]) if match else 0,
                                   'state': match[2] if match else 'All India',
                                   'values': [int(c.replace(',', '')) if c else None for c in cells]})
                elif blocks and label and not any(line[bounds[i]:bounds[i + 1]].strip() for i in range(9)):
                    if label in ('Kashmir', 'Daman & Diu', 'Daman and Diu'):
                        blocks[-1]['state'] += ' ' + label
            if len(blocks) != 37 or {b['serial'] for b in blocks} != set(range(37)):
                raise ValueError(f'AISHE state row count unexpected: {year} {offset}: {len(blocks)}')
            for b in blocks:
                normalized = ' '.join(b['state'].split())
                if offset == 0:
                    state_names[b['serial']] = normalized
                elif normalized != state_names[b['serial']]:
                    raise ValueError(f'AISHE state identity changed: {normalized}')
                for k, level in enumerate(levels):
                    male, female, total = b['values'][k * 3:k * 3 + 3]
                    if all(v is not None for v in (male, female, total)) and male + female != total:
                        raise ValueError(f'AISHE sex totals mismatch: {year} {normalized} {level}')
                    rows.append({'academic_year': year, 'state_ut': normalized,
                                 'geography_level': 'country' if not b['serial'] else 'state_ut',
                                 'education_level': level, 'male_pass_out': male,
                                 'female_pass_out': female, 'total_pass_out': total,
                                 'unit': 'persons_reported_passed_out', 'table': '33',
                                 'pdf_page': first + offset + 1, 'source_url': url,
                                 'quality_flag': 'blank_cells_are_missing_not_zero;actual_response_not_available_workforce'})
            for k, level in enumerate(levels):
                for col in range(3):
                    national = blocks[-1]['values'][k * 3 + col]
                    subtotal = sum(b['values'][k * 3 + col] or 0 for b in blocks[:-1])
                    if national is not None and national != subtotal:
                        raise ValueError(f'AISHE national reconciliation failed: {year} {level} {col}')
    emit('aishe_state_level_passouts', rows, url, 'academic_year × state/UT × education_level (includes labelled national totals)',
         'education supply proxy', 'Official public report; retain attribution. Not licensed candidate profiles.',
         coverage='2022-23 and 2023-24', geography='36 states/UTs plus India; no district detail in Table 33')


def nqr():
    workbook = openpyxl.load_workbook(RAW / 'nqr_public_qualification_summary.xlsx', read_only=True, data_only=True)
    values = list(workbook.active.values)
    rows = []
    for raw in values[3:]:
        if raw[0] is None:
            continue
        valid = str(raw[10] or '').strip()
        try:
            end = datetime.strptime(valid, '%d %b %Y').date()
            status = 'expired_as_of_snapshot' if end < TODAY else 'within_listed_validity'
        except ValueError:
            status = 'validity_date_unparsed_or_missing'
        rows.append({'source_serial': raw[0], 'title': raw[1], 'qualification_code': raw[2],
                     'sector': raw[4], 'nsqf_level': raw[5], 'maximum_hours': raw[6],
                     'minimum_hours': raw[7], 'version': raw[8], 'originally_approved': raw[9],
                     'valid_till': raw[10], 'validity_status': status, 'status_as_of': TODAY.isoformat(),
                     'awarding_body': raw[11], 'proposed_occupation': raw[13],
                     'qualification_type': raw[15], 'adopted_qualification': raw[16],
                     'training_delivery_hours_json': raw[17], 'source_url': 'https://nqr.gov.in/qualifications-search',
                     'quality_flag': 'registered_qualification_not_training_capacity;check_latest_version_before_recommending'})
    if len(rows) != 2814 or len({r['source_serial'] for r in rows}) != len(rows):
        raise ValueError('NQR exported row count/serials changed')
    emit('nqr_qualifications', rows, 'https://nqr.gov.in/qualifications-search', 'one row per exported qualification',
         'occupation and qualification standardisation; training requirements',
         'Official NCVET register linked by NSDC; public download, no explicit open-data licence verified. Preserve attribution and verify bulk redistribution terms.',
         coverage='Public export collected 2026-10-02; includes historical/expired qualifications',
         geography='national standards; not district capacity')


def courses():
    rows, pages = [], []
    for path in sorted(RAW.glob('skillindia_courses_page_*.json')):
        payload = json.loads(path.read_text(encoding='utf-8'))
        pages.append({'file': path.name, 'publisher_count': payload['pagination']['count'],
                      'rows': len(payload['results']), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        for r in payload['results']:
            flags = ['live_catalogue_changed_during_pagination', 'seats_and_certification_not_verified']
            if re.search(r'\b(test|testing|demo|dummy|sample)\b', str(r.get('name', '')) + ' ' + str(r.get('org', '')), re.I):
                flags.append('test_or_demo_candidate')
            if not r.get('start_type'):
                flags.append('start_date_semantics_unspecified')
            rows.append({k: r.get(k) for k in ['id', 'name', 'org', 'number', 'pacing', 'start', 'start_type',
                         'end', 'enrollment_start', 'enrollment_end', 'effort', 'hidden', 'invitation_only']} |
                        {'source_url': 'https://courses.skillindiadigital.gov.in/api/courses/v1/courses/?page_size=100',
                         'quality_flag': ';'.join(flags), 'recommendation_status': 'requires_provider_and_availability_review'})
    if len(rows) != 1916 or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Skill India downloaded unique course count mismatch')
    json_new(OUT / 'skillindia_pagination_evidence.json', {
        'downloaded_unique_rows': len(rows), 'advertised_counts': sorted({p['publisher_count'] for p in pages}),
        'consistent_point_in_time_snapshot': False, 'pages': pages,
        'note': 'Publisher count changed from 1921 to 1916 during pagination. No records were fabricated or padded.'})
    emit('skillindia_courses', rows, rows[0]['source_url'], 'one unique public course ID',
         'training catalogue discovery, subject to quality and availability review',
         'Public catalogue/API. No explicit bulk-reuse licence verified; retain attribution and confirm terms before external redistribution.',
         coverage='Collected 2026-10-02; course start dates are not necessarily release dates',
         geography='provider catalogue; no reliable delivery district or available seats')


def pmkvy():
    states = ['Andaman And Nicobar Islands', 'Andaman & Nicobar Islands', 'Andhra Pradesh', 'Arunachal Pradesh',
              'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh', 'Dadra And Nagar Haveli And Daman And Diu',
              'Dadra and Nagar Haveli', 'Daman And Diu', 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh',
              'Jammu And Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Ladakh', 'Lakshadweep',
              'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha',
              'Puducherry', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
              'Uttar Pradesh', 'Uttarakhand', 'West Bengal']
    pattern = re.compile(r'^(' + '|'.join(re.escape(s) for s in sorted(states, key=len, reverse=True)) + r')\s+(.+?)\s+([\d,]+|-)\s*$', re.I)
    reader = PdfReader(ROOT / 'data/raw/training/pmkvy_district_trained_2021_22.pdf')
    rows, national, unmatched = [], None, []
    for page_no, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ''
        text = re.sub(r'Andaman And Nicobar\s*\nIslands', 'Andaman And Nicobar Islands', text)
        text = re.sub(r'Dadra And Nagar Haveli And\s*\nDaman And Diu', 'Dadra And Nagar Haveli And Daman And Diu', text)
        lines = [' '.join(line.split()) for line in text.splitlines() if line.strip()]
        merged = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.lower() in {s.lower() for s in states} and i + 1 < len(lines):
                line += ' ' + lines[i + 1]
                i += 1
                if not re.search(r'\s(?:[\d,]+|-)\s*$', line) and i + 1 < len(lines) and re.fullmatch(r'[\d,]+|-', lines[i + 1]):
                    line += ' ' + lines[i + 1]
                    i += 1
            if re.fullmatch(r'[\d,]+', line) and merged and any(merged[-1].lower().startswith(s.lower() + ' ') for s in states):
                merged[-1] += ' ' + line
            else:
                merged.append(line)
            i += 1
        for line in merged:
            m = pattern.match(line)
            if m:
                rows.append({'state_ut': m[1], 'district': m[2], 'financial_year': '2021-22',
                             'trained': int(m[3].replace(',', '')) if m[3] != '-' else None, 'pdf_page': page_no,
                             'source_url': 'https://www.msde.gov.in/static/uploads/2024/05/Annexure-2.pdf',
                             'quality_flag': 'training_flow_not_available_jobseekers;historical_district_names' + (';reported_dash_preserved_as_missing' if m[3] == '-' else '')})
            elif re.match(r'^Total\s+[\d,]+$', line):
                national = int(line.split()[-1].replace(',', ''))
            elif re.match(r'^[A-Za-z].*\s[\d,]+$', line) and not line.startswith('Annexure'):
                unmatched.append(line)
    if unmatched or national != sum(r['trained'] or 0 for r in rows):
        raise ValueError(f'PMKVY reconciliation failed: unmatched={unmatched}, sum={sum(r["trained"] or 0 for r in rows)}, national={national}')
    if len({(r['state_ut'].lower(), r['district'].lower()) for r in rows}) != len(rows):
        raise ValueError('Duplicate PMKVY district grain')
    emit('pmkvy_district_training', rows, rows[0]['source_url'], 'one state/district training total for FY 2021-22',
         'historical skilling flow; government training baseline',
         'Official MSDE parliamentary annexure. OGD JSS download returned HTTP 403; this is an official upstream alternative, not an OGD API export.',
         coverage='FY 2021-22; parliamentary reply 2023-02-06', geography='district',
         national_trained_total=national, reconciliation='district sum equals published national total')


def existing():
    entries = [
        ('plfs_workforce_rates', 'data/processed/public_labour/public-labour-20261001-v2/plfs_workforce_rates.csv',
         'https://api.mospi.gov.in/api/plfs/getData', 'geography/time/indicator/survey dimensions', 'labour-force baseline',
         'Official MoSPI API; preserve dimensions, unspecified values, and 2025 methodology break. Not available Data Analysts.'),
        ('ncs_state_year_metrics', 'data/processed/ncs/ncs_state_year_metrics.csv',
         'https://ncs.gov.in/NCSReportDashboard', 'state/financial_year/metric', 'historical demand and registration context',
         'Official public dashboard aggregates; not live individual postings or candidate records.'),
        ('dvet_maharashtra_institutes', 'data/processed/training/dvet_maharashtra_institutes.csv',
         'https://admission.dvet.gov.in/', 'institute reference record', 'training-provider discovery',
         'Public official reference; verify effective academic year and seats before capacity recommendations.'),
        ('dgt_iti_grading', 'data/processed/training/dgt_iti_grading_2026_27.csv',
         'https://dgt.gov.in/', 'ITI grading record for 2026-27', 'training-provider context',
         'Official public grading table; NG is ungraded, not zero; ratings are not available seats.')]
    for name, filename, url, grain, use, constraints in entries:
        with (ROOT / filename).open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        emit(name, rows, url, grain, use, constraints, original_file=filename)


def kaggle(archive):
    with zipfile.ZipFile(archive) as z:
        original = list(csv.DictReader(io.StringIO(z.read('recruitment_decision_tree.csv').decode('utf-8-sig'))))
    fields = ['Serial_no', 'Python_exp', 'Experience_Years', 'Education', 'Internship', 'Score',
              'Salary * 10E4', 'Offer_History', 'Location', 'Recruitment_Status']
    rows = [{k: r[k] for k in fields} | {
        'source_url': 'https://www.kaggle.com/datasets/rafunlearnhub/recruitment-data',
        'data_class': 'prototype_recruitment_classification_unverified_provenance',
        'quality_flag': 'no_city_or_time;salary_unit_unverified;not_real_available_workforce'} for r in original]
    if len(rows) != 614:
        raise ValueError('Kaggle recruitment source changed')
    emit('kaggle_recruitment_demo', rows, rows[0]['source_url'], 'publisher recruitment-classification example row',
         'prototype ingestion and classification only',
         'Uploader lists CC0; provenance is unverified. Gender excluded. This is not a job-posting time series or verified job-seeker registry.',
         coverage='Uploader version 1, updated 2021-05-22; observation dates absent',
         geography='Urban/Rural/Semiurban only; no Maharashtra/Pune identification')


def database():
    path = OUT / 'labour_records.sqlite'
    if path.exists():
        raise FileExistsError(path)
    with sqlite3.connect(path) as db:
        for entry in TABLES:
            with (OUT / entry['file']).open(encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames
                # TEXT preserves publisher codes, missing cells and mixed-format values.
                # Numeric conversion is an explicit downstream normalization step.
                quoted = lambda s: '"' + s.replace('"', '""') + '"'
                db.execute('CREATE TABLE ' + quoted(entry['table']) + ' (' + ','.join(quoted(c) + ' TEXT' for c in columns) + ')')
                db.executemany('INSERT INTO ' + quoted(entry['table']) + ' VALUES (' + ','.join('?' for _ in columns) + ')',
                               ([row[c] if row[c] != '' else None for c in columns] for row in reader))
                count = db.execute('SELECT COUNT(*) FROM ' + quoted(entry['table'])).fetchone()[0]
                if count != entry['rows']:
                    raise ValueError('SQLite row-count mismatch')
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('SQLite integrity check failed')


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kaggle-archive', type=Path, required=True)
    parser.add_argument('--snapshot', default='20261002-v1')
    args = parser.parse_args()
    if Path(args.snapshot).name != args.snapshot or args.snapshot in ('.', '..'):
        raise ValueError('Snapshot must be a single folder name')
    OUT = ROOT / 'DATA_100PLUS' / args.snapshot
    OUT.mkdir(parents=True, exist_ok=False)
    courses()
    nqr()
    aishe()
    pmkvy()
    existing()
    kaggle(args.kaggle_archive)
    database()
    json_new(OUT / 'manifest.json', {'snapshot': OUT.name, 'created_at': datetime.now(timezone.utc).isoformat(),
        'tables': TABLES, 'total_table_rows': sum(t['rows'] for t in TABLES),
        'live_ncs_postings_acquired': False, 'individual_jobseeker_profiles_acquired': False,
        'reliable_gap_and_forecast_ready': False, 'note': 'Counts represent heterogeneous records, never a combined count of people.'})
    print('TOTAL', sum(t['rows'] for t in TABLES), flush=True)


if __name__ == '__main__':
    main()
