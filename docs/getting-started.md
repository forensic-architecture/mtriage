# Getting Started

Mtriage is a [command-line program](https://en.wikipedia.org/wiki/Command-line_interface) to orchestrate complex workflows that download media of various kinds, analyse them, and visualise results. To understand what mtriage can do, this tutorial will briefly outline the different components of an mtriage workflow, and then show you how to create one that analyses Youtube videos frame-by-frame with the [YOLOv3](https://towardsdatascience.com/review-yolov3-you-only-look-once-object-detection-eab75d7a1ba6) object detection classifer. To conclude, we'll briefly touch on how much more mtriage is capable of, and show how it is easy to extend mtriage to analyse other kinds of media, and create more site-specific workflows.

## Architecture
Mtriage has three kinds of components: selectors, analysers, and viewers. Each component manages a different stage of a workflow:
* **Selector** - indexes and then downloads media from a source, such as Youtube. Selectors can implement their own web scraping techniques, or simply leverage the search functionality of online platforms in order to return results. The Youtube selector, for example, takes as input a search terms and two dates (start and end), returning all the videos that Youtube returns for the search term that was uploaded between the two given dates.
* **Analyser** - analyses media that has been downloaded from a selector, producing *derived* media that contain the analysis results. An analyser may produce media that is of a different kind than its input media. The frames analyser, for example, takes a video as input and produces a set of images (one frame for each second, say) as output.
* **Viewer** - visualises derived media in an interactive website. Viewers make mtriage an end-to-end tool for analysing media, as they mean that you can present results, and even create interactive workstations, directly from analysis results.

## Downloading Mtriage
Start by cloning the source code:

```bash
git clone https://github.com/forensic-architecture/mtriage.git
```

Mtriage does not require any dependencies but [Python](https://www.python.org/) 3 and [Docker CE](https://docs.docker.com/install/). Mtriage should work with Python 2.x as well, but we recommend using 3. If you have a CUDA GPU, you can use [Nvidia Docker](https://github.com/NVIDIA/nvidia-docker) instead of Docker to make certain analysers more performant.

Once you have a Python and a Docker installed, install the three dependencies in requirements.txt. Two of these are for testing (pytest and black); the only runtime dependency is pyyaml. 
```
cd mtriage
pip install -r requirements.txt
```

Once the dependencies have been installed, run the test suite to ensure that everython is working. This command may take a while, as the first time you run mtriage it will download the [latest Docker image](https://cloud.docker.com/u/forensicarchitecture/repository/docker/forensicarchitecture/mtriage). Mtriage commands will run much faster after this first one:

```bash
./mtriage dev test
```

Assuming this command completed and all the tests passed, you are now ready to run mtriage workflows. 

## Running a Workflow
To get to know mtriage, we're going to run a workflow using four components:

1. **youtube**: a selector that takes a search term and time period, and the downloads all videos returned from that search as mtriage elements.
2. **frames**: extracts images at a rate of one frame per second from video elements. 
3. **yolov3**: makes predictions over one or more images using [YoloV3](https://pjreddie.com/darknet/yolo/) object detection. Predictions are saved in a JSON file.
4. **ranking**: takes JSON predictions and ranks them, so that the highest predictions are prioritised.

This workflow will produce a folder structure that is ready to be interactively visualised using [mtriage-viewer](https://github.com/forensic-architecture/mtriage-viewer/). TODO: link tutorial for mtriage-viewer here and at end.

### YAML configs 

Mtriage workflows are orchestrated using YAML files. When a new component (either an [analsyer](src/lib/analysers) or a [selector](src/lib/selectors) is added to mtriage, we also add an [example YAML](examples) file that shows how to configure and run it. These config files are very simple, and mostly consist of configuration specific to the component that is being run. For example, here is the config for the youtube run we'll do in a second:

```yaml
folder: media/demo_official
phase: select
module: youtube
config:
  search_term: "Triple chaser"
  uploaded_before: "2015-10-02T00:00:00Z"
  uploaded_after: "2015-10-01T00:00:00Z"
  daily: true
```


In order to analyse media with mtriage, we first need to find and download that media. This is the role of selectors: they designate and index a 'media space', and then download the media in that space as local mtriage elements. In this example we'll use the [youtube](src/lib/selectors/youtube) selector, which searches and downloads videos from Youtube.

Some components require a little extra config, such as creating an account for a platform or API and configuring mtriage with credentials, and the youtube selector is an example of this. Read and follow the instructions in the [youtube setup](docs/components/youtube.md) doc, and then return here to continue.

Once you've configured mtriage with youtube credentials, you can run the following command to select some sample media to use the [youtube](src/lib/selectors/youtube) analyser via the config listed above:

```bash
./mtriage run examples/youtube.yaml
```

After running the command, you should start seeing logs indicating that a scrape has been successful and that videos are being downloaded. Once this command has finished, we can sample frames from the downloaded videos using the following config:

```yaml
folder: media/demo_official
phase: analyse
module: frames
config:
  elements_in:
    - youtube
  fps: 1
```

This config specifies that, using the 'media/demo_official' folder as a work directory (in which we just ran the Youtube selector), and the elements created from the 'youtube' selector as input, run the frames analyser. We can run this using the following command:

```bash
./mtriage run examples/frames.yaml
```

Finally we will use the 'yolov3' analyser to detect objects in the frames just sampled. 
Before we run the analyser, we need to download the pretrained 'yolov3' weights:

```bash
cd src/lib/analysers/yolov3/config
bash download_weights.sh
cd ../../../../../
```

This is the config we will use for running the 'yolov3' analyser:

```yaml
folder: media/demo_official
phase: analyse
module: yolov3
config:
  elements_in:
    - youtube/frames
```

We can run the 'yolov3' analyser using the following command:

```bash
./mtriage run examples/youtube.yaml
```

Voila! If you look inside media/demo_official/youtube/derived/yolov3, you should see a set of folders that contain JSON files that contain a set of labels, scores, and frame numbers. In practice, you shouldn't need to dive inside mtriage working directories in this way, as you can use [mtriage-viewer](https://github.com/forensic-architecture/mtriage-viewer) to easily visualise the elements produced by various elements.

TODO: add link to mtriage-viewer tutorial.
TODO: add another section explaining how to chain all three passes using the meta analyser.
