import unittest
from src.live_employers import posting_metadata

class LiveEmployerTests(unittest.TestCase):
    def test_created_time_is_distinct_from_observation_time(self):
        row={'id':'abc','text':'Senior Data Analyst','categories':{'location':'Pune'},'createdAt':1735689600000,'hostedUrl':'https://jobs.lever.co/parallelwireless/abc'}
        result=posting_metadata(row,'2026-10-01T18:00:00+00:00')
        self.assertEqual(result['posted_date'],'2025-01-01')
        self.assertEqual(result['observed_date'],'2026-10-01')
        self.assertEqual(result['source_id'],'lever_parallelwireless')
        self.assertEqual(result['vacancy_count'],'')
    def test_missing_created_time_not_replaced_by_observed_date(self):
        result=posting_metadata({'id':'a','text':'Data Analyst','categories':{'location':'Pune'}},'2026-10-01T18:00:00+00:00')
        self.assertEqual(result['posted_date'],'')
        self.assertEqual(result['eligible_for_verified_market_demand'],'false')
