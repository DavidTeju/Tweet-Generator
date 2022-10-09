import time
from itertools import count

from random_word import RandomWords

from NgramModel import NgramModel
from inspector import tweet_to_sentences
from twitter import *
from tweet import tweet

randomizer = RandomWords()
bot = Twitter(os.environ["TWITTER_API_BEARER_TOKEN"],
              os.environ["TWITTER_API_KEY"],
              os.environ["TWITTER_API_KEY_SECRET"])
first_model = NgramModel.load_existing_model("main-model")

if __name__ == "__main__":
    """
    Will run training on model 100_000 times
    """
    tweet()

    for i in count():
        query = randomizer.get_random_word()
        for tweet in bot.get_tweets(query):
            first_model.train(tweet_to_sentences(tweet))
        time.sleep(3)
        if not (i % 80):
            tweet()
