__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

class PatternFinder:
    def __init__(self, master_config=None, logger=None) -> None:
        """
        This main objective of this class is to find matching patterns in sentence occurrences and match them with accepted list of patterns for
        generating the graphical connections e.g.
        EVE
        EVEE
        ENV where E is entity, V is verb and N is noun
        
        master_config: configuration for graph generator module
        logger: logger object
        """

        self._master_config = master_config
        self._logger = logger

        # Configuration based extraction
        self._acceptable_pattern_list = self._master_config['graphical_configurations']['pattern_match'] #this is the acceptable pattern of sentences.
        self._logger.info('GG: Pattern Finder based configurations loaded successfully')

        self._logger.info('GG: Pattern Finder initialized successfully')