import unittest
from src.model_data import extract_skills, role_scope, canonical_url, deduplicate, production_errors, readiness

class ModelDataTests(unittest.TestCase):
    def test_extracts_skill_aliases_without_matching_nosql(self):
        found=extract_skills('Python, SQL, PowerBI, Excel, NoSQL')
        self.assertEqual({r['skill_id'] for r in found},{'python','sql','power_bi','excel'})
    def test_nosql_alone_is_not_sql(self):
        self.assertEqual(extract_skills('NoSQL'),[])
    def test_title_not_uploader_category_sets_role(self):
        self.assertEqual(role_scope('Senior Data Analyst'),'target')
        self.assertEqual(role_scope('Business Analyst'),'adjacent_review')
        self.assertEqual(role_scope('Data Engineer'),'out_of_scope')
    def test_url_identity_keeps_job_id(self):
        self.assertEqual(canonical_url('https://EXAMPLE.com/job?id=1&utm_source=x#top'),'https://example.com/job?id=1')
        self.assertNotEqual(canonical_url('https://example.com/job?id=1'),canonical_url('https://example.com/job?id=2'))
    def test_dedup_keeps_all_duplicate_evidence(self):
        rows=[{'source_id':'a','source_job_id':'1','job_url':'https://example.com/job?id=1'}, {'source_id':'b','source_job_id':'2','job_url':'https://example.com/job?id=1&utm_medium=x'}]
        kept,links=deduplicate(rows)
        self.assertEqual(len(kept),1)
        self.assertEqual(len(links),1)
        self.assertEqual(links[0]['duplicate_source_id'],'b')
    def test_same_title_different_job_ids_not_merged(self):
        rows=[{'source_id':'a','source_job_id':str(i),'job_url':f'https://example.com/job?id={i}','job_title':'Data Analyst'} for i in [1,2]]
        self.assertEqual(len(deduplicate(rows)[0]),2)
    def test_prototype_cannot_enter_production(self):
        row={'source_id':'kaggle','source_job_id':'1','job_title':'Data Analyst','location':'Pune','description':'Python SQL','posted_date':'2025-06-10','observed_at':'2026-10-01','usage_permission':'confirmed','date_quality':'verified','source_tier':'3'}
        self.assertIn('prototype_source',production_errors(row))
    def test_invalid_date_not_accepted(self):
        row={'posted_date':'2026-02-31'}
        self.assertIn('posted_date_invalid',production_errors(row))
    def test_future_posting_not_accepted(self):
        row={'posted_date':'2026-11-01','observed_at':'2026-10-01'}
        self.assertIn('posting_after_observation',production_errors(row))
    def test_ready_for_demo_does_not_imply_ready_for_forecast(self):
        result=readiness(0,100,200)
        self.assertTrue(result['prototype_ingestion_ready'])
        self.assertFalse(result['verified_demand_ready'])
        self.assertFalse(result['gap_ready'])
        self.assertFalse(result['forecast_ready'])
        self.assertIsNone(result['forecast_confidence'])
