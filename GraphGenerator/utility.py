__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

import os
import yaml

from yaml.loader import SafeLoader

def read_config(config_file_path=None):
    if config_file_path is not None:
        with open(config_file_path) as f:
            data = yaml.load(f, Loader=SafeLoader)
        return data