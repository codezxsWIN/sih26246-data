import unittest
from src.clean_100plus_pack import course_flags, qualification_flags


class CatalogueFilteringTests(unittest.TestCase):
    def course(self, title, **changes):
        row = {'name': title, 'org': 'NSDC', 'quality_flag': '',
               'start_type': 'timestamp', 'start': '2024-01-01T00:00:00+00:00'}
        return row | changes

    def test_demo_and_underscore_placeholders_are_quarantined(self):
        for title in ['Democourse', 'DRC_Test_Demo_31Dec24', 'Test123']:
            with self.subTest(title=title):
                self.assertIn('suspected_test_demo_requires_review', course_flags(self.course(title)))

    def test_legitimate_testing_occupation_not_rejected_as_test_placeholder(self):
        self.assertEqual(course_flags(self.course('Software Vulnerability/Penetration Tester')), [])

    def test_placeholder_start_cannot_be_promoted_as_verified_date(self):
        flags = course_flags(self.course('Digital Literacy', start_type='empty', start='2030-01-01T00:00:00+00:00'))
        self.assertIn('start_date_semantics_unverified', flags)
        self.assertIn('future_or_timezone_unspecified_start', flags)

    def test_unknown_provider_requires_review_even_with_reasonable_title(self):
        self.assertIn('provider_label_outside_conservative_allowlist', course_flags(self.course('Python for Beginners', org='UnknownProvider')))

    def test_expired_qualification_not_used_as_current_standard(self):
        row = {'validity_status': 'expired_as_of_snapshot', 'title': 'Data Analyst',
               'qualification_code': 'CODE', 'sector': 'IT-ITeS', 'nsqf_level': 'Level 5', 'awarding_body': 'Body'}
        self.assertIn('expired_as_of_snapshot', qualification_flags(row))


if __name__ == '__main__':
    unittest.main()
