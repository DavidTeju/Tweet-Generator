import requests
from random_word import RandomWords

import inspector
from inspector import is_allowed
from NgramModel import NgramModel
from request_handler import *

randomizer = RandomWords()


def to_tweet_list(json_response: dict):
    to_return: list[str] = []
    if "includes" in json_response and "tweets" in json_response["includes"]:
        tweet_list: list[dict[str, str]] = json_response["includes"]["tweets"]
    elif "data" in json_response:
        tweet_list: list[dict] = json_response["data"]
    else:
        return []
    for tweet in tweet_list:
        if tweet["lang"] == "en":
            gen = list(is_allowed(tweet["text"].strip()))
            if gen[0]:  # If allowed, get modified string and append
                to_return.append(gen[1])
    return to_return


if __name__ == "__main__":
    first_model = NgramModel.load_existing_model("main-model")
    print(f"{first_model.num_tweets=}\n{first_model.num_sentences=}")
