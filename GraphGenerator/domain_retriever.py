__author__ = "konwar.m"
__copyright__ = "Copyright 2022, AI R&D"
__credits__ = ["konwar.m"]
__license__ = "Individual Ownership"
__version__ = "1.0.1"
__maintainer__ = "konwar.m"
__email__ = "rickykonwar@gmail.com"
__status__ = "Development"

import os
import nltk
import spacy
import pandas as pd

from tqdm import tqdm
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

from utility import read_config, write_yaml

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
        self._logger.info('GG: Domain retriever based nlp pipeline intialized successfully')

        # Retrieving english stopwords
        self._stop_words = set(stopwords.words('english'))
        self._logger.info('GG: Domain retriever based stopwords loaded successfully')

        # Configuration based extraction
        self._content_col_name = self._master_config['dataset_configurations']['content_col_name']
        self._date_col_name = self._master_config['dataset_configurations']['date_col_name']
        self._most_common_words_count = int(self._master_config['dataset_configurations']['most_common_words_count'])
        self._use_optimal_most_common_count = (self._master_config['dataset_configurations']['use_optimal_most_common_count'] == True)
        self._common_word_coverage_score = float(self._master_config['dataset_configurations']['common_word_coverage_score'])
        self._dump_domain_word_lists = (self._master_config['dataset_configurations']['dump_domain_words'] == True)
        self._preload_domain_word_lists = (self._master_config['dataset_configurations']['preload_domain_words'] == True)
        self._domain_collection_path = self._master_config['dataset_configurations']['extra_domain_words_path']
        self._logger.info('GG: Domain retriever based configurations loaded successfully')

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

    def get_optimal_most_common_count(self, word_counter : Counter):
        """
        This method decides the optimal most common count for the word counter
        To cover 70% of the word set
        """
        self._logger.info("GG: Domain word extractor: optimal common counter started")

        total_occurrences = sum([w[1] for w in word_counter.most_common()])
        current_occurrences = 0
        current_count = 0
        for w in word_counter.most_common():
            current_occurrences += w[1]
            current_count += 1
            if(float(current_occurrences / total_occurrences) > self._common_word_coverage_score):
                break

        self._logger.info("GG: Domain word extractor: optimal common counter completed successfully")
        self._logger.info(str.format("Coverage: total_occurrences:{}, covered_occurrences:{}, total_count of words:{}, considered count: {}", total_occurrences, current_occurrences, len(word_counter), current_count))

        return current_count

    def domain_words_extractor(self, input_file_path=None):
        """
        This method helps extract domain specific words and form an resultant dictionary at the end.
        """
        self._logger.info('GG: Domain word extraction started')

        def preload_domain_words():
            if os.path.exists(self._domain_collection_path):
                data = read_config(config_file_path=self._domain_collection_path)
                
                self._logger.info('GG: Preloading of domain words extracted')
                return data

        if self._preload_domain_word_lists:
            return preload_domain_words()

        df_input = pd.read_csv(input_file_path)
        domain_words_dict, final_domain_words_dict = {'nouns':[], 'verbs':[], 'propernouns':[]}, {'nouns':[], 'verbs':[], 'propernouns':[]}

        # Extracting verbs, nouns and propernouns from textual content
        for index, row_data in tqdm(df_input.iterrows(), total=df_input.shape[0], desc='Extracting domain words'):
            try:
                text_content = row_data[self._content_col_name].lower()
                tokenized_content = [w for w in word_tokenize(text_content) if not w in self._stop_words and not w in symbol_list]

                # Extracting POS information for toeknized content
                pos_content = self._nlp_pipeline(' '.join(tokenized_content))

                # Extracting only nouns, verbs and proper nouns from POS information for each token
                for token in pos_content:
                    if token.pos_.__eq__('NOUN'):
                        domain_words_dict['nouns'].append(token.text)
                    elif token.pos_.__eq__('PROPN'):
                        domain_words_dict['propernouns'].append(token.text)
                    elif token.pos_.__eq__('VERB'):
                        domain_words_dict['verbs'].append(token.text)

            except Exception as ex:
                print(ex)
                self._logger.error('Caught exception while extracting domain specific words: %s' %(str(ex)))
                continue
        self._logger.info('GG: POS data of domain specific words extracted successfully')
        

        # Extract the counter for each word in the domain dict
        verb_counter = Counter(domain_words_dict['verbs'])
        noun_counter = Counter(domain_words_dict['nouns'])   
        propnoun_counter = Counter(domain_words_dict['propernouns'])

        # Extract the optimal counted list
        optimal_most_common_noun_count = self.get_optimal_most_common_count(noun_counter) if self._use_optimal_most_common_count else self._most_common_words_count
        optimal_most_common_propernoun_count = self.get_optimal_most_common_count(propnoun_counter) if self._use_optimal_most_common_count else self._most_common_words_count
        optimal_most_common_verb_count = self.get_optimal_most_common_count(verb_counter) if self._use_optimal_most_common_count else self._most_common_words_count
        self._logger.info('GG: Optimal Counter for POS data information of domain specific words is applied successfully')

        # Retain only those words which justifies the common word counter score
        final_domain_words_dict['nouns'] = [w[0] for w in noun_counter.most_common(optimal_most_common_noun_count)]
        final_domain_words_dict['propernouns'] = [w[0] for w in propnoun_counter.most_common(optimal_most_common_propernoun_count)]
        final_domain_words_dict['verbs'] = [w[0] for w in verb_counter.most_common(optimal_most_common_verb_count)]
        self._logger.info('GG: Final domain specific words are extracted successfully')

        # Save the domain specific dictionary as yaml file
        if self._dump_domain_word_lists:
            write_yaml(file_path='domain_related_words.yaml', data_dict=final_domain_words_dict)
            self._logger.info('GG: Final domain specific words file written successfully')

        self._logger.info('GG: Domain word extraction completed successfully')

        return final_domain_words_dict