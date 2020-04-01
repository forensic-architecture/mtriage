import numpy as np
import os
import torch
from torch.autograd import Variable
from PIL import Image
from utils import transform, modified_resnet50, decode


def pre_analyse():
    """
    Init the logging, etc
    Init the model
    Same as KerasPretrained
    """
    t = transform()
    model = modified_resnet50()
    model.load_state_dict(
        torch.load("model.pth.tar", map_location=torch.device("cpu"),)["state_dict"]
    )
    model.eval()

    def get_preds(img_path):
        """
        Gives labelds and probabilities for a single image
        This is were we preprocess the image, using a function defined in the model class
        """
        # load image
        img = Image.open(img_path).convert("RGB")
        # process it
        x = t(img)
        # get in in the right format
        x = Variable(x).unsqueeze(0)
        # predictions
        output = model(x)
        # decode
        output = decode(output.cpu().data.numpy()[0])

        # filter
        # return pred, proba
        return output

    return get_preds("image.jpg")


print(pre_analyse())
