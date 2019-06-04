"""The LOCAL module is a media space selector that imports files from a local directory.

Media space selectors should export a single function:
    run(config, output_path)
"""
from .main import LocalSelector as main

__all__ = ["main"]
