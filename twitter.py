import os
from dataclasses import dataclass

import requests
from requests_oauthlib import OAuth1Session

import browser
from inspector import is_allowed


def parse_response_to_list(response: dict):
    """
    Extracts and cleans tweets from response

    :param response: the response from the Twitter API to parse
    :return: A cleaned list of tweets as strings
    """
    to_return: list[str] = []
    if "includes" in response and "tweets" in response["includes"]:
        tweet_list: list[dict[str, str]] = response["includes"]["tweets"]
    elif "data" in response:
        tweet_list: list[dict] = response["data"]
    else:
        return []
    for tweet in tweet_list:
        if tweet["lang"] == "en":
            gen = list(is_allowed(tweet["text"].strip()))
            if gen[0]:  # If allowed, get modified string and append
                to_return.append(gen[1])
    return to_return


search_param = {'query': '',
                "expansions": "attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,"
                              "geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id",
                "tweet.fields": "attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,"
                                "in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,"
                                "reply_settings,source,text,withheld",
                "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,"
                               "protected,public_metrics,url,username,verified,withheld",
                "place.fields": "contained_within,country,country_code,full_name,geo,id,name,place_type",
                "poll.fields": "duration_minutes,end_datetime,id,options,voting_status",
                "media.fields": "duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,"
                                "non_public_metrics,organic_metrics,promoted_metrics",
                "max_results": "50"
                }


@dataclass()
class Twitter:
    bearer_token: str
    consumer_key: str = ""
    consumer_secret: str = ""
    __search_url = "https://api.twitter.com/2/tweets/search/recent"

    def bearer_oauth(self, r):
        """
        construct and load authorization header for request

        :param r: request
        :return: the modified request
        """
        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r

    def get_tweets(self, keyword: str) -> list[str]:
        """
        Searches twitter for keyword

        :param keyword: a single-word string to query the Twitter API for
        :return: a list of tweets returned as strings
        """
        search_param["query"] = keyword
        to_return = dict()
        try:
            to_return = requests.get(Twitter.__search_url, search_param, auth=self.bearer_oauth).json()
        except Exception:
            print("skipped error")
        return parse_response_to_list(to_return)

    def post_tweet(self, tweet: str) -> bool:
        """
        Posts a tweet
        :param tweet: A string of text to post as a tweet
        :return: a boolean indicating success of the tweet
        """
        payload = {"text": tweet}

        # Get request token
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(self.consumer_key, client_secret=self.consumer_secret)

        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print(
                "There may have been an issue with the consumer_key or consumer_secret you entered."
            )
            return

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)

        verifier = browser.get_pin(authorization_url)

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        # Make the request
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        # Making the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )

        if response.status_code != 201:
            print(
                f"Request returned an error: {response.status_code} {response.text}.\tTrying again"
            )
            return False
        else:
            print(f"successfully posted tweet: {tweet} to {os.environ['TWITTER_USERNAME']}")
            return True
