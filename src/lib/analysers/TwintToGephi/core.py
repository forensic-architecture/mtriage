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
            data = json.load(f)
            data = pythonize(data)

        # usr = data['username']
        # output = TMP/f"{element.id}.json"
        self.logger(data)
        # if usr not in self.indexed_ids:
        #     all_tweets = self.get_all_tweets_for_username(usr)
        #     with open(output, "w+") as f:
        #         json.dump(all_tweets, f)
        #
        #     # TODO: filter replies by conversation ID
        #
        #     element.paths = [output]
        #     self.logger(f"User tweets scraped for {usr} in {element.id}.")

        return element

    def get_all_tweets_for_username(self, username):
        c = twint.Config()
        c.Username = username
        c.Store_object = True
        self.logger(f"Scraping tweets sent to {username}...")
        twint.run.Search(c)

        return to_serializable(twint.output.tweets_list)



module = TwintToGephi
