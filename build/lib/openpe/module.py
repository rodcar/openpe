import requests
from bs4 import BeautifulSoup
from .webscraper import WebScraper
from .utils import to_json, from_json, parse_html
import io
import pandas as pd
import re
from tqdm import tqdm
import math
from .dataset import Dataset

BASE_URL = "https://datosabiertos.gob.pe"
scraper = WebScraper(BASE_URL)

#def get_dataset_by_id(dataset_id: str) -> dict:
    #response = scraper.fetch_page(f"datasets/{dataset_id}")
    #return response.json()

def get_dataset_by_url(url):
    dataset = Dataset()
    dataset.url = url
    return expand_dataset(dataset)

#def get_datasets_by_multiple_categories(categories: list) -> list:
    #categories_str = ','.join(categories)
    #response = scraper.fetch_page(f"datasets?categories={categories_str}")
    #return response.json()

#def get_datasets(keyword: str) -> list:
    #response = scraper.fetch_page(f"datasets?search={keyword}")
    #return response.json()

def get_items(page_content):
    page = parse_html(page_content)
    list_container = page.find('div', class_='view-content')
    datasets = []
    
    for dataset_element in list_container.find_all('article', class_='node-search-result'):
        dataset = {}
        dataset['title'] = dataset_element.find('h2', class_='node-title').get_text(strip=True)
        dataset['url'] = dataset_element.find('h2', class_='node-title').a['href']
        dataset['organization'] = dataset_element.find('div', class_='group-membership').get_text(strip=True) if dataset_element.find('div', class_='group-membership') else ''
        
        # Check for topic (it might be nested in different divs)
        topic_div = dataset_element.find('a', class_='name')
        dataset['topic'] = topic_div.get_text(strip=True) if topic_div else "No topic"
        
        description_div = dataset_element.find('div', class_='node-description')
        if description_div:
            description = description_div.get_text(separator=' ', strip=True)
        else:
            description = "No description available"
        
        dataset['description'] = description            
        dataset['resources'] = []

        # Extracting all resource links (xlsx, docx, csv)
        resource_items = dataset_element.find_all('li')
        for item in resource_items:
            resource = {}
            if item.a is not None and 'data-format' in item.a.attrs:
                resource['format'] = item.a['data-format']
            else:
                resource['format'] = None
            if item.a is not None and 'href' in item.a.attrs:
                resource['format'] = item.a['href']
            else:
                resource['format'] = None
            dataset['resources'].append(resource)
    
        datasets.append(dataset)
    return datasets

def get_next_page_url(page_content):
    page = parse_html(page_content)
    
    # Find the pagination element
    pagination = page.find('ul', class_='pagination pager')
    pagination_info = {}

    if pagination is None:
        pagination_info['next_page_url'] = None
        return pagination_info
    # Get the "next" page URL
    next_page = pagination.find('li', class_='pager-next')
    if next_page:
        next_link = next_page.find('a')
        if next_link:
            pagination_info['next_page_url'] = next_link['href']
        else:
            pagination_info['next_page_url'] = None  # No next page (this could be the last page)

    return pagination_info['next_page_url']

def get_datasets_by_category(category, max_page=math.inf):
    page_url = f'search/field_topic/{category}/type/dataset?sort_by=changed'
    datasets = []
    page_counter = 0
        
    while page_counter < max_page:
        results = scraper.fetch_page(page_url)
        items = get_items(results)
        for item in items:
            dataset = Dataset(
                id=item.get('id', ''),
                title=item.get('title', ''),
                description=item.get('description', ''),
                categories=[category],
                url=item.get('url', ''),
                modified_date='',
                release_date='',
                publisher=item.get('organization', ''),
                metadata={}
            )
            datasets.append(dataset)
        page_url = get_next_page_url(results)
        
        if not page_url:
            break
        page_counter += 1
    return datasets

def expand_dataset(dataset):
    details = {}
    try:
        response = scraper.get_response(f'{BASE_URL}{dataset.url}')
        page = parse_html(response.content)

        link = page.find('a', {'title': 'json view of content'})['href']
        details['format_json_url'] = link

        metadata = scraper.get_response(link)

        details['format_json'] = metadata.json()
        dataset.metadata = metadata.json()
        dataset.title = metadata.json()['result'][0]['title']
        dataset.description = metadata.json()['result'][0]['notes']
        dataset.url = metadata.json()['result'][0]['url']
        dataset.id = metadata.json()['result'][0]['id']
        dataset.modified_date = metadata.json()['result'][0]['metadata_modified']
        dataset.release_date = metadata.json()['result'][0]['metadata_created']
        dataset.publisher = metadata.json()['result'][0]['groups'][0]['title']
        dataset.categories = metadata.json()['result'][0]['groups']
        
        data_dictionary_url = get_data_dictionary_url(metadata.json())

        if data_dictionary_url:
            dataset.data_dictionary = get_data_dictionary(data_dictionary_url)
        else:
            dataset.data_dictionary = 'Diccionario de datos no disponible'
    except AttributeError:
        # Handle case where find() returns None or href doesn't exist
        details['format_json_url'] = None
        details['format_json'] = None
        print("Error: Could not find JSON link element")
    except Exception as e:
        # Handle other potential errors (network issues, JSON parsing, etc.)
        details['format_json_url'] = None
        details['format_json'] = None
        print(f"Error processing URL: {str(e)}")
    return dataset

def get_data_dictionary_url(item):
    diccionario_url = None
    try:
        for resource in item['result'][0]['resources']:
            if "Diccionario" in resource['name']:
                diccionario_url = resource['url']
    except KeyError as e:
        # If 'resources' is missing, silently ignore and return None
        pass
    except Exception as e:
        print(f"Error processing item: {str(e)}")
    return diccionario_url
            
def get_data_dictionary(url, headers=None):
    scraper_with_headers = WebScraper(BASE_URL, headers=headers)
    try:
        # Fetch the response from the URL
        response = scraper_with_headers.get_response(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Store the content in an in-memory file
            in_memory_file = io.BytesIO(response.content)
            
            # Load the Excel file into a DataFrame
            df = pd.read_excel(in_memory_file)
            
            # Select only the first two columns, drop NaN values, and clean the data
            df_filtered = df.iloc[:, :2].dropna()  # First two columns and remove NaNs
            df_filtered = df_filtered.apply(lambda x: x.str.strip())  # Strip whitespace
            
            # Convert to string without index or header
            df_text = df_filtered.to_string(index=False, header=False, justify='left')
            
            # Clean up excessive spaces and format with tabs
            df_text_cleaned = re.sub(r' {3,}', '\t', df_text)
            df_text_cleaned = '\n'.join(line.lstrip() for line in df_text_cleaned.split('\n'))
            
            return df_text_cleaned
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            return None  # Or handle it differently
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing the Excel file: {e}")
        return None
    except ValueError as e:
        print(f"Error processing the DataFrame (e.g., empty or invalid data): {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def expand_datasets(datasets, filename=None):
    expanded_datasets = []
    # tqdm adds progress bar
    for dataset in tqdm(datasets, desc="Expanding datasets", unit="dataset"):
        expanded_datasets.append(expand_dataset(dataset))

        #dataset.metadata['details'] = dataset_details
        #data_dictionary_url = get_data_dictionary_url(dataset_details['format_json'])
        
        #if data_dictionary_url is not None:
            #dataset.metadata['data_dictionary'] = get_data_dictionary(data_dictionary_url)
        #else:
            #dataset.metadata['data_dictionary'] = 'Diccionario de datos no disponible'
    if filename:
        to_json([dataset.__dict__ for dataset in expanded_datasets], filename)
    return datasets