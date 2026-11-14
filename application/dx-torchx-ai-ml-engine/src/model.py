from __future__ import division, print_function

import pandas as pd
from PIL import Image

import torch
import torch.nn as nn
from torchvision import models, transforms

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

PREDICTABLE_CLASSES = [
    "Atelectasis",
    "Cardiomegaly",
    "Effusion",
    "Infiltration",
    "Mass",
    "Nodule",
    "Pneumonia",
    "Pneumothorax",
    "Consolidation",
    "Edema",
    "Emphysema",
    "Fibrosis",
    "Pleural_Thickening",
    "Hernia",
]
NUMBER_OF_CLASSES = len(PREDICTABLE_CLASSES)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

NORMALIZER = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)

NORMALIZER_TRAIN = transforms.Compose(
    [
        transforms.RandomHorizontalFlip(),
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


def densenet121():
    densenet_model = models.densenet121(
        weights="DEFAULT"
    )
    number_of_input_features = densenet_model.classifier.in_features
    densenet_model.classifier = nn.Sequential(
        nn.Linear(number_of_input_features, NUMBER_OF_CLASSES), nn.Sigmoid()
    )
    densenet_model = densenet_model.to(DEVICE)
    return densenet_model


class TrainedModel:
    def __init__(self):
        self.model = self.load_trained_model()
        self.thresholds = (
            pd.read_csv("optimal_class_thresholds.csv")
            .set_index("Class")["Threshold"]
            .to_dict()
        )
        self.y_true = (
            pd.read_csv("y_true.csv")
            .set_index("Image Index")
            .to_dict()
        )

    def load_trained_model(self):
        model = densenet121()
        model.load_state_dict(
            torch.load('trained_model.pth',
                       map_location=DEVICE,
                       weights_only=True,
                       )
        )
        model.eval()
        return model

    def predict_test_image(self, image: Image, image_name: str):
        normalized_image = NORMALIZER(image.convert("RGB"))
        x = normalized_image.unsqueeze(0)
        y_probs = self.model(x).detach().cpu().numpy().reshape(-1)
        predictions = []
        for index, class_name in enumerate(PREDICTABLE_CLASSES):
            predictions.append(
                {
                    "class_name": class_name,
                    "y_prob": round(y_probs[index], 3),
                    "y_predicted": (
                        1 if y_probs[index] > self.thresholds[class_name] else 0
                    ),
                    "y_true": self.get_y_true(class_name, image_name),
                    "threshold": self.thresholds[class_name],
                }
            )
        return pd.DataFrame(predictions)

    def get_y_true(self, class_name, image_name):
        try:
            return self.y_true[class_name][image_name]
        except:
            return 2

    def predict(self, image: Image):
        normalized_image = NORMALIZER(image.convert("RGB"))
        x = normalized_image.unsqueeze(0)
        y_probs = self.model(x).detach().cpu().numpy().reshape(-1)
        predictions = []
        for index, class_name in enumerate(PREDICTABLE_CLASSES):
            predictions.append(
                {
                    "class_name": class_name,
                    "y_prob": y_probs[index],
                    "y_predicted": (
                        1 if y_probs[index] > self.thresholds[class_name] else 0
                    ),
                    "threshold": self.thresholds[class_name],
                }
            )
        return pd.DataFrame(predictions)
