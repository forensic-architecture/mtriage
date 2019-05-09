# mtriage

##### scrape and analyse media on the web

mtriage is a command-line application that scrapes and analyses public domain media. mtriage is developed by [Forensic Architecture](https://forensic-architecture.org), and is intended for use by open source research agencies, journalists, and activists.

mtriage is a framework that orchestrates two different kinds of components:

* **selectors**: to search for and download media from various platforms.
* **analysers**: to derive data from media that has been retrieved by
    a selector.

### selectors
* youtube - search and download via the [v3 API](https://developers.google.com/youtube/v3/).

### analysers
* frames - extract one frame for each second from a video.
* ocr - analyse an image using [Google Cloud Platform](https://cloud.google.com/vision/docs/ocr).
<!-- * pytorch - run inference with a [PyTorch](https://pytorch.org/) model on an image. -->


## development
mtriage is currently in active development, and is not yet packaged in any way.
It uses [Docker](https://www.docker.com/products/docker-desktop) to manage
dependencies, and is written in Python.

### dependencies
- [Docker Desktop](https://docs.docker.com/install/) (versions for Linux, Mac,
    and Windows)
- [docker](https://docs.docker.com/install/) (python library, v3.5.0)

Follow the instructions relevant to your operating system to install Docker CE,
and then install the python dependency with:

```bash
python -m pip install docker
```

mtriage should work on any version of Python on your local, 2 or 3.

### building
mtriage runs inside a docker container. Build the image with the following
command:
```bash
python run.py build
```

Once this is successful, you can run the container with:
```bash
python run.py develop
```

You should see a bash prompt with your docker id:
```bash
root@034ae4106367:/src#
```

You are now ready to start using mtriage.


### running
Selectors and analysers are currently specified as runtime arguments to the
entrypoint script, "src/run.py". In "scripts" you can find a series of example
bash scripts that construct appropriate arguments and execute them.

A more robust interface for passing options is a work in progress.
