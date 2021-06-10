from pymorphy2 import MorphAnalyzer
from pymorphy2.tokenizers import simple_word_tokenize
import spacy
from cltk import NLP


class Preprocesser:
    """Wrapper class for all morphology preprocessing.

    Attributes:
        language: language of corpus being processed
    """

    def __init__(self, language):
        self.language = language
        self.spacy_analyzers = {
            "shake": "en_core_web_sm",
            "ger": "de_core_news_sm",
            "ita": "it_core_news_sm",
            "span": "es_core_news_sm"
        }
        self.cltk_analyzers = {
            "rom": "lat",
            "greek": "grc"
        }
        if language == "rus":
            self.analyzer = MorphAnalyzer()
        elif language in self.spacy_analyzers.keys():
            self.analyzer = spacy.load(self.spacy_analyzers[language])
        elif language in self.cltk_analyzers.keys():
            self.analyzer = NLP(language=self.cltk_analyzers[language])

    def lemmatize(self, line):
        self.lemmas = []
        play_lemmas = []
        if self.language == "rus":
            play_lemmas = [self.analyzer.parse(token)[0].normal_form
                             for token in simple_word_tokenize(line)]
        elif self.language in self.spacy_analyzers.keys():
            play_lemmas = [token.lemma_ for token in self.analyzer(line)]
        elif self.language in self.cltk_analyzers.keys():
            print(self.language)
            play_lemmas = self.analyzer.analyze(text=line).lemmata
        self.lemmas += play_lemmas
        return " ".join(play_lemmas)

    def pos(self, line):
        self.pos_dict = {}
        # parsing
        if self.language == "rus":
            play_pos = [self.analyzer.parse(token)[0].tag.POS
                        for token in simple_word_tokenize(line)]
        elif self.language in self.spacy_analyzers.keys():
            play_pos = [token.pos_ for token in self.analyzer(line)]
        elif self.language in self.cltk_analyzers.keys():
            print(self.language)
            play_pos = self.analyzer.analyze(text=line).pos
        return play_pos

    def count_items(self, play_items):
        item_dict = {}
        for item in play_items.split():
            if item not in item_dict:
                item_dict[item] = 1
            else:
                item_dict[item] += 1
        # percentages/shares instead of absolute values
        for item in item_dict:
            item_dict[item] = item_dict[item]/len(play_items)
        return item_dict
