import json
import unittest
from unittest.mock import patch
from openpe import Categories, Dataset, WebScraper
from openpe.module import get_datasets_by_category, expand_datasets

class TestModule(unittest.TestCase):
    
    def test_add_new_category(self):
        Categories.register_category("NEW_EDUCACION", "Educación")
        self.assertEqual(Categories.NEW_EDUCACION, "Educación")

    @unittest.skip("Skipping test_get_datasets_by_category")
    def test_get_datasets_by_category(self):
        datasets = get_datasets_by_category(Categories.MEDIO_AMBIENTE, max_page=1)
        self.assertEqual(len(datasets), 10)
        self.assertIsInstance(datasets[0], Dataset)

    @unittest.skip("Skipping test_get_datasets_by_category_multiple_pages")
    def test_get_datasets_by_category_multiple_pages(self):
        datasets = get_datasets_by_category(Categories.MEDIO_AMBIENTE, max_page=3)
        self.assertEqual(len(datasets), 30)
        self.assertIsInstance(datasets[0], Dataset)

    def test_expand_datasets(self):
        datasets = get_datasets_by_category(Categories.MEDIO_AMBIENTE, max_page=1)
        expanded_datasets = expand_datasets(datasets[:1])
        #print(expanded_datasets[0].__repr__(simple=True))
        self.assertEqual(len(expanded_datasets), 1)

if __name__ == '__main__':
    unittest.main()