"""
created by: Donghyeon Won
"""
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models


def transform():
    return transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )


def decode(preds):
    classes = [
        "protest",
        "violence",
        "sign",
        "photo",
        "fire",
        "police",
        "children",
        "group_20",
        "group_100",
        "flag",
        "night",
        "shouting",
    ]
    return [(x, preds[c]) for c, x in enumerate(classes)]


class FinalLayer(nn.Module):
    """modified last layer for resnet50 for our dataset"""

    def __init__(self):
        super(FinalLayer, self).__init__()
        self.fc = nn.Linear(2048, 12)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out = self.fc(x)
        out = self.sigmoid(out)
        return out


def modified_resnet50():
    model = models.resnet50(pretrained=True)
    model.fc = FinalLayer()
    return model
