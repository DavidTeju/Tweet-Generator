import signal
import time

import schedule as schedule
from random_word import RandomWords

from NgramModel import NgramModel
from inspector import tweet_to_sentences
from twitter import *

randomizer = RandomWords()
bot = Twitter(os.environ["TWITTER_API_BEARER_TOKEN"],
              os.environ["TWITTER_API_KEY"],
              os.environ["TWITTER_API_KEY_SECRET"])
my_model = NgramModel.load_existing_model("main-model")
"""to use a new model instead, use the NgramModel constructor"""


def query_and_train(model: NgramModel, client):
    """
    calls the methods to query the Twitter API and train the model

    :param model: model to train
    :param client: Twitter object to handle twitter processes
    """
    query = randomizer.get_random_word()
    for each_tweet in client.get_tweets(query):
        model.train(tweet_to_sentences(each_tweet))


def generate_and_post_tweet(model, api_client):
    api_client.post_tweet(model.generate_tweet())


def exit_gracefully(*args):
    global exit_now
    exit_now = True


if __name__ == "__main__":
    # I scheduled the training sequence to run every 3 seconds and the tweet to run every 3 hours
    schedule.every(3).seconds.do(lambda: query_and_train(my_model, bot))
    schedule.every(3).hours.do(lambda: generate_and_post_tweet(my_model, bot))

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    exit_now = False
    while not exit_now:
        schedule.run_pending()
        time.sleep(1)

    my_model.backup()
    print("Processes successfully stopped")
