"""Package public-safe evidence as additive, offline teammate SQLite snapshots.

Never imports personal profiles, fetches the network or overwrites snapshots.
"""
import argparse
import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = {
    'postings': 'data/processed/live_employers/employer-snapshot-20261001-v1/public_employer_posting_observations.csv',
    'skills': 'data/processed/live_employers/employer-snapshot-20261001-v1/skill_mentions.csv',
    'ncs': 'data/processed/ncs/ncs_maharashtra_year_metrics.csv',
    'rates': 'data/processed/public_labour/public-labour-20261001-v2/plfs_workforce_rates.csv',
    'baselines': 'data/processed/public_labour/public-labour-20261001-v2/workforce_baseline_estimates.csv',
}
TABLES = {
    'recruiter': ('source_files', 'employers', 'recruiter_accounts', 'job_postings', 'job_skills', 'aggregate_demand'),
    'job_seekers': ('source_files', 'candidate_profiles', 'candidate_skills', 'aggregate_jobseekers', 'labour_rates', 'workforce_baselines'),
}
NUMERIC_FIELDS = {
    'value', 'lfpr_percent', 'ur_percent', 'wpr_percent',
    'unemployed_per_100_population', 'implied_employed_per_100_population',
    'wpr_rounding_residual', 'available_data_analysts_estimate',
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def boolean(value):
    if value not in ('true', 'false'):
        raise ValueError(f'Expected true/false, got {value!r}')
    return int(value == 'true')


def insert(connection, table, row):
    # Table names are internal constants; columns must belong to the schema.
    allowed = {field[1] for field in connection.execute(f'PRAGMA table_info("{table}")')}
    if not row or not set(row) <= allowed:
        raise ValueError(f'Unexpected fields for {table}: {set(row) - allowed}')
    columns = ', '.join('"' + key + '"' for key in row)
    placeholders = ', '.join('?' for _ in row)
    connection.execute(f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})', list(row.values()))


def populate_recruiter(connection, inputs):
    employers = {}
    posting_ids = {}
    for row in inputs['postings']:
        identity = (row['source_id'], row['company'])
        if identity not in employers:
            employer_id = 'employer_' + hashlib.sha256('|'.join(identity).encode()).hexdigest()[:24]
            employers[identity] = employer_id
            insert(connection, 'employers', {
                'employer_id': employer_id, 'company_name': row['company'],
                'source_id': row['source_id'], 'source_file_id': 'postings',
            })
        key = (row['source_id'], row['source_job_id'])
        if key in posting_ids:
            raise ValueError('Multiple observations for one posting: use a new snapshot or schema version')
        posting_id = '|'.join(key)
        posting_ids[key] = posting_id
        result = {key: value or None for key, value in row.items() if key != 'company'}
        result.update(posting_id=posting_id, employer_id=employers[identity],
                      occupation='Data Analyst', source_file_id='postings')
        result['vacancy_count'] = int(row['vacancy_count']) if row['vacancy_count'] else None
        result['source_tier'] = int(row['source_tier'])
        for field in ('eligible_for_verified_market_demand', 'source_is_ncs'):
            result[field] = boolean(row[field])
        insert(connection, 'job_postings', result)
    for row in inputs['skills']:
        result = {key: value for key, value in row.items() if key not in ('source_id', 'source_job_id')}
        result['posting_id'] = posting_ids[(row['source_id'], row['source_job_id'])]
        insert(connection, 'job_skills', result)
    for row in inputs['ncs']:
        if row['metric'] in ('Vacancies', 'Active Employer'):
            insert(connection, 'aggregate_demand', dict(row, value=int(row['value']), source_file_id='ncs'))


def populate_job_seekers(connection, inputs):
    for row in inputs['ncs']:
        if row['metric'] in ('Jobseeker Registered', 'Active Jobseekers'):
            insert(connection, 'aggregate_jobseekers', dict(row, value=int(row['value']), source_file_id='ncs'))
    for source_id, table in (('rates', 'labour_rates'), ('baselines', 'workforce_baselines')):
        for row in inputs[source_id]:
            result = {key: value or None for key, value in row.items()}
            for field in NUMERIC_FIELDS & row.keys():
                result[field] = float(row[field]) if row[field] else None
            if source_id == 'rates':
                result['available_analyst_supply'] = boolean(row['available_analyst_supply'])
            result['source_file_id'] = source_id
            insert(connection, table, result)


def export_tables(connection, output, tables):
    output.mkdir(parents=True, exist_ok=True)
    counts = {}
    for table in tables:
        cursor = connection.execute(f'SELECT * FROM "{table}" ORDER BY rowid')
        rows = cursor.fetchall()
        with (output / (table + '.csv')).open('x', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow([field[0] for field in cursor.description])
            writer.writerows(rows)
        counts[table] = len(rows)
    return counts


def build(output_dir, root=ROOT):
    """Build from fixed acquired inputs; fail if any intended output already exists."""
    output = Path(output_dir)
    targets = [output / 'manifest.json']
    for name, tables in TABLES.items():
        targets.append(output / (name + '.sqlite'))
        targets.extend(output / (name + '_data') / (table + '.csv') for table in tables)
    for target in targets:
        if target.exists():
            raise FileExistsError(f'Preserving existing file: {target}. Choose a new --output-dir.')

    inputs = {name: read_csv(root / path) for name, path in SOURCE_PATHS.items()}
    sources = {name: {'repository_path': path, 'sha256': sha256(root / path)} for name, path in SOURCE_PATHS.items()}
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        'schema_version': 2,
        'built_at': datetime.now(timezone.utc).isoformat(),
        'evidence_observed_date': '2026-10-01',
        'source_files': sources,
        'databases': {},
        'readiness': {
            'public_evidence_packaged': True,
            'individual_jobseekers_available': False,
            'individual_recruiter_accounts_available': False,
            'live_ncs_postings_available': False,
            'available_pune_data_analysts_estimated': False,
            'reliable_gap_or_forecast_ready': False,
        },
        'limitations': [
            'One employer-published posting is not representative market demand; vacancy headcount unknown.',
            'No individual candidate profiles or recruiter accounts acquired.',
            'NCS state/year counts are aggregates; metric definitions and partial FY need care.',
            'PLFS baselines are all-role rates; do not mix vintages, reference statuses or frequencies.',
            'Public access does not itself establish redistribution or model-training permission.',
            'No authorized candidate importer or matching/forecast engine is implemented here.',
        ],
    }
    for name, tables in TABLES.items():
        target = output / (name + '.sqlite')
        with target.open('xb'):
            pass
        connection = sqlite3.connect(target)
        try:
            connection.executescript((root / 'DATABASES/schema' / (name + '.sql')).read_text(encoding='utf-8'))
            selected_sources = ('postings', 'skills', 'ncs') if name == 'recruiter' else ('ncs', 'rates', 'baselines')
            with connection:
                for source_id in selected_sources:
                    insert(connection, 'source_files', dict(source_file_id=source_id, **sources[source_id]))
                populate = populate_recruiter if name == 'recruiter' else populate_job_seekers
                populate(connection, inputs)
            if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError(f'Database integrity failed: {name}')
            if connection.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError(f'Broken foreign keys: {name}')
            counts = export_tables(connection, output / (name + '_data'), tables)
        finally:
            connection.close()
        manifest['databases'][target.name] = {
            'sha256': sha256(target), 'row_counts': counts, 'csv_folder': name + '_data',
        }
    with (output / 'manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, indent=2)
        stream.write('\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'DATABASES/v2')
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result['databases'], indent=2))


if __name__ == '__main__':
    main()
