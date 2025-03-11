import requests
from bs4 import BeautifulSoup
from .webscraper import WebScraper

BASE_URL = "https://datosabiertos.gob.pe"

def example_function():
    return "Hello, World!"

def fetch_datasets_by_category(category: str) -> list:
    scraper = WebScraper(BASE_URL)
    response = scraper.fetch_page(f"datasets?category={category}")
    return response.json()

def fetch_dataset_by_id(dataset_id: str) -> dict:
    scraper = WebScraper(BASE_URL)
    response = scraper.fetch_page(f"datasets/{dataset_id}")
    return response.json()

def fetch_datasets_by_url(url: str) -> list:
    scraper = WebScraper(url)
    response = scraper.fetch_page(url)
    return response.json()

def fetch_datasets_by_multiple_categories(categories: list) -> list:
    scraper = WebScraper(BASE_URL)
    categories_str = ','.join(categories)
    response = scraper.fetch_page(f"datasets?categories={categories_str}")
    return response.json()

def search_datasets(keyword: str) -> list:
    scraper = WebScraper(BASE_URL)
    response = scraper.fetch_page(f"datasets?search={keyword}")
    return response.json()