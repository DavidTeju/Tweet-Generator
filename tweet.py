def tweet(model, bot):
    bot.post_tweet(model.generate_tweet())
