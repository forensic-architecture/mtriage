# mtriage

### NB: currently unstable, in active development, and should not be used in production

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
- Docker Desktop (Mac installation [here](https://docs.docker.com/v17.12/docker-for-mac/install/), Ubuntu installation [here](https://docs.docker.com/v17.12/install/linux/docker-ce/ubuntu/)).
- [docker](https://docs.docker.com/install/) (python library, v3.5.0)

Follow the instructions relevant to your operating system to install Docker CE,
and then install the python dependency with:

```bash
python -m pip install -r requirements.txt
```

(Note that mtriage was developed using Python 3, but you should be able to run it with 2.x as well.)

### configuration setup
Selectors and analysers often rely on private credentials such as API keys. mtriage deals with these in two ways:

* **`.env` file at the top level**: contains API keys and other environment variables, which are made available when
    mtriage is running.
* **`credentials` folder**: in some cases, components require JSON configs, such as for GCP service accounts. mtriage
    currently deals with this by adding a path to the credentials file in `.env`, and adding the credential file itself
    in the `credentials` folder.

The specific configuration steps depend on which components you intend to use. For every component you wish to use, run
through its setup:

##### selectors
* [youtube](docs/config/youtube.md)
##### analysers
* frames
* ocr

### running
You can run mtriage in a Docker container with:
```bash
python run.py develop
```

Selectors and analysers are currently specified as runtime arguments to the
entrypoint script, "src/run.py". In "scripts" you can find a series of example
bash scripts that construct appropriate arguments and execute them.

A more robust interface for passing options is a work in progress.


### building locally
You can build the mtriage image locally via run.py as well:
```bash
python run.py build


