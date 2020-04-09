import os
import json
import twint
from pathlib import Path
from lib.common.analyser import Analyser

# from lib.common.exceptions import ElementShouldSkipError
from lib.common.etypes import Etype
from lib.util.twint import to_serializable, pythonize

TMP = Path("/tmp")


class TwintToGephi(Analyser):
    def pre_analyse(self, _):
        # keeps a record of which user ids have been indexed so that there's no
        # repeated work.
        self.indexed_ids = []

    def analyse_element(self, element: Etype.Json, _) -> Etype.Any:
        with open(element.paths[0], "r") as f:
            orig_tweet = json.load(f)
            orig_tweet = pythonize(orig_tweet)

        tweet_with_replies = [orig_tweet]
        reply_count = orig_tweet["replies_count"]
        # retweet_count = orig_tweet["retweets_count"]
        usr = orig_tweet["username"]

        # TODO: get retweets, as they are mentions
        # if retweet_count > 0:
        #     retweets = self.get_all_retweets(usr)

        if reply_count > 0 and usr not in self.indexed_ids:
            self.indexed_ids.append(usr)

            all_tweets = self.get_all_tweets_sent_to(usr)
            conv_tweets = [
                tweet
                for tweet in all_tweets
                if tweet["conversation_id"] == orig_tweet["conversation_id"]
            ]
            if len(conv_tweets) > 0:
                tweet_with_replies = tweet_with_replies + conv_tweets
                self.logger(f"{len(conv_tweets)} replies added to tweet {element.id}.")

        output = TMP / f"{element.id}.json"
        with open(output, "w+") as f:
            json.dump(tweet_with_replies, f)

        element.paths = [output]

        return element

    def get_all_retweets(self, username):
        c = twint.Config()
        c.Username = username
        c.Retweets = True
        twint.run.Profile(c)

    def get_all_tweets_sent_to(self, username):
        """ See https://github.com/twintproject/twint/issues/513 """
        c = twint.Config()
        c.To = f"@{username}"
        c.Retweets = True
        c.Since = self.config["uploaded_after"]
        c.Until = self.config["uploaded_before"]
        c.Store_object = True
        self.logger(f"Scraping tweets sent to {username}...")
        twint.run.Search(c)
        results = twint.output.tweets_list
        twint.output.tweets_list = []

        return to_serializable(results)


module = TwintToGephi
