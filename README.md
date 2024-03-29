# Tweet-Generator

###### Built-in model trained on 60,402 tweets.

###### See bot in action: https://twitter.com/RandTweeterbot

A machine learning python program using a custom/bare-bone ngram model trained on tweets to generate new human-alike
tweets

### Pre-reqs:

- Google Chrome must be installed if you want to use the tweet feature
- python3.9 and up
- git

## SetUp

1. #### Clone the repo (and cd into folder):
    ```bash
    git clone https://github.com/DavidTeju/Tweet-Generator
    cd Tweet-Generator
    ```
2. #### Set up virtual environment and install package dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate # for Linux/MacOs
   # just 'venv/bin/activate' for windows
    pip3 install -r requirements.txt
    ```
3. #### Set environment variables
    ```bash
   export TWITTER_USERNAME="REPLACE_WITH_YOUR_VALUES"
   export TWITTER_PASSWORD="REPLACE_WITH_YOUR_VALUES"
   # the username and password for the twitter account to post to
   
   export TWITTER_API_KEY="REPLACE_WITH_YOUR_VALUES"
   export TWITTER_API_KEY_SECRET="REPLACE_WITH_YOUR_VALUES"
   export TWITTER_API_BEARER_TOKEN="REPLACE_WITH_YOUR_VALUES"
   # you should have been given this when you created 
   # your twitter developer account
   
   # To add variables permanently, paste this into ~./bashrc or ~/.zshrc
   #                               (using $ echo 'command' >> ~/.bashrc)
   # For Windows, replace export with setx
    ```

## Use it

```bash
python main.py
```

The default main.py has three scheduled processes

- The first process will load the existing model, query Twitter for new tweets, and train the model on queried tweets
  every 3 seconds
- The second process will generate a random sentence and tweet it every 1 hour
- The third process will update the `.pickle` file every 10 minutes (although you can initialize a model to auto-update)

To run in background:

```bash
nohup python main.py & disown
```

To stop the processes safely, you may keyboard interrupt `^C` or kill the process `kill <pid>`  
To find the `pid`, run

```bash
ps -ef | grep -v grep | grep -i "python main.py" | awk '{print $2}'
```

This may not work if you have some other program with similar process path running. Instead, you can run

```bash
ps -xj | grep -v grep | grep -i "python main.py"
```

and pick out which is the actual process to kill. The PID should
be the number in the second column

I encourage you to modify main.py in any way to change around the function using what's built in. I've extensively
documented everything

## How does the model work?

A request handler generates random words to query the twitter search API. A data cleaner then works to improve the
quality of the tweet
data to be used to train the model. The cleaner disqualifies tweets that the program suspects to be low quality: vulgar,
sexual, too short
or spam. The data cleaner also cuts out trailing hashtags that don't contribute to the context/substance of the tweet,
and converts contextual
mentions/hashtags to their proper form. For example:
> I just had the best #coffee ever. I feel #ready for my day with @Sarah. #Morning #Coffee #Happy

would become:
> I just had the best coffee ever. I feel ready for my day with Sarah.

The cleaned tweets are then split into sentences and used to train the model.

The model is trained by converting the sentences into n-grams (in the case of the main-model, a trigram). The ngrams are
then stored in a
counter, to record the frequency of different words given a specific context, and a separate dictionary, that stores the
possible next
word candidates given a context, is updated with new candidates.

## What is left to be done?

The ultimate goal is to have the capability for people to connect the bot to their Twitter account and have it post for
them. I will need to work on:

1. a web page where people can sign in to twitter to delegate the bot
2. An API that can scale and schedule tweets for hundreds of people
