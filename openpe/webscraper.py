import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, base_url: str, headers: dict = None):
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    def get_response(self, url: str):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response

    def fetch_page(self, endpoint: str) -> str:
        response = self.get_response(f"{self.base_url}/{endpoint}")
        return response.content

    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')

    def extract_data(self, soup: BeautifulSoup, selector: str) -> list:
        elements = soup.select(selector)
        return [element.get_text() for element in elements]