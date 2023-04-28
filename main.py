import logging
import shutil
import signal
import time

import schedule as schedule
from random_word import RandomWords

from NgramModel import NgramModel
from inspector import tweet_to_sentences
from twitter import *

logging.basicConfig(filename="tweeter.log",
                    format='%(levelname)s (%(asctime)s): %(message)s',
                    level=logging.INFO,
                    encoding="utf-8")
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
    posted = False
    while not posted:
        tweet = model.generate_tweet()
        posted = api_client.post_tweet(tweet)


def exit_gracefully(*args):
    global exit_now
    exit_now = True


def log_and_backup():
    shutil.copyfile("models/main-model.pickle", "backup/main-model.pickle")
    my_model.backup()
    logging.info("Model backed up")


if __name__ == "__main__":
    for i in signal.valid_signals():
        if i in [signal.SIGKILL, signal.SIGSTOP]:
            continue
        signal.signal(i, exit_gracefully)

    # I scheduled the training sequence to run every 3 seconds and the tweet to run every 3 hours
    generate_and_post_tweet(my_model, bot)
    schedule.every(4).seconds.do(lambda: query_and_train(my_model, bot))
    schedule.every(1).hours.do(lambda: generate_and_post_tweet(my_model, bot))
    schedule.every(10).minutes.do(log_and_backup)

    exit_now = False
    while not exit_now:
        schedule.run_pending()
        time.sleep(1)
    my_model.backup()
    logging.info("Process killed with successful backup")
