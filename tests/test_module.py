import json
import unittest
from openpe import example_function, Categories, Dataset  # Use package-level imports

class TestModule(unittest.TestCase):
    def setUp(self):
        # Reset custom categories before each test
        Categories._custom_categories.clear()

    def test_example_function(self):
        self.assertEqual(example_function(), "Hello, World!")

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

if __name__ == '__main__':
    unittest.main()