Code for running inference for predicting bounding boxes for canisters in images.

Setup

This code works with Python2.7 and was run using a GeForce GTX 1080.
The Driver Version is 430.50 and the CUDA Version is 10.1.

You need to download the weightfile for the weights of the few shot detector, in addition to the dynamics weights.
wget 


```python2 predict_images.py --weightfile weights/000020.weights --img_dest predictions --valid_images val_can.txt```
The main arguments you need to pass for the script `predict_image.py` are 
--valid_images: path for the text file with the list of images to run inference on

                       
For help about the rest of the arguments for predict_image.py:
```python2 predict_images.py -h```

The training code used for obtaining the weights is in https://github.com/christegho/Fewshot_Detection which is a modified version of the original code for the paper 