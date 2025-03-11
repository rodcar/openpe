import json
import unittest
from unittest.mock import patch
from openpe import Categories, Dataset, WebScraper
from openpe.module import get_datasets_by_category, expand_datasets

class TestModule(unittest.TestCase):
    def setUp(self):
        # Reset custom categories before each test
        Categories._custom_categories.clear()
    
    def test_add_new_category(self):
        Categories.register_category("NEW_EDUCACION", "Educación")
        self.assertEqual(Categories.NEW_EDUCACION, "Educación")

    def test_dataset_initialization(self):
        dataset = Dataset(
            id="1",
            title="Sample Dataset",
            description="A sample dataset",
            categories=["Category1"],
            url="http://example.com",
            modified_date="2023-01-01",
            release_date="2023-01-01",
            publisher="Publisher",
            metadata={"key": "value"}
        )
        self.assertEqual(dataset.id, "1")
        self.assertEqual(dataset.title, "Sample Dataset")
        self.assertEqual(dataset.description, "A sample dataset")
        self.assertEqual(dataset.categories, ["Category1"])
        self.assertEqual(dataset.url, "http://example.com")
        self.assertEqual(dataset.modified_date, "2023-01-01")
        self.assertEqual(dataset.release_date, "2023-01-01")
        self.assertEqual(dataset.publisher, "Publisher")
        self.assertEqual(dataset.metadata, {"key": "value"})

    def test_dataset_to_json(self):
        dataset = Dataset(
            id="1",
            title="Sample Dataset",
            description="A sample dataset",
            categories=["Category1"],
            url="http://example.com",
            modified_date="2023-01-01",
            release_date="2023-01-01",
            publisher="Publisher",
            metadata={"key": "value"}
        )
        expected_json = json.dumps({
            "id": "1",
            "title": "Sample Dataset",
            "description": "A sample dataset",
            "categories": ["Category1"],
            "url": "http://example.com",
            "modified_date": "2023-01-01",
            "release_date": "2023-01-01",
            "publisher": "Publisher",
            "metadata": {"key": "value"}
        })
        self.assertEqual(dataset.to_json(), expected_json)

    def test_get_datasets_by_category(self):
        datasets = get_datasets_by_category(Categories.MEDIO_AMBIENTE, max_page=1)
        self.assertEqual(len(datasets), 10)

    def test_expand_datasets(self):
        datasets = get_datasets_by_category(Categories.MEDIO_AMBIENTE, max_page=1)
        expanded_datasets = expand_datasets([datasets[0]])
        self.assertEqual(len(expanded_datasets), 1)
        self.assertNotEqual(expanded_datasets[0]['data_dictionary'], {})

if __name__ == '__main__':
    unittest.main()