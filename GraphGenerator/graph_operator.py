__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

import copy

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
        
        # Graph Operator supporting modules
        self._entity_extractor = entity_extractor
        self._pos_identifier = pos_identifier
        self._domain_retriever = domain_retriever
        self._pattern_finder = pattern_finder
        self._graph_generator = graph_generator
        self._logger.info('GG: Graph operator supporting modules loaded successfully')

        # Configuration based extraction / Graph specific variables
        self._dump_domain_words = (self._master_config['dataset_configurations']['dump_domain_words'] == 'True')
        self._content_col_name = self._master_config['dataset_configurations']['content_col_name']
        self._graph_nodes = ['Person', 'Organization', 'Object', 'Location']
        self._domain_words = {'nouns':[], 'verbs':[], 'propnouns':[]}
        self._node_entity_mapping = self._extract_node_entity_mapping()

        self._logger.info('GG: Graph operator based initialized successfully')

    def _extract_node_entity_mapping(self) -> dict():
        """
        This method extracts full mapping of node type and entity type

        returns:
        Dictionary of E and N based items for specific patterns
        """
        return {
            "E": {
                "B-ORG": "Organization",
                "I-ORG" : "Organization",
                "B-PER": "Person",
                "I-PER" : "Person",
                "B-MISC": "Object",
                "I-MISC" : "Object",
                "B-LOC": "Location",
                "I-LOC" : "Location",
            },
            "N" : "Object"
        }

    def process_input(self) -> None:
        """
        This method starts the file processing and calls the entire pipeline starting with entity extraction, pos identifier, domain word retriever and graph generation
        """
        try:
            # Extracting input file path from master configuration
            input_file_path = self._master_config['dataset_configurations']['data_file_path'] if self._master_config['dataset_configurations']['data_file_path'] != '' else None
            if input_file_path is None:
                self._logger.error('Input file path is not existing. Please provide and retry again')
                return

            # Extracting domain specific terms
            self._domain_words = self._domain_retriever.domain_words_extractor(input_file_path=input_file_path)

            # Converting domain specific terms datastructures to set for easy computation
            self._domain_nouns_set = set(self._domain_words['nouns'])
            self._domain_verbs_set = set(self._domain_words['verbs'])
            
            # Setting up graoh schema
            self.setup_graph_schema()

        except Exception as ex:
            print(ex)
            self._logger.error('Caught error while processing the input data: %s' %(str(ex)))

    def setup_graph_schema(self):
        """
        This method is responsible for executing queries from domain words extracted and setting up the graph DB
        """
        # Selected graphical nodes to be created
        node_list = copy.deepcopy(self._graph_nodes)
        node_infos = [{'name':entity_name} for entity_name in node_list]
        
        # Selected graphical relationships to be created
        verb_list = copy.deepcopy(self._domain_words['verbs'])
        relationship_infos = [{'name':relationship_name} for relationship_name in verb_list]