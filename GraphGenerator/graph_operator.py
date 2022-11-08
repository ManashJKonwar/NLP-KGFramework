__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

from entity_extractor import EntityExtractor
from pos_identifier import PosIdentifier
from domain_retriever import DomainRetriever
from pattern_finder import PatternFinder
from graph_generator import GraphGenerator

class GraphOperator:
    def __init__(self, 
                master_config, 
                logger, 
                entity_extractor: EntityExtractor,
                pos_identifier: PosIdentifier,
                domain_retriever: DomainRetriever,
                pattern_finder: PatternFinder,
                graph_generator: GraphGenerator
                ) -> None:
        """
        The main objective of this class is to perform state of are NLP operations for making the input data ready to be ingested to the neo4j graph instance.
        The operations are as follows:
        a. extract entities from given text
        b. extract pos of given text
        c. extract domain speciic terminologies
        d. generate the graph relationships among these entities

        master_config: configuration for graph generator module
        logger: logger object
        """

        self._master_config = master_config
        self._logger = logger
        self._entity_extractor = entity_extractor
        self._pos_identifier = pos_identifier
        self._domain_retriever = domain_retriever
        self._pattern_finder = pattern_finder
        self._graph_generator = graph_generator

        self._logger.info('GG: Graph operator based initialized successfully')