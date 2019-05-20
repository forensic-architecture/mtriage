# -*- coding: utf-8 -*-
"""Expose API parameters from the v3 Youtube API as a selector.

Config:
    uploaded_after (str): limit to videos uploaded after this date.
    uploaded_before (str): limit to videos uploaded before this date.
    search_term (str): search term to submit to Youtube's black box.
    daily (bool): if true, the selector will aggregate daily searches.
"""

import argparse, os, sys
from datetime import datetime, timedelta
import pandas as pd
import json

import googleapiclient.discovery
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CREDENTIALS_FILE = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
BASE_DIR = os.environ.get("BASE_DIR")
GOOGLE_CREDS = service_account.Credentials.from_service_account_file(f"{BASE_DIR}/{CREDENTIALS_FILE}")

def print_log(msg, logs):
    logs.append(msg + "\n")
    print(msg)


def youtube_search(options, pageToken=None):
    youtube = googleapiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=GOOGLE_CREDS
    )

    request = youtube.search().list(
        pageToken=pageToken,
        q=options["q"],
        publishedBefore=options["before"],
        publishedAfter=options["after"],
        part="id,snippet",
        maxResults=50,
        safeSearch="none",
        type="video",
    )
    return request.execute()


def add_to_csv_obj(csv_obj, s_res):
    for search_result in s_res:
        videoId = search_result["id"]["videoId"]
        title = search_result["snippet"]["title"]
        channelId = search_result["snippet"]["channelId"]
        desc = search_result["snippet"]["description"]
        publishedAt = search_result["snippet"]["publishedAt"]
        url = "https://www.youtube.com/watch?v=%s" % videoId
        csv_obj.append(
            {
                "url": url,
                "title": title.replace(",", ";"),
                "desc": desc.replace(",", ";"),
                "published": publishedAt[0:10],
            }
        )
    return csv_obj


def insert_df_row(row, df):
    df.loc[-1] = row
    df.index = df.index + 1
    df.sort_index(inplace=True)
    return df


def str2bool(v):
    if v.lower() in ("yes", "true", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected")


def youtube_search_all_pages(args, logs):
    csv_obj = []
    print_log(
        "Search terms: %s\n Start: %s\n End: %s"
        % (args["q"], args["after"], args["before"]),
        logs,
    )
    try:
        s_res = youtube_search(args)
        count = 0
        while ("nextPageToken" in s_res) and (len(s_res.get("items", [])) != 0):
            print_log("\tScraping page %s..." % count, logs)
            count += 1
            csv_obj = add_to_csv_obj(csv_obj, s_res.get("items", []))
            s_res = youtube_search(args, pageToken=s_res["nextPageToken"])
        # add the last one
        print_log("\tAll pages scraped.", logs)
        if count > 1:
            csv_obj = add_to_csv_obj(csv_obj, s_res.get("items", []))
        return csv_obj
    except HttpError as e:
        print_log("An HTTP error %d occured." % e.resp.status, logs)
        print(e.content)
        return "ERROR"


def days_between(start, end):
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


# logs is a list of strings.
def add_search_to_obj(args, results, logs):
    new_results = youtube_search_all_pages(args, logs)
    return new_results


def selector_run(config, output_path):
    logs = []
    results = []

    print_log("Query: %s" % config["search_term"], logs)
    print_log("Start: %s" % config["uploaded_after"], logs)
    print_log("End: %s" % config["uploaded_after"], logs)
    print_log("Output file: %s" % output_path, logs)

    if config["daily"]:
        print_log(
            "Scraping daily, from %s -- %s"
            % (config["uploaded_after"], config["uploaded_before"]),
            logs,
        )
        print_log("-----------------", logs)
        for after, before in days_between(
            config["uploaded_after"], config["uploaded_before"]
        ):
            print_log("-------------", logs)
            args_obj = {}
            args_obj["q"] = config["search_term"]
            args_obj["before"] = before
            args_obj["after"] = after
            results = results + add_search_to_obj(args_obj, results, logs)
    df = pd.DataFrame(results)

    print_log("\n\n----------------", logs)
    print_log(
        "Scrape successful, %d results in %s" % ((len(df) - 1), output_path), logs
    )

    return df, logs
