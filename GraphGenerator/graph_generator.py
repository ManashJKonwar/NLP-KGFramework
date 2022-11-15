__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

import copy

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
        self._graph_host_name = self._master_config['graphical_configurations']['host_name']
        self._graph_user_name = self._master_config['graphical_configurations']['user_name']
        self._graph_password = self._master_config['graphical_configurations']['password']
        self._graph_name = self._master_config['graphical_configurations']['graph_name']
        self._logger.info('GG: Graph generator based configurations loaded successfully')

        if self._graph_selected.__eq__('neo4j'):
            self._graph_connector = Neo4JConnection(
                                        host_name=self._graph_host_name,
                                        user_name=self._graph_user_name,
                                        password=self._graph_password,
                                        graph_name=self._graph_name
                                    )
        
        self._logger.info('GG: Graph generator intialized successfully')

    def generate_graph_schema(self, node_infos, relationship_infos):
        """
        This method is to setup the graph schema for given nodal infos and relationship infos
        """
        # Checks and create the graph schema if it does not exists
        if self._graph_selected.__eq__('neo4j'):
            # Uncomment for enterprise version
            # self._graph_connector.query("CREATE OR REPLACE DATABASE %s" %(self._graph_name))
            # self._logger.info('GG: Graph created successfully')

            graph_selected_query = """
            SHOW DATABASE %s YIELD * RETURN count(*) as count
            """ %(self._graph_name)
            response = self._graph_connector.query(query=graph_selected_query)

            if response[0][0]==1:
                self._logger.info('GG: Graph Database exists')
            else:
                self._logger.error('GG: Graph Database does not exist')
                return

        # Generate the node level indices
        self.generate_nodes_schema(node_infos)

    def generate_nodes_schema(self, node_infos):
        """
        This method creates the initial nodes (vertices) with the given list of node_infos
        """
        self._logger.info('GG: Generating node level vertices started')

        new_node_available = False
        query_list = []
        node_to_be_added = []

        if self._graph_selected.__eq__('neo4j'):
            existing_nodes_query = """
            MATCH (n) WHERE n.name =~ '(.+)\(.+\)' return n
            """
            response = self._graph_connector.query(query=existing_nodes_query, db=self._graph_name)
            if isinstance(response, list) and len(list) == 0:
                pass
            else:
                existing_nodes = copy.deepcopy(response)

            # Checking if the new nodes to be added are already present and select
            # only those which needs to be freshly created inside the graph
            query_list = []
            to_be_added = []

            for node_info in node_infos:
                #skip this if it already exists.
                if str.lower(node_info['name']) in existing_nodes:
                    continue
                query_list.append(str.format('CREATE VERTEX {}(PRIMARY_ID id STRING, name STRING) WITH STATS="OUTDEGREE_BY_EDGETYPE", PRIMARY_ID_AS_ATTRIBUTE="true"', node_info['name']))
                new_node_available = True
                node_to_be_added.append(node_info)

            full_query = "\n".join(query_list)
            full_query = "USE GLOBAL" + "\n" + full_query
            self._logger.info("creating vertex types globally.")
            result = self.connection.gsql(full_query)

            self._logger.info(str.format("result: {}", result))

        if new_node_available:
            #adding the created nodes into the graph
            self._logger.info("adding new nodes to graph's schema.")
            self.add_nodes_to_graph_schema(node_to_be_added)


class Neo4JConnection:
    def __init__(self, **kwargs):
        """
        The main objective of this class is to initiate the neo4j python connector object based on configuration of graph database

        host_name(str): neo4j instance to connect to
        user_name(str): username for accessing the graph db
        password(str): password for accessing the graph db
        graph_name(str): graph name to create
        """
        self._host_name = kwargs.get('host_name')
        self._user_name = kwargs.get('user_name')
        self._password = kwargs.get('password')
        self._graph_name = kwargs.get('graph_name')
        self._db_driver = self._get_connector()

    def close(self):
        if self._db_driver is not None:
            self._db_driver.close()
    
    def query(self, query, db=None):
        assert self._db_driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self._db_driver.session(database=db) if db is not None else self._db_driver.session() 
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
            return response

    def get_db_driver(self):
        """
        This method is a getter function to retrieve the neo 4j connector object
        
        return:
        neo 4j connector object
        """
        return self._db_driver

    def _get_connector(self):
        """
        This method intiatees the neo 4j connector object based on provided configurations

        return: 
        neo 4j connector object
        """
        try:
            from neo4j import GraphDatabase
            return GraphDatabase.driver(self._host_name, auth=(self._user_name, self._password))
        except Exception as ex:
            print(ex)
            return None