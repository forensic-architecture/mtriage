import json
import re
import argparse, os, sys
from subprocess import call, STDOUT
from lib.common.selector import Selector
from lib.common.etypes import Etype

# from .select import selector_run
# from .retrieve import id_from_url, vid_exists, get_meta_path
from datetime import datetime, timedelta

class 4ChanSelector(Selector):
    def get_out_etype(self):
        return Etype.Union(Etype.Video, Etype.Json)

    def index(self, config):
        results = self._run(config)
        if len(results) > 0:
            out = []
            out.append(list(results[0].keys()))
            out.extend([x.values() for x in results])
            return out
        return None

    def pre_retrieve(self, config, element_dir):
        self.ydl = youtube_dl.YoutubeDL(
            {
                "outtmpl": f"{element_dir}/%(id)s/%(id)s.mp4",
                "format": "worstvideo[ext=mp4]",
            }
        )

    def retrieve_element(self, element, config):
        dest = element["base"]
        url = element["url"]
        ydl = self.ydl
        with ydl:
            vid_id = self._id_from_url(url)
            vid_does_exist = self._vid_exists(dest)

            if vid_does_exist:
                self.logger(f"{vid_id} has already been downloaded.")
            try:
                result = ydl.extract_info(url)
                with open(self._get_meta_path(dest), "w+") as fp:
                    json.dump(result, fp)
                self.logger(f"{vid_id}: video and meta downloaded successfully.")
            except youtube_dl.utils.DownloadError:
                self.logger(
                    f"Something went wrong downloading {vid_id}. It may have been deleted."
                )

    def _run(self, config):
        results = []

        self.logger(f"Query: {config['search_term']}")
        if "uploaded_after" in config:
            self.logger(f"Start: {config['uploaded_after']}")

        if "uploaded_before" in config:
            self.logger(f"End: {config['uploaded_before']}")

        if "daily" in config.keys() and config["daily"]:
            self.logger(
                f"Scraping daily, from {config['uploaded_after']} -- {config['uploaded_before']}"
            )
            self.logger("-----------------")
            for after, before in self._days_between(
                config["uploaded_after"], config["uploaded_before"]
            ):
                self.logger("-------------")
                args_obj = {}
                args_obj["q"] = config["search_term"]
                args_obj["before"] = before
                args_obj["after"] = after
                new_results = self._add_search_to_obj(args_obj, results)
                results = results + new_results

        else:
            args_obj = {}
            args_obj["q"] = config["search_term"]

            if "uploaded_before" in config.keys():
                args_obj["before"] = config["uploaded_before"]
            if "uploaded_after" in config.keys():
                args_obj["after"] = config["uploaded_after"]

            new_results = self._add_search_to_obj(args_obj, results)
            results = results + new_results

        self.logger("\n\n----------------")
        self.logger(f"Scrape successful, {len(results) - 1} results.")

        return results

    def _add_search_to_obj(self, args, results):
        new_results = self._youtube_search_all_pages(args)
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
            count = 0
            while ("nextPageToken" in s_res) and (len(s_res.get("items", [])) != 0):
                self.logger(f"\tScraping page {count}...")
                count += 1
                csv_obj = self._add_to_csv_obj(csv_obj, s_res.get("items", []))
                s_res = self._youtube_search(args, pageToken=s_res["nextPageToken"])
            # add the last one
            self.logger("\tAll pages scraped.")
            if count > 1:
                csv_obj = self._add_to_csv_obj(csv_obj, s_res.get("items", []))
            return csv_obj
        except HttpError as e:
            self.logger(f"An HTTP error {e.resp.status} occured.")
            print(e.content)
            return csv_obj

    def _youtube_search(self, options, pageToken=None):
        youtube = googleapiclient.discovery.build(
            YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=GOOGLE_CREDS
        )

        args = {
            "pageToken": pageToken,
            "q": options["q"],
            "part": "id,snippet",
            "maxResults": 50,
            "safeSearch": "none",
            "type": "video",
        }

        if "before" in options:
            args["publishedBefore"] = options["before"]
        if "after" in options:
            args["publishedAfter"] = options["after"]

        request = youtube.search().list(**args)

        return request.execute()

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

    def _get_meta_path(self, dest):
        return f"{dest}/meta.json"

    # def _get_folder_path(self, base_folder, vid_id):
    #     return f"{base_folder}/{vid_id}"

    def _id_from_url(self, url):
        id_search = re.search(
            "https:\/\/www\.youtube\.com\/watch\?v\=(.*)", url, re.IGNORECASE
        )
        if id:
            return id_search.group(1)
        return None

    def _vid_exists(self, dest):
        try:
            m_vid_file = list(
                filter(lambda x: re.match("(.*\.mp4)|(.*\.mkv)", x), os.listdir(dest))
            )
            # video has already been downloaded.
            if len(m_vid_file) != 1:
                return False
            return True
        except FileNotFoundError:
            return False
