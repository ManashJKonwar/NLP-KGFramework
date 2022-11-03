__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

import os
import sys
import logging, logging.config

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Loggers.generate_logger import graph_logger
from utility import read_config
from entity_extractor import EntityExtractor
from pos_identifier import PosIdentifier

# Creates the logger base directory if it does not exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configuring graph generator based logger
logging.config.dictConfig(graph_logger)

# Reading configurations and setting relevant logger object
config = read_config(os.path.join('GraphGenerator', 'config.yaml')) # Reading graph generator config file
logger = logging.getLogger('graph_generator_handler') # Retrieve Logger Handler

def graph_generator_initialize():
    logger.info('App Start: Graph Generate Module initializing.')

def graph_generator_start():
    logger.info('Graph Generator Module has been invoked')
    
    # Initiating the entity extraction module
    entity_extractor = EntityExtractor(master_config=config, logger=logger)
    # Initiating the pos module
    pos_identifier = PosIdentifier(master_config=config, logger=logger)

if __name__ == "__main__":
    graph_generator_initialize()
    graph_generator_start()