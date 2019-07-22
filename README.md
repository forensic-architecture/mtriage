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
* youtube - search and download via the [v3 API](https://developers.google.com/youtube/v3/).
* local - use media that already exists on your filesystem. 

### analysers
* frames - extract frames from videos as images.
* yolov3 - detect and classify objects in images using [YoloV3](https://pjreddie.com/darknet/yolo/) trained on [ImageNet](http://www.image-net.org/) classes.
* keras_pretrained - classify objects in images using [Resnet50 trained on
    ImageNet](https://resources.wolframcloud.com/NeuralNetRepository/resources/ResNet-50-Trained-on-ImageNet-Competition-Data).
* ocr - analyse an image using optical character recognition from [Google Cloud Platform](https://cloud.google.com/vision/docs/ocr).

## setup 
mtriage is currently in active development, and is not yet packaged in any way.
It uses [Docker](https://www.docker.com/products/docker-desktop) to manage dependencies, which you will need to download to ensure mtriage works as expected. 

- Docker Desktop (Mac installation [here](https://docs.docker.com/v17.12/docker-for-mac/install/), Ubuntu installation [here](https://docs.docker.com/v17.12/install/linux/docker-ce/ubuntu/)).

Follow the instructions relevant to your operating system to install Docker CE.

You also need to ensure that a version of [Python](https://www.python.org/downloads/) is installed on your computer.
Most modern operating systems have a version installed by default. 

### additional setup
Depending on what components you intend to use, there may be additional setup
required. Ensure to read the documentation for each component you wish to use. 

## Run 
Once you have Docker and Python installed, you can run mtriage using one of the
examples provided. From this folder:
```bash
./mtriage run examples/_demo/youtube.yaml 
```

When you first run mtriage, it will download the necessary Docker images to
your system. The first time you run it, it may take several minutes to get up
and running. Subsequent uses will be much faster.
