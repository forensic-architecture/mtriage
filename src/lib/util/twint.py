LABELS = [
    "id",
    "conversation_id",
    "datestamp",
    "timestamp",
    "timezone",
    "user_id",
    "username",
    "name",
    "place",
    "tweet",
    "mentions",
    "urls",
    "photos",
    "replies_count",
    "retweets_count",
    "likes_count",
    "hashtags",
    "cashtags",
    "link",
    "retweet",
    "quote_url",
    "video",
    "user_rt_id",
    "near",
    "geo",
    "source",
    "retweet_date",
]


def pythonize(t):
    """ Make valid fields ints, essentially deserialize """
    t["retweet"] = True if t["retweet"] == "True" else False
    t["likes_count"] = int(t["likes_count"])
    t["replies_count"] = int(t["replies_count"])
    t["retweets_count"] = int(t["retweets_count"])
    t["photos"] = t["photos"].split(",")
    t["hashtags"] = t["hashtags"].split(",")
    t["urls"] = t["urls"].split(",")
    return t


def attr_is_list(attr):
    return attr.strip() in [
        "photos",
        "mentions",
        "urls",
        "mentions",
        "hashtags",
        "cashtags",
    ]


def jsont(t, as_list):
    """ return all fields in a JSON-serializable way """
    if not as_list:
        return {
            l: ",".join(getattr(t, l)) if attr_is_list(l) else getattr(t, l)
            for l in LABELS
        }
    else:
        td = t.__dict__
        out = []
        for l in LABELS:
            if attr_is_list(l):
                out.append(",".join(td[l]))
            else:
                out.append(td[l])
        return out


def to_serializable(tweets, as_list=False):
    vls = [jsont(t, as_list) for t in tweets]
    if as_list:
        vls.insert(0, LABELS)
    return vls
