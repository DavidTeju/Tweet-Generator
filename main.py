import json
import os

from random_word import RandomWords

from NgramModel import NgramModel
from inspector import tweet_to_sentences
from twitter import *

randomizer = RandomWords()

if __name__ == "__main__":
    # print(json.dumps(dict(os.environ), indent=4))
    first_model = NgramModel.load_existing_model("main-model")
    # test_mode = NgramModel(4, "Test")
    #
    # test_mode.train(["David has gone to the table where he is not welcome",
    #                  "Sarah is at the party where she is not welcome because she wants to drink beer"])

    bot = Twitter(os.environ["TWITTER_API_BEARER_TOKEN"],
                  os.environ["TWITTER_API_KEY"],
                  os.environ["TWITTER_API_KEY_SECRET"])

    bot.post_tweet("testing environment variables")

    # for i in range(5):
    #     searcher.post_tweet(first_model.generate_tweet())

    # for i in count():
    # query = randomizer.get_random_word()
    # for tweet in bot.get_tweets(query):
    #     first_model.train(tweet_to_sentences(tweet))
    # print(i)
