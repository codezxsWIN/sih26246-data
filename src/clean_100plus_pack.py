"""Separate conservative working records from bulk publisher catalogues.

Excluded records are quarantined for review, not deleted or declared fraudulent.
Unknown provider labels are not automatically trusted; expired standards and
synthetic recruitment examples are never promoted to current labour evidence.
"""
import argparse
import csv
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .acquire import ROOT

INPUT = ROOT / 'DATA_100PLUS/20261002-v6'
OUTPUT = ROOT / 'CLEAN_DATA/20261002-v3'
NOW = datetime(2026, 10, 2, tzinfo=timezone.utc)
ALLOWLIST = {'nsdc', 'nsdc_india', 'nationalassociationofsoftwareandservicecompanies',
             'symbiosisopeneducationsociety', 'nielit', 'microsoft',
             'tourismandhospitalityskillcouncil', 'agricultureskillcouncilofindia',
             'beautywellnesssectorskillcouncil'}
REPORT = {}
TABLES = {}


def read(name):
    with (INPUT / (name + '.csv')).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows, fields):
    with (OUTPUT / (name + '.csv')).open('x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def partition(source, target, decide, transform=None):
    original = read(source)
    kept, excluded, reasons = [], [], {}
    for row in original:
        flags = decide(row)
        if flags:
            excluded.append(row | {'excluded_reason': ';'.join(flags)})
            for flag in flags:
                reasons[flag] = reasons.get(flag, 0) + 1
        else:
            kept.append(transform(row.copy()) if transform else row.copy())
    if len(kept) + len(excluded) != len(original):
        raise ValueError('Row accounting failed')
    fields = list(kept[0]) if kept else list(original[0])
    write(target, kept, fields)
    write(target + '_quarantine', excluded, list(original[0]) + ['excluded_reason'])
    REPORT[target] = {'input': len(original), 'retained': len(kept), 'quarantined': len(excluded),
                      'reason_counts_nonexclusive': reasons, 'source_table': source}
    TABLES[target] = (kept, fields)
    print(target, json.dumps(REPORT[target]), flush=True)


def course_flags(row):
    flags = []
    title = ' '.join(row['name'].split())
    title_tokens = title.replace('_', ' ')
    if re.search(r'\b(test(?:course|assessment|\d+)?|testing|demo\w*|dummy\w*|sample|asdf)\b', title_tokens, re.I) or 'test_or_demo_candidate' in row['quality_flag']:
        flags.append('suspected_test_demo_requires_review')
    if len(title) < 8 or title.lower() in {'how to login', 'new course', 'course', 'untitled'}:
        flags.append('placeholder_or_navigation_title')
    if row['org'].lower() not in ALLOWLIST:
        flags.append('provider_label_outside_conservative_allowlist')
    if row['start_type'] != 'timestamp':
        flags.append('start_date_semantics_unverified')
    try:
        start = datetime.fromisoformat(row['start'].replace('Z', '+00:00'))
        if start.tzinfo is None or start > NOW:
            flags.append('future_or_timezone_unspecified_start')
    except ValueError:
        flags.append('start_date_missing_or_unparsed')
    return flags


def course_clean(row):
    row['name'] = ' '.join(row['name'].split())
    row['quality_flag'] = 'filtered_catalogue_metadata;provider_label_not_identity_verification;seats_and_certification_unverified;not_point_in_time_complete'
    row['recommendation_status'] = 'catalogue_candidate_only_not_verified_available_training'
    return row


def qualification_flags(row):
    return ([row['validity_status']] if row['validity_status'] != 'within_listed_validity' else []) + (
        ['essential_qualification_metadata_missing'] if any(not row[k].strip() for k in ['title', 'qualification_code', 'sector', 'nsqf_level', 'awarding_body']) else [])


def qualification_clean(row):
    for key in list(row):
        if isinstance(row[key], str):
            row[key] = ' '.join(row[key].split())
    row['nsqf_level_label'] = row['nsqf_level']
    match = re.fullmatch(r'Level\s+([\d.]+)', row['nsqf_level'])
    row['nsqf_level'] = float(match[1]) if match else None
    for key in ['maximum_hours', 'minimum_hours']:
        row[key + '_label'] = row[key]
        match = re.fullmatch(r'([\d,]+)\s+Hours?', row[key], re.I)
        row[key] = int(match[1].replace(',', '')) if match else None
    row['version'] = None if row['version'].lower() in ('', 'version') else row['version']
    for key in ['originally_approved', 'valid_till']:
        row[key + '_label'] = row[key]
        try:
            row[key] = datetime.strptime(row[key], '%d %b %Y').date().isoformat()
        except ValueError:
            row[key] = None
    row['source_serial'] = int(row['source_serial'])
    row['quality_flag'] = 'publisher_listed_validity;version_and_hours_missing_where_unparseable;not_training_capacity'
    return row


def education_clean(row):
    for key in ['male_pass_out', 'female_pass_out', 'total_pass_out', 'pdf_page']:
        row[key] = int(row[key]) if row[key] else None
    row['quality_flag'] = 'reported_education_flow_not_available_workforce;missing_sex_cells_remain_null'
    return row


def training_clean(row):
    row['trained'] = int(row['trained'])
    row['pdf_page'] = int(row['pdf_page'])
    return row


def plfs_clean(row):
    row['value'] = float(row['value'])
    return row


def main():
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='20261002-v3')
    args = parser.parse_args()
    if Path(args.snapshot).name != args.snapshot or args.snapshot in ('.', '..'):
        raise ValueError('Snapshot must be a single folder name')
    OUTPUT = ROOT / 'CLEAN_DATA' / args.snapshot
    OUTPUT.mkdir(parents=True, exist_ok=False)
    partition('skillindia_courses', 'course_catalogue_candidates', course_flags, course_clean)
    partition('nqr_qualifications', 'valid_qualifications', qualification_flags, qualification_clean)
    partition('aishe_state_level_passouts', 'education_passout_observations',
              lambda r: (['aggregate_total_excluded_to_prevent_double_counting'] if r['geography_level'] == 'country' or r['education_level'] == 'Grand Total' else []) +
                        (['passout_total_missing'] if not r['total_pass_out'] else []), education_clean)
    partition('pmkvy_district_training', 'district_training_observations',
              lambda r: ['publisher_dash_or_missing_training_count'] if not r['trained'] else [], training_clean)
    partition('plfs_workforce_rates', 'fully_specified_workforce_rates',
              lambda r: ['survey_reference_or_year_type_unspecified'] if not r['reference_status'] or not r['year_type'] else [], plfs_clean)
    qualified = TABLES['valid_qualifications'][0]
    slice_rows = [r for r in qualified if r['sector'] in {'IT-ITeS', 'Automotive', 'Electronics & HW'}]
    write('mvp_sector_qualifications', slice_rows, TABLES['valid_qualifications'][1])
    REPORT['mvp_sector_qualifications'] = {'rows': len(slice_rows), 'subset_of': 'valid_qualifications',
                                         'sectors': ['IT-ITeS', 'Automotive', 'Electronics & HW']}
    TABLES['mvp_sector_qualifications'] = (slice_rows, TABLES['valid_qualifications'][1])
    with sqlite3.connect(OUTPUT / 'filtered_labour_records.sqlite') as db:
        for table, (rows, fields) in TABLES.items():
            numeric = {'trained': 'INTEGER', 'male_pass_out': 'INTEGER', 'female_pass_out': 'INTEGER',
                       'total_pass_out': 'INTEGER', 'pdf_page': 'INTEGER', 'value': 'REAL',
                       'nsqf_level': 'REAL', 'maximum_hours': 'INTEGER', 'minimum_hours': 'INTEGER', 'source_serial': 'INTEGER'}
            quote = lambda v: '"' + v.replace('"', '""') + '"'
            db.execute('CREATE TABLE ' + quote(table) + '(' + ','.join(quote(k) + ' ' + numeric.get(k, 'TEXT') for k in fields) + ')')
            db.executemany('INSERT INTO ' + quote(table) + ' VALUES (' + ','.join('?' for _ in fields) + ')',
                           ([r[k] if r[k] != '' else None for k in fields] for r in rows))
            if db.execute('SELECT COUNT(*) FROM ' + quote(table)).fetchone()[0] != len(rows):
                raise ValueError('Filtered database count mismatch')
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Filtered database integrity failure')
    with (OUTPUT / 'quality_report.json').open('x', encoding='utf-8') as f:
        json.dump({'rules_version': 1, 'status_as_of': NOW.isoformat(), 'tables': REPORT,
                   'provider_label_allowlist': sorted(ALLOWLIST),
                   'kaggle_demo_in_current_labour_engine': False,
                   'reliable_gap_forecast_ready': False,
                   'note': 'Quarantine is exclusion pending review, not proof that each excluded record is garbage. No padding or zero imputation. The MVP sector table is a subset, not additional unique records.'}, f, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()
