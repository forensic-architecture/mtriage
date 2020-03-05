# Code for running inference for predicting bounding boxes for canisters in images.

### Description
This code allows to run inference on a list of images using the fewshot detector, trained to detect canisters. The fewshot detector is based on the paper [Few-shot Object Detection via Feature Reweighting](https://arxiv.org/abs/1812.01866), and was trained using the code base in <https://github.com/christegho/Fewshot_Detection> which is a modification of the original repo for the paper <https://github.com/bingykang/Fewshot_Detection>.

### Setup
This code works with Python2.7.
The requiremnents can be downloaded via `pip install -r requirements.txt`.
Training and testing was done on GeForce GTX 1080, with a Driver Version 430.50 and a CUDA Version 10.1.

You need to download the weightfile for the weights of the few shot detector, in addition to the dynamics weights.
```
# copy the weights folder for the fewshot detector within mtriage/src/lib/analysers/fewshot_detector/
gsutil cp -r gs://safariland-element/models/fewshot-detector/weights .
```

### Running Inference
Usage:
```
python3 predict_images.py \
            --weightfile weights/000020.weights \
            --img_dest predictions \
            --valid_images val_can.txt \
            --dynamic_weight_file weights/dynamic_weights.pkl
```

Use script `predict_images.py` to get predicted bounding boxes for the canisters for a list of images which paths are specified in `val_can.txt`. The script draws the predicted bounding boxes with a confidence scores and saves the new images in the file path `predictions`.

Make sure to change the paths accordingly to math the paths on your machine.

There are other arguments you can pass, for explanations:
```python2 predict_images.py -h```

To run inference on a single image, use `prediction_utils.py` as below:
```
python3 prediction_utils.py \
            --weightfile weights/000020.weights \
            --valid_images path_to_image \
            --dynamic_weight_file weights/dynamic_weights.pkl
```
Note the image and the bounding boxes are saved in `test.jpg` when you run `prediction_utils.py`.