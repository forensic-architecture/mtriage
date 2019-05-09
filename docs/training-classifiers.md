## Training Classifiers 

ALl the classifiers supported by our code are trained on the 1000 class ImageNet dataset by default. If you want to see the labels available, please refer to [Classify-read-me](docs/Classify-Read-Me.md). If you would like to train the classifiers on other data sets, here you can find a list of some existing options:  


#### Supervisely
The most straightforward method for creating models is to use the platform [supervisely](https://supervise.ly/). This platform provides a way to annotate data, prepare a synthetic data set, train models, and download them without ever having to bring up an ipython notebook.

(nb: supervisely is a web platform, but needs cloud configuration or CUDA hardware. TODO)
(Q: should I be explaining how to use supervisely in more detail? I have been reading about it but not sure)

#### Tensorflow
Another way to train models is to use the process documented in [tensorflow for poets](https://codelabs.developers.google.com/codelabs/tensorflow-for-poets/index.html?index=..%2F..%2Findex#0). This is a great way to train a basic image classifier with various categories, which doesn't require any bounding box annotation (you label the training set by putting them in appropriate folders).

#### Keras
The third and perhaps most flexible way to train models is using [keras](https://keras.io/), and generalising the methodology from [this excellent 11-part series on keras and python](https://pythonprogramming.net/loading-custom-data-deep-learning-python-tensorflow-keras/).

### Installation
In the [tensorflow](/tensorflow) directory there are scripts to setup a ready-made environment in [Docker](https://www.docker.com/) for training models using tensorflow and keras. You can also refer to the [README](docs/README.md)] for a brief explanation of how to install and use Docker. 

```bash
cd tensorflow  [Q: is this directory supposed to be one of the folders that are included in the github download? I don't see any directory called tensorflow at the moment; alternatively, are they supposed to download tensorflow manually?]
sh setup.sh # downloads tensorflow models and builds Docker image locally
sh run.sh # starts Docker container with appropriate volume/port mapping
```
Visit [http://localhost:8080](http://localhost:8080) and use the token displayed in the console after running the last command. Tensorboard is also available at [http://localhost:6006](http://localhost:6006)


### training data
#### google images
the excellent CLI `google_images_download` is part of the Pipfile. to retrieve more than 100 images at a time, you need to download [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads), unzip, and pass the appropriate path to the binary. the suggestion is to put the binary in `/usr/local/bin`, and then you can copy and paste the following command to download images for a search:

```bash
googleimagesdownload --keywords "tanks" --limit 1000 --chromedriver /usr/local/bin/chromedriver
```

another handy tool is [findimagedupes](https://gitlab.com/opennota/findimagedupes), especially if you are creating datasets by interweaving google searches (which will inevitably have overlapping images returned).
