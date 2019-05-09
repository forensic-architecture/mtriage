"""The YOUTUBE module is a media space selector that leverage's Youtube's API v3.

Media space selectors should export a single function:
    run(config, output_path)

Config JSON structure for the Youtube module, TODO.
"""
from .main import YoutubeSelector as main

__all__ = ["main"]
