import twint
import json
from lib.common.selector import Selector
from lib.common.etypes import Etype


class TwitterSelector(Selector):
    """ A selector for scraping tweets.

    It leverages 'twint' - https://github.com/twintproject/twint - under
    the hood.
    """

    def index(self, config):
        c = twint.Config()
        c.Search = config["search_term"]
        c.Since = config["uploaded_after"]
        c.Until = config["uploaded_before"]
        c.Show_hashtags = True
        c.Store_object = True

        twint.run.Search(c)

        def extract_fields(t):
            return [t.id, t.datetime, t.tweet, ",".join(t.hashtags), ",".join(t.photos)]

        tweets = list(map(extract_fields, twint.output.tweets_list))
        tweets.insert(0, ["id", "datetime", "tweet", "hashtags", "photos"])
        return tweets

    def retrieve_element(self, element, config):
        dest = element["base"]
        # TODO(lachie): download all associated images, and video if it exists.

        with open(f"{dest}/tweet.json", "w+") as fp:
            json.dump(element, fp)
