import twint
import json
from urllib.request import urlretrieve
from pathlib import Path
from lib.common.selector import Selector
from lib.common.etypes import Etype, LocalElementsIndex
from lib.common.util import files

TMP = Path("/tmp")


class Twitter(Selector):
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
        return LocalElementsIndex(tweets)

    def retrieve_element(self, element, _):
        base = TMP / element.id
        base.mkdir(parents=True, exist_ok=True)
        with open(base / "tweet.json", "w+") as fp:
            json.dump(element.__dict__, fp)

        # retrieve photos
        photos = element.photos.split(",")
        if len(photos) < 1 or photos[0] == "":
            self.logger(f"{element.id} downloaded.")
            return Etype.cast(element.id, files(base))

        for url in photos:
            fname = url.rsplit("/", 1)[-1]
            urlretrieve(url, base / fname)

        self.logger(f"{element.id} downloaded (with images).")
        self.disk.delete_local_on_write = True
        return Etype.cast(element.id, files(base))


module = Twitter
