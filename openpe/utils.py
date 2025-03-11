import json
from bs4 import BeautifulSoup

def to_json(items, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(items, file, ensure_ascii=False, indent=4)

def from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def parse_html(html_content):
    return BeautifulSoup(html_content, 'html.parser')