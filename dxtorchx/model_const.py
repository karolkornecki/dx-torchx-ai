import torch
import torch.nn as nn
from torchvision import models, transforms

# Funkcja sprawdza czy do obliczeń użyty będzie procesor graficzny
def is_gpu():
    return torch.cuda.is_available()


DEVICE = torch.device("cuda" if is_gpu() else "cpu")

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

# średnia i odchylenie standardowe zbioru ImageNET, służy do normalizacji obrazów
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

# normalizator obrazów dla modelu podczas treningu
NORMALIZER_TRAIN = transforms.Compose(
    [
        # dodaje "augmentacje" danych poprzez horizontal-flipping, zgodnie z dokumentem poniżej:
        # "CheXNet: Radiologist-Level Pneumonia Detection on Chest X-Rays with Deep Learning" - Pranav Rajpurkar et al.
        transforms.RandomHorizontalFlip(),
        # zmieniam rozmiar na 256 w krótszym boku
        transforms.Resize(256),
        # a następnie środkuje i przycinam aby otrzymać zdjęcie o rozmiarze 224x224 wymagane przez model w architekturze Densenet
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        # normalizacja z użyciem średniej i odchylenia standardowego zbioru ImageNET
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


def densenet121():
    densenet_model = models.densenet121(
        weights="DEFAULT"
    )  # wagi z treningu na ImageNET
    number_of_input_features = densenet_model.classifier.in_features
    # zmieniam z domyślnej dla DenseNet klasyfikacji 1000 kategorii na 14
    densenet_model.classifier = nn.Sequential(
        nn.Linear(number_of_input_features, NUMBER_OF_CLASSES), nn.Sigmoid()
    )
    densenet_model = densenet_model.to(DEVICE)
    return densenet_model