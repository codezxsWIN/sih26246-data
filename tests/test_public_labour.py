import unittest
from src.public_labour import api_url, normalize_plfs, workforce_baselines

class PublicLabourTests(unittest.TestCase):
    def test_server_page_limit_enforced(self):
        with self.assertRaises(ValueError):api_url('getData',{'limit':500})
    def test_only_documented_endpoint_allowed(self):
        with self.assertRaises(ValueError):api_url('http://localhost',{})
    def test_query_value_cannot_be_shell_code(self):
        url=api_url('getData',{'year':"2024'; Write-Host hacked"})
        self.assertNotIn("'",url)
        self.assertIn('%27',url)
    def test_geography_comes_from_response_not_requested_filter(self):
        row={'state':'All India','frequency':'Monthly','indicator':'UR (Unemployment Rate, in per cent)','year':'2025','month':'April','value':'5.1','unit':'%'}
        result=normalize_plfs([row],'evidence.json','https://api.mospi.gov.in')[0]
        self.assertEqual(result['geography'],'All India')
        self.assertEqual(result['role_scope'],'all_roles')
    def test_invalid_percentage_rejected(self):
        with self.assertRaises(ValueError):normalize_plfs([{'value':'NaN','unit':'%'}],'x','x')
    def test_matching_rates_produce_baseline_not_analyst_supply(self):
        rows=[{'state':'Maharashtra','frequency':'Annually','indicator':name,'year':'2024','year_type':'Calendar Year','sector':'urban','gender':'person','AgeGroup':'15 years and above','weekly_status':'PS+SS','value':str(value),'unit':'%'} for name,value in [('LFPR',60),('WPR',57),('UR',5)]]
        result=workforce_baselines(normalize_plfs(rows,'x','x'))
        self.assertEqual(result[0]['unemployed_per_100_population'],3.0)
        self.assertEqual(result[0]['available_data_analysts_estimate'],'')
    def test_incompatible_reference_status_not_joined(self):
        rows=[{'state':'Maharashtra','frequency':'Annually','indicator':name,'year':'2024','sector':'urban','gender':'person','AgeGroup':'15 years and above','weekly_status':status,'value':'50','unit':'%'} for name,status in [('LFPR','PS+SS'),('UR','CWS')]]
        self.assertEqual(workforce_baselines(normalize_plfs(rows,'x','x')),[])
