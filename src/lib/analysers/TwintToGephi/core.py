import os
import json
import twint
import pandas as pd
from pathlib import Path
from lib.common.analyser import Analyser
from lib.common.etypes import Etype
from lib.util.twint import to_serializable, pythonize


from collections import namedtuple
from datetime import datetime


def fmt_timestmap(dstamp, tstamp, tzone):
    ds = datetime.strptime(dstamp, "%Y-%m-%d")
    fmtted_ds = ds.strftime("%m/%d/%y")
    return f"{fmtted_ds} {tstamp}"


TMP = Path("/tmp")
TweetEdge = namedtuple(
    "TweetEdge", "date tweet urls domains hashtags tweet_id inreplyto_id"
)


class CsvGraph:
    node_labels = [
        "Vertex",
        "Followed",
        "Followers",
        "Tweets",
        "Favorites",
        "Description",
        "Location",
        "Web",
        "Time Zone",
        "Joined Twitter Date (UTC)",
    ]
    edge_labels = [
        "Vertex 1",
        "Vertex 2",
        "Width",
        "Relationship",
        "Relationship Date (UTC)",
        "Tweet",
        "URLs in Tweet",
        "Domains in Tweet",
        "Hashtags in Tweet",
        "Tweet Date (UTC)",
        "Twitter Page for Tweet",
        "Imported ID",
        "In-Reply-To Tweet ID",
    ]

    def __init__(self):
        self.nodes = []
        self.edges = []

    def has_node(self, name: str):
        return name in self.nodes

    def add_node(self, name: str):
        if name not in self.nodes:
            self.nodes.append(name)

    def add_edge(self, _from: dict, _to: dict):
        is_reply = _to is not None

        self.add_node(_from["username"])
        if is_reply:
            self.add_node(_to["username"])

        edge = TweetEdge(
            date=fmt_timestmap(
                _from["datestamp"], _from["timestamp"], _from["timezone"]
            ),
            tweet=_from["tweet"],
            urls=_from["urls"],
            domains=[],  # NB: no domains provided in obj
            hashtags=_from["hashtags"],
            tweet_id=_from["id"],
            inreplyto_id=_to["id"] if _to is not None else None,
        )

        self.edges.append(
            [
                _from["username"],
                _to["username"] if is_reply else _from["username"],
                1,  # width defaults to 1
                "Tweet" if not is_reply else "Replies To",  # relationship
                edge.date,  # relationship date
                edge.tweet,
                "- ".join(edge.urls) if isinstance(edge.urls, list) else edge.urls,
                "- ".join(edge.domains)
                if isinstance(edge.domains, list)
                else edge.domains,
                "- ".join(edge.hashtags)
                if isinstance(edge.hashtags, list)
                else edge.hashtags,
                edge.date,  # tweet date
                f"https://twitter.com/${_from['username']}/status/${_from['id']}",
                edge.tweet_id,  # the tweet's id
                ""
                if not is_reply
                else edge.inreplyto_id,  # the id of the tweet to which this replies.
            ]
        )

    def to_xlsx(self, path):
        """ Save graph as XLSX file. The default tab will be edges, with an extra tab for nodes. """
        edge_df = pd.DataFrame.from_records(self.edges)
        edge_df.columns = CsvGraph.edge_labels
        node_df = pd.DataFrame.from_records([[x] for x in self.nodes])
        node_df.columns = ["Vertex"]

        writer = pd.ExcelWriter(path, engine="xlsxwriter")
        edge_df.to_excel(writer, sheet_name="Edges")
        node_df.to_excel(writer, sheet_name="Vertices")
        writer.save()


class TwintToGephi(Analyser):
    def pre_analyse(self, _):
        # keeps a record of which user ids have been indexed so that there's no
        # repeated work.
        self.indexed_ids = []
        # usernames (to easily check whether a user exists in the graph or not)
        self.graph = CsvGraph()

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
            # TODO: keep a record so that we don't need to rescrape
            # self.indexed_ids.append(usr)

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

    def add_to_graph(self, t, inreplyto=None):
        """ Add the relevant rows (for `nodes` and `edges`) to a graph from
            a Twint-formatted tweet (Python dictionary) """
        self.graph.add_node(t["username"])

        self.graph.add_edge(t, inreplyto)

    def post_analyse(self, _):
        # TODO: a kind of hack... should maybe make available as a func, i.e. `self.get_analysed()`
        analysed_els = self.disk.read_elements([self.dest_q])
        for el in analysed_els:
            el_json = el.paths[0]
            with open(el_json) as f:
                tweets = json.load(f)

            initial_tweet = tweets[0]
            self.logger(f"Adding tweet {initial_tweet['id']} to graph...")
            self.add_to_graph(initial_tweet)
            for tweet in tweets[1:]:
                self.logger(f"Adding reply {tweet['id']} to graph...")
                self.add_to_graph(tweet, inreplyto=initial_tweet)

        xlsx_path = TMP / "final.xlsx"
        self.graph.to_xlsx(xlsx_path)
        return Etype.Any("FINAL", xlsx_path)


module = TwintToGephi
