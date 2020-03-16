## Running a Workflow
To get to know mtriage, we're going to run a workflow using four components:

1. **Youtube**: a selector that takes a search term and time period, and the downloads all videos returned from that search as mtriage elements.
2. **Frames**: extracts images at a rate of one frame per second from video elements. 
3. **KerasPretrained**: makes predictions over one or more images using [ResNet50](https://arxiv.org/abs/1512.03385) trained on ImageNet. Predictions are saved in a JSON file.
4. **Rank**: takes JSON predictions produced from KerasPretrained and ranks them, scoring those with more positively predicted frames higher.

### YAML configs 

Mtriage workflows are orchestrated using YAML files. These config files indicate components used to select and/or process media. Most mtriage YAML files are very simple, and mostly consist of configuration specific to the components being run. For example, here is the config for the youtube run we'll do in a second:

```yaml
folder: media/demo_official/1
select:
  name: Local
  config:
    source: data/demo/1local
    # aggregate: true
```


In order to analyse media with mtriage, we first need to 'select' that media from somewhere. Selectors designate and index a 'media space', and then download the relevant media in that space as local mtriage elements (elements are essentially folders). In this example we'll use the [Local](../src/lib/selectors/Local) selector, which simply selects from media already on your computer's file system.


