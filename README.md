# openpe

A library for searching datasets on datosabiertos.gob.pe

## Installation

You can install the package using pip:

```sh
pip install openpe
```

## Usage

Here's a basic example of how to use the library:

```python
import openpe

# Search for datasets
datasets = openpe.search('education')
for dataset in datasets:
    print(dataset['title'])

# Use the Dataset class
dataset = openpe.Dataset(
    id="dataset_id",
    title="Education Data",
    description="A dataset about education",
    categories=[openpe.Categories.EDUCACION, openpe.Categories.SALUD],
    url="http://example.com/dataset/123",
    modified_date="2023-10-01",
    release_date="2023-01-01",
    publisher="Ministry of Education",
    metadata={"source": "datosabiertos.gob.pe", "format": "CSV"}
)

print(dataset.title)
print(dataset.description)
print(dataset.categories)
print(dataset.modified_date)
print(dataset.release_date)
print(dataset.publisher)
print(dataset.metadata)
print(dataset.to_json())

# Use the WebScraper class
scraper = openpe.WebScraper(url="http://example.com")
data = scraper.scrape()
print(data)

# Fetch datasets by category
datasets_by_category = openpe.fetch_datasets_by_category(openpe.Categories.EDUCACION)
print(datasets_by_category)

# Fetch dataset by id
dataset_by_id = openpe.fetch_dataset_by_id("dataset_id")
print(dataset_by_id)

# Fetch datasets by URL
datasets_by_url = openpe.fetch_datasets_by_url("http://example.com/api/datasets")
print(datasets_by_url)

# Fetch datasets by multiple categories
datasets_by_multiple_categories = openpe.fetch_datasets_by_multiple_categories([openpe.Categories.EDUCACION, openpe.Categories.SALUD])
print(datasets_by_multiple_categories)

# Search datasets by keyword
datasets_by_keyword = openpe.search_datasets("education")
print(datasets_by_keyword)
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the maintainer at ivan@example.com.
