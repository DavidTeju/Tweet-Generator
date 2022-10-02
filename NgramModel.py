import os
from collections import Counter
from itertools import count
from os import path

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
        self.ngram_count: Counter[tuple] = Counter()
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
        file = open(self.pickle_path, "wb")
        cloudpickle.dump(self, file)
        file.close()

    @staticmethod
    def load_existing_model(name: str):
        file = open(NgramModel.pathify(name), "rb")
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
