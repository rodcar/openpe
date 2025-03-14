import json
import os
import requests
from .webscraper import WebScraper
from .utils import to_json, parse_html
import io
import pandas as pd
import re
from tqdm import tqdm
import math
from .dataset import Dataset
import time

BASE_URL = "https://datosabiertos.gob.pe"
scraper = WebScraper(BASE_URL)

#def get_dataset_by_id(dataset_id: str) -> dict:
    #response = scraper.fetch_page(f"datasets/{dataset_id}")
    #return response.json()

def get_dataset(url):
    #delete datosabiertos.gob.pe and alternatives on the url
    url = re.sub(r'https?://(www\.)?datosabiertos.gob.pe', '', url)

    if not url.startswith('/'):
        url = '/dataset/' + url
    #print(f'url updated {url}')
    dataset = Dataset(
        url=url,
        id='',
        title='',
        description='',
        categories=[],
        modified_date='',
        release_date='',
        publisher='',
        metadata={}
    )
    return expand_dataset(dataset)

#def get_datasets_by_multiple_categories(categories: list) -> list:
    #categories_str = ','.join(categories)
    #response = scraper.fetch_page(f"datasets?categories={categories_str}")
    #return response.json()

#def get_datasets(keyword: str) -> list:
    #response = scraper.fetch_page(f"datasets?search={keyword}")
    #return response.json()

# download the dataset files or resource in a new folder: dataset id.json
def download_dataset(dataset: Dataset):
    dataset.download_files()

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

    if pagination is None:
        return None
        
    # Get the "next" page URL
    next_page = pagination.find('li', class_='pager-next')
    if next_page:
        next_link = next_page.find('a')
        if next_link and next_link.get('href'):
            return next_link['href']
    
    # If we reach here, there's no next page
    return None

def get_datasets(category, limit=math.inf, show_progress=True):
    page_url = f'search/field_topic/{category}/type/dataset?sort_by=changed'
    datasets = []
    page_counter = 0
    items_per_page = 10

    iterator = tqdm(total=limit, desc="Fetching datasets", unit=" dataset") if show_progress else range(limit)

    while len(datasets) < limit and page_url:
        try:
            results = scraper.fetch_page(page_url)
            items = get_items(results)
            for item in items:
                if len(datasets) >= limit:
                    break
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

                if len(datasets) < limit:
                    dataset = expand_dataset(dataset)
                    datasets.append(dataset)
                    if show_progress:
                        iterator.update(1)
            
            page_url = get_next_page_url(results)
            page_counter += 1
        except Exception as e:
            print(f"Error fetching page: {e}")
            break

    if show_progress:
        iterator.close()
    
    return datasets

def expand_dataset(dataset, include_data_dictionary=False):
    details = {}
    
    try:
        response = scraper.get_response(f'{BASE_URL}{dataset.url}')
        page = parse_html(response.content)

        link = page.find('a', {'title': 'json view of content'})['href']
        details['format_json_url'] = link

        metadata = scraper.get_response(link)

        details['format_json'] = metadata.json()
        dataset.metadata = metadata.json()
        
        # Safely extract fields with defaults for missing values
        result = metadata.json().get('result', [{}])[0] if metadata.json().get('result') else {}
        
        dataset.title = result.get('title', '')
        dataset.description = result.get('notes', '')  # Using get() with default empty string
        dataset.url = result.get('url', '')
        dataset.id = result.get('id', '')
        dataset.modified_date = result.get('metadata_modified', '')
        dataset.release_date = result.get('metadata_created', '')
        
        # Handle nested groups data safely
        try:
            if result.get('groups') and len(result['groups']) > 0:
                dataset.publisher = result['groups'][0].get('title', '')
                dataset.categories = result['groups']
            else:
                dataset.publisher = ''
                dataset.categories = []
        except (KeyError, IndexError, TypeError):
            dataset.publisher = ''
            dataset.categories = []
        
        if include_data_dictionary:
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

def expand_datasets(datasets, filename=None, show_progress=True):
    expanded_datasets = []
    iterator = tqdm(datasets, desc="Expanding datasets", unit="dataset") if show_progress else datasets

    for dataset in iterator:
        expanded_datasets.append(expand_dataset(dataset))
        time.sleep(1)  # Add a 5 seconds wait

    if filename:
        to_json([dataset.__dict__ for dataset in expanded_datasets], filename)
    return datasets

def save(datasets):
    """
    Save a dataset or list of datasets in JSON format inside the 'datasets' folder.
    Each dataset is saved in its own subfolder named after its ID.
    
    Args:
        datasets: A single Dataset object or a list of Dataset objects.
    
    Returns:
        None
    """
    # Convert single dataset to list for uniform handling
    if not isinstance(datasets, list):
        datasets = [datasets]
    
    # Create datasets directory if it doesn't exist
    os.makedirs('datasets', exist_ok=True)
    
    for dataset in datasets:
        # Create a directory for this dataset
        dataset_dir = os.path.join('datasets', dataset.id)
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Convert dataset to a serializable dictionary
        # This assumes that dataset can be serialized to JSON
        dataset_dict = dataset.to_dict() if hasattr(dataset, 'to_dict') else dataset.__dict__
        
        # Save dataset as JSON
        json_path = os.path.join(dataset_dir, f"{dataset.id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dataset_dict, f, indent=4, ensure_ascii=False)

def load(dataset_name=None):
    """
    Load datasets from the 'datasets' folder.
    
    Args:
        dataset_name (str, optional): Name of a specific dataset to load.
            If not provided, all datasets will be loaded.
            This can be either the dataset ID (folder name) or the dataset's display name.
    
    Returns:
        Dataset or list[Dataset]: A single Dataset object if dataset_name is provided,
            or a list of Dataset objects if no dataset_name is provided.
    """
    datasets_dir = 'datasets'
    
    # Check if datasets directory exists
    if not os.path.isdir(datasets_dir):
        if dataset_name:
            raise FileNotFoundError(f"Dataset directory not found: {datasets_dir}")
        return []
    
    # Direct match - check if dataset_name is actually an ID (folder name)
    if dataset_name and os.path.isdir(os.path.join(datasets_dir, dataset_name)):
        dataset_dir = os.path.join(datasets_dir, dataset_name)
        json_path = os.path.join(dataset_dir, f"{dataset_name}.json")
        
        if os.path.isfile(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                dataset_dict = json.load(f)
            return Dataset(**dataset_dict)
    
    # If no direct match or no specific dataset requested, load all datasets
    datasets = []
    for item in os.listdir(datasets_dir):
        item_path = os.path.join(datasets_dir, item)
        # Check if it's a directory
        if os.path.isdir(item_path):
            json_path = os.path.join(item_path, f"{item}.json")
            # Check if the JSON file exists
            if os.path.isfile(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        dataset_dict = json.load(f)
                    
                    # Create dataset object
                    dataset = Dataset(**dataset_dict)
                    
                    # If looking for a specific dataset by name
                    if dataset_name:
                        # Check if the dataset name matches in metadata
                        try:
                            if (dataset.metadata and 
                                'result' in dataset.metadata and 
                                dataset.metadata['result'] and 
                                dataset.metadata['result'][0].get('name') == dataset_name):
                                return dataset
                        except (KeyError, IndexError, AttributeError):
                            # Skip this dataset if there's an issue with the metadata structure
                            pass
                    else:
                        datasets.append(dataset)
                except Exception as e:
                    print(f"Error loading dataset {item}: {e}")
    
    # If we're looking for a specific dataset but didn't find it
    if dataset_name:
        raise FileNotFoundError(f"No dataset found with name: {dataset_name}")
    
    return datasets