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
from domain_retriever import DomainRetriever
from pattern_finder import PatternFinder
from graph_generator import GraphGenerator
from graph_operator import GraphOperator

entity_extractor, pos_identifier, domain_retriever, pattern_finder, graph_generator = None, None, None, None, None

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

def initialize_supporting_modules():
    logger.info('App Start: Graph Generator Supporting modules initialization started')
    
    global entity_extractor, pos_identifier, domain_retriever, pattern_finder, graph_generator
    # Initiating the entity retrieval module
    entity_extractor = EntityExtractor(master_config=config, logger=logger)
    # Initiating the pos retrieval module
    pos_identifier = PosIdentifier(master_config=config, logger=logger)
    # Intiating the domain retrieval module
    domain_retriever = DomainRetriever(master_config=config, logger=logger)
    # Initiating the pattern finder module
    pattern_finder = PatternFinder(master_config=config, logger=logger)
    # Intiating the graph generator module
    graph_generator = GraphGenerator(master_config=config, logger=logger)

    logger.info('App Start: Graph Generator Supporting modules initialized successfully')

def generate_graph_from_input():
    logger.info('App Start: Graph Operator initialization started')

    global entity_extractor, pos_identifier, domain_retriever, pattern_finder, graph_generator
    graph_operator = GraphOperator(
                        master_config=config, 
                        logger=logger, 
                        entity_extractor=entity_extractor, 
                        pos_identifier=pos_identifier, 
                        domain_retriever=domain_retriever, 
                        pattern_finder=pattern_finder, 
                        graph_generator=graph_generator
                    )
    logger.info('App Start: Graph Operator initialized successfully')

    graph_operator.process_input()
    logger.info('App Start: Graph data generated successfully')

if __name__ == "__main__":
    graph_generator_initialize()
    initialize_supporting_modules()
    generate_graph_from_input()