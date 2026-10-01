import csv
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.build_team_databases import build


class TeamDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'databases'
        self.manifest = build(self.output)

    def connect(self, name):
        connection = sqlite3.connect(self.output / name)
        connection.execute('PRAGMA foreign_keys=ON')
        self.addCleanup(connection.close)
        return connection

    def test_both_databases_pass_integrity_and_foreign_key_checks(self):
        for name in ('recruiter.sqlite', 'job_seekers.sqlite'):
            connection = self.connect(name)
            self.assertEqual(connection.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(connection.execute('PRAGMA user_version').fetchone()[0], 1)

    def test_recruiter_evidence_is_real_but_not_representative_market_demand(self):
        connection = self.connect('recruiter.sqlite')
        self.assertEqual(connection.execute('SELECT count(*) FROM employers').fetchone()[0], 1)
        self.assertEqual(connection.execute('SELECT count(*) FROM job_postings').fetchone()[0], 1)
        self.assertEqual(connection.execute('SELECT count(*) FROM job_skills').fetchone()[0], 5)
        self.assertEqual(connection.execute('SELECT count(*) FROM recruiter_accounts').fetchone()[0], 0)
        self.assertEqual(connection.execute('SELECT vacancy_count, eligible_for_verified_market_demand FROM job_postings').fetchone(), (None, 0))
        self.assertEqual(connection.execute('SELECT count(*) FROM aggregate_demand').fetchone()[0], 24)

    def test_jobseeker_aggregates_do_not_become_candidate_profiles(self):
        connection = self.connect('job_seekers.sqlite')
        for table, count in [('candidate_profiles', 0), ('candidate_skills', 0),
                             ('aggregate_jobseekers', 24), ('labour_rates', 180),
                             ('workforce_baselines', 60)]:
            self.assertEqual(connection.execute(f'SELECT count(*) FROM {table}').fetchone()[0], count)
        self.assertEqual(connection.execute('SELECT count(*) FROM workforce_baselines WHERE available_data_analysts_estimate IS NOT NULL').fetchone()[0], 0)
        self.assertFalse(self.manifest['readiness']['individual_jobseekers_available'])
        self.assertFalse(self.manifest['readiness']['reliable_gap_or_forecast_ready'])

    def test_foreign_keys_reject_orphan_skill_evidence(self):
        connection = self.connect('recruiter.sqlite')
        with self.assertRaises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO job_skills VALUES ('missing', 'python', 'Python', 'evidence', 'https://example.invalid', '2026-10-01')")

    def test_publisher_unspecified_survey_dimensions_remain_unknown(self):
        connection = self.connect('job_seekers.sqlite')
        self.assertEqual(connection.execute('SELECT count(*) FROM labour_rates WHERE year_type IS NULL AND reference_status IS NULL').fetchone()[0], 147)
        self.assertEqual(connection.execute('SELECT count(*) FROM workforce_baselines WHERE year_type IS NULL AND reference_status IS NULL').fetchone()[0], 49)

    def test_existing_snapshot_is_never_overwritten(self):
        target = self.output / 'recruiter.sqlite'
        original = hashlib.sha256(target.read_bytes()).hexdigest()
        with self.assertRaises(FileExistsError):
            build(self.output)
        self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), original)

    def test_csv_exports_match_database_tables_including_empty_profiles(self):
        for name, entry in self.manifest['databases'].items():
            for table, count in entry['row_counts'].items():
                with (self.output / entry['csv_folder'] / (table + '.csv')).open(encoding='utf-8', newline='') as stream:
                    reader = csv.DictReader(stream)
                    self.assertIsNotNone(reader.fieldnames)
                    self.assertEqual(len(list(reader)), count)

    def test_shared_schema_has_no_contact_or_government_identity_columns(self):
        forbidden = {'name', 'full_name', 'email', 'phone', 'aadhaar', 'pan', 'resume', 'resume_text', 'password'}
        for name in ('recruiter.sqlite', 'job_seekers.sqlite'):
            connection = self.connect(name)
            for (table,) in connection.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                fields = {row[1] for row in connection.execute(f'PRAGMA table_info({table})')}
                self.assertFalse(fields & forbidden, table)

    def test_manifest_hashes_cover_sources_and_downloadable_databases(self):
        disk = json.loads((self.output / 'manifest.json').read_text(encoding='utf-8'))
        for name, entry in disk['databases'].items():
            self.assertEqual(entry['sha256'], hashlib.sha256((self.output / name).read_bytes()).hexdigest())
        self.assertEqual(len(disk['source_files']), 5)


if __name__ == '__main__':
    unittest.main()
