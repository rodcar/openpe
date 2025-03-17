import requests
from bs4 import BeautifulSoup
import logging
import os
from datetime import datetime
from openpe.errors import log_error

class WebScraper:
    def __init__(self, base_url: str = '', headers: dict = None):
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        self.session = requests.Session()

    def get_response(self, url: str, headers=None, verify=True, timeout=600):
        """
        Fetch the response from a URL.
        
        Args:
            url (str): The URL to fetch
            headers (dict, optional): Custom headers for the request
            verify (bool): Whether to verify SSL certificates
            timeout (int): Request timeout in seconds
            
        Returns:
            requests.Response: The response object
        """
        try:
            # Merge headers if provided
            request_headers = self.headers.copy()
            if headers:
                request_headers.update(headers)
                
            response = self.session.get(url, headers=request_headers, verify=verify, timeout=timeout)
            return response
        except Exception as e:
            log_error(f"Error fetching URL: {url}, Error: {str(e)}")
            return None

    def fetch_page(self, endpoint: str) -> str:
        response = self.get_response(f"{self.base_url}/{endpoint}")
        return response.content

    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')

    def extract_data(self, soup: BeautifulSoup, selector: str) -> list:
        elements = soup.select(selector)
        return [element.get_text() for element in elements]