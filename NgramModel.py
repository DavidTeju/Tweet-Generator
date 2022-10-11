import os
import random
from collections import Counter
from itertools import count
from os import path
from typing import Any

import cloudpickle


class NgramModel:

    def __init__(self, n: int, name=""):
        self.n = n
        self.pickle_path = self.pathify(name or self.gen_pickle_name())
        if path.exists(self.pickle_path):  # Ask if they intend to overwrite existing pickle
            if input(f"overwrite {self.pickle_path}? (Y/N)").upper() != "Y":
                self.pickle_path = self.pathify(self.gen_pickle_name())
        self.context_options: dict[tuple, set[str]] = dict()
        # dict [context, list of possible tokens]
        self.ngram_count: Counter[tuple[tuple, str]] = Counter()
        # dict [tuple [context, token], count]
        self.num_tweets = 0
        self.num_sentences = 0

    def train(self, tweet_as_list: list[str]):
        self.num_tweets += 1
        for sentence in tweet_as_list:
            self.num_sentences += 1
            # print("Sentence: ", sentence)
            generated = self.generate_Ngrams(sentence)
            self.ngram_count.update(generated)
            for ngram in generated:
                self.add_to_set(ngram)
        self.update_pickle_state()

    def generate_Ngrams(self, string: str):
        words = string.split(" ")
        words = ["<start>"] * (self.n - 1) + words + ["<end>"] * (self.n - 1)

        list_of_tup = []

        for i in range(len(words) + 1 - self.n):
            list_of_tup.append((tuple(words[i + j] for j in range(self.n - 1)), words[i + self.n - 1]))

        return list_of_tup

    def add_to_set(self, ngram: tuple[tuple[str, ...], str]):
        if ngram[0] not in self.context_options:
            self.context_options[ngram[0]] = set()
        self.context_options[ngram[0]].add(ngram[1])

    def update_pickle_state(self):
        os.makedirs("models", exist_ok=True)
        with open(self.pickle_path, "wb") as file:
            cloudpickle.dump(self, file)

    def generate_tweet(self):
        context = "<start>", "<start>", "<start>"
        text = ""
        while True:
            next_word = self.next_word(context)
            context = (*context[1:], next_word)
            if next_word == "<end>":
                break
            text += next_word + " "
        return text

    def next_word(self, context):
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
        return self.ngram_count[(context, token)] / context_freq

    def calculate_freq(self, context: tuple):
        freq = 0
        for token in self.context_options[context]:
            freq += self.ngram_count[(context, token)]

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
