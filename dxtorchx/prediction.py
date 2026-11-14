from __future__ import division, print_function

import os
import os.path

import pandas as pd
import torch
from PIL.ImageFile import ImageFile

from dxtorchx.model_const import densenet121, NORMALIZER, PREDICTABLE_CLASSES, DEVICE

TRAINED_MODEL_DIR = os.path.join("final_model", "results_DENSENET_121_RELEASE")
TRAINED_MODEL_NAME = "checkpoint_DENSENET_121_RELEASE.pth"
TRAINED_MODEL_OPTIMAL_THRESHOLD_FILE = "optimal_class_thresholds.csv"
TRAINED_MODEL_Y_TRUE = "y_true_DENSENET_121_RELEASE.csv"


class TrainedModel:
    def __init__(self):
        self.model = self.load_trained_model()
        self.thresholds = (
            pd.read_csv(
                os.path.join(TRAINED_MODEL_DIR, TRAINED_MODEL_OPTIMAL_THRESHOLD_FILE)
            )
            .set_index("Class")["Threshold"]
            .to_dict()
        )
        self.y_true = (
            pd.read_csv(os.path.join(TRAINED_MODEL_DIR, TRAINED_MODEL_Y_TRUE))
            .set_index("Image Index")
            .to_dict()
        )

    @staticmethod
    def load_trained_model():
        model = densenet121()
        model.load_state_dict(
            torch.load(
                str(os.path.join(TRAINED_MODEL_DIR, TRAINED_MODEL_NAME)),
                map_location=DEVICE,
                weights_only=True,
            )
        )
        model.eval()
        return model

    def predict_test_image(self, image: ImageFile, image_name: str):
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
                    "y_true": self.y_true[class_name][image_name],
                }
            )
        return pd.DataFrame(predictions)

    def predict(self, image: ImageFile):
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
                }
            )
        return pd.DataFrame(predictions)
