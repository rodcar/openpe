import json
import os
from .webscraper import WebScraper
import time
import pandas as pd
import glob

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
            ValueError: If the file format is not supported
        """
        # Build the path to the dataset directory
        dataset_dir = os.path.join('datasets', self.id)
        
        if not os.path.isdir(dataset_dir):
            raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
        
        # If a specific filename is provided
        if filename:
            file_path = os.path.join(dataset_dir, filename)
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            return self._load_file_as_dataframe(file_path)
        
        # Search for data files with common extensions
        data_files = []
        for ext in ['.csv', '.xlsx', '.xls', '.json', '.parquet']:
            found_files = glob.glob(os.path.join(dataset_dir, f'*{ext}'))
            #print(f"Found files with extension {ext}: {found_files}")
            data_files.extend(found_files)
        
        # Filter out the dataset metadata JSON file and data dictionaries
        data_files = [f for f in data_files 
                     if not f.endswith(f"{self.id}.json") 
                     and "diccionario de datos" not in os.path.basename(f).lower()
                     and "Diccionario de datos" not in os.path.basename(f)]
        #print(f"Filtered data files: {data_files}")
        
        if not data_files:
            raise FileNotFoundError(f"No data files found in {dataset_dir}")
        
        # If there's only one data file, return it as a DataFrame
        if len(data_files) == 1:
            #print(f"Only one data file found: {data_files[0]}")
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
            # Try different encodings if one fails
            try:
                return pd.read_csv(file_path)
            except UnicodeDecodeError:
                return pd.read_csv(file_path, encoding='latin1')
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        elif file_ext == '.json':
            return pd.read_json(file_path)
        elif file_ext == '.parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")