# Install 

Mtriage is a tool developed at [Forensic Architecture](https://forensic-architecture.org) to orchestrate complex workflows that download media of various kinds, analyse them, and visualise results. To understand what mtriage can do, this tutorial will briefly outline the different components of an mtriage workflow, and then show you how to create one that analyses Youtube videos frame-by-frame with a Resnet50 object detection classifer pretrained on ImageNet. To conclude, we'll briefly touch on how much more mtriage is capable of, and show how it is easy to extend mtriage to analyse other kinds of media. 

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

Mtriage has two primary dependencies: [Python](https://www.python.org/) 3 and [Docker CE](https://docs.docker.com/install/). Mtriage will _probably_ work with Python 2.x as well, but it's untested. If you have a CUDA GPU, you can use [Nvidia Docker](https://github.com/NVIDIA/nvidia-docker) instead of Docker to make certain analysers more performant.

Once you have Python and Docker installed, install the three dependencies in requirements.txt. Two of these are for testing (pytest and black); the only runtime dependency is [pyyaml](https://pyyaml.org/). 
```
cd mtriage
pip install -r requirements.txt
```

Run the test suite to ensure that everython is working. This command may take a while, as the first time you run mtriage it will download the [latest Docker image](https://cloud.docker.com/u/forensicarchitecture/repository/docker/forensicarchitecture/mtriage). Mtriage commands will run much faster after this first one:

```bash
./mtriage dev test
```

Assuming this command completed and all the tests passed, you are now ready to run mtriage workflows! 


