import time
from itertools import count

import schedule as schedule
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


def train_model(model: NgramModel):
    query = randomizer.get_random_word()
    for each_tweet in bot.get_tweets(query):
        model.train(tweet_to_sentences(each_tweet))


def generate_and_post_tweet(model, api_client):
    api_client.post_tweet(model.generate_tweet())


def exit_gracefully(*args):
    global exit_now
    exit_now = True


if __name__ == "__main__":
    schedule.every(3).seconds.do(lambda: train_model(first_model))
    schedule.every(3).hours.do(lambda: tweet(first_model, bot))

    while True:
        schedule.run_pending()
        time.sleep(1)
