import signal
import time

import psutil
import schedule as schedule
from random_word import RandomWords

from NgramModel import NgramModel
from inspector import tweet_to_sentences
from twitter import *

process = psutil.Process(os.getpid())

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
    print("query: ", format_bytes(process.memory_info().rss))

    query = randomizer.get_random_word()
    for each_tweet in client.get_tweets(query):
        model.train(tweet_to_sentences(each_tweet))


def generate_and_post_tweet(model, api_client):
    print("post tweet: ", format_bytes(process.memory_info().rss))

    posted = False
    while not posted:
        posted = api_client.post_tweet(model.generate_tweet())


def format_bytes(size):
    # 2**10 = 1024
    power = 2 ** 10
    n = 0
    power_labels = {0: '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n] + 'bytes'


def exit_gracefully(*args):
    global exit_now
    exit_now = True


if __name__ == "__main__":
    # I scheduled the training sequence to run every 3 seconds and the tweet to run every 3 hours
    schedule.every(3).seconds.do(lambda: query_and_train(my_model, bot))
    schedule.every(1).hours.do(lambda: generate_and_post_tweet(my_model, bot))
    schedule.every(10).minutes.do(my_model.backup)

    for i in signal.valid_signals():
        if (i == signal.SIGKILL or
                i == signal.SIGSTOP):
            continue
        signal.signal(i, exit_gracefully)

    exit_now = False
    while not exit_now:
        schedule.run_pending()
        time.sleep(1)
    my_model.backup()
    print("Processes successfully stopped")
