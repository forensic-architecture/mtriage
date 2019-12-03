# mtriage

[![Build Status](https://travis-ci.com/forensic-architecture/mtriage.svg?branch=master)](https://travis-ci.com/forensic-architecture/mtriage)

##### select, download, and analyse media 

mtriage is a command-line application that can be used to scrape and analyse 
media. mtriage is developed by [Forensic Architecture](https://forensic-architecture.org), and is intended for use 
by open source research agencies, journalists, and activists.

mtriage consists of two types of components:

* **selectors**: to search for and download media from various platforms.
* **analysers**: to derive data from media that has been retrieved by a selector.

Below are the following components that are supported. If you are interested in
helping us to develop additional selectors and analysers, please consider
joining [the conversaton on Discord](https://discord.gg/FJ4XsCg).

### selectors
* youtube - search by query with optional date range (time uploaded), download video and metadata. 
* twitter - search by query, download tweets and images.
* local - use media that already exists on your filesystem. 

### analysers
* convert_audio - convert audio files between formats.
* extract_audio - extract audio from a video.
* fastai_model - detect and classify iages using weights trained using
    [FastAI](https://github.com/fastai/fastai).
* frames - extract frames from videos as images using ffmpeg.
* frames_opencv - extract frames from videos as images using opencv, deleting 
    frames if they are too similar at extraction.
* imagededup - deduplicate images that are too similar using the 
    [imagededup](https://github.com/idealo/imagededup) module. (Good to use
    after using 'frames'.)
* keras_pretrained - classify objects in images using [Resnet50 trained on
    ImageNet](https://resources.wolframcloud.com/NeuralNetRepository/resources/ResNet-50-Trained-on-ImageNet-Competition-Data).
* ocr - analyse an image using optical character recognition from [Google Cloud Platform](https://cloud.google.com/vision/docs/ocr).
* yolov3 - detect and classify objects in images using [YoloV3](https://pjreddie.com/darknet/yolo/) trained on [ImageNet](http://www.image-net.org/) classes.


## setup 
mtriage is currently in active development, and is not yet packaged in any way.
It uses [Docker](https://www.docker.com/products/docker-desktop) to manage dependencies, which you will need to download to ensure mtriage works as expected. 

- Docker Desktop (Mac installation [here](https://docs.docker.com/v17.12/docker-for-mac/install/), Ubuntu installation [here](https://docs.docker.com/v17.12/install/linux/docker-ce/ubuntu/)).

Follow the instructions relevant to your operating system to install Docker CE.

You also need to ensure that a version of [Python](https://www.python.org/downloads/) is installed on your computer.
Most modern operating systems have a version installed by default. 

### additional setup
Depending on what components you intend to use, there may be additional setup
required. Check the [component docs folder](./docs/components) before using an 
analyser or if you run into an authentication or setup issue.

## run 
Once you have Docker and Python installed, you can run mtriage using one of the
examples provided. From this folder:
```bash
pip install -r requirements.txt
./mtriage run examples/_demo/youtube.yaml 
```

When you first run mtriage, it will download the necessary Docker images to
your system. The first time you run it, it may take several minutes to get up
and running. Subsequent uses will be much faster.

## options 

### `./mtriage run path/to/file.yaml`

The primary command to trigger new mtriage workflows. Each run takes a YAML
file that specifies which selectors and analysers to run (i.e. `./mtriage run
examples/youtube.yaml`). See [examples folder](./examples) for examples of how
to specify different analyser options.

You can also pass the following flags to the run command:

| flag  | description |
|-------|-------------|
| `--gpu` | Run using the mtriage GPU image. This will speed up certain analysers that depend on it |
| `--tag` | Allows you to run mtriage with a custom build by passing the name of the Docker image tag you used during the custom build (see below) |
| `--dry` | Primarily for testing. Will not run any command, but instead return the command that will be run. |

### `./mtriage dev build`

The command to build an mtriage Docker image from source code. You won't need
this unless you are developing mtriage, as the latest images are also on [Docker
Hub](https://hub.docker.com/repository/docker/forensicarchitecture/mtriage).

| flag  | description |
|-------|-------------|
| `--gpu` | Build the GPU image. Will build the CPU image otherwise |
| `--tag` | Give your build a custom tag. Will default to 'dev' or 'dev-gpu' |
| `--blacklist` | Give build a path to a blacklist that lists which components to exclude. See [example.blacklist.txt](./example.blacklist.txt) for format. |
| `--whitelist` | Give build a path to a whitelist that lists which components to include. |
| `--dry` | Primarily for testing. Will not run any command, but instead return the command that will be run. |

### `./mtriage dev test`

Run all mtriage tests. These run in two parts for the time being: one inside 
Docker, and one on your local Python installation.

| flag  | description |
|-------|-------------|
| `--verbose` | Run verbose tests, showing all print statements in the console. |
| `--gpu` | Test the GPU image. Will build the CPU image otherwise |
| `--tag` | Test with a custom tag. Will default to 'dev' or 'dev-gpu' |
| `--dry` | Primarily for testing. Will not run any command, but instead return the command that will be run. |

### `./mtriage dev clean `

Remove all mtriage Docker containers, stopped or running.

### `./mtriage dev`

Open a bash shell inside mtriage's Docker container. For debugging.

| flag  | description |
|-------|-------------|
| `--gpu` | Run the GPU image. Will run the CPU image otherwise |
| `--tag` | Run with a custom tag. Will default to 'dev' or 'dev-gpu' |
| `--dry` | Primarily for testing. Will not run any command, but instead return the command that will be run. |


