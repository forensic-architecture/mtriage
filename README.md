# mtriage

[![Build Status](https://travis-ci.com/forensic-architecture/mtriage.svg?branch=master)](https://travis-ci.com/forensic-architecture/mtriage)

##### select, download, and analyse media 

mtriage is a command-line application to orchestrate complex scraping and
analysis workflows. mtriage is developed at [Forensic Architecture](https://forensic-architecture.org), 
and is intended for use by open source research agencies, journalists, and
activists. To learn more about why we developed mtriage, you can read [an
overview of our reasons here](docs/overview.md).

## getting started

First thing's first; follow the instructions to install mtriage:
* [Install](docs/install.md)

Once installed, the best way to get started with mtriage is to work through the
three tutorials:
* [1. Getting started](docs/tutorial/1/README.md)
* [2. Chaining analysers](docs/tutorial/2/README.md)
* [3. An end-to-end workflow](docs/tutorial/3/README.md)

---

## supported components

Below is a list of currently supported components. If you are interested in
helping us to develop additional selectors and analysers, please consider
joining [the conversaton on Discord](https://discord.gg/FJ4XsCg). We're
accepting PRs for new components, but the internal documentation leaves
a little bit wanting at the moment, so best to communicate with us directly on
the #mtriage channel.

### selectors
* Youtube - search by query with optional date range (time uploaded), download video and metadata. 
* Twitter - search by query, download tweets and images.
* Local - use media that already exists on your filesystem. 

### analysers
* ConvertAudio - convert audio files between formats.
* ExtractAudio - extract audio from a video.
* ExtractTypes - extract elements that contain media with specified extensions.
* Frames - extract frames from videos as images using ffmpeg.
* ImageDedup - deduplicate images that are too similar using the 
    [imagededup](https://github.com/idealo/imagededup) module. (Good to use
    after using 'frames'.)
* KerasPretrained - classify objects in images using [Resnet50 trained on
    ImageNet](https://resources.wolframcloud.com/NeuralNetRepository/resources/ResNet-50-Trained-on-ImageNet-Competition-Data).
* Rank - generate a JSON file containing the rankings for videos classified
    with KerasPretrained.



