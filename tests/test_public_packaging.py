import unittest
from src.acquire import ROOT
from src.package_model_pack import additional_public_raw_files

class PublicPackagingTests(unittest.TestCase):
    def test_successful_public_api_evidence_included(self):
        files=additional_public_raw_files(ROOT)
        self.assertEqual(len(files),18)
        self.assertTrue(all(p.startswith('data/raw/public_labour/public-labour-20261001-v2/') for p in files))
        self.assertNotIn('data/raw/training/dvet_pune_region_govt_2022.pdf',files)
