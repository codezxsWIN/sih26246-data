import unittest
from src.extract_extra import grade_row
from src.collect_dvet import options

class ExtraTests(unittest.TestCase):
    def test_cfi_prefix_is_not_dropped(self):
        row=grade_row('7180 CFI2700001 0.6 0.5 0.5 3 1 0.8 0 0.3 6.7',158)
        self.assertEqual(row['state_code_from_iti_id'],'27')
    def test_publisher_spaced_code_preserved(self):
        row=grade_row('5452 G 32000622 2.4 0.2 0.3 3 1 0.8 0 0.3 8',120)
        self.assertEqual(row['publisher_code_text'],'G 32000622')
        self.assertEqual(row['state_code_from_iti_id'],'32')
    def test_grade_parse_preserves_ng(self):
        row=grade_row('41 GR27000542 0 0 0.5 NG NG NG 0 0 NG',3)
        self.assertEqual(row['final_grade'],'NG')
        self.assertEqual(row['state_code_from_iti_id'],'27')
    def test_grade_nonrow_is_skipped(self):
        self.assertIsNone(grade_row('ANNEXURE-I',1))
    def test_invalid_grade_token_is_rejected(self):
        with self.assertRaises(ValueError):grade_row('1 GR27000009 3 1 1 1 1 1 0 0 BAD',2)
    def test_option_placeholder_excluded(self):
        self.assertEqual(options('<select id="x"><option value="-1">Select</option><option value="7">Fitter</option></select>','#x'),[{'id':'7','name':'Fitter'}])
