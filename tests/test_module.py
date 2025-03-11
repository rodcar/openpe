import json
import unittest
from unittest.mock import patch
from openpe import example_function, Categories, Dataset, WebScraper  # Use package-level imports

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

    @patch('openpe.webscraper.requests.get')
    def test_webscraper_fetch_page(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html></html>"
        scraper = WebScraper(base_url="http://example.com")
        html = scraper.fetch_page("some-endpoint")
        self.assertEqual(html, "<html></html>")

    def test_webscraper_parse_html(self):
        scraper = WebScraper(base_url="http://example.com")
        html = "<html><body><div class='some-class'>Test</div></body></html>"
        soup = scraper.parse_html(html)
        self.assertEqual(soup.find('div', class_='some-class').get_text(), "Test")

    def test_webscraper_extract_data(self):
        scraper = WebScraper(base_url="http://example.com")
        html = "<html><body><div class='some-class'>Test1</div><div class='some-class'>Test2</div></body></html>"
        soup = scraper.parse_html(html)
        data = scraper.extract_data(soup, "div.some-class")
        self.assertEqual(data, ["Test1", "Test2"])

if __name__ == '__main__':
    unittest.main()