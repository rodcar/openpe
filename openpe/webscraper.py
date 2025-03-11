import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def fetch_page(self, endpoint: str) -> str:
        response = requests.get(f"{self.base_url}/{endpoint}")
        response.raise_for_status()
        return response.text

    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')

    def extract_data(self, soup: BeautifulSoup, selector: str) -> list:
        elements = soup.select(selector)
        return [element.get_text() for element in elements]