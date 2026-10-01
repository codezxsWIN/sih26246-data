import tempfile,unittest
from pathlib import Path
from src.model_pack import create_run_directory, fallback_record, build, import_jobs
from src.model_data import IMPORT_FIELDS
from src.extract_ncs import csv_write
from src.acquire import ROOT

class ModelPackTests(unittest.TestCase):
    def test_claimed_permission_does_not_bypass_source_review(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'jobs.csv'
            row={k:'' for k in IMPORT_FIELDS}
            row.update(source_id='unapproved',source_job_id='1',job_title='Data Analyst',location='Pune',description='SQL',posted_date='2025-01-01',observed_at='2025-01-02',source_tier='1',usage_permission='confirmed',date_quality='verified')
            csv_write(path,[row],IMPORT_FIELDS)
            accepted,rejected=import_jobs(ROOT,path)
            self.assertEqual(accepted,[])
            self.assertIn('source_not_reviewed_and_approved',rejected[0]['reasons'])
    def test_personal_contact_column_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'jobs.csv'
            csv_write(path,[],[*IMPORT_FIELDS,'email'])
            with self.assertRaises(ValueError):import_jobs(ROOT,path)
    def test_existing_run_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'run';create_run_directory(target)
            marker=target/'keep.txt';marker.write_text('original')
            with self.assertRaises(FileExistsError):create_run_directory(target)
            self.assertEqual(marker.read_text(),'original')
    def test_fallback_date_and_salary_are_not_invented(self):
        row={'job_id':'1','job_title':'Data Analyst','location':'Pune','skills_required':'SQL','salary_disclosed':'False','salary_min_lpa':'0','salary_max_lpa':'0','scraped_at':'2025-06-10'}
        result=fallback_record(row,'2026-10-01')
        self.assertEqual(result['posted_date'],'')
        self.assertEqual(result['salary_min_lpa'],'')
        self.assertEqual(result['eligible_for_verified_demand'],'false')
    def test_real_pack_build_preserves_inputs_and_separates_prototype(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            result=build(ROOT,path/'run',path/'prototype')
            self.assertTrue(result['existing_data_unchanged'])
            self.assertEqual(result['verified_postings'],0)
            self.assertGreater(result['prototype_postings'],0)
            self.assertFalse(result['forecast_ready'])
            self.assertTrue((path/'run'/'production_jobs.csv').exists())
            self.assertTrue((path/'prototype'/'jobs.csv').exists())
