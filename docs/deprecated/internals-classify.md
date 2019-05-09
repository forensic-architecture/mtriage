# Phase 3: Classify Images
---

Our classifier takes in a dataset of sampled video frames as images and returns a JSON file containing a list of frames that have been positively identified as containing tanks, along with the prediction scores of these frames and selected YouTube meta data.

![classify_structure.png](src/classify/classify_structure.png)

The code uses three different APIs, [Keras](https://keras.io), [PyTorch](https://pytorch.org/docs/master/) and [DarkNet](https://pjreddie.com/darknet/). PyTorch and Keras are low and high level APIs written in Python. DarkNet is a stand alone API written in C, although there are several open source Python wrappers available. The only major difference between the three is the CNN models that they support by default.

## INPUT to Phase 3

Phase 2 produces a series of folders named by ID of YouTube video, where each folder contains:

1. Metadata from YouTube about the video `meta.json`
2. Folders with frames from the video, named by sampling function (default 
"fps1", frames per second = 1)

Classification of these videos can be performed by calling a Python program `classify/src/main.py`, which takes in a JSON configuration file `$path_to_config.json`.

	python classify/src/main.py $path_to_config [flags]

Optional flags that determines the functionality of the python program are as follows:

	--generate : Generate Predictions (generate full prediction databases from CNN and sampled frames)
	--analyse : Analyse Predictions (analyse prediction databases for prescence of specified class)
	--batch [N] : Maximum video batch size for analysis (default=-1)
	--cpu : Enforce CPU use (default=True)
	--gpu : Enforce GPU use

Selection of CPU and GPU architecture can be be useful when running multiple stages of analysis, since only the generation of prediction databases will benefit greatly from the use of GPUs (NB: if both CPU and GPU flags are called, CPU will override).  

If you are using the DarkNet API, then you will also need to enter the file path to the `darknet` installation folder.

	python classify/src/main.py $path_to_config.json $path_to_darknet_folder [flags]

### Config File: `$path_to_config.json`

The configuration details that are passed into phase 3 are written as a JSON object. An example JSON configuration file for phase 3 is structured as follows:

	{
		"filepath" : "/absolute/path/to/produced-images",
		“labels” :  ["tank"],
		"hardware" : "local",
		"model" : {
			"api" : "keras",
			"classifier" : "MobileNet"
				}
		"sampling": [
			{
				"name" : "fps1",
				"fmt" : "bmp"
			},
			{
				"name" : "fpv10",
				"fmt" : "jpg"
			}
		]
	}

This object includes

`"filepath"` : Absolute file path to sampled video folder produced by phase 2

`"labels"` : List of image object labels to search for

`"hardware"`: Server choice, either `"local"` or `"sherlock"` (cloud based)
	
`"model"`
   : A nested object containing "api" and "classifier" choices
   
`"model["api"]"` : API choice, either `"keras"`, `"pytorch"` or `"darknet"`

`"model["classifier"]"` : Choice of pre-trained CNN used (see list below)

`"sampling"` : A nested object containing multiple `"name"` and `"fmt"` choices
	
`"sampling["name"]"` : Name of video sampling function used to select frames (determines image folder name)
	
`"sampling["fmt"]"` : Format of frame images

The `filepath` and `label` objects always have to be specified. Default settings for the other objects are:

	"hardware" : "local"
	"model["api"]" : "keras"
	"model["classifier"]" : "MobileNet"
	"sampling["name"]" : "fps1"
	"sampling["fmt"]" : "jpg"


Because each classifier supports certain APIs, so the 'api' field needs to be chosen after the 'classifier' field. 
Supported classifiers for each API are listed below. All are trained on the 1000 class ImageNet dataset (http://www.image-net.org).

Classifier | keras | pytorch | darknet|
-----------|:-----:|:------:|:------:|
​[VGG-16](https://arxiv.org/pdf/1409.1556.pdf)    |<span style="color:green">√</span>|<span style="color:green">√</span>|<span style="color:green">√</span>|
​[Inceptionv3](https://arxiv.org/pdf/1409.4842.pdf)  |<span style="color:green">√</span>|<span style="color:green">√</span>|<span style="color:red">X</span>|
​​​[ResNet50](https://arxiv.org/pdf/1512.03385.pdf)   |<span style="color:green">√</span>|<span style="color:green">√</span>|<span style="color:green">√</span>|
​​​​[MobileNet](https://arxiv.org/pdf/1704.04861.pdf)  |<span style="color:green">√</span>|<span style="color:red">X</span>|<span style="color:red">X</span>|
​​​​​[DarkNet19](https://arxiv.org/pdf/1612.08242.pdf) |<span style="color:red">X</span>|<span style="color:red">X</span>|<span style="color:green">√</span>|
​​​​​​[DarkNet53](https://pjreddie.com/media/files/papers/YOLOv3.pdf)  |<span style="color:red">X</span>|<span style="color:red">X</span>|<span style="color:green">√</span>|

Since ImageNet is the data set that is used to train all of the classifiers available by default, any label in ImageNet can be passed as the 'label' option. A few useful ones for military investigations include:
  * tank
  * missile
  * military uniform
  * mortar
  * cannon
  * assault rifle
  * rifle
  * projectile
  * jeep
  * aircraft carrier
  * submarine
  * wreck
  * half track
  * warplane
  A full JSON with all available labels can be found [here](https://s3.amazonaws.com/outcome-blog/imagenet/labels.json).

## OUTPUT from Phase 3

### Results file: `results.json`

An example output JSON object from phase 3 produces is structured as follows:

	{
		"labels" : ["tank"],
		"timestamp" : "datetime",
		"hardware" : "local",
		"classifier" : "MobileNet",
		"positive_threshold" : 35,
		"videos" : {
			vid_id: {
				'title': 'My vid 1',
				'description': 'A video I made...',
				'webpage_url': 'https://youtube.com/watch?v=vid_id',
				'upload_date': '20181201',
				'duration': 131,
				'results' : {label: {'frames': [...],
					'scores': [...]}}
				},
			}
	}
​
This JSON includes the `"labels"`, `"hardware"` and `"model"` objects which are taken directly from the configurational file. Other objects include

`"timestamp"` : Timestamp of when phase 3 finished

`"positive_threshold"` : Ordinal rank within which a classification is considered positive.

`"videos"` : Nested object containing results of video classification

`"videos[vid_id]"` : ID of sampled video produced by phase 2

`"videos[vid_id["title"]]"` : Title of video

`"videos[vid_id["description"]]"` : Description of video

`"videos[vid_id["webpage_url"]]"` : Webpage url of video

`"videos[vid_id["upload_date"]]"` : Uploaded date of video

`"videos[vid_id["duration"]]"` : Duration of video in seconds

`"videos[vid_id["results"][label]["scores"]]"` : List of positive classification scores corresponding to "frames" (%)

`"videos[vid_id["results"][label]["frames"]]"` : List of frames positively classified as label

### Performance Benchmarking

Running on a p2.xlarge Nvidia Tesla K80 GPU (64GB RAM) based on SherlockML, we obtain the following performance using the ImageNet datset.

Speed is mesured in images classified per second; the optimal rank threshold maximises the F1 score for each CNN.

 Model      | Speed (s-1) | Rank (n) | Accuracy (%) | Precision (%) | Recall (%) | F1 (%) |
-----------:|-------------|----------|--------------|----------------|-------------|----------|
VGG16     | 35  |  19   | 95.1  | 98.0  | 95.1  | 96.5
Inception | 58  |  15   | 96.1  | 97.5  | 96.0  | 96.8
ResNet50  | 47  |  24   | 97.2  | 98.0  | 97.2  | 97.6  
MobileNet | 90  |  14   | 97.1  | 98.7  | 97.1  | 97.9
DarkNet19 | 50  |  16   | 97.6  | 99.0  | 96.3  | 97.6
DarkNet53 | 28  |  13   | 98.3  | 99.1  | 97.5  | 98.3



