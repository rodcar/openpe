# Initialize your library

from .categories import Categories
from .errors import log_error  # Add this import
from .dataset import Dataset
from .webscraper import WebScraper
from .utils import to_json, from_json
from .module import get_dataset, get_datasets, expand_datasets, download_dataset, save, load, expand_dataset, stats

import os
import json