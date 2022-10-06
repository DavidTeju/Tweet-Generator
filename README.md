# Tweet-Generator
###### Trained on 21,925 tweets
TODO: add how to use
## Summary
A machine learning python program using a custom/barebone ngram model trained on tweets to generate new human-alike tweets
## How does this work?
A request handler generates random words to query the twitter search API. A data cleaner then works to improve the quality of the tweet 
data to be used to train the model. The cleaner disqualifies tweets that the program suspects to be low quality: vulgar, sexual, too short
or spam. The data cleaner also cuts out trailing hashtags that don't contribute to the context/subsance of the tweet, and converts contextual
mentions/hashtags to their proper form. For example:
```
I just had the best #coffee ever. I feel #ready for my day with @Sarah. #Morning #Coffee #Happy
```
would become:
```
I just had the best coffee ever. I feel ready for my day with Sarah.
```
The cleaned tweets are then split into sentences and used to train the model.  

The model is trained by converting the sentences into n-grams (in the case of the main-model, a trigram). The ngrams are then stored in a 
counter, to record the frequency of different words given a specific context, and a separate dictionary, that stores the possible next 
word candidates given a context, is updated with new candidates.  

After every call to the train function, the model is pickled and stored at a specified or default path
## What is left to be done?
The ultimate goal is to have a twitter bot that regularly tweets automatically generated text. I will need to work on:
1. a function to assign a probability to a word candidate given a context. 
2. a function to weighted randomly select a word candidate. This word candidate will then be used to construct the next context until a 
complete sentence/tweet has been generated.
3. a scheduler to control the rate of requests/training as well as the rate of tweeting by the bot
4. integrating the bot to create tweets automatically
