import json
import unittest
from unittest.mock import patch
import openpe as pe
from openpe import Categories, Dataset

class TestModule(unittest.TestCase):
    
    def test_add_new_category(self):
        Categories.register_category("NEW_EDUCACION", "Educación")
        self.assertEqual(Categories.NEW_EDUCACION, "Educación")

    @unittest.skip("Skipping test_get_datasets_by_category")
    def test_get_datasets_by_category(self):
        datasets = pe.get_datasets_by_category(Categories.MEDIO_AMBIENTE, max_page=1)
        self.assertEqual(len(datasets), 10)
        self.assertIsInstance(datasets[0], Dataset)

    @unittest.skip("Skipping test_get_datasets_by_category_multiple_pages")
    def test_get_datasets_by_category_multiple_pages(self):
        datasets = pe.get_datasets_by_category(Categories.MEDIO_AMBIENTE, max_page=3)
        self.assertEqual(len(datasets), 30)
        self.assertIsInstance(datasets[0], Dataset)

    def test_expand_datasets(self):
        datasets = pe.get_datasets_by_category(Categories.MEDIO_AMBIENTE, max_page=1)
        expanded_datasets = pe.expand_datasets(datasets[:1], show_progress=False)
        #print(expanded_datasets[0].__repr__(simple=True))
        self.assertEqual(len(expanded_datasets), 1)
    
    def test_get_dataset_by_url(self):
            url = 'https://www.datosabiertos.gob.pe/dataset/dataset-01-cartera-proyectos-lambayeque-activos'
            dataset = pe.get_dataset_by_url(url)
            dataset.__repr__(simple=True)
            
if __name__ == '__main__':
    unittest.main()