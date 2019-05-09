## Crawling
This is the main infrastructure that exists in this repo. This document specifies the current way of deploying the scripts through the terminal. At the moment, the CLI is not finalized and the arguments need to be specified in the files, as explained below. Future versions will allow the user to specify parameters directly through the CLI. 

The crawler currently functions in three stages: 

Phase 1: Search
 * [crawler/youtube/1.index](crawler/youtube/1.index) 

 It queries the youtube API with a search term and a range of dates. This generates a  CSV/XLS file that includes YouTube videos uploaded within that range of dates and that include the search term in the title. Before running the script, modify the search term, dates, and output folder in the file [1.index](crawler/youtube/1.index). Once ready, run:  
```bash
sh 1.index.sh
```
A results folder is then created with a 'results.csv' and a 'logs.txt'. Logs are also printed to STDOUT as the scrape runs.

Phase 2: Retrieve
 * [crawler/youtube/2.retrieve](crawler/youtube/2.retrieve)  
 
 It downloads all videos in the CSV file generated from '1.index'. It then samples the files to produce one image set per video. The default sampling algorith is one frame per second.

 ```bash
sh 2.retrieve.sh
```
The output of phase 2 is a series of folders named by the ID of each YouTube video, where each folder contains metadata from YouTube as a json objects, and folders with frames from the video.

Phase 3: Classify
 * [crawler/youtube/3.classify](crawler/youtube/3.classify) 

It takes in a dataset of sampled video frames as image files and returns a JSON file containing a list of frames that have been positively identified as containing a specified object, along with the prediction scores of these frames and selected YouTube meta data. For the time being, we generate the configuration object with a small script that is triggered as follows: 
 ```bash
sh 3.classify.sh
```
At the moment, the different parameters need to be specified in the file [3.classify.sh](crawler/youtube/3.classify). These parameters include the input path, hardware, api, classifier, and label. 

Before running, please refer to the more detailed documentation specific to this phase, which you can find in [internals-classify](docs/internals-classify.md).

