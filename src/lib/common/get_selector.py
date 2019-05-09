from lib.selectors.youtube import main as YoutubeSelector


def get_selector(key):
    return {"youtube": YoutubeSelector}.get(key)
