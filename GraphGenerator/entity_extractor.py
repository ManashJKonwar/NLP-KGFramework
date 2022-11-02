__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

class EntityExtractor:
    def __init__(self, master_config=None, logger=None) -> None:
        """
        This main objective of this class is to extract all possible entities available in the unstructured
        data. This is achieved by making use of BERT based models which are trained specifically for extarcting 
        entities.
        
        master_config: configuration for graph generator module
        logger: logger object
        """

        self._master_config = master_config
        self._logger = logger

        # Extracts entity based tokenizer and model objects
        self._entity_tokenizer, self._entity_model = self._retrieve_model_essentials()
        self._logger.info('GG: Entity extractor tokenizer and model intialized successfully')

        # Initialize entity extraction pipeline
        self._ner_pipeline = pipeline('ner', model=self._entity_model, tokenizer=self._entity_tokenizer)
        self._logger.info('GG: Entity extractor pipeline intialized successfully')

        # Intialize confidence score for ner
        self._confidence_score = float(self._master_config['dataset_configurations']['entity_confidence_score']) # 0.7
        self._logger.info('GG: Entity extractor intialized successfully')

    def _retrieve_model_essentials(self):
        """
        This method is responsible to intialize the bert tokenizer and also load the configured model
        responsible for extracting entities.

        return:
        tokenizer (bert tokenizer object)
        model (bert entity extractor model)
        """
        tokenizer, model = None, None
        try:
            if self._master_config['model_configurations']['load_bert_from_local']:
                tokenizer = AutoTokenizer.from_pretrained(self._master_config['model_configurations']['local_bert_model_path'], local_files_only=True)
                model = AutoModelForTokenClassification.from_pretrained(self._master_config['model_configurations']['local_bert_model_path'], local_files_only=True)
            else:
                tokenizer = AutoTokenizer.from_pretrained(self._master_config['model_configurations']['remote_bert_model_path'])
                model = AutoModelForTokenClassification.from_pretrained(self._master_config['model_configurations']['remote_bert_model_path'])
        except Exception as ex:
            print(ex)
            self._logger.error('GG: Caught Exception while retrieving model related files: %s' %(str(ex)))
        finally:
            return tokenizer, model