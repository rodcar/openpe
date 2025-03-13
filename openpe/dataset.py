import json
import os
from .webscraper import WebScraper
import time
import pandas as pd
import glob
import io  # Add this import

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
        self.data_dictionary = data_dictionary

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

    def to_dict(self):
        """
        Convert the Dataset object to a JSON serializable dictionary.
        
        Returns:
            dict: A dictionary representation of the Dataset.
        """
        # Create a base dictionary from the object's attributes
        dataset_dict = {k: v for k, v in self.__dict__.items()}
        
        # Handle any non-serializable objects or custom serialization logic
        # Add custom serialization for specific attributes if needed
        
        return dataset_dict

    def download_files(self, base_folder="datasets"):
        scraper = WebScraper()
        folder_name = os.path.join(base_folder, self.id)
        os.makedirs(folder_name, exist_ok=True)
        
        for resource in self.metadata['result'][0]['resources']:
            resource_url = resource['url']
            resource_format = resource['format']
            resource_name = resource['name']
            
            response = scraper.get_response(resource_url)
            if response.status_code == 200:
                file_extension = resource_format.lower()
                file_path = os.path.join(folder_name, f"{resource_name}.{file_extension}")
                
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                
                time.sleep(5)  # Wait for 5 seconds before downloading the next file
            else:
                print(f"Failed to download {resource_name}. Status code: {response.status_code}")
        
        with open(os.path.join(folder_name, f"{self.id}.json"), 'w', encoding='utf-8') as json_file:
            json.dump(self.to_dict(), json_file, ensure_ascii=False, indent=4)

    def data(self, filename=None):
        """
        Load dataset files as pandas DataFrames.
        
        Args:
            filename (str, optional): Specific file to load. If None, loads all data files.
        
        Returns:
            pandas.DataFrame: If there's only one data file and no filename specified
            dict: Mapping of filenames to pandas DataFrames if multiple files are found
            pandas.DataFrame: The specific file requested if filename is provided
            
        Raises:
            FileNotFoundError: If the dataset directory or requested file doesn't exist
                and no downloadable resources are available
            ValueError: If the file format is not supported
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
                    if "diccionario de datos" not in resource_name and "diccionario" not in resource_name:
                        data_resources.append(resource)
                
                # If looking for a specific file by name
                if filename:
                    matching_resources = [r for r in data_resources 
                                         if r['name'] == filename or f"{r['name']}.{r['format'].lower()}" == filename]
                    if matching_resources:
                        return self._download_and_load_dataframe(matching_resources[0])
                
                # If no specific file is requested and there's only one data resource
                elif len(data_resources) == 1:
                    return self._download_and_load_dataframe(data_resources[0])
                
                # If multiple data resources
                elif data_resources:
                    data_dict = {}
                    for resource in data_resources:
                        try:
                            resource_name = f"{resource['name']}.{resource['format'].lower()}"
                            data_dict[resource_name] = self._download_and_load_dataframe(resource)
                        except Exception as e:
                            print(f"Error downloading {resource['name']}: {e}")
                    return data_dict
        
        # If we have local files, process them
        if data_files:
            if len(data_files) == 1:
                return self._load_file_as_dataframe(data_files[0])
            
            # If there are multiple data files, return a dictionary of DataFrames
            data_dict = {}
            for file_path in data_files:
                filename = os.path.basename(file_path)
                try:
                    data_dict[filename] = self._load_file_as_dataframe(file_path)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            
            return data_dict
        
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
        if response.status_code != 200:
            raise ValueError(f"Failed to download resource. Status code: {response.status_code}")
        
        # Create in-memory file object
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