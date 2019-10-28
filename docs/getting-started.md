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

Once you have a Python and a Docker installed, run the test suite to ensure that everython is working. This command may take a while, as the first time you run mtriage it takes some time to appropriately prepare. Mtriage commands will run much faster afterwards:

```bash
cd mtriage
./mtriage test
```

Assuming this command completed and all the tests passed, you are now ready to run mtriage workflows. 

## Creating a workflow
To get to know mtriage, we're going to create a workflow that uses four components components:
1. Youtube (selector)
2. Frames (analyser)
3. YOLOv3 (analyser)

This workflow will yield an interactive visualisation of where objects are detected in videos that looks as follows (each cell represents a video, and red frames represent an object detection):

TODO: add picture.

TODO: add CLI commands to specify once done.
