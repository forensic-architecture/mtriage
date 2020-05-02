import json
import requests
import os
import html2text
from pathlib import Path
from urllib.request import urlretrieve
from lib.common.selector import Selector
from lib.common.etypes import Etype, LocalElementsIndex
from lib.common.util import files

TMP = Path("/tmp")


class FourChan(Selector):
    """ A selector that leverages the native 4chan API.

    https://github.com/4chan/4chan-API
    """

    def index(self, config):
        viable_boards = [
            "a",
            "aco",
            "adv",
            "an",
            "asp",
            "b",
            "bant",
            "biz",
            "c",
            "cgl",
            "ck",
            "cm",
            "co",
            "d",
            "diy",
            "e",
            "f",
            "fa",
            "fit",
            "g",
            "gd",
            "gif",
            "h",
            "hc",
            "his",
            "hm",
            "hr",
            "i",
            "ic",
            "int",
            "jp",
            "k",
            "lgbt",
            "lit",
            "m",
            "mlp",
            "mu",
            "n",
            "news",
            "o",
            "out",
            "p",
            "po",
            "pol",
            "qa",
            "qst",
            "r",
            "r9k",
            "s",
            "s4s",
            "sci",
            "soc",
            "sp",
            "t",
            "tg",
            "toy",
            "trash",
            "trv",
            "tv",
            "u",
            "v",
            "vg",
            "vip",
            "vp",
            "vr",
            "w",
            "wg",
            "wsg",
            "wsr",
            "x",
            "y",
        ]
        results = []
        board = config["board"]
        if board not in viable_boards:
            self.error_logger("Your chosen board does not exist on 4chan!")
            quit()
        # Create a HTML parser for parsing comments
        h = html2text.HTML2Text()
        h.ignore_links = False

        req = f"https://a.4cdn.org/{board}/threads.json"

        content = json.loads(requests.get(req).content)
        for page_index, page in enumerate(content):
            self.logger(f"Scraping page number: {page_index+1}")
            for thread_index, threads in enumerate(page["threads"]):
                self.logger(
                    f"Extracting posts from thread number: {thread_index+1}"
                )
                thread_id = threads["no"]
                req = f"https://a.4cdn.org/{board}/thread/{thread_id}.json"
                thread_content = json.loads(requests.get(req).content)[
                    "posts"
                ]  # thread content is a list of posts
                for post_index, post in enumerate(thread_content):
                    self.logger(
                        f"Extracting media and comments from post number: {post_index+1}"
                    )
                    post_row = []
                    post_row.append(post["no"])
                    post_row.append(thread_id)
                    post_row.append(post["time"])

                    try:
                        comment = post["com"]
                    except KeyError:
                        comment = "..."
                    else:
                        comment = h.handle(comment)
                    post_row.append(comment)

                    # Filename
                    try:
                        filename = post["filename"]
                    except KeyError:
                        filename = ""

                    if filename != "":
                        time_id = post["tim"]
                        extension = post["ext"]
                        full_file = f"{filename}{extension}"
                        file_url = (
                            f"https://i.4cdn.org/{board}/{time_id}{extension}"
                        )
                        post_row.append(full_file)
                        post_row.append(extension)
                        post_row.append(file_url)
                    elif filename == "":
                        post_row.append("")
                        post_row.append("")
                        post_row.append("")
                    results.append(post_row)
        self.logger("Scraping metadata complete")
        results.insert(
            0, ["id", "thread_id", "datetime", "comment", "filename", "ext", "url"]
        )
        return LocalElementsIndex(results)

    def retrieve_element(self, element, _):
        base = TMP / element.id
        base.mkdir(parents=True, exist_ok=True)

        fn = element.filename
        identifier = element.id
        comment = element.comment
        url = element.url

        with open(base / f"{identifier}_comment.txt", "w+") as f:
            f.write(comment)

        if url != "":
            urlretrieve(url, base / fn)

        return Etype.cast(element.id, files(base))

module = FourChan
