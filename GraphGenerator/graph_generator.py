__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

class GraphGenerator:
    def __init__(self, master_config=None, logger=None) -> None:
        """
        The main objective of this class is to build the graph database nodes and relationships on the graph database end. It has extreme support
        to take care of multiple databases such as Neo4j Graph DB, Arango Graph DB, etc

        master_config: configuration for graph generator module
        logger: logger object
        """

        self._master_config = master_config
        self._logger = logger

        # Configuration based extraction
        self._graph_selected = self._master_config['graphical_configurations']['selected_graph_database']

        if self._graph_selected.__eq__('neo4j'):
            self._graph_connection = Neo4JConnection()