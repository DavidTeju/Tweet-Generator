import os
import random
from collections import Counter, defaultdict
from itertools import count
from os import path

import cloudpickle


class NgramModel:
    start = "<start>"
    end = "<end>"

    def __init__(self, n: int, name="", auto_pickle=False):
        """
        Create a new model

        :param n: n in n-gram, number of words in ngram
        :param name: name of model. Will be used to name pickle file
        :param auto_pickle: True if model should auto-backup after every call to self.train()
        """
        self.n = n
        self.pickle_path = self.pathify(name or self.gen_pickle_name())
        if path.exists(self.pickle_path):  # Ask if they intend to overwrite existing pickle
            if input(f"overwrite {self.pickle_path}? (Y/N)\n").upper() != "Y":
                self.pickle_path = self.pathify(self.gen_pickle_name())
        self.context_options: dict[tuple, Counter[str]] = defaultdict(Counter)
        # dict [context, Counter of possible tokens]
        self.num_tweets = 0
        self.num_sentences = 0
        self.auto_pickle = auto_pickle

    def train(self, tweet_as_list: list[str]):
        self.num_tweets += 1
        for sentence in tweet_as_list:
            self.num_sentences += 1
            generated = self.generate_Ngrams(sentence)
            for ngram in generated:
                self.context_options[ngram[0]].update([ngram[1]])
        if self.auto_pickle:
            self.backup()

    def generate_Ngrams(self, string: str):
        words = string.split(" ")
        words = [self.start] * (self.n - 1) + words + [self.end] * (self.n - 1)

        list_of_tup = []

        for i in range(len(words) + 1 - self.n):
            list_of_tup.append((tuple(words[i + j] for j in range(self.n - 1)), words[i + self.n - 1]))

        return list_of_tup

    def backup(self):
        os.makedirs("models", exist_ok=True)
        with open(self.pickle_path, "wb") as file:
            cloudpickle.dump(self, file)

    def generate_tweet(self):
        context = self.start, self.start, self.start
        text = ""
        while True:
            next_word = self.next_word(context)
            context = *context[1:], next_word
            if next_word == self.end:
                break
            text += next_word + " "
        return text

    def next_word(self, context: tuple[str, str, str]):
        options = list(self.context_options[context])
        weights = [self.get_word_prob(context, word) for word in options]
        return random.choices(options, weights, k=1)[0]

    context_freq_cache: dict[tuple, int] = dict()

    # Very huge oversight on my part not adding a counter for contexts, so now I have to set up a cache to prevent
    # having to recalculate the context frequency for the context of every word

    def get_word_prob(self, context: tuple, token: str):
        """Gets the probability of a word given a context

        :param context: the n words preceding the token word
        :param token: the word for which to find the probability
        :return: a simple event probability of the word
        """
        context_freq = self.context_freq_cache.get((self, context)) or self.calculate_freq(context)
        return self.context_options[context][token] / context_freq
        # return self.ngram_count[(context, token)] / context_freq

    def calculate_freq(self, context: tuple):
        freq = sum(freq for freq in self.context_options[context].values())
        self.context_freq_cache[self, context] = freq
        return freq

    @staticmethod
    def load_existing_model(name: str):
        with open(NgramModel.pathify(name), "rb") as file:
            obj: NgramModel = cloudpickle.load(file)
        return obj

    @staticmethod
    def pathify(name):
        return f"models/{name}.pickle"

    @staticmethod
    def gen_pickle_name():
        for i in count():
            new_name = f"unnamed-pickle-{i}"
            if not path.exists(NgramModel.pathify(new_name)):
                return new_name
