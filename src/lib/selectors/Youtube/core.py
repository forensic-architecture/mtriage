import yt_dlp 
import json
import re
import argparse, os, sys
import math
from subprocess import call, STDOUT
from pathlib import Path
from lib.common.selector import Selector
from lib.common.etypes import Etype, Union, LocalElementsIndex
from lib.common.util import files
from lib.common.exceptions import ElementShouldSkipError

from datetime import datetime, timedelta

import googleapiclient.discovery
from googleapiclient.errors import HttpError

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
API_KEY = os.environ.get("GOOGLE_API_KEY")
TMP = Path("/tmp")


class Youtube(Selector):
    out_etype = Union(Etype.Json, Etype.Video)

    def index(self, _) -> LocalElementsIndex:
        results = self._run()
        if len(results) > 0:
            out = []
            out.append(list(results[0].keys()))
            out.extend([x.values() for x in results])
            return LocalElementsIndex(out)
        return None

    def pre_retrieve(self, _):
        self.ydl = yt_dlp.YoutubeDL(
            {
                "outtmpl": f"{TMP}/%(id)s/%(id)s.mp4",
                "format": "worstvideo[ext=mp4]",
            }
        )

    def retrieve_element(self, element, _):
        with self.ydl:
            try:
                result = self.ydl.extract_info(element.url)
                meta = TMP / element.id / "meta.json"
                with open(meta, "w+") as fp:
                    json.dump(result, fp)
                self.logger(f"{element.id}: video and meta downloaded successfully.")
                self.disk.delete_local_on_write = True
                return Etype.cast(element.id, files(TMP / element.id))
            except yt_dlp.utils.DownloadError:
                raise ElementShouldSkipError(
                    f"Something went wrong downloading {element.id}. It may have been deleted."
                )

    def _run(self):
        self.logger(f"Query: {self.config['search_term']}")
        if "uploaded_after" in self.config:
            self.logger(f"Start: {self.config['uploaded_after']}")

        if "uploaded_before" in self.config:
            self.logger(f"End: {self.config['uploaded_before']}")

        if self.config.get("daily"):
            results = []
            self.logger(
                f"Scraping daily, from {self.config['uploaded_after']} -- {self.config['uploaded_before']}"
            )
            self.logger("-----------------")
            for after, before in self._days_between(
                self.config["uploaded_after"], self.config["uploaded_before"]
            ):
                results = results + self.get_results(before, after)

        else:
            results = self.get_results(
                self.config.get("uploaded_before"), self.config.get("uploaded_after")
            )

        self.logger("\n\n----------------")
        self.logger(f"Scrape successful, {len(results) - 1} results.")

        return results

    def get_results(self, before, after):
        args_obj = {"q": self.config["search_term"]}

        if before is not None:
            args_obj["before"] = self.config["uploaded_before"]
        if "uploaded_after" in self.config.keys():
            args_obj["after"] = self.config["uploaded_after"]

        new_results = self._youtube_search_all_pages(args_obj)
        if new_results is None:
            raise Exception("Something went wrong")
        return new_results

    def _add_to_csv_obj(self, csv_obj, s_res):
        for search_result in s_res:
            videoId = search_result["id"]["videoId"]
            title = search_result["snippet"]["title"]
            channelId = search_result["snippet"]["channelId"]
            desc = search_result["snippet"]["description"]
            publishedAt = search_result["snippet"]["publishedAt"]
            url = f"https://www.youtube.com/watch?v={videoId}"
            id = self._id_from_url(url)
            csv_obj.append(
                {
                    "url": url,
                    "title": title.replace(",", ";"),
                    "desc": desc.replace(",", ";"),
                    "published": publishedAt[0:10],
                    "id": id,
                }
            )
        return csv_obj

    def _youtube_search_all_pages(self, args):
        csv_obj = []
        self.logger(
            f"Search terms: {args['q']}\n Start: {args['after'] if 'after' in args else ''}\n End: {args['before'] if 'before' in args else ''}"
        )
        try:
            s_res = self._youtube_search(args)
            count = 1
            while True:
                self.logger(f"\tScraping page {count}...")
                count += 1
                csv_obj = self._add_to_csv_obj(csv_obj, s_res.get("items", []))

                if (not "nextPageToken" in s_res) or (len(s_res.get("items", [])) == 0):
                    break

                s_res = self._youtube_search(args, pageToken=s_res["nextPageToken"])
            self.logger("\tAll pages scraped.")
            return csv_obj
        except HttpError as e:
            self.logger(f"An HTTP error {e.resp.status} occured.")
            print(e.content)
            return None

    def _youtube_search(self, options, pageToken=None):
        # modified from https://github.com/youtube/api-samples/blob/master/python/search.py
        if API_KEY is None:
            raise ElementShouldSkipError("No GOOGLE_API_KEY specified in .env")
        youtube = googleapiclient.discovery.build(
            YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY
        )

        theargs = {
            "pageToken": pageToken,
            "q": options["q"],
            "part": "id,snippet",
            "maxResults": 50,
            "safeSearch": "none",
            "type": "video",
        }

        if "before" in options:
            theargs["publishedBefore"] = options["before"]
        if "after" in options:
            theargs["publishedAfter"] = options["after"]

        request = youtube.search().list(**theargs)

        s = request.execute()

        return s

    def _days_between(self, start, end):
        bef = datetime.strptime(end[:-1], "%Y-%m-%dT%H:%M:%S")
        aft = datetime.strptime(start[:-1], "%Y-%m-%dT%H:%M:%S")
        between = (bef - aft).days
        return [
            (
                ((aft + timedelta(days=dt)).strftime("%Y-%m-%dT") + "00:00:00Z"),
                ((aft + timedelta(days=dt)).strftime("%Y-%m-%dT") + "23:59:59Z"),
            )
            for dt in range(between)
        ]

    def _id_from_url(self, url):
        id_search = re.search(
            "https:\/\/www\.youtube\.com\/watch\?v\=(.*)", url, re.IGNORECASE
        )
        if id:
            return id_search.group(1)
        return None


module = Youtube
