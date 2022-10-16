import gc
import signal
import time

import schedule as schedule
from daemon import DaemonContext
from random_word import RandomWords

from NgramModel import NgramModel
from inspector import tweet_to_sentences
from twitter import *

randomizer = RandomWords()
bot = Twitter(os.environ["TWITTER_API_BEARER_TOKEN"],
              os.environ["TWITTER_API_KEY"],
              os.environ["TWITTER_API_KEY_SECRET"])
loader = lambda: NgramModel.load_existing_model("main-model")
my_model = None
"""to use a new model instead, use the NgramModel constructor"""


def query_and_train(client):
    """
    calls the methods to query the Twitter API and train the model

    :param client: Twitter object to handle twitter processes
    """
    global my_model
    my_model = loader()
    for _ in range(200):
        if exit_now: break
        print("here")
        query = randomizer.get_random_word()
        for each_tweet in client.get_tweets(query):
            my_model.train(tweet_to_sentences(each_tweet))
    my_model.backup()
    my_model = None
    del my_model
    gc.collect()


def generate_and_post_tweet(api_client):
    model = loader()
    posted = False
    while not posted:
        posted = api_client.post_tweet(model.generate_tweet())
    model = None
    del model
    gc.collect()


def exit_gracefully(*args):
    global exit_now
    exit_now = True


def run_server():
    global exit_now
    # I scheduled the training sequence to run every 3 seconds and the tweet to run every 3 hours
    schedule.every().hours.do(lambda: query_and_train(bot))
    schedule.every(3).hours.do(lambda: generate_and_post_tweet(bot))
    # schedule.every(10).minutes.do(my_model.backup)

    signal.signal(signal.SIGINT, exit_gracefully)

    for i in signal.valid_signals():
        if (i == signal.SIGKILL or
                i == signal.SIGSTOP):
            continue
        signal.signal(i, exit_gracefully)

    while not exit_now:
        schedule.run_pending()
        time.sleep(1)
    print("Processes successfully stopped")


if __name__ == "__main__":
    exit_now = False
    """This is simply a way for me to make this a background process so it isn't closed on the server"""
    # run_server()
    with open("log", "w+") as file:
        with DaemonContext(stderr=file, stdout=file):
            run_server()
