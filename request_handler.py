url = "https://api.twitter.com/2/tweets/search/recent"

bearer_token = "replace"
# TODO: take this out

param = {'query': '',
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


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r
