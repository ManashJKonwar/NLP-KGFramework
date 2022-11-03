__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

import spacy

class PosIdentifier:
    def __init__(self, master_config=None, logger=None) -> None:
        """
        This main objective of this class is to identify all possible part of speech for each token in the unstructured
        data. This is achieved by making use of spacy.
        
        master_config: configuration for graph generator module
        logger: logger object
        """

        self._master_config = master_config
        self._logger = logger

        # Initialize pos identifying pipeline
        self._pos_pipeline = self._load_spacy_model(
                                model_name='en_core_web_sm', 
                                exclude_list=[]
                            )
        self._logger.info('GG: Part of Speech pipeline intialized successfully')

    def _load_spacy_model(self, model_name='en_core_web_sm', exclude_list=None):
        """
        This method loads spacy model based on language name else download it and
        load it
        model_name (str): model name to load
        exclude_list (list, str): The model components to exclude for loaded language model
        """
        excluded_steps = ["tagger", "parser", "ner", "entity_linker", 
                        "entity_ruler", "textcat", "morphologizer",
                        "attribute_ruler", "senter", "sentencizer", 
                        "token2vec", "transformer"] if exclude_list is None else exclude_list
        try:
            spacy_model = spacy.load(model_name, exclude=excluded_steps)
        except OSError:
            spacy.cli.download(model_name)
            spacy_model = spacy.load(model_name, exclude=excluded_steps)
        finally:
            return spacy_model