import json
import os
from .webscraper import WebScraper
import time
import pandas as pd
import glob
import io
import re  # Add import for regex processing
import urllib.parse  # Add this import for URL decoding
from .errors import log_error  # Updated import to avoid circular dependency
import requests

class Dataset:
    def __init__(self, id: str, title: str, description: str, categories: list, url: str, modified_date: str, release_date: str, publisher: str, metadata: dict, data_dictionary: str = None):
        self.id = id
        self.title = title
        self.description = description
        self.categories = categories
        self.url = url
        self.modified_date = modified_date
        self.release_date = release_date
        self.publisher = publisher
        self.metadata = metadata
        self._data_dictionary = data_dictionary  # Changed to private attribute

    def __repr__(self, simple=False):
        if simple:
            return f"Dataset(title={self.title}, description={self.description}, categories={self.categories}, url={self.url})"
        return f"Dataset(id={self.id}, title={self.title}, description={self.description}, categories={self.categories}, url={self.url}, modified_date={self.modified_date}, release_date={self.release_date}, publisher={self.publisher}, metadata={self.metadata}, data_dictionary={self.data_dictionary})"

    def to_json(self):
        return json.dumps({
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "categories": self.categories,
            "url": self.url,
            "modified_date": self.modified_date,
            "release_date": self.release_date,
            "publisher": self.publisher,
            "metadata": self.metadata,
            "data_dictionary": self.data_dictionary
        })

    @property
    def data_dictionary(self):
        """
        Property that returns the data dictionary. If it's None or empty,
        it will attempt to fetch the data dictionary from the dataset resources.
        """
        if self._data_dictionary is None or self._data_dictionary == "":
            self._data_dictionary = self.get_data_dictionary()
        return self._data_dictionary
    
    @data_dictionary.setter
    def data_dictionary(self, value):
        """Setter for data_dictionary property"""
        self._data_dictionary = value
    
    def get_data_dictionary(self):
        """
        Searches for and retrieves the data dictionary from the dataset resources.
        
        Returns:
            str: The content of the data dictionary, or None if not found
        """
        #print(f"DEBUG: Starting to retrieve data dictionary for dataset {self.id}")
        if not self.metadata or 'result' not in self.metadata or not self.metadata['result'] or 'resources' not in self.metadata['result'][0]:
            print("DEBUG: No metadata or resources found")
            return None
            
        resources = self.metadata['result'][0]['resources']
        #print(f"DEBUG: Found {len(resources)} resources in metadata")
        dictionary_keywords = ["diccionario de datos", "diccionario", "Diccionario de datos", "Diccionario de Datos", "Diccionario De Datos"]
        
        # Filter resources to find data dictionary
        dictionary_resources = []
        for resource in resources:
            resource_name = resource.get('name', '').lower()
            for keyword in dictionary_keywords:
                if keyword in resource_name:
                    #print(f"DEBUG: Found potential data dictionary: {resource_name}")
                    dictionary_resources.append(resource)
                    break
        
        if not dictionary_resources:
            #print("DEBUG: No data dictionary resources found")
            return None
        
        # Try to download and process the first matching dictionary resource
        try:
            #print(f"DEBUG: Attempting to process {len(dictionary_resources)} data dictionary resources")
            scraper = WebScraper()
            resource = dictionary_resources[0]
            resource_url = resource['url']
            resource_format = resource.get('format', '').lower()
            #print(f"DEBUG: Downloading data dictionary from {resource_url} (format: {resource_format})")
            
            # Download the content
            response = scraper.get_response(resource_url)
            #print(f"DEBUG: Download status code: {response.status_code if response else 'None'}")
            if response is None or response.status_code != 200:
                return None
                
            content = response.content
            #print(f"DEBUG: Downloaded content size: {len(content)} bytes")
            
            # Process based on format
            if resource_format == 'pdf':
                #print("DEBUG: Found PDF data dictionary")
                # For PDF, just return the URL since we can't easily extract text
                return f"PDF data dictionary available at: {resource_url}"
            elif resource_format in ['.xlsx', '.xls', 'xlsx', 'xls']:
                #print("DEBUG: Processing Excel data dictionary")
                # Process Excel files like in module.get_data_dictionary()
                try:
                    # Store the content in an in-memory file
                    in_memory_file = io.BytesIO(content)
                    
                    # Load the Excel file into a DataFrame
                    df = pd.read_excel(in_memory_file)
                    #print(f"DEBUG: Excel data loaded, shape: {df.shape}")
                    
                    # Select only the first two columns, drop NaN values, and clean the data
                    df_filtered = df.iloc[:, :2].dropna()  # First two columns and remove NaNs
                    #print(f"DEBUG: Filtered data shape: {df_filtered.shape}")
                    df_filtered = df_filtered.apply(lambda x: x.str.strip() if hasattr(x, 'str') else x)  # Strip whitespace
                    
                    # Convert to string without index or header
                    df_text = df_filtered.to_string(index=False, header=False, justify='left')
                    
                    # Clean up excessive spaces and format with tabs
                    df_text_cleaned = re.sub(r' {3,}', '\t', df_text)
                    df_text_cleaned = '\n'.join(line.lstrip() for line in df_text_cleaned.split('\n'))
                    #print(f"DEBUG: Processed text length: {len(df_text_cleaned)} chars")
                    
                    return df_text_cleaned
                except Exception as e:
                    #print(f"DEBUG: Error processing Excel file: {e}")
                    return f"{resource_format.upper()} data dictionary available at: {resource_url}"
            else:
                #print(f"DEBUG: Attempting to decode text content from {resource_format} file")
                # For text formats, decode and return the content
                try:
                    text_content = content.decode('utf-8')
                    #print(f"DEBUG: Successfully decoded with utf-8, length: {len(text_content)}")
                    return text_content
                except UnicodeDecodeError:
                    #print("DEBUG: utf-8 decode failed, trying latin1")
                    try:
                        text_content = content.decode('latin1')
                        #print(f"DEBUG: Successfully decoded with latin1, length: {len(text_content)}")
                        return text_content
                    except:
                        #print("DEBUG: All decoding attempts failed")
                        return f"Data dictionary available at: {resource_url}"
        except Exception as e:
            #print(f"DEBUG: Error retrieving data dictionary: {str(e)}")
            return None

    def to_dict(self):
        """
        Convert the Dataset object to a JSON serializable dictionary.
        
        Returns:
            dict: A dictionary representation of the Dataset.
        """
        # Create a base dictionary from the object's attributes
        dataset_dict = {k.lstrip('_'): v for k, v in self.__dict__.items()}
        
        # Handle any non-serializable objects or custom serialization logic
        # Add custom serialization for specific attributes if needed
        
        return dataset_dict

    def _extract_filename_from_url(self, url):
        """
        Extract the actual filename from a URL and decode URL-encoded characters.
        
        Args:
            url (str): The URL to extract the filename from
            
        Returns:
            str: The extracted and decoded filename, or None if extraction fails
        """
        if not url:
            return None
            
        try:
            # Extract the filename from the last part of the URL path
            match = re.search(r'/([^/]+)$', url)
            if match:
                # Decode URL-encoded characters (like %20 to space)
                return urllib.parse.unquote(match.group(1))
        except Exception:
            pass
        
        return None

    def _get_file_size(self, url, verify_ssl=True):
        """
        Check file size without downloading the full content by making a HEAD request.
        
        Args:
            url (str): URL of the file
            verify_ssl (bool): Whether to verify SSL certificates
            
        Returns:
            int or None: Size of the file in bytes, or None if size can't be determined
        """
        scraper = WebScraper()
        try:
            response = scraper.session.head(url, verify=verify_ssl, allow_redirects=True, timeout=10)
            if response.status_code == 200 and 'Content-Length' in response.headers:
                return int(response.headers['Content-Length'])
        except Exception:
            pass
        return None

    def download_files(self, base_folder="datasets", log_errors=False, skip_existing=False, verify_ssl=True, max_size=-1, request_timeout=30):
        """
        Downloads all files associated with the dataset.
        
        Args:
            base_folder (str): Base folder to store downloaded files (default: "datasets")
            log_errors (bool): Whether to log errors (default: False)
            skip_existing (bool): Whether to skip files that already exist locally (default: False)
            verify_ssl (bool): Whether to verify SSL certificates (default: True)
            max_size (int): Maximum file size in bytes to download, -1 means no limit (default: -1)
            request_timeout (int): Timeout in seconds for HTTP requests (default: 30)
            
        Returns:
            None
        """
        scraper = WebScraper()
        folder_name = os.path.join(base_folder, self.id)
        os.makedirs(folder_name, exist_ok=True)
        
        # Check if metadata has the expected structure
        if not self.metadata:
            if log_errors:
                dataset_identifier = f"Title: {self.title or 'Unknown'}, URL: {self.url or 'Unknown'} ID: {self.id}"
                log_error(f"No metadata available for dataset - {dataset_identifier}")
            #print(f"Warning: No metadata available for dataset {self.id}")
            # Save the dataset info even if no files are downloaded
            with open(os.path.join(folder_name, f"{self.id}.json"), 'w', encoding='utf-8') as json_file:
                json.dump(self.to_dict(), json_file, ensure_ascii=False, indent=4)
            return
            
        # Check if 'result' key exists
        if 'result' not in self.metadata or not self.metadata['result']:
            #print(f"Warning: No 'result' found in metadata for dataset {self.id}")
            # Save the dataset info even if no files are downloaded
            with open(os.path.join(folder_name, f"{self.id}.json"), 'w', encoding='utf-8') as json_file:
                json.dump(self.to_dict(), json_file, ensure_ascii=False, indent=4)
            return
            
        # Check if 'resources' key exists
        if 'resources' not in self.metadata['result'][0]:
            #print(f"Warning: No 'resources' found in metadata for dataset {self.id}")
            # Save the dataset info even if no files are downloaded
            with open(os.path.join(folder_name, f"{self.id}.json"), 'w', encoding='utf-8') as json_file:
                json.dump(self.to_dict(), json_file, ensure_ascii=False, indent=4)
            return
        
        resources = self.metadata['result'][0]['resources']
        
        for resource in resources:
            # Check if resource has required keys
            if 'url' not in resource:
                #print(f"Warning: Resource missing URL in dataset {self.id}")
                continue
                
            resource_url = resource['url']
            resource_format = resource.get('format', 'unknown')
            
            # Skip download if URL is empty
            if resource_url == '':
                #print(f"Skipping {resource.get('name', 'unnamed resource')} as URL is empty")
                continue
            
            # Extract filename from URL or fall back to resource name
            filename = self._extract_filename_from_url(resource_url)
            if not filename:
                # Fall back to original method
                resource_name = resource.get('name', f'file_{id(resource)}')
                file_extension = resource_format.lower()
                filename = f"{resource_name}.{file_extension}"
            
            # Ensure the filename is URL-decoded (in case it wasn't done in _extract_filename_from_url)
            filename = urllib.parse.unquote(filename)
            
            file_path = os.path.join(folder_name, filename)
            
            # Check if file exists and skip_existing is True
            if skip_existing and os.path.exists(file_path):
                #print(f"Skipping {filename} as it already exists locally")
                continue
            
            # Check file size if max_size is set
            if max_size > 0:
                try:
                    response = scraper.session.head(resource_url, verify=verify_ssl, timeout=request_timeout)
                    if "Content-Length" in response.headers:
                        file_size = int(response.headers["Content-Length"])
                        if file_size > max_size:
                            message = f"Skipping {filename} as its size ({file_size} bytes) exceeds the maximum size limit ({max_size} bytes)"
                            if log_errors:
                                log_error(message)
                            else:
                                print(message)
                            continue
                except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                    message = f"Warning: Could not check size of {filename} due to connection error: {str(e)}"
                    if log_errors:
                        log_error(message)
                    else:
                        print(message)
                    # Continue with download attempt anyway
                except Exception as e:
                    message = f"Warning: An unexpected error occurred while checking size of {filename}: {str(e)}"
                    if log_errors:
                        log_error(message)
                    else:
                        print(message)
                    # Continue with download attempt anyway
            response = scraper.get_response(resource_url, verify=verify_ssl, timeout=request_timeout)
            if response is not None and response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                
                time.sleep(5)  # Wait for 5 seconds before downloading the next file
            else:
                status = response.status_code if response else "None (request failed)"
                if log_errors:
                    log_error(f"Failed to download {filename}. Status code: {status}")
                else:
                    print(f"Failed to download {filename}. Status code: {status}")
        
        with open(os.path.join(folder_name, f"{self.id}.json"), 'w', encoding='utf-8') as json_file:
            json.dump(self.to_dict(), json_file, ensure_ascii=False, indent=4)

    def data(self, filename=None, file_index=0):
        """
        Load dataset files as pandas DataFrames.
        
        Args:
            filename (str, optional): Specific file to load. If None, loads the first available data file.
            file_index (int, optional): When multiple files are available and no filename is specified,
                                        determines which file to load (default: 0 - first file).
        
        Returns:
            pandas.DataFrame: The loaded dataset as a DataFrame
                
        Raises:
            FileNotFoundError: If the dataset directory or requested file doesn't exist
                and no downloadable resources are available
            ValueError: If the file format is not supported or if the file_index is out of range
        """
        # Build the path to the dataset directory
        dataset_dir = os.path.join('datasets', self.id)
        
        # Check if directory exists and search for local files
        local_files_exist = os.path.isdir(dataset_dir)
        data_files = []
        
        if local_files_exist:
            # Search for data files with common extensions
            for ext in ['.csv', '.xlsx', '.xls', '.json', '.parquet']:
                found_files = glob.glob(os.path.join(dataset_dir, f'*{ext}'))
                data_files.extend(found_files)
            
            # Filter out the dataset metadata JSON file and data dictionaries
            data_files = [f for f in data_files 
                         if not f.endswith(f"{self.id}.json") 
                         and "diccionario de datos" not in os.path.basename(f).lower()
                         and "Diccionario de datos" not in os.path.basename(f)
                         and "Diccionario De Datos" not in os.path.basename(f)]
        
        # If a specific filename is provided and exists locally
        if filename and local_files_exist:
            file_path = os.path.join(dataset_dir, filename)
            if os.path.isfile(file_path):
                return self._load_file_as_dataframe(file_path)
        
        # If no local files found or looking for a specific file that's not local,
        # check if we can download on-demand from metadata
        if not data_files or (filename and not os.path.isfile(os.path.join(dataset_dir, filename))):
            # Check if we have metadata with resources
            if self.metadata and 'result' in self.metadata and self.metadata['result'] and 'resources' in self.metadata['result'][0]:
                resources = self.metadata['result'][0]['resources']
                
                # Filter out data dictionaries
                data_resources = []
                for resource in resources:
                    resource_name = resource['name'].lower() if resource.get('name') else ''
                    resource_format = resource['format'].lower() if 'format' in resource else ''
                    if ("diccionario de datos" not in resource_name and 
                        "diccionario" not in resource_name and
                        resource_format != 'pdf'):
                        data_resources.append(resource)
                
                # If looking for a specific file by name
                if filename:
                    matching_resources = [r for r in data_resources 
                                         if r['name'] == filename or f"{r['name']}.{r['format'].lower()}" == filename]
                    if matching_resources:
                        return self._download_and_load_dataframe(matching_resources[0])
                
                # If there are data resources available
                elif data_resources:
                    # Check if file_index is valid
                    if file_index >= 0 and file_index < len(data_resources):
                        return self._download_and_load_dataframe(data_resources[file_index])
                    elif data_resources:
                        # If file_index is out of range, use the first resource
                        print(f"Warning: file_index {file_index} is out of range. Using first available resource.")
                        return self._download_and_load_dataframe(data_resources[0])
        
        # If we have local files, process them
        if data_files:
            # Check if file_index is valid for local files
            if file_index >= 0 and file_index < len(data_files):
                return self._load_file_as_dataframe(data_files[file_index])
            else:
                # If file_index is out of range, use the first file
                print(f"Warning: file_index {file_index} is out of range. Using first available file.")
                return self._load_file_as_dataframe(data_files[0])
        
        # If we reach here, we couldn't find or download any data files
        raise FileNotFoundError(f"No data files found locally or available for download in dataset {self.id}")

    def _download_and_load_dataframe(self, resource):
        """
        Download a resource and load it as a pandas DataFrame.
        
        Args:
            resource (dict): Resource metadata containing URL and format
            
        Returns:
            pandas.DataFrame: The loaded data
            
        Raises:
            ValueError: If file format is not supported or download fails
        """
        scraper = WebScraper()
        resource_url = resource['url']
        resource_format = resource['format'].lower() if 'format' in resource else ''
        
        # Determine format from URL if not specified
        if not resource_format:
            if resource_url.endswith('.csv'):
                resource_format = 'csv'
            elif resource_url.endswith('.xlsx') or resource_url.endswith('.xls'):
                resource_format = 'xlsx'
            elif resource_url.endswith('.json'):
                resource_format = 'json'
            elif resource_url.endswith('.parquet'):
                resource_format = 'parquet'
            else:
                resource_format = 'csv'  # Default assumption
        
        # Check if format is supported
        if resource_format not in ['csv', 'xlsx', 'xls', 'json', 'parquet']:
            raise ValueError(f"Unsupported file format: {resource_format}")
        # Download the file
        response = scraper.get_response(resource_url)
        if response is None:
            raise ValueError("Failed to download resource. Response was None")
        if response.status_code != 200:
            raise ValueError(f"Failed to download resource. Status code: {response.status_code}")
        
        # Create in-memory file object
        content = response.content
        content = response.content
        
        # For CSV files, use our existing encoding and separator detection logic
        if resource_format == 'csv':
            # Try multiple encodings and separators
            encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
            separators = [',', ';', '\t', '|']
            
            # First try different encodings with default separator
            for encoding in encodings:
                try:
                    return pd.read_csv(io.BytesIO(content), encoding=encoding)
                except UnicodeDecodeError:
                    continue
                except pd.errors.ParserError:
                    # If it's a parser error, we might have the right encoding but wrong separator
                    pass
            
            # If we reach here, try different separators with each encoding
            for encoding in encodings:
                for sep in separators:
                    try:
                        return pd.read_csv(io.BytesIO(content), encoding=encoding, sep=sep)
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
            
            # Final fallback - try to read with the most permissive settings
            return pd.read_csv(io.BytesIO(content), encoding='latin1', sep=None, engine='python')
        
        elif resource_format in ['xlsx', 'xls']:
            return pd.read_excel(io.BytesIO(content))
        elif resource_format == 'json':
            return pd.read_json(io.BytesIO(content))
        elif resource_format == 'parquet':
            return pd.read_parquet(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported file format: {resource_format}")

    def _load_file_as_dataframe(self, file_path):
        """
        Load a file as a pandas DataFrame based on its extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            pandas.DataFrame: The loaded data
            
        Raises:
            ValueError: If the file format is not supported
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            # Try multiple encodings and separators
            encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
            separators = [',', ';', '\t', '|']
            
            # First try different encodings with default separator
            for encoding in encodings:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except UnicodeDecodeError:
                    continue
                except pd.errors.ParserError:
                    # If it's a parser error, we might have the right encoding but wrong separator
                    pass
            
            # If we reach here, try different separators with each encoding
            for encoding in encodings:
                for sep in separators:
                    try:
                        return pd.read_csv(file_path, encoding=encoding, sep=sep)
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
            
            # If all attempts fail, try to convert the file to UTF-8 and then read it
            try:
                # Read the file in binary mode
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Try to decode with a fallback encoding
                decoded = content.decode('latin1', errors='replace')
                
                # Create a temporary UTF-8 file
                utf8_path = file_path + '.utf8'
                with open(utf8_path, 'w', encoding='utf-8') as f:
                    f.write(decoded)
                
                # Try to read the UTF-8 file with different separators
                for sep in separators:
                    try:
                        df = pd.read_csv(utf8_path, encoding='utf-8', sep=sep)
                        # If successful, clean up and return
                        os.remove(utf8_path)
                        return df
                    except pd.errors.ParserError:
                        continue
                
                # Clean up if all separators failed
                if os.path.exists(utf8_path):
                    os.remove(utf8_path)
                    
            except Exception as e:
                # If all else fails, raise a detailed error
                raise ValueError(f"Could not read CSV file {file_path}: {str(e)}")
            
            # Final fallback - try to read with the most permissive settings
            return pd.read_csv(file_path, encoding='latin1', sep=None, engine='python')
            
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        elif file_ext == '.json':
            return pd.read_json(file_path)
        elif file_ext == '.parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def get_files_dict(self):
        """
        Returns a dictionary of files available in the dataset.
        
        Returns:
            dict: Dictionary with file names as keys and file information as values
        """
        if not self.metadata or 'result' not in self.metadata or not self.metadata['result'] or 'resources' not in self.metadata['result'][0]:
            return {}
                
        resources = self.metadata['result'][0]['resources']
        files_dict = {}
        
        for i, resource in enumerate(resources):
            name = resource.get('name', f'file_{i}')
            # Make sure keys are unique by appending an index if duplicated
            key = name
            counter = 1
            while key in files_dict:
                key = f"{name}_{counter}"
                counter += 1
                    
            files_dict[key] = {
                'format': resource.get('format', ''),
                'url': resource.get('url', '')
            }
        
        return files_dict

    def format_files(self):
        """
        Returns a formatted string representation of the files available in the dataset.
        
        Returns:
            str: Formatted string showing files details
        """
        files_dict = self.get_files_dict()  # Updated to use get_files_dict()
        
        if not files_dict:
            return "No files available for this dataset."
        
        result = f"\n=== Archivos del dataset: {self.title} ===\n"
        
        for i, (name, info) in enumerate(files_dict.items(), 1):
            format_str = info['format'].upper() if info['format'] else 'UNKNOWN'
            result += f"\n{i}. {name} ({format_str})"
            result += f"\n   URL: {info['url']}"
            result += "\n"  # Empty line for better readability
        
        return result

    def print_files(self):
        """
        Pretty prints the files available in the dataset.
        
        Returns:
            None: This method prints to stdout and doesn't return a value
        """
        print(self.format_files())

    @property
    def files(self):
        """
        Property that returns a formatted string representation of files.
        
        Returns:
            str: Formatted string showing files details
        """
        return self.format_files()