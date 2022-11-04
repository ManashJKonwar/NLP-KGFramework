__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

import nltk
import spacy

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# List of symbols to not consider for tokenization
symbol_list = ['`','~', '!','@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '[', '}', ']', '|', '\\', ':', ';', '"', '\'',',', '<', '.', '>', '?', '/' ]

# Install nltk related resource if it is not installed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try: 
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class DomainRetriever:
    def __init__(self, master_config=None, logger=None) -> None:
        """
        This main objective of this class is to go through a given full-dataset and 
        understand the most used common words in order to create a list of domain relationships 
        and nouns for the graph.
        
        master_config: configuration for graph generator module
        logger: logger object
        """

        self._master_config = master_config
        self._logger = logger

        # Initialize nlp pipeline
        self._nlp_pipeline = self._load_spacy_model(
                                model_name='en_core_web_sm', 
                                exclude_list=[]
                            )
        self._logger.info('GG: Part of Speech pipeline intialized successfully')

        # Retrieving english stopwords
        self._stop_words = set(stopwords.words('english'))
        self._logger.info('GG: Stopwords loaded successfully')

        # Configuration based extraction
        self._content_name = self._master_config['dataset_configurations']['content_name']
        self._most_common_words_count = int(self._master_config['dataset_configurations']['most_common_words_count'])
        self._dump_domain_word_lists = (self._master_config['dataset_configurations']['dump_domain_words'] == 'True')
        self._preload_domain_word_lists = (self._master_config['dataset_configurations']['preload_domain_words'] == 'True')
        self._domain_collection_path = self._master_config['dataset_configurations']['extra_domain_words_path']
        self._logger.info('GG: Configuration loaded successfully')

        self._logger.info('GG: Domian retriever intialized successfully')

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