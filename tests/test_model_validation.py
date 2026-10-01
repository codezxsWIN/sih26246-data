import unittest
from src.validate_model_pack import validate_jobs

class ValidationTests(unittest.TestCase):
    def test_join_mismatch_rejected(self):
        with self.assertRaises(ValueError):validate_jobs([{'record_id':'a','eligible_for_verified_demand':'false'}],[],'false')
    def test_prototype_cannot_be_marked_verified(self):
        with self.assertRaises(ValueError):validate_jobs([{'record_id':'a','eligible_for_verified_demand':'true'}],[{'record_id':'a','eligible_for_verified_demand':'true','sql':'1'}],'false')
    def test_binary_features_required(self):
        with self.assertRaises(ValueError):validate_jobs([{'record_id':'a','eligible_for_verified_demand':'false'}],[{'record_id':'a','eligible_for_verified_demand':'false','sql':'2'}],'false')
    def test_valid_join(self):
        validate_jobs([{'record_id':'a','eligible_for_verified_demand':'false'}],[{'record_id':'a','eligible_for_verified_demand':'false','sql':'1'}],'false')
